# Python standard lib imports
import json
import os
import logging
import time

# Django imports
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.conf import settings

# Third-party imports
import boto3, botocore
from celery.result import AsyncResult

# Local imports
from .forms import DataForm
from .models import Column, Table, Contact
from .utils import get_column_types
# Have to do an absolute import here for celery. See
# http://docs.celeryproject.org/en/latest/userguide/tasks.html#task-naming-relative-imports
from upload.tasks import load_infile


#------------------------------------#
# Take file uploaded by user, use
# csvkit to generate a DB schema, and write
# to an SQL table. Copy file and related 
# information to S3 bucket.
#------------------------------------#
# TODO accept more than one file
@login_required
def upload_file(request):
    # Get form data, assign default values in case it's missing information.
    form = DataForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            # Assign form values to variables
            table_name = form.cleaned_data['table_name']
            path = '/tmp/{}.csv'.format(table_name)

            # Handle uploaded file in chunks so we don't overwhelm the system's memory
            with open(path, 'wb+') as f:
                for chunk in request.FILES['data_file'].chunks():
                    f.write(chunk)

            # Store the table config details in session storage so that other views can
            # access it.
            request.session['table_params'] = {
                'path': path,
                'delimiter': form.cleaned_data['delimiter'],
                'db_name': form.cleaned_data['db_name'],
                'source': form.cleaned_data['source'],
                'table_name': table_name
            }

            return redirect('/categorize/')

    # If request method isn't POST or if the form data is invalid
    return render(request, 'upload/file-select.html', {'form': form})

#------------------------------------#
# Prompt the user to select categories
# for each column in the data, then
# begin upload task
#------------------------------------#
@login_required
def categorize(request):
    # Infer column datatypes
    path = request.session['table_params']['path']
    headers = get_column_types(path)
    request.session['headers'] = headers

    context = {
        'headers': headers,
        'ajc_categories': Column.INFORMATION_TYPE_CHOICES,
        'datatypes': Column.MYSQL_TYPE_CHOICES
    }

    return render(request, 'upload/categorize.html', context)


#------------------------------------#
# Poll to check the completion status of celery 
# task. If task has succeeded, return a sample of the
# data. If failed, return error message
#------------------------------------#
@login_required
def check_task_status(request):
    p_id = request.session['task_id']
    response = AsyncResult(p_id)
    data = {
        'status': response.status,
        'result': response.result
    }

    # If the task is successful, write information about the upload to the Django DB
    if data['status'] == 'SUCCESS' and not data['result']['error']:
        # Create a table object in the database only if the write to the AJC
        # DB is successful
        params = request.session['table_params']
        t = Table(
            table=params['table_name'],
            database=params['db_name'],
            user=request.user,
            source=params['source']
        )

        # Create column objects for each column in the headers list
        for header in request.session['headers']:
            c = Column(table=t, 
                column=header['name'],
                mysql_type=header['datatype'],
                information_type=header['category'],
                column_size=header['length']
            )

        t.save()
        c.save()

    try:
        return JsonResponse(data)
    except TypeError:
        gt

@login_required
def upload(request):
    # Begin load data infile query as a separate task so it doesn't slow response
    # load_infile accepts the following arguments:
    # (db_name, table_name, path, delimiter=',')
    # TODO figure out how to validate a programatically generated form
    if request.method == 'POST':
        params = request.session['table_params']
        fparams = {key: value for key, value in params.items() if key != 'source'}

        task = load_infile.delay(**fparams)
        request.session['task_id'] = task.id # Use the id to poll Redis for task status
        headers = request.session['headers']

        keys = [x for x in request.POST if x != 'csrfmiddlewaretoken']
        for key in keys:
            # Stupidly complex logic to get the key of the dict item with a name matching the 
            # current name. Set that headers category value
            hindex = [i for i, val in enumerate(headers) if headers[i]['name'] == key][0]
            headers[hindex]['category'] = request.POST[key]

        return render(request, 'upload/upload.html', {'table': request.session['table_params']['table_name']})

#------------------------------------#
# Log a user out
#------------------------------------#
def logout_user(request):
    logout(request)
    messages.add_message(request, messages.ERROR, 'You have been logged out')
    return redirect('/login/')

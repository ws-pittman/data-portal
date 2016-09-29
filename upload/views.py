# Python standard library imports
import subprocess

# Django imports
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.template import RequestContext

# Third-party imports
import boto3, botocore
import csvkit

def upload_file(request):
    if request.method == 'POST':
        messages.add_message(request, messages.ERROR, 'A file with that name already exists')
        return HttpResponseRedirect('/')
        fcontent = request.FILES['file-input'].read()
        fkey = request.FILES['file-input'].name

        # Access bucket using credentials in ~/.aws/credentials
        s3 = boto3.resource('s3')
        bucket = s3.Bucket('ajc-data-warehouse')

        # Check if a file with the same name already exists in the
        # S3 bucket, and if so throw an error
        try:
            bucket.download_file(fkey, '/tmp/boto_test')
        except botocore.exceptions.ClientError:
            pass

        # Write the file to the /tmp/ directory, then use
        # csvkit to generate the CREATE TABLE query
        path = '/tmp/' + fkey
        with open(path, 'w') as f:
            f.write(fcontent)
        
        query = subprocess.check_output(['csvsql', path])

        # Return a preview of the top few rows in the table
        # and check if the casting is correct
        # Return a log of the issues that need to be fixed

        # Write the file to Amazon S3
        bucket.put_object(Key=fkey, Body=fcontent)
        return HttpResponse('File uploaded to S3.<br> Query: ' + query)


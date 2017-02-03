# Django imports
from django.shortcuts import render

# Local module imports
#from .forms import DataForm
from .utils import warehouse_search, table_search

def search(request):
    results = []
    context = {'results': results}

    if request.method == 'POST':
        query = request.POST.get('query', None)
        context['query'] = query
        context['results'] = warehouse_search(query)

    return render(request, 'search/search.html', context)


def show_full_dataset(request):
    results = []

    if request.method == 'POST':
        query = request.POST.get('query', None)
        table = request.POST.get('table', None)
        search_columns = request.POST.get('search_columns', None)
        preview = False

        results.append(table_search(query, table, search_columns, preview))

    return render(request,'search/search.html', {'results': results})


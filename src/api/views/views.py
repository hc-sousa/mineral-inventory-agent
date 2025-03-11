from django.shortcuts import render

from src import settings

# Create your views here.
def index(request):
    return render(request, 'app/index.html')
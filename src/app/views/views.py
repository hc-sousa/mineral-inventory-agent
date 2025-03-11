from django.shortcuts import render
from django.core.mail import send_mail

from src import settings

# Create your views here.
def index(request):
    return render(request, 'app/index.html')

def product(request):
    return render(request, 'app/product/product_page.html')
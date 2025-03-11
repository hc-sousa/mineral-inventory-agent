from django.urls import path
from api import views

urlpatterns = [
    path('', views.index, name='index'),
    
    #v1
    path('v1/', views.index, name='index'),
]
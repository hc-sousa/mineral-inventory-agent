"""src URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from api import views
from django.conf import settings

urlpatterns = [
    path('dashboard/admin/', admin.site.urls),
    path('', include('user_management.urls')),
    path('api/', include('api.urls')),
    path('__reload__/', include('django_browser_reload.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('media/<path:path>', views.fetch_media, name='get_media'),
]

if 'allauth' in settings.INSTALLED_APPS:
    urlpatterns.append(path('accounts/', include('allauth.urls')))

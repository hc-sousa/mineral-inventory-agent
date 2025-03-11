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
from app import views
from django.conf import settings

urlpatterns = [
    path('dashboard/admin/', admin.site.urls),
    path('', include('user_management.urls')),
    path('__reload__/', include('django_browser_reload.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('media/<path:path>', views.fetch_media, name='get_media'),
]

if 'landing_page' in settings.INSTALLED_APPS:
    urlpatterns.append(path('', include('landing_page.urls')))
    urlpatterns.append(path('app/', include('app.urls')))
else:
    urlpatterns.append(path('', include('app.urls')))
    
if 'documentation' in settings.INSTALLED_APPS:
    urlpatterns.append(path('docs/', include('documentation.urls')))

if 'allauth' in settings.INSTALLED_APPS:
    urlpatterns.append(path('accounts/', include('allauth.urls')))

if 'stripe_payments' in settings.INSTALLED_APPS:
    urlpatterns.append(path('payment/', include('stripe_payments.urls')))

if 'legal' in settings.INSTALLED_APPS:
    urlpatterns.append(path('legal/', include('legal.urls')))

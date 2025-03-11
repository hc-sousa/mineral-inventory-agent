from django.conf import settings

def project_name(request):
    return {
        'PROJECT_NAME': settings.PROJECT_NAME
    }

def google_analytics_id(request):
    return {'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID}
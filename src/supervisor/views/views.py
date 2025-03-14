from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

def supervisor_dashboard(request):
    """
    Render the supervisor dashboard page
    """
    return render(request, 'supervisor/dashboard.html', {
        'title': 'Supervisor Dashboard',
    })

@login_required
def agent_settings(request):
    """
    Render the agent settings page
    """
    return render(request, 'supervisor/settings.html', {
        'title': 'Agent Settings',
    })

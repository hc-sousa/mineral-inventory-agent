from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from supervisor.views.requests import user_request

def chat_home(request):
    """
    Render the chat interface home page
    """
    return render(request, 'chat/index.html')

@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """
    Handle incoming chat messages and forward them to the orchestration layer
    """
    try:
        # Pass the request directly to the user_request function
        # This ensures we get all the functionality including mineral data
        return user_request(request)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

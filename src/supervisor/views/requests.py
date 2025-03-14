from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
@require_http_methods(["POST"])
def user_request(request):
    """
    Handle incoming chat messages and forward them to the orchestration layer
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        
        # For demo purposes, just echo back the message
        response_data = {
            'success': True,
            'reply': f"Echo: {user_message}",
            'message_id': 123  # This would come from your orchestration layer
        }
        
        return JsonResponse(response_data)
         
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

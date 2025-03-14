from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
from supervisor.utils.utils import process_user_request

@csrf_exempt
@require_http_methods(["POST"])
def user_request(request):
    """
    Handle incoming chat messages and forward them to the supervisor agent
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        conversation_id = data.get('conversation_id', str(uuid.uuid4()))
        
        # Use the langchain-based supervisor agent to process the request
        response_data = process_user_request(user_message, conversation_id)
        
        # Include any potential mineral data for the form
        # This is a placeholder for potential future integration
        # where the agent might extract structured mineral data
        mineral_data = {}
        
        # Check if response contains any extractable mineral information
        # This would require more sophisticated parsing in a real implementation
        if response_data.get('success', False) and "mineral_data" in response_data:
            mineral_data = response_data["mineral_data"]
        
        return JsonResponse({
            'success': response_data.get('success', False),
            'reply': response_data.get('reply', ''),
            'message_id': response_data.get('message_id', None),
            'conversation_id': conversation_id,
            'mineral_data': mineral_data
        })
         
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

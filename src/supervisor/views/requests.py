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
        conversation_history = data.get('conversation_history', [])
        
        print(f"Processing request with message: '{user_message}' and conversation_id: {conversation_id}")
        
        # Use the langchain-based supervisor agent to process the request
        response_data = process_user_request(
            user_message, 
            conversation_id=conversation_id, 
            conversation_history=conversation_history
        )
        
        # Include any potential mineral data for the form
        mineral_data = {}
        
        # Check if response contains any extractable mineral information
        if response_data.get('success', False) and "mineral_data" in response_data:
            mineral_data = response_data["mineral_data"]
            print(f"Sending mineral data to frontend: {mineral_data}")
            
            # Explicitly check for price fields
            price_fields = ['starting_price', 'reserve_price', 'buy_now_price']
            for field in price_fields:
                if field in mineral_data:
                    print(f"Price field {field} = {mineral_data[field]} (type: {type(mineral_data[field])})")
        
        return JsonResponse({
            'success': response_data.get('success', False),
            'reply': response_data.get('reply', ''),
            'message_id': response_data.get('message_id', None),
            'conversation_id': conversation_id,
            'mineral_data': mineral_data
        })
         
    except Exception as e:
        print(f"Error in user_request: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

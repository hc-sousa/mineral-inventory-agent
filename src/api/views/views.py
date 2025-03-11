from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view

@api_view(["GET"])
@extend_schema(
    summary='Test Connection Endpoint',
    description='''\
This endpoint is used to check if the API is operational.
It returns a JSON object indicating the connection status. 
Use this endpoint as a health-check for the API.
Example response:
{
  "status": "ok"
}
''',
    responses={
        200: {
            'type': 'object',
            'properties': {
                'status': {
                    'type': 'string',
                    'description': 'A message indicating that the API is working correctly.',
                    'example': 'ok'
                }
            }
        }
    },
    examples=[
        {
            'description': 'A successful connection check example',
            'value': {'status': 'ok'}
        }
    ]
)
def test_connection(request):
    """
    Test Connection API

    Checks if the API is responsive. Returns a JSON response with status.
    """
    return JsonResponse({'status': 'ok'})
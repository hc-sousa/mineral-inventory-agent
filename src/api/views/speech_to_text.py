import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ..utils.speech_to_text import convert_audio_to_text, save_uploaded_file


@method_decorator(csrf_exempt, name='dispatch')
class SpeechToTextView(APIView):
    """API view to handle speech-to-text conversion requests."""
    
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        """
        Handle POST request with audio file upload.
        
        Expected request format:
        - multipart/form-data with an 'audio' field containing the audio file
        
        Returns:
            Response with transcribed text or error message
        """
        if 'audio' not in request.FILES:
            return Response(
                {"error": "No audio file provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        audio_file = request.FILES['audio']
        
        # Check file extension (be more permissive with browser-recorded audio)
        file_name = audio_file.name
        file_extension = os.path.splitext(file_name)[1].lower() if '.' in file_name else '.wav'
        supported_extensions = ['.wav', '.wave', '.webm', '.ogg', '.mp3']
        
        if file_extension and file_extension not in supported_extensions:
            return Response(
                {"error": f"Unsupported audio format. Supported formats: {', '.join(supported_extensions)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save the uploaded file temporarily
        temp_file_path = save_uploaded_file(audio_file, file_extension)
        
        if not temp_file_path:
            return Response(
                {"error": "Failed to process uploaded file"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        try:
            # Process the audio file and convert to text
            result = convert_audio_to_text(temp_file_path)
            
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            if result["status"] == "success":
                return Response({"text": result["text"]}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": result["message"]},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
        except Exception as e:
            # Clean up the temporary file in case of any exception
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

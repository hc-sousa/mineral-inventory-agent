import mimetypes
import os
from django.http import FileResponse, JsonResponse

from src import settings

def get_media(path):
    media_root = settings.MEDIA_ROOT
    file_path = os.path.join(media_root, path)
    if os.path.exists(file_path):
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        file = open(file_path, 'rb')
        response = FileResponse(file, content_type=content_type)
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
        
        return response
    return JsonResponse({'error': 'File not found'}, status=404)
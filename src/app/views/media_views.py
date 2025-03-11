

from django.views.decorators.http import require_GET
from app.utils.media_utils import get_media

@require_GET
def fetch_media(request, path):
    return get_media(path)
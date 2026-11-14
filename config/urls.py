import mimetypes

from django.contrib import admin
from django.core.files.storage import default_storage
from django.http import FileResponse, Http404
from django.urls import path, include
from django.conf import settings


def serve_local_media(request, path):
    try:
        media_file = default_storage.open(path, 'rb')
    except (FileNotFoundError, ValueError):
        raise Http404('Media file not found')
    content_type = mimetypes.guess_type(path)[0] or 'application/octet-stream'
    return FileResponse(media_file, content_type=content_type)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portfolio.urls')),
]

if not settings.CLOUDINARY_CONFIGURED:
    urlpatterns += [
        path('media/<path:path>', serve_local_media, name='local_media'),
    ]

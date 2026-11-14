<<<<<<< HEAD
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
=======
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
>>>>>>> 07de66dde5064f8633f14e637dc81016f6857888

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portfolio.urls')),
]

<<<<<<< HEAD
if not settings.CLOUDINARY_CONFIGURED:
    urlpatterns += [
        path('media/<path:path>', serve_local_media, name='local_media'),
    ]
=======
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
>>>>>>> 07de66dde5064f8633f14e637dc81016f6857888

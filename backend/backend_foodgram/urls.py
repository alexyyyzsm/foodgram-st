from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from api.utils import recipe_absolute_uri


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('link/<str:short_link>', recipe_absolute_uri),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

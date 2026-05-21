from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('events.urls')),
    path('users/', include('users.urls')),

    #built-in django authentication system 
    path('accounts/', include('django.contrib.auth.urls')),

    path('', include('pages.urls')),
    path("tickets/", include("tickets.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

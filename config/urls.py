from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('events.urls')),
    path('users/', include('users.urls')),

    #built-in django authentication system 
    path('accounts/', include('django.contrib.auth.urls')),

    #path("tickets/", include("tickets.urls")),
    #path("pages/", include("pages.urls")),
]

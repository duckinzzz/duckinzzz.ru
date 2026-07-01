from django.contrib import admin
from django.urls import path, include

from config.views import health, ready

handler404 = 'frontend.views.page_not_found'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health, name='health'),
    path('ready/', ready, name='ready'),
    path('', include('frontend.urls')),
    path('', include('crstats.urls')),
    path('', include('botstats.urls')),
]

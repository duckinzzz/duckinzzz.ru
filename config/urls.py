from django.contrib import admin
from django.urls import path, include

handler404 = 'frontend.views.page_not_found'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('frontend.urls')),
    path('', include('crstats.urls')),
]

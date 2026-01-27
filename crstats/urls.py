from django.urls import path
from . import views

urlpatterns = [
    path('clech-stats/', views.index, name='crstats_index'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('clech-stats/', views.index, name='crstats_index'),
    path('clech-stats/api/player/<str:name>/', views.player_data, name='crstats_player_data'),
]

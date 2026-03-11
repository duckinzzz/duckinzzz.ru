from django.urls import path

from . import views


app_name = 'killanews'

urlpatterns = [
    path('news/', views.news_index, name='news_index'),
    path('news/<slug:news_slug>/', views.news_detail, name='news_detail'),
    path('news/<slug:news_slug>/<path:asset_path>', views.news_asset, name='news_asset'),
]

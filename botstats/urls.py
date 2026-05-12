from django.urls import path

from . import views

app_name = 'botstats'

urlpatterns = [
    path('botstats/api/', views.BotDataListCreate.as_view(), name='api'),
    path('botstats/', views.botstats_page, name='index'),
    path('botstats/login/', views.login_view, name='login'),
    path('botstats/logout/', views.logout_view, name='logout'),
]

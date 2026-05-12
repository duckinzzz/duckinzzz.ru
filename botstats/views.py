from functools import wraps

from django.conf import settings
from django.shortcuts import redirect, render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BotData
from .serializers import BotDataSerializer


def login_required_page(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('botstats_authed'):
            return redirect('botstats:login')
        return view(request, *args, **kwargs)
    return wrapper


class BotDataListCreate(APIView):
    def get(self, request):
        queryset = BotData.objects.all()
        bot_name = request.query_params.get('bot_name')
        if bot_name:
            queryset = queryset.filter(bot_name=bot_name)

        serializer = BotDataSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        token = request.data.get('token')
        if token != settings.BOTSTATS_API_TOKEN:
            return Response({'error': 'invalid token'}, status=status.HTTP_403_FORBIDDEN)

        serializer = BotDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def login_view(request):
    error = None
    if request.method == 'POST':
        if request.POST.get('password') == settings.BOTSTATS_API_TOKEN:
            request.session['botstats_authed'] = True
            return redirect('botstats:index')
        error = 'Wrong password'

    return render(request, 'botstats/login.html', {'error': error})


def logout_view(request):
    request.session.pop('botstats_authed', None)
    return redirect('botstats:login')


@login_required_page
def botstats_page(request):
    bot_name_filter = request.GET.get('bot_name', '')
    entries = BotData.objects.all()
    bot_names = BotData.objects.order_by().values_list('bot_name', flat=True).distinct()

    if bot_name_filter:
        entries = entries.filter(bot_name=bot_name_filter)

    return render(request, 'botstats/index.html', {
        'entries': entries,
        'bot_names': bot_names,
        'selected_bot': bot_name_filter,
    })

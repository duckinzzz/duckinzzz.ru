from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BotData
from .serializers import BotDataSerializer


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

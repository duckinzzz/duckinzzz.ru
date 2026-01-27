from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from .models import BattleLog

PLAYERS = {
    "#UY2VY9YUG": "grandison",
    "#Q8899QUY": "(-РашеР-)",
    "#289U8CQR2": "duckinzzz",
    "#VG9CR9R2J": "Шапа Шуточкин",
    "#20QP9JGGRQ": "клечик нямочкин",
    "#RLJVGUJL": "Lucky",
    "#22009JPCCQ": "flamboyx",
}

def humanize_time(delta):
    minutes = int(delta.total_seconds() // 60)
    hours = minutes // 60
    days = hours // 24

    if minutes < 60:
        return f"{minutes} мин назад"
    elif hours < 24:
        return f"{hours} час назад" if hours == 1 else f"{hours} часов назад"
    else:
        return f"{days} день назад" if days == 1 else f"{days} дней назад"


def index(request):
    data = {}

    for tag, name in PLAYERS.items():
        logs = BattleLog.objects.filter(player_tag=tag).order_by('battle_time')
        data[name] = {
            'x': list(range(1, len(logs) + 1)),
            'y': [log.starting_trophies + log.trophy_change for log in logs],
            'custom': [
                {
                    'battle_time': log.battle_time.strftime("%d.%m.%Y %H:%M"),
                    'change': log.trophy_change,
                    'enemy': log.enemy_tag
                }
                for log in logs
            ]
        }

    now = timezone.now()

    last_battles = BattleLog.objects.order_by('-battle_time')[:10]

    last_battles_data = [
        {
            "player": PLAYERS.get(log.player_tag, log.player_tag),
            "before": log.starting_trophies,
            "change": log.trophy_change,
            "ago": humanize_time(now - log.battle_time),
        }
        for log in last_battles
    ]

    return render(
        request,
        "crstats/index.html",
        {
            "data": data,
            "default_player": "Шапа Шуточкин",
            "last_battles": last_battles_data,
        }
    )

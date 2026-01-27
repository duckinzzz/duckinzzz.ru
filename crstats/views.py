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

    return render(request, "crstats/index.html", {"data": data, "default_player": "Шапа Шуточкин"})

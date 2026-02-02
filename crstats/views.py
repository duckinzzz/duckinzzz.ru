from datetime import timedelta

from django.shortcuts import render
from django.utils import timezone

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

base_lvl = {
    'common': 1,
    'rare': 3,
    'epic': 6,
    'legendary': 9,
    'champion': 11,
}


def russian_plural(n, forms):
    n = abs(n) % 100
    if 11 <= n <= 14:
        return forms[2]
    n = n % 10
    if n == 1:
        return forms[0]
    if 2 <= n <= 4:
        return forms[1]
    return forms[2]


def humanize_time(delta):
    seconds = int(delta.total_seconds())
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24

    if seconds < 60:
        return f"{seconds} {russian_plural(seconds, ['секунда', 'секунды', 'секунд'])} назад"
    elif minutes < 60:
        return f"{minutes} {russian_plural(minutes, ['минута', 'минуты', 'минут'])} назад"
    elif hours < 24:
        return f"{hours} {russian_plural(hours, ['час', 'часа', 'часов'])} назад"
    else:
        return f"{days} {russian_plural(days, ['день', 'дня', 'дней'])} назад"


def battle_info_from_raw(raw):
    def format_cards(cards):
        return [
            {
                'name': card['name'],
                'level': card['level'] + base_lvl[card['rarity']] - 1,
                'rarity': card['rarity'],
                'elixirCost': card.get('elixirCost', 0),
                'iconUrls': card['iconUrls'],
                'isEvo': 'True' if card.get('evolutionLevel') else 'False'
            }
            for card in cards
        ]

    p, e = raw['team'][0], raw['opponent'][0]

    return {
        'player': {'crowns': p['crowns'], 'cards': format_cards(p['cards'])},
        'enemy': {'nickname': e['name'], 'crowns': e['crowns'], 'cards': format_cards(e['cards'])}
    }


def index(request):
    data = {}

    MAX_BATTLES_PER_PLAYER = 1000

    recent_cutoff = timezone.now() - timedelta(days=7)

    for tag, name in PLAYERS.items():
        logs = BattleLog.objects.filter(
            player_tag=tag,
            battle_time__gte=recent_cutoff
        ).order_by('battle_time')[:MAX_BATTLES_PER_PLAYER]

        logs_list = list(logs)

        data[name] = {
            'x': list(range(1, len(logs_list) + 1)),
            'y': [log.starting_trophies + log.trophy_change for log in logs_list],
            'custom': [
                {
                    'battle_time': log.battle_time.isoformat(),
                    'change': log.trophy_change,
                    'enemy': log.enemy_tag,
                    'battle_info': battle_info_from_raw(log.raw_data)
                }
                for log in logs_list
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

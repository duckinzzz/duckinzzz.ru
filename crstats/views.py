import json

from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.utils import timezone
from django.utils.safestring import mark_safe

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

NAME_TO_TAG = {name: tag for tag, name in PLAYERS.items()}

base_lvl = {
    'common': 1,
    'rare': 3,
    'epic': 6,
    'legendary': 9,
    'champion': 11,
}

CHART_BATTLES_PER_PLAYER = 30
DEFAULT_PLAYER = "Шапа Шуточкин"


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


def build_player_payload(tag, catalog):
    """Build a player's chart payload and merge any new cards into `catalog`.

    Cards inside `battle_info` are stored as light refs: {id, level, isEvo}.
    The shared `catalog` maps id -> {name, rarity, elixirCost, iconUrls}.
    """
    latest_logs = BattleLog.objects.filter(player_tag=tag).order_by('-battle_time')[:CHART_BATTLES_PER_PLAYER]
    logs_list = list(reversed(latest_logs))

    def card_ref(card):
        cid = card['id']
        if cid not in catalog:
            catalog[cid] = {
                'name': card['name'],
                'rarity': card['rarity'],
                'elixirCost': card.get('elixirCost', 0),
                'iconUrls': card['iconUrls'],
            }
        return {
            'id': cid,
            'level': card['level'] + base_lvl[card['rarity']] - 1,
            'isEvo': bool(card.get('evolutionLevel')),
        }

    def battle_info(raw):
        p, e = raw['team'][0], raw['opponent'][0]
        return {
            'player': {'crowns': p['crowns'], 'cards': [card_ref(c) for c in p['cards']]},
            'enemy': {'nickname': e['name'], 'crowns': e['crowns'], 'cards': [card_ref(c) for c in e['cards']]},
        }

    return {
        'x': list(range(1, len(logs_list) + 1)),
        'y': [log.starting_trophies + log.trophy_change for log in logs_list],
        'custom': [
            {
                'battle_time': log.battle_time.isoformat(),
                'change': log.trophy_change,
                'enemy': log.enemy_tag,
                'battle_info': battle_info(log.raw_data),
            }
            for log in logs_list
        ],
    }


def index(request):
    catalog = {}
    default_tag = NAME_TO_TAG.get(DEFAULT_PLAYER)
    initial_data = {DEFAULT_PLAYER: build_player_payload(default_tag, catalog)}

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

    def js(value):
        return mark_safe(json.dumps(value, ensure_ascii=False).replace('</', '<\\/'))

    return render(
        request,
        "crstats/index.html",
        {
            "data_json": js(initial_data),
            "cards_catalog_json": js(catalog),
            "players_json": js(list(PLAYERS.values())),
            "default_player": DEFAULT_PLAYER,
            "last_battles": last_battles_data,
        }
    )


def player_data(request, name):
    tag = NAME_TO_TAG.get(name)
    if not tag:
        raise Http404("unknown player")
    catalog = {}
    payload = build_player_payload(tag, catalog)
    return JsonResponse({"player": payload, "catalog": catalog})

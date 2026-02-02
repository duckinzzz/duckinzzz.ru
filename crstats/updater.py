from datetime import datetime, timedelta

import requests
from django.utils import timezone

from config import settings
from .models import BattleLog

API_TOKEN = settings.CR_API_TOKEN

PLAYERS = {
    "#UY2VY9YUG": "grandison",
    "#Q8899QUY": "(-РашеР-)",
    "#289U8CQR2": "duckinzzz",
    "#VG9CR9R2J": "Шапа Шуточкин",
    "#20QP9JGGRQ": "клечик нямочкин",
    "#RLJVGUJL": "Lucky",
    "#22009JPCCQ": "flamboyx",
}


def fetch_battlelog(player_tag):
    tag_encoded = player_tag.replace("#", "%23")
    url = f"https://api.clashroyale.com/v1/players/{tag_encoded}/battlelog"

    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {API_TOKEN}"},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"  ✗ API Error for {player_tag}: {e}")
        return []


def update_database():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking for updates...")

    cutoff_time = timezone.now() - timedelta(hours=24)

    new_battles_count = 0

    for player_tag, player_name in PLAYERS.items():
        try:
            battlelog = fetch_battlelog(player_tag)
            if not battlelog:
                continue

            existing_times = set(
                BattleLog.objects.filter(
                    player_tag=player_tag,
                    battle_time__gte=cutoff_time
                ).values_list('battle_time', flat=True)
            )

            for battle in battlelog:
                if battle.get("type") != "PvP":
                    continue

                battle_time = timezone.datetime.fromisoformat(
                    battle["battleTime"].replace('Z', '+00:00')
                )

                if battle_time in existing_times:
                    continue

                if battle_time < cutoff_time:
                    continue

                try:
                    BattleLog.objects.create(
                        battle_time=battle_time,
                        player_tag=battle["team"][0]["tag"],
                        enemy_tag=battle["opponent"][0]["tag"],
                        starting_trophies=int(battle["team"][0]["startingTrophies"]),
                        trophy_change=int(battle["team"][0].get("trophyChange", 0)),
                        raw_data=battle,
                    )
                    print(f"  ✓ {player_name}: new battle at {battle_time.strftime('%H:%M:%S')}")
                    new_battles_count += 1
                except Exception as e:
                    print(f"  ✗ Error saving battle for {player_name}: {e}")

        except Exception as e:
            print(f"  ✗ Error processing {player_name}: {e}")

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Check complete. Added {new_battles_count} new battles.\n")

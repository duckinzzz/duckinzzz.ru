from datetime import datetime

import pandas as pd
import requests

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
    response = requests.get(url, headers={"Authorization": f"Bearer {API_TOKEN}"})
    return response.json()


def build_dataframe(battlelog):
    rows = []
    for battle in battlelog:
        if battle.get("type") == "PvP":
            rows.append({
                "battle_time": pd.to_datetime(battle["battleTime"], utc=True),
                "starting_trophies": int(battle["team"][0]["startingTrophies"]),
                "trophy_change": int(battle["team"][0].get("trophyChange", 0)),
                "player_tag": battle["team"][0]["tag"],
                "enemy_tag": battle["opponent"][0]["tag"],
                "raw_data": battle,
            })
    return pd.DataFrame(rows).sort_values("battle_time").reset_index(drop=True)


def update_database():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Проверка обновлений...")
    all_battles = []

    for tag in PLAYERS.keys():
        try:
            df = build_dataframe(fetch_battlelog(tag))
            all_battles.append(df)
        except Exception as e:
            print(f"  ✗ Ошибка для {PLAYERS[tag]}: {e}")

    if not all_battles:
        return

    df_new = pd.concat(all_battles, ignore_index=True)
    df_new = df_new.sort_values("battle_time").reset_index(drop=True)

    for tag in PLAYERS.keys():
        existing = BattleLog.objects.filter(player_tag=tag).order_by("-battle_time")[:50]
        df_existing = pd.DataFrame(list(existing.values("player_tag", "battle_time")))

        df_check = df_new[df_new["player_tag"] == tag].merge(
            df_existing, on=["player_tag", "battle_time"], how="left", indicator=True
        )
        df_fresh = df_check[df_check["_merge"] == "left_only"].drop(columns="_merge")

        for _, row in df_fresh.iterrows():
            BattleLog.objects.create(
                battle_time=row["battle_time"],
                player_tag=row["player_tag"],
                enemy_tag=row["enemy_tag"],
                starting_trophies=row["starting_trophies"],
                trophy_change=row["trophy_change"],
                raw_data=row["raw_data"],
            )
            print(f"  ✓ {PLAYERS[row['player_tag']]}: новый бой {row['battle_time']}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Проверка завершена.\n")

import os
import time
import requests
from flask import Flask
from threading import Thread
from telegram import Bot

BRAWL_API = os.getenv("BRAWL_API")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PLAYER_TAG = os.getenv("PLAYER_TAG")  # senza #

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot online!"

last_battle_time = None

def check_player():
    global last_battle_time

    bot = Bot(token=TELEGRAM_TOKEN)
    url = f"https://api.brawlstars.com/v1/players/%23{PLAYER_TAG}/battlelog"
    headers = {"Authorization": f"Bearer {BRAWL_API}"}

    while True:
        try:
            r = requests.get(url, headers=headers)

            if r.status_code == 200:
                data = r.json()
                latest_battle = data["items"][0]
                battle_time = latest_battle["battleTime"]
                trophy_change = latest_battle["battle"].get("trophyChange", 0)

                if last_battle_time is None:
                    last_battle_time = battle_time

                elif battle_time != last_battle_time:
                    bot.send_message(
                        chat_id=CHAT_ID,
                        text=f"🎮 Nuova partita!\nVariazione coppe: {trophy_change}"
                    )
                    last_battle_time = battle_time

        except Exception as e:
            print("Errore:", e)

        time.sleep(300)

Thread(target=check_player).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

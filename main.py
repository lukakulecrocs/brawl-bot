import os
import time
import requests
from threading import Thread
from telegram import Bot
from flask import Flask

# =========================
# VARIABILI D'AMBIENTE
# =========================
BRAWL_API = os.getenv("BRAWL_API")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PLAYER_TAG = os.getenv("PLAYER_TAG")  # SENZA #

# =========================
# FLASK (serve solo per Render)
# =========================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot online!"

# =========================
# STATO GIOCATORE
# =========================
last_trophies = None

# =========================
# CONTROLLO OGNI 5 MINUTI
# =========================
def check_player():
    global last_trophies

    bot = Bot(token=TELEGRAM_TOKEN)
    url = f"https://api.brawlstars.com/v1/players/%23{PLAYER_TAG}"
    headers = {"Authorization": f"Bearer {BRAWL_API}"}

    while True:
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                data = r.json()
                current_trophies = data.get("trophies")

                if last_trophies is None:
                    last_trophies = current_trophies

                elif current_trophies != last_trophies:
                    bot.send_message(
                        chat_id=CHAT_ID,
                        text=f"🟢 Il giocatore sta giocando! (trofei cambiati: {last_trophies} → {current_trophies})"
                    )
                    last_trophies = current_trophies

        except Exception as e:
            print("Errore:", e)

        time.sleep(300)  # 5 minuti

# =========================
# AVVIO THREAD
# =========================
Thread(target=check_player).start()

# =========================
# AVVIO FLASK
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
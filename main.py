import os
import requests
import json
import time
from flask import Flask
from threading import Thread

# ----------------------------
# CONFIG – variabili d'ambiente
# ----------------------------
BRAWL_API = os.environ.get("BRAWL_API")            # la tua chiave Brawl Stars
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")  # token del bot Telegram
CHAT_ID = os.environ.get("CHAT_ID")                # tuo chat ID Telegram (es. 6303733664)
PLAYER_TAG = "%23R9J82PJV9"                        # tag del giocatore da monitorare (# → %23)

# ----------------------------
# FLASK SERVER
# ----------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot awake!"

# ----------------------------
# FUNZIONE BOT – controlla trofei
# ----------------------------
def bot_loop():
    headers = {"Authorization": f"Bearer {BRAWL_API}"}
    url = f"https://api.brawlstars.com/v1/players/{PLAYER_TAG}"

    while True:
        try:
            # richiesta dati giocatore
            r = requests.get(url, headers=headers)
            data = r.json()
            current_trophies = data.get("trophies", None)
            if current_trophies is None:
                time.sleep(300)
                continue

            # leggi trofei salvati
            try:
                with open("trophies.json", "r") as f:
                    old_trophies = json.load(f)["trophies"]
            except:
                old_trophies = current_trophies

            # se cambiano trofei → manda Telegram
            if current_trophies != old_trophies:
                message = f"🚨 Il giocatore {PLAYER_TAG} ha cambiato trofei!\nPrima: {old_trophies}\nOra: {current_trophies}"
                requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                    data={"chat_id": CHAT_ID, "text": message}
                )

            # salva trofei attuali
            with open("trophies.json", "w") as f:
                json.dump({"trophies": current_trophies}, f)

        except Exception as e:
            print("Errore:", e)

        # loop ogni 5 minuti
        time.sleep(300)

# ----------------------------
# ESEGUI BOT IN THREAD
# ----------------------------
Thread(target=bot_loop).start()

# ----------------------------
# ESEGUI FLASK APP
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

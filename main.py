
import os
import time
import requests
from flask import Flask
from threading import Thread
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

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
is_online = False

# =========================
# CONTROLLO OGNI 5 MINUTI
# =========================
def check_player():
    global last_trophies, is_online

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
                    is_online = True
                    bot.send_message(
                        chat_id=CHAT_ID,
                        text="🟢 Il giocatore sta giocando! (trofei cambiati)"
                    )
                    last_trophies = current_trophies
                else:
                    is_online = False

        except Exception as e:
            print("Errore:", e)

        time.sleep(300)  # 5 minuti

# =========================
# COMANDO /status
# =========================
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_online:
        await update.message.reply_text("🟢 ONLINE (trofei cambiati)")
    else:
        await update.message.reply_text("🔴 OFFLINE (trofei invariati)")

# =========================
# AVVIO BOT TELEGRAM
# =========================
def start_telegram():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("status", status))
    application.run_polling()

# =========================
# AVVIO THREAD
# =========================
Thread(target=check_player).start()
Thread(target=start_telegram).start()

# =========================
# AVVIO FLASK
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
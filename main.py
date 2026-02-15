import os
import asyncio
import requests
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# =========================
# VARIABILI
# =========================
BRAWL_API = os.getenv("BRAWL_API")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PLAYER_TAG = os.getenv("PLAYER_TAG")  # SENZA #

# =========================
# FLASK
# =========================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot online!"

def run_flask():
    app.run(host="0.0.0.0", port=8000)

# =========================
# STATO
# =========================
last_trophies = None
is_online = False

# =========================
# CONTROLLO OGNI 5 MINUTI
# =========================
async def check_player(application):
    global last_trophies, is_online

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
                    await application.bot.send_message(
                        chat_id=CHAT_ID,
                        text="🟢 Il giocatore sta giocando!"
                    )
                    last_trophies = current_trophies
                else:
                    is_online = False

        except Exception as e:
            print("Errore:", e)

        await asyncio.sleep(300)

# =========================
# COMANDO /status
# =========================
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_online:
        await update.message.reply_text("🟢 ONLINE")
    else:
        await update.message.reply_text("🔴 OFFLINE")

# =========================
# MAIN
# =========================
async def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("status", status))

    asyncio.create_task(check_player(application))

    await application.run_polling()

if __name__ == "__main__":
    Thread(target=run_flask).start()
    asyncio.run(main())
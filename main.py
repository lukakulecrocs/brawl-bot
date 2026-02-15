import os
import requests
import json
import time
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ----------------------------
# CONFIG – variabili d'ambiente
# ----------------------------
BRAWL_API = os.environ.get("BRAWL_API")           # chiave API Brawl Stars
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN") # token bot Telegram
CHAT_ID = os.environ.get("CHAT_ID")               # chat ID Telegram
PLAYER_TAG = os.environ.get("PLAYER_TAG")         # tag giocatore (senza #)

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
    url = f"https://api.brawlstars.com/v1/players/%23{PLAYER_TAG}"  # il # va url encoded come %23
    import telegram
    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    while True:
        try:
            r = requests.get(url, headers=headers)
            data = r.json()
            current_trophies = data.get("trophies", None)
            if current_trophies is None:
                time.sleep(300)
                continue

            # Legge trofei precedenti
            try:
                with open("trophies.json", "r") as f:
                    old_trophies = json.load(f)["trophies"]
            except:
                old_trophies = current_trophies

            # Se cambia, invia notifica
            if current_trophies != old_trophies:
                message = f"🚨 Il giocatore ha cambiato trofei!\nPrima: {old_trophies}\nOra: {current_trophies}"
                bot.send_message(chat_id=CHAT_ID, text=message)

            # Salva nuovo stato
            with open("trophies.json", "w") as f:
                json.dump({"trophies": current_trophies}, f)

        except Exception as e:
            print("Errore:", e)

        # Loop ogni 5 minuti
        time.sleep(300)

# ----------------------------
# COMANDO TELEGRAM /status
# ----------------------------
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {"Authorization": f"Bearer {BRAWL_API}"}
    url = f"https://api.brawlstars.com/v1/players/%23{PLAYER_TAG}"

    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            trophies = data.get("trophies", "sconosciuti")
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"Il giocatore ha {trophies} trofei. ⚡")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Non sono riuscito a contattare il server Brawl Stars.")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"Errore: {e}")

# ----------------------------
# FUNZIONE TELEGRAM BOT
# ----------------------------
def telegram_bot():
    app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app_bot.add_handler(CommandHandler("status", status))
    app_bot.run_polling()

# ----------------------------
# ESEGUI BOT AUTOMATICO E COMANDO TELEGRAM
# ----------------------------
Thread(target=bot_loop).start()
Thread(target=telegram_bot).start()

# ----------------------------
# ESEGUI FLASK APP
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

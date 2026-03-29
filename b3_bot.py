import os

TOKEN = os.environ.get("8430351852:AAF50usp88gBEQ9XAlS98pOCVs8aBNztAqc")
URL = os.environ.get("https://robo-b3-24h-sap4.onrender.com")

print("DEBUG TOKEN:", TOKEN)
print("DEBUG URL:", URL)
import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("8430351852:AAF50usp88gBEQ9XAlS98pOCVs8aBNztAqc")
URL = os.environ.get("https://robo-b3-24h-1.onrender.com")

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot B3 online 24h!")

application.add_handler(CommandHandler("start", start))

# Webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.process_update(update)
    return "ok"

@app.route("/")
def home():
    return "Bot rodando 24h!"

# Set webhook
@app.before_first_request
def setup_webhook():
    application.bot.set_webhook(f"{URL}/{TOKEN}")

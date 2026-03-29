import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Carrega o .env
load_dotenv()

TOKEN = "8649054750:AAG9zpiWu_Od9yy_47GW9VY3Ac1ad-ZK6ZE"
URL = "https://robo-b3-24h-sap4.onrender.com"

print("TOKEN:", TOKEN)
print("URL:", URL)

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot B3 online 24h!")

application.add_handler(CommandHandler("start", start))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.process_update(update)
    return "ok"

@app.route("/")
def home():
    return "Bot rodando 24h!"

@app.before_first_request
def setup_webhook():
    application.bot.set_webhook(f"{URL}/{TOKEN}")

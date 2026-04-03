import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TOKEN = "8649054750:AAG9zpiWu_Od9yy_47GW9VY3Ac1ad-ZK6ZE"
URL = "https://robo-b3-24h.onrender.com"

print("TOKEN:", TOKEN)
print("URL:", URL)

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot B3 online 24h!")

application.add_handler(CommandHandler("start", start))

# Webhook
@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

@app.route("/")
def home():
    return "Bot rodando 24h!"

# Iniciar webhook
async def main():
    await application.bot.set_webhook(f"{URL}/{TOKEN}")

asyncio.run(main())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

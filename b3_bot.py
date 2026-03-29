import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

TOKEN = os.environ.get("8430351852:AAF50usp88gBEQ9XAlS98pOCVs8aBNztAqc")
URL = os.environ.get("https://robo-b3-24h-1.onrender.com")

app = Flask(__name__)
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

def start(update, context):
    update.message.reply_text("🤖 Bot B3 online 24h!")

dispatcher.add_handler(CommandHandler("start", start))

@app.route('/')
def home():
    return 'Bot rodando 24h!'

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

if __name__ == "__main__":
    # MUITO IMPORTANTE PARA O RENDER
    port = int(os.environ.get("PORT", 10000))
    bot.setWebhook(f"{URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=port)

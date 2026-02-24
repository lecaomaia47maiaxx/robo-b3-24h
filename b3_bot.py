from datetime import datetime
import os
import yfinance as yf
from flask import Flask, request

from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, ContextTypes

# =========================
# CONFIG
# =========================

TELEGRAM_TOKEN = "8709112968:AAHvkruRIiOuGK07-PI8RBWVgp7jrHqlox8"
CHAT_ID = "8352381582"
   


ATIVOS = ["PETR4.SA","VALE3.SA","ITUB4.SA","BBDC4.SA","BBAS3.SA"]

# =========================
# FUNÇÕES
# =========================

def variacao_dia(ticker):
    try:
        df = yf.download(ticker, period="5d", interval="1d", progress=False)
        if df.empty or len(df) < 2:
            return "N/D"
        ultimo = float(df["Close"].iloc[-1])
        anterior = float(df["Close"].iloc[-2])
        var = ((ultimo - anterior)/anterior)*100
        return f"{var:.2f}%"
    except:
        return "N/D"

def gerar_relatorio():
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    texto = ""
    for ativo in ATIVOS:
        nome = ativo.replace(".SA","")
        texto += f"{nome}: {variacao_dia(ativo)}\n"

    return f"""
📊 RELATÓRIO B3
⏰ {agora}

🔥 TOP 5
{texto}
"""

# =========================
# TELEGRAM APP
# =========================

app = Flask(__name__)
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
bot = Bot(token=TELEGRAM_TOKEN)

@app.route("/")
def home():
    return "Bot online"

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    await application.process_update(update)
    return "ok"

@app.route("/relatorio")
def relatorio_manual():
    bot.send_message(chat_id=CHAT_ID, text=gerar_relatorio())
    return "Relatório enviado"

# =========================
# INICIALIZAÇÃO
# =========================

if __name__ == "__main__":
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}")
    app.run(host="0.0.0.0", port=8080)

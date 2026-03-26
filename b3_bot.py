import os
import yfinance as yf
import ta
import time
from datetime import datetime

from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = "8430351852:AAF50usp88gBEQ9XAlS98pOCVs8aBNztAqc"
CHAT_ID = "8430351852"


def analisar_ativo(ticker):
    try:
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)

        if df.empty:
            return "Sem dados"

        close = df["Close"]

        rsi = ta.momentum.RSIIndicator(close=close, window=14).rsi().dropna()

        if rsi.empty:
            return "RSI indisponível"

        rsi_atual = float(rsi.iloc[-1])

        if rsi_atual < 30:
            sinal = "🟢 COMPRA"
        elif rsi_atual > 70:
            sinal = "🔴 VENDA"
        else:
            sinal = "⚪ NEUTRO"

        return f"{sinal} (RSI {rsi_atual:.2f})"

    except Exception as e:
        return f"Erro: {str(e)}"


def gerar_relatorio():
    ativos = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "BBAS3.SA"]

    texto = "📊 RELATÓRIO B3\n\n"

    for ativo in ativos:
        texto += f"{ativo} → {analisar_ativo(ativo)}\n"

    return texto


def start(update: Update, context: CallbackContext):
    update.message.reply_text("🤖 Robô B3 ativo!\nDigite /relatorio")


def relatorio(update: Update, context: CallbackContext):
    update.message.reply_text(gerar_relatorio())


def enviar_relatorio_automatico():
    bot = Bot(token=TOKEN)
    while True:
        agora = datetime.now()

        # Envia relatório todo dia às 18:00
        if agora.hour == 18 and agora.minute == 0:
            bot.send_message(chat_id=CHAT_ID, text=gerar_relatorio())
            time.sleep(60)

        time.sleep(30)


def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("relatorio", relatorio))

    print("Bot rodando...")

    # Rodar envio automático em paralelo
    import threading
    t = threading.Thread(target=enviar_relatorio_automatico)
    t.start()

    updater.start_polling(drop_pending_updates=True)
    updater.idle()


if __name__ == "__main__":
    main()

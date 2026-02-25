import os
import requests
import yfinance as yf
import pandas as pd
import ta
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = "8430351852:AAF50usp88gBEQ9XAlS98pOCVs8aBNztAqc"
CHAT_ID = "8352381582"

# ===============================
# FUNÇÃO DE ANÁLISE
# ===============================

def analisar_ativo(ticker):
    try:
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)

        if df.empty:
            return "Sem dados"

        close = df["Close"].squeeze()

        rsi = ta.momentum.RSIIndicator(close=close, window=14).rsi()
        rsi_atual = float(rsi.dropna().iloc[-1])

        if rsi_atual < 30:
            return f"COMPRA (RSI {rsi_atual:.2f})"
        elif rsi_atual > 70:
            return f"VENDA (RSI {rsi_atual:.2f})"
        else:
            return f"NEUTRO (RSI {rsi_atual:.2f})"

    except Exception as e:
        return f"Erro: {str(e)}"

# ===============================
# RELATÓRIO
# ===============================

def gerar_relatorio():
    ativos = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "BBAS3.SA"]

    texto = "📊 RELATÓRIO B3\n\n"

    for ativo in ativos:
        texto += f"{ativo} → {analisar_ativo(ativo)}\n"

    return texto

# ===============================
# COMANDO /start
# ===============================

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Robô B3 iniciado 🚀\nDigite /relatorio para receber análise.")

# ===============================
# COMANDO /relatorio
# ===============================

def relatorio(update: Update, context: CallbackContext):
    texto = gerar_relatorio()
    update.message.reply_text(texto)

# ===============================
# MAIN
# ===============================

def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("relatorio", relatorio))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

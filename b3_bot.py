import os
import yfinance as yf
import pandas as pd
import ta

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# ==========================================
# CONFIGURAÇÃO
# ==========================================

TOKEN = "8430351852:AAF50usp88gBEQ9XAlS98pOCVs8aBNztAqc"

# ==========================================
# FUNÇÃO DE ANÁLISE
# ==========================================

def analisar_ativo(ticker):
    try:
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)

        if df.empty:
            return "Sem dados"

        close = df["Close"].squeeze()

        rsi = ta.momentum.RSIIndicator(close=close, window=14).rsi()
        rsi = rsi.dropna()

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

# ==========================================
# GERAR RELATÓRIO
# ==========================================

def gerar_relatorio():
    ativos = [
        "PETR4.SA",
        "VALE3.SA",
        "ITUB4.SA",
        "BBDC4.SA",
        "BBAS3.SA"
    ]

    texto = "📊 RELATÓRIO AUTOMÁTICO B3\n\n"

    for ativo in ativos:
        resultado = analisar_ativo(ativo)
        texto += f"{ativo} → {resultado}\n"

    return texto

# ==========================================
# COMANDOS TELEGRAM
# ==========================================

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🤖 Robô B3 iniciado com sucesso!\n\nDigite /relatorio"
    )

def relatorio(update: Update, context: CallbackContext):
    texto = gerar_relatorio()
    update.message.reply_text(texto)

# ==========================================
# MAIN
# ==========================================

def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("relatorio", relatorio))

    print("Bot rodando...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

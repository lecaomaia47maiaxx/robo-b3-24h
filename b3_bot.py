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

        df = yf.download(ticker, period="3mo", interval="1d", progress=False) analisar_ativo(ticker):
    try:
        df = yf.download(ticker, period="3mo", interval="1d"            retornar "Sem dados"False)

        if df.empty:
            return "Sem dados"

        fechar = df["Fechar"].apertar()["Close"            retornar "RSI indisponível".squeeze()

        rsi = ta.momentum.RSIIndicator(close=close, window=14).rsi()
        rsi = rsi.dropna()

        if rsi.empty:
            return "RSI indisponível"

        rsi_atual = float(rsi.iloc[-1])            sinal = "🟢 COMPRA"(rsi.iloc[-1])

        if rsi_atual < 30:
            sinal = "🟢 COMPRA"
            sinal = "🔴 VENDA"elif rsi_atual > 70:
            sinal = "🔴 VENDA"
        outro:            sinal = "⚪ NEUTRO":
            sinal = "⚪ NEUTRO"

        retornar f"{sinal} (RSI {rsi_atual:.2f})"return f"{sinal} (RSI {rsi_atual:.2f})"

    exceto Exception como e:        retornar f"Erro: {str(e)}" Exception as e:
        return f"Erro: {str(e)}"

# ==========================================
        "PETR4.SA",
# ==========================================

def gerar_relatorio():
    ativos = [
        "PETR4.SA"        "VALE3.SA",
        "VALE3.SA"        "ITUB4.SA",
        "ITUB4.SA"        "BBDC4.SA",
        "BBDC4.SA"        "BBAS3.SA"
        "BBAS3.SA"
    ]    texto = "📊 RELATÓRIO AUTOMÁTICO B3\n\n"

    texto = "📊 RELATÓRIO AUTOMÁTICO B3\n\n"

    para ativo em ativo:        texto += f"{ativo} → {resultado}\n" ativo in ativos:
        resultado = analisar_ativo(ativo)
        texto += f"{ativo} → {resultado}\n"

    texto de retorno        "🤖 Robô B3 iniciado com sucesso!\n\n" texto

# ==========================================
# COMANDOS DO TELEGRAM
# ==========================================

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🤖 Robô B3 iniciado com sucesso!\n\n"
        "Digite /relatório para receber a análise.""Digite /relatorio para receber a análise."
    )    dp.add_handler(CommandHandler("start", start))

def relatorio(update: Update, context: CallbackContext):
    texto = gerar_relatorio()
    update.message.reply_text(texto)

# ==========================================
# MAIN
# ==========================================

def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start"    dp.add_handler(CommandHandler("relatório", relatorio))))
    dp.add_handler(CommandHandler("relatorio"    print("Bot rodando...")))

    print("Bot rodando..."    atualizador.iniciar_polling()
se __name__ == "__main__":start_polling()
    updater.idle()

if __name__ == "__main__"    principal()
    main()

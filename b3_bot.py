import asyncio
from datetime import datetime
import pandas as pd
import numpy as np
import yfinance as yf

from telegram import Bot
from telegram.ext import ApplicationBuilder, ContextTypes

TELEGRAM_TOKEN = "8430351852:AAF50usp88gBEQ9XAlS98pOCVs8aBNztAqc"
CHAT_ID = "8352381582"

# =========================
# CONFIGURAÇÕES
# =========================

ATIVOS_TOP = [
    "PETR4.SA",
    "VALE3.SA",
    "ITUB4.SA",
    "BBDC4.SA",
    "BBAS3.SA"
]

INDICES = {
    "S&P500": "^GSPC",
    "Nasdaq": "^IXIC",
    "Dow Jones": "^DJI",
    "IBOV": "^BVSP",
    "BTC": "BTC-USD"
}

# =========================
# INDICADORES
# =========================

def calcular_rsi(series, period=14):
    delta = series.diff()
    ganho = delta.clip(lower=0)
    perda = -delta.clip(upper=0)
    media_ganho = ganho.rolling(period).mean()
    media_perda = perda.rolling(period).mean()
    rs = media_ganho / media_perda
    rsi = 100 - (100 / (1 + rs))
    return rsi

def analisar_ativo(ticker):

    try:
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)

        if df.empty or len(df) < 30:
            return "Sem dados suficientes"

        close = df["Close"]

        ema9 = close.ewm(span=9).mean()
        ema21 = close.ewm(span=21).mean()
        rsi = calcular_rsi(close)

        rsi_atual = rsi.iloc[-1]

        if ema9.iloc[-1] > ema21.iloc[-1] and rsi_atual > 55:
            sinal = "🟢 COMPRA"
        elif ema9.iloc[-1] < ema21.iloc[-1] and rsi_atual < 45:
            sinal = "🔴 VENDA"
        else:
            sinal = "⚪ NEUTRO"

        return f"{sinal} (RSI {rsi_atual:.1f})"

    except Exception as e:
        return "Erro análise"

def variacao_dia(ticker):

    try:
        df = yf.download(ticker, period="5d", interval="1d", progress=False)

        if df.empty or len(df) < 2:
            return "N/D"

        ultimo = df["Close"].iloc[-1]
        anterior = df["Close"].iloc[-2]

        var = ((ultimo - anterior) / anterior) * 100

        return f"{var:.2f}%"

    except:
        return "N/D"

# =========================
# RELATÓRIO
# =========================

def gerar_relatorio():

    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    texto_indices = ""
    for nome, ticker in INDICES.items():
        texto_indices += f"{nome}: {variacao_dia(ticker)}\n"

    texto_top = ""
    for ativo in ATIVOS_TOP:
        nome = ativo.replace(".SA", "")
        texto_top += f"{nome} → {analisar_ativo(ativo)}\n"

    mensagem = f"""
📊 RELATÓRIO INSTITUCIONAL B3
⏰ {agora}

🌎 MERCADO GLOBAL
{texto_indices}

🔥 TOP 5 MAIS LÍQUIDAS
{texto_top}

📌 Modelo técnico: EMA 9x21 + RSI 14
"""

    return mensagem

# =========================
# ENVIO AUTOMÁTICO
# =========================

async def enviar_relatorio(context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    mensagem = gerar_relatorio()
    await bot.send_message(chat_id=CHAT_ID, text=mensagem)

async def main():

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Envia ao iniciar
    app.job_queue.run_once(enviar_relatorio, when=5)

    # Envia a cada 1 hora
    app.job_queue.run_repeating(enviar_relatorio, interval=3600, first=3600)

    print("🚀 Robô institucional rodando...")

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

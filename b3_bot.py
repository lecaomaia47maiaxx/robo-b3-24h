import asyncio
import yfinance as yf
import pandas as pd
import ta
from telegram import Bot
import os

# ===== CONFIG =====
TOKEN = "8430351852:AAF50usp88gBEQ9XAlS98pOCVs8aBNztAqc"
CHAT_ID = "8352381582"

bot = Bot(token=TOKEN)

ACOES = [
    "PETR4.SA","VALE3.SA","ITUB4.SA",
    "BBDC4.SA","ABEV3.SA","BBAS3.SA",
    "WEGE3.SA","MGLU3.SA","SUZB3.SA","RENT3.SA"
]

def baixar(ticker):
    df = yf.download(ticker, period="6mo", interval="1d", progress=False)
    if df.empty:
        return None
    return df.dropna()

def calcular_score(acao):
    df = baixar(acao)
    if df is None or len(df) < 50:
        return None

    close = df["Close"]
    volume = df["Volume"]

    sma9 = close.rolling(9).mean().iloc[-1]
    sma21 = close.rolling(21).mean().iloc[-1]
    rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]
    vol_medio = volume.rolling(20).mean().iloc[-1]
    vol_atual = volume.iloc[-1]

    score = 50
    score += 20 if sma9 > sma21 else -20
    score += 15 if rsi < 30 else (-15 if rsi > 70 else 0)
    score += 10 if vol_atual > vol_medio else 0

    return max(0, min(100, score))

def classificar(score):
    if score >= 70:
        return "🔥 FORTE COMPRA"
    elif score <= 30:
        return "🔻 FORTE VENDA"
    else:
        return "⚖ NEUTRO"

async def enviar(texto):
    partes = [texto[i:i+4000] for i in range(0, len(texto), 4000)]
    for parte in partes:
        await bot.send_message(chat_id=CHAT_ID, text=parte)

async def scanner():
    while True:
        print("Executando análise...")

        ranking = []
        alertas = []

        for acao in ACOES:
            try:
                score = calcular_score(acao)
                if score is None:
                    continue

                sinal = classificar(score)
                ranking.append((acao.replace(".SA",""), score, sinal))

                if score >= 70 or score <= 30:
                    alertas.append(f"{acao.replace('.SA','')} | {score} | {sinal}")

            except Exception as e:
                print("Erro:", acao, e)

        ranking.sort(key=lambda x: x[1], reverse=True)

        texto = "📊 SCANNER B3 24H\n\n"
        for r in ranking:
            texto += f"{r[0]} | {r[1]} | {r[2]}\n"

        await enviar(texto)

        if alertas:
            alerta = "⚡ ALERTAS FORTES ⚡\n\n" + "\n".join(alertas)
            await enviar(alerta)

        await asyncio.sleep(900)  # 15 min

if __name__ == "__main__":
    print("Robô B3 iniciado...")
    asyncio.run(scanner())

import asyncio
import requests
import yfinance as yf
import pandas as pd
import numpy as np
import os
from datetime import datetime, time
from telegram import Bot

TOKEN = "8430351852:AAF50usp88gBEQ9XAlS98pOCVs8aBNztAqc"
CHAT_ID = "8352381582"
ALPHA_KEY = "OYSICYD1972XILCB"

bot = Bot(token=TOKEN)

# ========== CONFIG ==========
INDICES = {
    "Dow Jones": "^DJI",
    "S&P500": "^GSPC",
    "Nasdaq": "^IXIC",
    "DAX": "^GDAXI",
    "FTSE": "^FTSE",
    "Nikkei": "^N225"
}

COMMODITIES = {
    "WTI": "CL=F",
    "Ouro": "GC=F",
    "Minério": "BZ=F"
}

ACOES = {
    "PETR4": "PETR4.SA",
    "VALE3": "VALE3.SA",
    "BBAS3": "BBAS3.SA"
}

# ================= UTIL =================

def variacao_dia(ticker):
    df = yf.download(ticker, period="2d", interval="1d", progress=False)
    if len(df) < 2:
        return None
    return round(((df["Close"].iloc[-1] / df["Close"].iloc[-2]) - 1) * 100, 2)

def sentimento_global():
    score = 0
    detalhes = {}
    for nome, ticker in INDICES.items():
        var = variacao_dia(ticker)
        if var is None:
            continue
        detalhes[nome] = var
        score += 1 if var > 0 else -1
    if score > 2:
        sent = "ALTISTA 📈"
    elif score < -2:
        sent = "BAIXISTA 📉"
    else:
        sent = "NEUTRO ⚖"
    return sent, detalhes

def tendencia_ibov():
    df = yf.download("^BVSP", period="1y", interval="1d", progress=False)
    if len(df) < 200:
        return "Dados insuficientes"
    mm200 = df["Close"].rolling(200).mean().iloc[-1]
    atual = df["Close"].iloc[-1]
    return "ALTA (MM200)" if atual > mm200 else "BAIXA (MM200)"

def correlacao(t1, t2):
    df1 = yf.download(t1, period="3mo", progress=False)["Close"]
    df2 = yf.download(t2, period="3mo", progress=False)["Close"]
    df = pd.concat([df1, df2], axis=1).dropna()
    if len(df) < 10:
        return None
    return round(df.corr().iloc[0,1], 2)

def noticias():
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&apikey={ALPHA_KEY}"
    r = requests.get(url)
    data = r.json()
    if "feed" not in data:
        return ["Sem notícias disponíveis"]
    noticias = []
    for item in data["feed"][:3]:
        noticias.append(item["title"])
    return noticias

# ================= RELATORIO =================

async def enviar_relatorio():
    sent, detalhes = sentimento_global()
    ibov = tendencia_ibov()

    msg = "📊 *RELATÓRIO GLOBAL + B3 ALEX*\n\n"
    msg += f"🌍 Sentimento Global: {sent}\n"
    msg += f"📈 Tendência IBOV: {ibov}\n\n"

    msg += "📌 Índices Globais:\n"
    for nome, var in detalhes.items():
        msg += f"{nome}: {var}%\n"

    msg += "\n📌 Commodities:\n"
    for nome, ticker in COMMODITIES.items():
        var = variacao_dia(ticker)
        if var:
            msg += f"{nome}: {var}%\n"

    msg += "\n📌 Ações Brasil:\n"
    for nome, ticker in ACOES.items():
        var = variacao_dia(ticker)
        if var:
            msg += f"{nome}: {var}%\n"

    msg += "\n📌 Correlações:\n"
    corr_vale = correlacao("VALE3.SA", "BZ=F")
    corr_petro = correlacao("PETR4.SA", "CL=F")
    msg += f"Vale ↔ Minério: {corr_vale}\n"
    msg += f"Petrobras ↔ Petróleo: {corr_petro}\n"

    msg += "\n📌 Notícias Importantes:\n"
    for n in noticias():
        msg += f"• {n}\n"

    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")

# ================= SCHEDULER =================

async def scheduler():
    while True:
        agora = datetime.now().time()
        if agora >= time(9,0) and agora <= time(9,5):
            await enviar_relatorio()
            await asyncio.sleep(86400)
        await asyncio.sleep(60)

if __name__ == "__main__":
    print("🚀 Robô Global iniciado")
    asyncio.run(scheduler())

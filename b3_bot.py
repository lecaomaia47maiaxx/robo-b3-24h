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
ALPHA_KEY = " OYSICYD1972XILCB"

bot = Bot(token=TOKEN)

ACOES_LIQUIDAS = [
    "PETR4.SA","VALE3.SA","ITUB4.SA",
    "BBDC4.SA","BBAS3.SA","WEGE3.SA"
]

# ================= FUNÇÕES BÁSICAS =================

def variacao_dia(ticker):
    df = yf.download(ticker, period="2d", interval="1d", progress=False)
    if len(df) < 2:
        return None
    return round(((df["Close"].iloc[-1] / df["Close"].iloc[-2]) - 1) * 100, 2)

def correlacao(t1, t2):
    df1 = yf.download(t1, period="1mo", progress=False)["Close"]
    df2 = yf.download(t2, period="1mo", progress=False)["Close"]
    df = pd.concat([df1, df2], axis=1).dropna()
    if len(df) < 10:
        return None
    return round(df.corr().iloc[0,1], 2)

# ================= MÓDULOS NOVOS =================

def ewz_vs_ibov():
    ewz = variacao_dia("EWZ")
    ibov = variacao_dia("^BVSP")
    corr = correlacao("EWZ", "^BVSP")
    return ewz, ibov, corr

def fluxo_estrangeiro():
    df = yf.download("EWZ", period="5d", progress=False)
    if len(df) < 2:
        return "Indefinido"
    volume = df["Volume"].iloc[-1]
    media = df["Volume"].mean()
    if volume > media * 1.3:
        return "Entrada forte"
    elif volume < media * 0.7:
        return "Saída forte"
    else:
        return "Fluxo normal"

def moedas():
    brl = variacao_dia("BRL=X")
    eur = variacao_dia("EURUSD=X")
    jpy = variacao_dia("JPY=X")
    return brl, eur, jpy

def btc_vs_sp():
    corr = correlacao("BTC-USD", "^GSPC")
    btc = variacao_dia("BTC-USD")
    return btc, corr

def noticias():
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&apikey={ALPHA_KEY}"
    r = requests.get(url)
    data = r.json()
    if "feed" not in data:
        return ["Sem notícias disponíveis"]
    return [item["title"] for item in data["feed"][:3]]

# ================= ALERTAS HORÁRIOS =================

def analisar_acao(ticker):
    df = yf.download(ticker, period="3mo", progress=False)
    if len(df) < 30:
        return None

    close = df["Close"]
    mm21 = close.rolling(21).mean().iloc[-1]
    preco = close.iloc[-1]

    delta = close.diff()
    ganho = delta.clip(lower=0).rolling(14).mean()
    perda = -delta.clip(upper=0).rolling(14).mean()
    rs = ganho / perda
    rsi = 100 - (100 / (1 + rs))
    rsi_atual = rsi.iloc[-1]

    if preco > mm21 and rsi_atual > 55:
        return "COMPRA"
    elif preco < mm21 and rsi_atual < 45:
        return "VENDA"
    return None

# ================= RELATÓRIO 09:00 =================

async def enviar_relatorio():
    msg = "📊 *RELATÓRIO GLOBAL + B3 ALEX*\n\n"

    ewz, ibov, corr = ewz_vs_ibov()
    fluxo = fluxo_estrangeiro()
    brl, eur, jpy = moedas()
    btc, btc_corr = btc_vs_sp()

    msg += "📌 EWZ vs IBOV\n"
    msg += f"EWZ: {ewz}% | IBOV: {ibov}%\n"
    msg += f"Correlação: {corr}\n"
    msg += f"Fluxo Estrangeiro: {fluxo}\n\n"

    msg += "💱 Moedas vs USD\n"
    msg += f"BRL: {brl}% | EUR: {eur}% | JPY: {jpy}%\n\n"

    msg += "🪙 Bitcoin\n"
    msg += f"BTC: {btc}%\n"
    msg += f"Correlação BTC vs S&P500: {btc_corr}\n\n"

    msg += "📰 Notícias:\n"
    for n in noticias():
        msg += f"• {n}\n"

    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")

# ================= ALERTAS 1H =================

async def alertas_horarios():
    mensagens = []
    for acao in ACOES_LIQUIDAS:
        sinal = analisar_acao(acao)
        if sinal:
            nome = acao.replace(".SA","")
            mensagens.append(f"{nome}: {sinal}")

    if mensagens:
        texto = "🚨 *ALERTAS DO MOMENTO*\n\n" + "\n".join(mensagens)
        await bot.send_message(chat_id=CHAT_ID, text=texto, parse_mode="Markdown")

# ================= LOOP PRINCIPAL =================

# ================= LOOP PRINCIPAL =================

async def scheduler():
    print("🚀 Robô Institucional Ativo")

    primeira_execucao = True

    while True:
        agora = datetime.now().time()

        # 🔥 TESTE IMEDIATO AO INICIAR
        if primeira_execucao:
            await bot.send_message(chat_id=CHAT_ID, text="🚀 TESTE IMEDIATO DO RELATÓRIO")
            await enviar_relatorio()
            primeira_execucao = False

        # 📊 RELATÓRIO OFICIAL 09:00
        if time(9,0) <= agora <= time(9,5):
            await enviar_relatorio()
            await asyncio.sleep(3600)

        # 🚨 ALERTAS A CADA 1 HORA
        await alertas_horarios()

        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(scheduler())

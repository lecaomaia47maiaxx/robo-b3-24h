import asyncio
import requests
import yfinance as yf
import pandas as pd
import os
from datetime import datetime, time
from telegram import Bot

# ================= CONFIG =================

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
    try:
        df = yf.download(ticker, period="2d", interval="1d", progress=False)
        if len(df) < 2:
            return None
        return round(((df["Close"].iloc[-1] / df["Close"].iloc[-2]) - 1) * 100, 2)
    except:
        return None

def correlacao(t1, t2):
    try:
        df1 = yf.download(t1, period="1mo", progress=False)["Close"]
        df2 = yf.download(t2, period="1mo", progress=False)["Close"]
        df = pd.concat([df1, df2], axis=1).dropna()
        if len(df) < 10:
            return None
        return round(df.corr().iloc[0,1], 2)
    except:
        return None

# ================= MÓDULOS =================

def ewz_vs_ibov():
    ewz = variacao_dia("EWZ")
    ibov = variacao_dia("^BVSP")
    corr = correlacao("EWZ", "^BVSP")
    return ewz, ibov, corr

def fluxo_estrangeiro():
    try:
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
    except:
        return "Indefinido"

def moedas():
    return (
        variacao_dia("BRL=X"),
        variacao_dia("EURUSD=X"),
        variacao_dia("JPY=X")
    )

def btc_vs_sp():
    return (
        variacao_dia("BTC-USD"),
        correlacao("BTC-USD", "^GSPC")
    )

def noticias():
    try:
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&apikey={ALPHA_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()
        if "feed" not in data:
            return ["Sem notícias relevantes"]
        return [item["title"] for item in data["feed"][:3]]
    except:
        return ["Erro ao buscar notícias"]

# ================= ANÁLISE TÉCNICA =================

def analisar_acao(ticker):
    try:
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
    except:
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

# ================= LOOP PRINCIPAL ESTÁVEL =================

async def scheduler():
    print("🚀 Robô Institucional Ativo")

    primeira_execucao = True

    while True:
        try:
            agora = datetime.now().time()

            if primeira_execucao:
                await bot.send_message(chat_id=CHAT_ID, text="🚀 Robô Global iniciado com sucesso")
                await enviar_relatorio()
                primeira_execucao = False

            if time(9,0) <= agora <= time(9,5):
                await enviar_relatorio()
                await asyncio.sleep(3600)

            await alertas_horarios()
            await asyncio.sleep(3600)

        except Exception as e:
            print("Erro no loop:", e)
            await asyncio.sleep(60)

# ================= START =================

if __name__ == "__main__":
    asyncio.run(scheduler())

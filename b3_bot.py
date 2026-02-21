import asyncio
import os
import yfinance as yf
import pandas as pd
import ta
from telegram import Bot
import requests

# ================= CONFIG =================

TOKEN = "8430351852:AAF50usp88gBEQ9XAlS98pOCVs8aBNztAqc"
CHAT_ID = "8352381582"

if not TOKEN or not CHAT_ID:
    raise Exception("TOKEN ou CHAT_ID não configurado no Railway.")

bot = Bot(token=TOKEN)

ACOES = [
    "PETR4.SA","VALE3.SA","ITUB4.SA",
    "BBDC4.SA","ABEV3.SA","BBAS3.SA",
    "WEGE3.SA","MGLU3.SA","SUZB3.SA","RENT3.SA"
]

INDICES_GLOBAIS = [
    "^GSPC",  # S&P500
    "^IXIC",  # Nasdaq
    "^DJI",   # Dow Jones
    "^BVSP"   # IBOV
]

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

# ================= DOWNLOAD =================

def baixar(ticker, periodo="3mo"):
    try:
        df = yf.download(
            ticker,
            period=periodo,
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=False,
            session=session
        )
        if df.empty:
            return None
        return df.dropna()
    except:
        return None

# ================= SENTIMENTO GLOBAL =================

def sentimento_mercado():
    score = 0
    total = 0

    for indice in INDICES_GLOBAIS:
        df = baixar(indice, "5d")
        if df is None or len(df) < 2:
            continue

        hoje = df["Close"].iloc[-1]
        ontem = df["Close"].iloc[-2]

        if hoje > ontem:
            score += 1
        else:
            score -= 1

        total += 1

    if total == 0:
        return "INDEFINIDO"

    if score >= 2:
        return "🟢 ALTISTA"
    elif score <= -2:
        return "🔴 BAIXISTA"
    else:
        return "🟡 NEUTRO"

# ================= ANÁLISE DA AÇÃO =================

def analisar_acao(df):
    close = df["Close"]
    volume = df["Volume"]

    sma9 = close.rolling(9).mean().iloc[-1]
    sma21 = close.rolling(21).mean().iloc[-1]
    rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]
    vol_media = volume.rolling(20).mean().iloc[-1]
    vol_atual = volume.iloc[-1]

    score = 0

    if sma9 > sma21:
        score += 1
    else:
        score -= 1

    if rsi < 30:
        score += 1
    elif rsi > 70:
        score -= 1

    if vol_atual > vol_media:
        score += 1

    if score >= 2:
        return "🟢 COMPRA"
    elif score <= -1:
        return "🔴 VENDA"
    else:
        return "🟡 NEUTRO"

# ================= ENVIO =================

async def enviar(texto):
    partes = [texto[i:i+4000] for i in range(0, len(texto), 4000)]
    for parte in partes:
        await bot.send_message(chat_id=CHAT_ID, text=parte)

# ================= LOOP =================

async def scanner():
    print("Robô iniciado com sucesso.")

    while True:
        print("Executando análise diária...")

        sentimento = sentimento_mercado()

        compras = []
        vendas = []
        neutros = []

        for acao in ACOES:
            df = baixar(acao)

            if df is None or len(df) < 30:
                continue

            sinal = analisar_acao(df)
            nome = acao.replace(".SA","")

            if "COMPRA" in sinal:
                compras.append(nome)
            elif "VENDA" in sinal:
                vendas.append(nome)
            else:
                neutros.append(nome)

            print(f"{nome} -> {sinal}")

        texto = "📊 ANÁLISE DIÁRIA B3\n\n"
        texto += f"Sentimento de Mercado: {sentimento}\n\n"

        texto += "🟢 AÇÕES EM COMPRA:\n"
        texto += "\n".join(compras) if compras else "Nenhuma"
        texto += "\n\n"

        texto += "🔴 AÇÕES EM VENDA:\n"
        texto += "\n".join(vendas) if vendas else "Nenhuma"
        texto += "\n\n"

        texto += "🟡 NEUTRAS:\n"
        texto += "\n".join(neutros) if neutros else "Nenhuma"

        await enviar(texto)

        print("Análise enviada. Próxima execução em 15 minutos.\n")

        await asyncio.sleep(900)

# ================= START =================

if __name__ == "__main__":
    asyncio.run(scanner())

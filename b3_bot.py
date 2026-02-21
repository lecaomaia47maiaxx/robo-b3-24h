import asyncio
import yfinance as yf
import pandas as pd
import numpy as np
from telegram import Bot
import ta

# ================= CONFIG =================

TOKEN = "8430351852:AAF50usp88gBEQ9XAlS98pOCVs8aBNztAqc"
CHAT_ID = "8352381582"

bot = Bot(token=TOKEN)

ACOES = [
    "PETR4.SA","VALE3.SA","ITUB4.SA",
    "BBDC4.SA","ABEV3.SA","BBAS3.SA",
    "WEGE3.SA","MGLU3.SA","SUZB3.SA","RENT3.SA"
]

# ================= DOWNLOAD =================

def baixar_dados(ticker):
    try:
        df = yf.Ticker(ticker).history(
            period="6mo",
            interval="1d",
            auto_adjust=True
        )

        if df is None or df.empty:
            print(f"[ERRO] {ticker} vazio")
            return None

        df = df.dropna()
        if len(df) < 50:
            print(f"[ERRO] {ticker} poucos dados")
            return None

        return df

    except Exception as e:
        print(f"[ERRO DOWNLOAD] {ticker}: {e}")
        return None


# ================= SENTIMENTO GLOBAL =================

def sentimento_mercado():
    indices = ["^GSPC","^IXIC","^DJI","^GDAXI","^FTSE","^N225"]
    score = 0

    for ticker in indices:
        df = baixar_dados(ticker)
        if df is None:
            continue

        if df["Close"].iloc[-1] > df["Close"].iloc[-2]:
            score += 1
        else:
            score -= 1

    if score >= 2:
        return "ALTISTA 🌍📈"
    elif score <= -2:
        return "BAIXISTA 🌍📉"
    else:
        return "NEUTRO 🌎"


# ================= TENDÊNCIA IBOV =================

def tendencia_ibov():
    df = baixar_dados("^BVSP")
    if df is None:
        return "Indefinida"

    close = df["Close"]
    sma200 = close.rolling(200).mean()

    if close.iloc[-1] > sma200.iloc[-1]:
        return "Alta (acima da MM200) 📈"
    else:
        return "Baixa (abaixo da MM200) 📉"


# ================= ANALISE AÇÃO =================

def analisar_acao(ticker):
    df = baixar_dados(ticker)
    if df is None:
        return None

    close = df["Close"]
    volume = df["Volume"]

    sma9 = close.rolling(9).mean()
    sma21 = close.rolling(21).mean()
    sma200 = close.rolling(200).mean()

    rsi = ta.momentum.RSIIndicator(close).rsi()

    variacao_dia = ((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100

    score = 0

    # Estratégia mais agressiva
    if sma9.iloc[-1] > sma21.iloc[-1]:
        score += 1
    else:
        score -= 1

    if close.iloc[-1] > sma200.iloc[-1]:
        score += 1
    else:
        score -= 1

    if rsi.iloc[-1] < 70:
        score += 1
    if rsi.iloc[-1] > 30:
        score += 1

    if variacao_dia > 0:
        score += 1
    else:
        score -= 1

    # Classificação
    if score >= 3:
        sinal = "🟢 COMPRA"
    elif score <= -2:
        sinal = "🔴 VENDA"
    else:
        sinal = "🟡 NEUTRO"

    return {
        "ticker": ticker.replace(".SA",""),
        "score": score,
        "sinal": sinal,
        "variacao": round(variacao_dia,2)
    }


# ================= EXECUÇÃO =================

async def executar():
    print("Executando análise...")

    sentimento = sentimento_mercado()
    ibov = tendencia_ibov()

    compras = []
    vendas = []
    neutras = []
    ranking = []

    for acao in ACOES:
        resultado = analisar_acao(acao)
        if resultado is None:
            continue

        ranking.append(resultado)

        if "COMPRA" in resultado["sinal"]:
            compras.append(resultado)
        elif "VENDA" in resultado["sinal"]:
            vendas.append(resultado)
        else:
            neutras.append(resultado)

    ranking = sorted(ranking, key=lambda x: x["score"], reverse=True)

    mensagem = f"""
📊 ANÁLISE DIÁRIA B3

🌍 Sentimento Global: {sentimento}
📈 Tendência IBOV: {ibov}

━━━━━━━━━━━━━━━━━━

🟢 AÇÕES EM COMPRA:
"""

    if compras:
        for c in compras:
            mensagem += f"{c['ticker']} | Score {c['score']} | {c['variacao']}%\n"
    else:
        mensagem += "Nenhuma\n"

    mensagem += "\n🔴 AÇÕES EM VENDA:\n"

    if vendas:
        for v in vendas:
            mensagem += f"{v['ticker']} | Score {v['score']} | {v['variacao']}%\n"
    else:
        mensagem += "Nenhuma\n"

    mensagem += "\n🔥 TOP 3 MAIS FORTES DO DIA:\n"

    for top in ranking[:3]:
        mensagem += f"{top['ticker']} ({top['score']} pts | {top['variacao']}%)\n"

    await bot.send_message(chat_id=CHAT_ID, text=mensagem)


async def scheduler():
    while True:
        try:
            await executar()
        except Exception as e:
            print("Erro geral:", e)

        await asyncio.sleep(3600)  # roda a cada 1 hora


if __name__ == "__main__":
    print("Robô B3 iniciado...")
    asyncio.run(scheduler())

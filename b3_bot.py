import yfinance as yf
import requests
import time
import asyncio
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from telegram import Bot
from datetime import datetime

# ================= CONFIG =================

TELEGRAM_TOKEN = "8430351852:AAF50usp88gBEQ9XAlS98pOCVs8aBNztAqc"
CHAT_ID = "8352381582"
NEWS_API_KEY = "OYSICYD1972XILCB"

# ==========================================

# ===== FUNÇÃO VARIAÇÃO CORRIGIDA =====

def get_variation(ticker):
    try:
        df = yf.download(
            ticker,
            period="5d",
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        if df.empty or len(df) < 2:
            return "N/D"

        close = df["Close"]

        # força float real
        ultimo = float(close.iloc[-1])
        anterior = float(close.iloc[-2])

        variacao = ((ultimo - anterior) / anterior) * 100

        return f"{variacao:.2f}%"

    except Exception as e:
        print(f"Erro variação {ticker}: {e}")
        return "N/D"

# ===== RSI + EMA CORRIGIDO =====

def get_rsi_signal(ticker):
    try:
        df = yf.download(
            ticker,
            period="3mo",
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        if df.empty or len(df) < 30:
            return "Dados insuficientes"

        close = df["Close"].astype(float)

        ema9 = EMAIndicator(close, window=9).ema_indicator()
        ema21 = EMAIndicator(close, window=21).ema_indicator()
        rsi = RSIIndicator(close, window=14).rsi()

        rsi_atual = float(rsi.iloc[-1])

        if ema9.iloc[-1] > ema21.iloc[-1] and rsi_atual > 55:
            return f"🟢 COMPRA (RSI {rsi_atual:.1f})"
        elif ema9.iloc[-1] < ema21.iloc[-1] and rsi_atual < 45:
            return f"🔴 VENDA (RSI {rsi_atual:.1f})"
        else:
            return f"⚪ NEUTRO (RSI {rsi_atual:.1f})"

    except Exception as e:
        print(f"Erro análise {ticker}: {e}")
        return "Erro análise"

# ===== NOTÍCIAS =====

def get_news(query):
    try:
        url = (
            f"https://newsapi.org/v2/everything?"
            f"q={query}&language=pt&sortBy=publishedAt&pageSize=2"
            f"&apiKey={NEWS_API_KEY}"
        )

        r = requests.get(url, timeout=10).json()

        if "articles" not in r or len(r["articles"]) == 0:
            return "Sem notícias relevantes.\n"

        noticias = ""
        for art in r["articles"][:2]:
            noticias += f"• {art['title']}\n"

        return noticias

    except Exception as e:
        print("Erro notícias:", e)
        return "Erro ao buscar notícias.\n"

# ===== RELATÓRIO ORGANIZADO =====

def gerar_relatorio():
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    sp500 = get_variation("^GSPC")
    nasdaq = get_variation("^IXIC")
    dow = get_variation("^DJI")

    ibov = get_variation("^BVSP")
    ewz = get_variation("EWZ")
    btc = get_variation("BTC-USD")
    dxy = get_variation("DX-Y.NYB")

    top5 = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "BBAS3.SA"]

    sinais = ""
    for acao in top5:
        nome = acao.replace(".SA", "")
        sinal = get_rsi_signal(acao)
        sinais += f"{nome} → {sinal}\n"

    noticias_mercado = get_news("mercado financeiro brasil")
    noticias_petr = get_news("PETR4 Petrobras")
    noticias_vale = get_news("VALE3 Vale")
    noticias_bancos = get_news("Itaú Bradesco Banco do Brasil")

    mensagem = f"""
📊 RELATÓRIO INSTITUCIONAL B3
⏰ {agora}

🇺🇸 PRE-MARKET EUA
S&P500: {sp500}
Nasdaq: {nasdaq}
Dow Jones: {dow}

🇧🇷 BRASIL
IBOV: {ibov}
EWZ: {ewz}
DXY: {dxy}
BTC: {btc}

🔥 TOP 5 MAIS LÍQUIDAS (RSI + EMA 9x21)
{sinais}

📰 MERCADO
{noticias_mercado}

🛢 PETROBRAS
{noticias_petr}

⛏ VALE
{noticias_vale}

🏦 BANCOS
{noticias_bancos}

📌 Modelo técnico: EMA 9x21 + RSI 14
"""

    return mensagem

# ===== TELEGRAM V20 =====

async def enviar_async():
    bot = Bot(token=TELEGRAM_TOKEN)
    msg = gerar_relatorio()
    await bot.send_message(chat_id=CHAT_ID, text=msg)

def enviar_relatorio():
    asyncio.run(enviar_async())

# ===== LOOP =====

if __name__ == "__main__":
    print("🚀 Robô Institucional iniciado")
    enviar_relatorio()

    while True:
        print("⏳ Aguardando 1 hora...")
        time.sleep(3600)
        enviar_relatorio()

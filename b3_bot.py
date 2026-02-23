import yfinance as yf
import pandas as pd
import requests
import time
import asyncio
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from telegram import Bot
from datetime import datetime

# ================= CONFIG =================

TELEGRAM_TOKEN = "8430351852:AAF50usp88gBEQ9XAlS98pOCVs8aBNztAqc"
CHAT_ID = "8352381582"
NEWS_API_KEY = "OYSICYD1972XILCB"

# ==========================================

# ===== INDICADORES =====

def get_rsi_signal(ticker):
    try:
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)
        df.dropna(inplace=True)

        ema9 = EMAIndicator(df['Close'], window=9).ema_indicator()
        ema21 = EMAIndicator(df['Close'], window=21).ema_indicator()
        rsi = RSIIndicator(df['Close'], window=14).rsi()

        if ema9.iloc[-1] > ema21.iloc[-1] and rsi.iloc[-1] > 55:
            return "🟢 COMPRA"
        elif ema9.iloc[-1] < ema21.iloc[-1] and rsi.iloc[-1] < 45:
            return "🔴 VENDA"
        else:
            return "⚪ NEUTRO"
    except:
        return "Erro análise"

def get_variation(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="1d", progress=False)
        var = ((df['Close'][-1] - df['Close'][-2]) / df['Close'][-2]) * 100
        return round(var, 2)
    except:
        return 0

# ===== NOTÍCIAS =====

def get_news(query):
    try:
        url = f"https://newsapi.org/v2/everything?q={query}&language=pt&sortBy=publishedAt&pageSize=3&apiKey={NEWS_API_KEY}"
        r = requests.get(url).json()
        news = ""
        if "articles" in r:
            for art in r["articles"][:3]:
                news += f"• {art['title']}\n"
        return news if news else "Sem notícias relevantes.\n"
    except:
        return "Erro ao buscar notícias.\n"

# ===== RELATÓRIO =====

def gerar_relatorio():
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Pre-market EUA
    sp500 = get_variation("^GSPC")
    nasdaq = get_variation("^IXIC")
    dow = get_variation("^DJI")

    # Macro
    ibov = get_variation("^BVSP")
    ewz = get_variation("EWZ")
    btc = get_variation("BTC-USD")
    dxy = get_variation("DX-Y.NYB")

    # Top 5 líquidas
    top5 = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "BBAS3.SA"]
    sinais = ""
    for acao in top5:
        sinal = get_rsi_signal(acao)
        sinais += f"{acao.replace('.SA','')} → {sinal}\n"

    # Notícias
    noticias_mercado = get_news("mercado financeiro brasil")
    noticias_petr = get_news("PETR4 Petrobras")
    noticias_vale = get_news("VALE3 Vale")
    noticias_bancos = get_news("Itaú Bradesco Banco do Brasil")

    mensagem = f"""
📊 RELATÓRIO INSTITUCIONAL B3
⏰ {agora}

🇺🇸 PRE-MARKET EUA
S&P500: {sp500}%
Nasdaq: {nasdaq}%
Dow: {dow}%

🇧🇷 BRASIL
IBOV: {ibov}%
EWZ: {ewz}%
DXY: {dxy}%
BTC: {btc}%

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

# ===== ENVIO TELEGRAM V20 =====

async def enviar_async():
    bot = Bot(token=TELEGRAM_TOKEN)
    msg = gerar_relatorio()
    await bot.send_message(chat_id=CHAT_ID, text=msg)

def enviar_relatorio():
    asyncio.run(enviar_async())

# ===== LOOP PRINCIPAL =====

if __name__ == "__main__":
    print("🚀 Robô Institucional iniciado...")
    enviar_relatorio()

    while True:
        print("⏳ Aguardando 1 hora...")
        time.sleep(3600)
        enviar_relatorio()

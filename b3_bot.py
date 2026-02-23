import yfinance as yf
import pandas as pd
import requests
import time
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from telegram import Bot
from datetime import datetime

# ================= CONFIG =================

TELEGRAM_TOKEN = "SEU_TELEGRAM_TOKEN"
CHAT_ID = "SEU_CHAT_ID"
NEWS_API_KEY = "SUA_NEWS_API_KEY"

bot = Bot(token=TELEGRAM_TOKEN)

# ==========================================

def get_rsi_signal(ticker):
    df = yf.download(ticker, period="3mo", interval="1d")
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

def get_variation(ticker):
    df = yf.download(ticker, period="2d", interval="1d")
    var = ((df['Close'][-1] - df['Close'][-2]) / df['Close'][-2]) * 100
    return round(var,2)

def get_news(query):
    url = f"https://newsapi.org/v2/everything?q={query}&language=pt&sortBy=publishedAt&pageSize=3&apiKey={NEWS_API_KEY}"
    r = requests.get(url).json()
    news = ""
    if "articles" in r:
        for art in r["articles"][:3]:
            news += f"• {art['title']}\n"
    return news if news else "Sem notícias relevantes no momento.\n"

def gerar_relatorio():
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    # ===== PRE MARKET EUA =====
    sp500 = get_variation("^GSPC")
    nasdaq = get_variation("^IXIC")
    dow = get_variation("^DJI")

    # ===== RELAÇÕES MACRO =====
    ibov = get_variation("^BVSP")
    ewz = get_variation("EWZ")
    btc = get_variation("BTC-USD")
    dxy = get_variation("DX-Y.NYB")

    # ===== TOP 5 MAIS LIQUIDAS =====
    top5 = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "BBAS3.SA"]

    sinais = ""
    for acao in top5:
        sinal = get_rsi_signal(acao)
        sinais += f"{acao.replace('.SA','')} → {sinal}\n"

    # ===== NOTÍCIAS =====
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
Dow Jones: {dow}%

🇧🇷 BRASIL
IBOV: {ibov}%
EWZ: {ewz}%
DXY: {dxy}%
BTC: {btc}%

🔥 TOP 5 MAIS LÍQUIDAS
{sinais}

📰 NOTÍCIAS MERCADO
{noticias_mercado}

🛢 PETROBRAS
{noticias_petr}

⛏ VALE
{noticias_vale}

🏦 BANCOS
{noticias_bancos}

📌 Análise baseada em EMA 9x21 + RSI 14
"""

    return mensagem

def enviar_relatorio():
    try:
        msg = gerar_relatorio()
        bot.send_message(chat_id=CHAT_ID, text=msg)
        print("Relatório enviado com sucesso.")
    except Exception as e:
        print("Erro:", e)

# ===== LOOP PRINCIPAL =====

if __name__ == "__main__":
    enviar_relatorio()  # Disparo imediato

    while True:
        time.sleep(3600)  # 1 hora
        enviar_relatorio()

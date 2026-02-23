import requests
import pandas as pd
import time
import asyncio
from telegram import Bot
from datetime import datetime

# ================= CONFIG =================

TELEGRAM_TOKEN = "8430351852:AAF50usp88gBEQ9XAlS98pOCVs8aBNztAqc"
CHAT_ID = "8352381582"
ALPHA_KEY = "OYSICYD1972XILCB"
NEWS_API_KEY = "0359528914754b7fbaf98081fbf0ac98"

# ==========================================

# ===== BUSCAR DADOS ALPHA VANTAGE =====

def get_daily_data(symbol):
    try:
        url = (
            f"https://www.alphavantage.co/query?"
            f"function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}"
            f"&outputsize=compact&apikey={ALPHA_KEY}"
        )

        r = requests.get(url, timeout=15).json()

        if "Time Series (Daily)" not in r:
            return None

        df = pd.DataFrame.from_dict(r["Time Series (Daily)"], orient="index")
        df = df.astype(float)
        df = df.sort_index()

        return df

    except Exception as e:
        print("Erro Alpha:", e)
        return None

# ===== VARIAÇÃO =====

def get_variation(symbol):
    df = get_daily_data(symbol)

    if df is None or len(df) < 2:
        return "N/D"

    ultimo = df["4. close"].iloc[-1]
    anterior = df["4. close"].iloc[-2]

    var = ((ultimo - anterior) / anterior) * 100
    return f"{var:.2f}%"

# ===== RSI MANUAL =====

def calcular_rsi(series, period=14):
    delta = series.diff()
    ganho = delta.clip(lower=0)
    perda = -delta.clip(upper=0)

    media_ganho = ganho.rolling(period).mean()
    media_perda = perda.rolling(period).mean()

    rs = media_ganho / media_perda
    rsi = 100 - (100 / (1 + rs))

    return rsi

# ===== SINAL =====

def get_signal(symbol):
    df = get_daily_data(symbol)

    if df is None or len(df) < 30:
        return "Dados insuficientes"

    close = df["4. close"]

    ema9 = close.ewm(span=9).mean()
    ema21 = close.ewm(span=21).mean()
    rsi = calcular_rsi(close)

    rsi_atual = rsi.iloc[-1]

    if ema9.iloc[-1] > ema21.iloc[-1] and rsi_atual > 55:
        return f"🟢 COMPRA (RSI {rsi_atual:.1f})"
    elif ema9.iloc[-1] < ema21.iloc[-1] and rsi_atual < 45:
        return f"🔴 VENDA (RSI {rsi_atual:.1f})"
    else:
        return f"⚪ NEUTRO (RSI {rsi_atual:.1f})"

# ===== NOTÍCIAS =====

def get_news(query):
    try:
        url = (
            f"https://newsapi.org/v2/everything?"
            f"q={query}&language=pt&pageSize=2&apiKey={NEWS_API_KEY}"
        )

        r = requests.get(url).json()

        if "articles" not in r or len(r["articles"]) == 0:
            return "Sem notícias relevantes.\n"

        texto = ""
        for art in r["articles"][:2]:
            texto += f"• {art['title']}\n"

        return texto

    except:
        return "Erro ao buscar notícias.\n"

# ===== RELATÓRIO =====

def gerar_relatorio():
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    sp500 = get_variation("SPY")
    ibov = get_variation("BOVA11.SA")
    ewz = get_variation("EWZ")
    btc = get_variation("BTCUSD")

    top5 = {
        "PETR4": "PETR4.SA",
        "VALE3": "VALE3.SA",
        "ITUB4": "ITUB4.SA",
        "BBDC4": "BBDC4.SA",
        "BBAS3": "BBAS3.SA"
    }

    sinais = ""
    for nome, ticker in top5.items():
        sinais += f"{nome} → {get_signal(ticker)}\n"

    mensagem = f"""
📊 RELATÓRIO INSTITUCIONAL B3
⏰ {agora}

🇺🇸 EUA (ETF Proxy)
S&P500 (SPY): {sp500}

🇧🇷 BRASIL
IBOV (BOVA11): {ibov}
EWZ: {ewz}
BTC: {btc}

🔥 TOP 5 MAIS LÍQUIDAS
{sinais}

📌 Modelo técnico: EMA 9x21 + RSI 14
"""

    return mensagem

# ===== TELEGRAM =====

async def enviar_async():
    bot = Bot(token=TELEGRAM_TOKEN)
    msg = gerar_relatorio()
    await bot.send_message(chat_id=CHAT_ID, text=msg)

def enviar_relatorio():
    asyncio.run(enviar_async())

# ===== LOOP =====

if __name__ == "__main__":
    print("🚀 Robô Institucional Alpha iniciado")
    enviar_relatorio()

    while True:
        print("⏳ Aguardando 1 hora...")
        time.sleep(3600)
        enviar_relatorio()

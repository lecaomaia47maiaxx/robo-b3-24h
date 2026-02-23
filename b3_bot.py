import requests
import pandas as pd
import time
import asyncio
from telegram import Bot
from datetime import datetime

TELEGRAM_TOKEN = "8430351852:AAF50usp88gBEQ9XAlS98pOCVs8aBNztAqc"
CHAT_ID = "8352381582"
TWELVE_KEY = "59c25209cf3141f088781b53e576eb55"

# ===================== TWELVEDATA =====================

def get_data(symbol):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&outputsize=100&apikey={TWELVE_KEY}"
    r = requests.get(url).json()

    if "values" not in r:
        print("Erro API:", r)
        return None

    df = pd.DataFrame(r["values"])
    df["close"] = df["close"].astype(float)
    df = df.sort_values("datetime")
    return df

# ===================== RSI =====================

def calcular_rsi(series, period=14):
    delta = series.diff()
    ganho = delta.clip(lower=0)
    perda = -delta.clip(upper=0)
    media_ganho = ganho.rolling(period).mean()
    media_perda = perda.rolling(period).mean()
    rs = media_ganho / media_perda
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ===================== SINAL =====================

def get_signal(symbol):

    df = get_data(symbol)

    if df is None or len(df) < 30:
        return "Sem dados"

    close = df["close"]

    ema9 = close.ewm(span=9).mean()
    ema21 = close.ewm(span=21).mean()
    rsi = calcular_rsi(close)

    rsi_atual = rsi.iloc[-1]

    if ema9.iloc[-1] > ema21.iloc[-1] and rsi_atual > 55:
        sinal = "🟢 COMPRA"
    elif ema9.iloc[-1] < ema21.iloc[-1] and rsi_atual < 45:
        sinal = "🔴 VENDA"
    else:
        sinal = "⚪ NEUTRO"

    return f"{sinal} (RSI {rsi_atual:.1f})"

# ===================== VARIAÇÃO =====================

def get_variation(symbol):

    df = get_data(symbol)

    if df is None or len(df) < 2:
        return "N/D"

    ultimo = df["close"].iloc[-1]
    anterior = df["close"].iloc[-2]

    var = ((ultimo - anterior) / anterior) * 100

    return f"{var:.2f}%"

# ===================== RELATÓRIO =====================

def gerar_relatorio():

    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    sp500 = get_variation("SPY")
    ibov = get_variation("BOVA11")
    btc = get_variation("BTC/USD")

    ativos = {
        "PETR4": "PETR4",
        "VALE3": "VALE3",
        "ITUB4": "ITUB4",
        "BBDC4": "BBDC4",
        "BBAS3": "BBAS3"
    }

    sinais = ""

    for nome, ticker in ativos.items():
        sinais += f"{nome} → {get_signal(ticker)}\n"

    mensagem = f"""
📊 RELATÓRIO INSTITUCIONAL B3
⏰ {agora}

🇺🇸 EUA
S&P500 (SPY): {sp500}

🇧🇷 BRASIL
IBOV (BOVA11): {ibov}
BTC: {btc}

🔥 TOP 5 MAIS LÍQUIDAS
{sinais}

📌 Modelo técnico: EMA 9x21 + RSI 14
"""

    return mensagem

# ===================== TELEGRAM =====================

async def enviar():
    bot = Bot(token=TELEGRAM_TOKEN)
    msg = gerar_relatorio()
    await bot.send_message(chat_id=CHAT_ID, text=msg)

if __name__ == "__main__":
    print("🚀 Robô TwelveData iniciado")
    asyncio.run(enviar())

    while True:
        time.sleep(3600)
        asyncio.run(enviar())

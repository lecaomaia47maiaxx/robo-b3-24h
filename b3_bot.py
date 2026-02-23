import requests
import pandas as pd
import time
import asyncio
from telegram import Bot
from datetime import datetime

TELEGRAM_TOKEN = "8430351852:AAF50usp88gBEQ9XAlS98pOCVs8aBNztAqc"
CHAT_ID = "8352381582"
ALPHA_KEY = "OYSICYD1972XILCB"

# ===================== ALPHA =====================

def get_daily(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=compact&apikey={ALPHA_KEY}"
    r = requests.get(url).json()

    if "Time Series (Daily)" not in r:
        print("Limite atingido ou erro:", r)
        return None

    df = pd.DataFrame.from_dict(r["Time Series (Daily)"], orient="index")
    df = df.astype(float)
    df = df.sort_index()
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

# ===================== RELATÓRIO =====================

def gerar_relatorio():

    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    # 🔥 REDUZIMOS PARA 5 CHAMADAS
    ativos = {
        "PETR4": "PETR4.SA",
        "VALE3": "VALE3.SA",
        "ITUB4": "ITUB4.SA",
        "BBDC4": "BBDC4.SA",
        "BBAS3": "BBAS3.SA"
    }

    sinais = ""

    for nome, ticker in ativos.items():

        df = get_daily(ticker)

        if df is None or len(df) < 30:
            sinais += f"{nome} → Sem dados\n"
            continue

        close = df["4. close"]

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

        sinais += f"{nome} → {sinal} (RSI {rsi_atual:.1f})\n"

        time.sleep(12)  # 🔥 evita estourar limite

    mensagem = f"""
📊 RELATÓRIO INSTITUCIONAL B3
⏰ {agora}

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
    print("🚀 Robô iniciado")
    asyncio.run(enviar())

    while True:
        time.sleep(3600)
        asyncio.run(enviar())

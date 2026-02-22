import asyncio
import yfinance as yf
import pandas as pd
from telegram import Bot
import ta

# ================== IDENTIFICAÇÃO ==================
print("🔥 ROBÔ B3 NOVO 100% ATIVO 🔥")

# ================== CONFIG ==================
TOKEN = "8430351852:AAF50usp88gBEQ9XAlS98pOCVs8aBNztAqc"
CHAT_ID = "8352381582"

bot = Bot(token=TOKEN)

ACOES = [
    "PETR4.SA","VALE3.SA","ITUB4.SA",
    "BBDC4.SA","ABEV3.SA","BBAS3.SA",
    "WEGE3.SA","MGLU3.SA","SUZB3.SA","RENT3.SA"
]

# ================== DOWNLOAD ==================
def baixar(ticker):
    try:
        df = yf.Ticker(ticker).history(period="6mo", interval="1d")
        if df.empty:
            return None
        return df.dropna()
    except:
        return None


# ================== SENTIMENTO GLOBAL ==================
def sentimento_global():
    indices = ["^GSPC","^IXIC","^DJI","^GDAXI","^FTSE","^N225"]
    score = 0

    for ind in indices:
        df = baixar(ind)
        if df is None or len(df) < 2:
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


# ================== TENDÊNCIA IBOV ==================
def tendencia_ibov():
    df = baixar("^BVSP")
    if df is None or len(df) < 200:
        return "DADOS INSUFICIENTES"

    close = df["Close"]
    mm200 = close.rolling(200).mean()

    if close.iloc[-1] > mm200.iloc[-1]:
        return "ALTA (acima MM200) 📈"
    else:
        return "BAIXA (abaixo MM200) 📉"


# ================== ANALISE AÇÃO ==================
def analisar(ticker):
    df = baixar(ticker)
    if df is None or len(df) < 200:
        return None

    close = df["Close"]
    volume = df["Volume"]

    sma9 = close.rolling(9).mean()
    sma21 = close.rolling(21).mean()
    sma200 = close.rolling(200).mean()

    rsi = ta.momentum.RSIIndicator(close).rsi()

    variacao = ((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100

    score = 0

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

    if variacao > 0:
        score += 1
    else:
        score -= 1

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
        "variacao": round(variacao,2)
    }


# ================== EXECUÇÃO ==================
async def executar():
    sentimento = sentimento_global()
    ibov = tendencia_ibov()

    compras = []
    vendas = []
    neutras = []
    ranking = []

    for acao in ACOES:
        resultado = analisar(acao)
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
🚀 ROBÔ B3 NOVO ATIVO

📊 ANÁLISE DIÁRIA B3

🌍 Sentimento Global: {sentimento}
📈 Tendência IBOV: {ibov}

━━━━━━━━━━━━━━━━━━

🟢 AÇÕES EM COMPRA:
"""

    mensagem += "\n".join([f"{c['ticker']} | {c['variacao']}%" for c in compras]) if compras else "Nenhuma"

    mensagem += "\n\n🔴 AÇÕES EM VENDA:\n"
    mensagem += "\n".join([f"{v['ticker']} | {v['variacao']}%" for v in vendas]) if vendas else "Nenhuma"

    mensagem += "\n\n🔥 TOP 3 DO DIA:\n"
    for top in ranking[:3]:
        mensagem += f"{top['ticker']} ({top['variacao']}%)\n"

    await bot.send_message(chat_id=CHAT_ID, text=mensagem)


async def scheduler():
    while True:
        try:
            await executar()
        except Exception as e:
            print("Erro:", e)

        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(scheduler())

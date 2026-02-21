import asyncio
import os
import yfinance as yf
import pandas as pd
import ta
from telegram import Bot

# ================= CONFIG =================
TOKEN = "8430351852:AAF50usp88gBEQ9XAlS98pOCVs8aBNztAqc"
CHAT_ID = "8352381582"

if not TOKEN or not CHAT_ID:
    raise Exception("TOKEN ou CHAT_ID não configurado nas variáveis do Railway.")

bot = Bot(token=TOKEN)

ACOES = [
    "PETR4.SA","VALE3.SA","ITUB4.SA",
    "BBDC4.SA","ABEV3.SA","BBAS3.SA",
    "WEGE3.SA","MGLU3.SA","SUZB3.SA","RENT3.SA"
]

# ================= FUNÇÕES =================

def baixar_dados(ticker):
    try:
        df = yf.download(
            ticker,
            period="6mo",
            interval="1d",
            progress=False,
            auto_adjust=True
        )
        if df.empty:
            print(f"Sem dados para {ticker}")
            return None
        return df.dropna()
    except Exception as e:
        print(f"Erro ao baixar {ticker}: {e}")
        return None


def calcular_score(df):
    close = df["Close"]
    volume = df["Volume"]

    sma9 = close.rolling(9).mean().iloc[-1]
    sma21 = close.rolling(21).mean().iloc[-1]

    rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]

    vol_media = volume.rolling(20).mean().iloc[-1]
    vol_atual = volume.iloc[-1]

    score = 50

    # Tendência
    score += 20 if sma9 > sma21 else -20

    # RSI
    if rsi < 30:
        score += 15
    elif rsi > 70:
        score -= 15

    # Volume
    if vol_atual > vol_media:
        score += 10

    return max(0, min(100, int(score)))


def classificar(score):
    if score >= 70:
        return "🔥 FORTE COMPRA"
    elif score <= 30:
        return "🔻 FORTE VENDA"
    else:
        return "⚖ NEUTRO"


async def enviar_mensagem(texto):
    partes = [texto[i:i+4000] for i in range(0, len(texto), 4000)]
    for parte in partes:
        await bot.send_message(chat_id=CHAT_ID, text=parte)


# ================= LOOP PRINCIPAL =================

async def scanner():
    print("Robô iniciado com sucesso.")

    while True:
        print("Iniciando nova análise...")

        ranking = []
        alertas = []

        for acao in ACOES:
            df = baixar_dados(acao)

            if df is None or len(df) < 30:
                continue

            try:
                score = calcular_score(df)
                sinal = classificar(score)

                nome = acao.replace(".SA","")
                ranking.append((nome, score, sinal))

                if score >= 70 or score <= 30:
                    alertas.append(f"{nome} | {score} | {sinal}")

                print(f"{nome} analisada | Score: {score}")

            except Exception as e:
                print(f"Erro ao analisar {acao}: {e}")

        if not ranking:
            await enviar_mensagem("⚠ Nenhum dado disponível no momento.")
            await asyncio.sleep(900)
            continue

        ranking.sort(key=lambda x: x[1], reverse=True)

        texto = "📊 SCANNER B3 24H\n\n"
        for item in ranking:
            texto += f"{item[0]} | {item[1]} | {item[2]}\n"

        await enviar_mensagem(texto)

        if alertas:
            alerta_texto = "⚡ ALERTAS FORTES ⚡\n\n" + "\n".join(alertas)
            await enviar_mensagem(alerta_texto)

        print("Análise concluída. Aguardando 15 minutos...\n")

        await asyncio.sleep(900)  # 15 minutos


# ================= START =================

if __name__ == "__main__":
    asyncio.run(scanner())  

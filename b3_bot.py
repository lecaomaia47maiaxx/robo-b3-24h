import asyncio
import yfinance as yf
import pandas as pd
import ta
from telegram import Bot
from datetime import datetime

# ==========================
# CONFIGURAÇÕES
# ==========================

TOKEN = "8430351852:AAF50usp88gBEQ9XAlS98pOCVs8aBNztAqc"
CHAT_ID = "8352381582"

bot = Bot(token=TOKEN)

# Lista de ações B3
TICKERS = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA",
    "BBAS3.SA", "WEGE3.SA", "ABEV3.SA", "MGLU3.SA",
    "PETR3.SA", "B3SA3.SA"
]

IBOV = "^BVSP"

# ==========================
# FUNÇÃO DOWNLOAD
# ==========================

def baixar_dados(ticker):
    try:
        df = yf.download(
            ticker,
            period="1y",
            interval="1d",
            progress=False,
            threads=False
        )

        if df is None or df.empty:
            print(f"[ERRO] Sem dados: {ticker}")
            return None

        df.dropna(inplace=True)
        return df

    except Exception as e:
        print(f"[ERRO DOWNLOAD] {ticker}: {e}")
        return None

# ==========================
# ANALISE PROFISSIONAL
# ==========================

def analisar_acao(df):
    df["SMA20"] = ta.trend.sma_indicator(df["Close"], window=20)
    df["SMA200"] = ta.trend.sma_indicator(df["Close"], window=200)
    df["RSI"] = ta.momentum.rsi(df["Close"], window=14)
    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd_diff()

    ultima = df.iloc[-1]

    score = 0

    # Tendência principal (Média 200)
    if ultima["Close"] > ultima["SMA200"]:
        score += 1
    else:
        score -= 1

    # Tendência curta
    if ultima["Close"] > ultima["SMA20"]:
        score += 1
    else:
        score -= 1

    # RSI
    if ultima["RSI"] < 35:
        score += 1
    elif ultima["RSI"] > 65:
        score -= 1

    # MACD
    if ultima["MACD"] > 0:
        score += 1
    else:
        score -= 1

    # Percentual do dia
    variacao = ((ultima["Close"] / df["Close"].iloc[-2]) - 1) * 100

    return score, variacao

# ==========================
# TENDÊNCIA IBOV
# ==========================

def tendencia_ibov():
    df = baixar_dados(IBOV)
    if df is None:
        return "Indefinida"

    df["SMA200"] = ta.trend.sma_indicator(df["Close"], window=200)
    ultima = df.iloc[-1]

    if ultima["Close"] > ultima["SMA200"]:
        return "📈 Alta (Acima da Média 200)"
    else:
        return "📉 Baixa (Abaixo da Média 200)"

# ==========================
# SCANNER PRINCIPAL
# ==========================

async def scanner():
    while True:
        print("🔎 Iniciando varredura...")

        compras = []
        vendas = []
        ranking = []

        for ticker in TICKERS:
            df = baixar_dados(ticker)
            if df is None:
                continue

            score, variacao = analisar_acao(df)

            ranking.append((ticker, variacao))

            # MODO MAIS AGRESSIVO
            if score >= 1:
                compras.append(f"{ticker} | {variacao:.2f}%")
            elif score <= -1:
                vendas.append(f"{ticker} | {variacao:.2f}%")

        ranking.sort(key=lambda x: x[1], reverse=True)
        top3 = ranking[:3]

        ibov_status = tendencia_ibov()

        mensagem = f"""
📊 <b>SCANNER B3 PROFISSIONAL 24H</b>
🕒 {datetime.now().strftime('%d/%m/%Y %H:%M')}

📌 <b>Tendência IBOV:</b>
{ibov_status}

🔥 <b>Top 3 Força do Dia:</b>
"""

        for acao in top3:
            mensagem += f"• {acao[0]} | {acao[1]:.2f}%\n"

        mensagem += "\n🟢 <b>Sinais de COMPRA:</b>\n"
        mensagem += "\n".join(compras) if compras else "Nenhuma"

        mensagem += "\n\n🔴 <b>Sinais de VENDA:</b>\n"
        mensagem += "\n".join(vendas) if vendas else "Nenhuma"

        await bot.send_message(chat_id=CHAT_ID, text=mensagem, parse_mode="HTML")

        print("✅ Enviado com sucesso.")
        await asyncio.sleep(1800)  # 30 minutos

# ==========================
# EXECUÇÃO
# ==========================

if __name__ == "__main__":
    asyncio.run(scanner())

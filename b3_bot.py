from datetime import datetime
import pandas as pd
import numpy as np
import yfinance as yf

from telegram.ext import ApplicationBuilder, ContextTypes

# ==============================
# CONFIGURAÇÕES
# ==============================

TELEGRAM_TOKEN = "8709112968:AAHvkruRIiOuGK07-PI8RBWVgp7jrHqlox8"
CHAT_ID = "8352381582"

ATIVOS_TOP = [
    "PETR4.SA",
    "VALE3.SA",
    "ITUB4.SA",
    "BBDC4.SA",
    "BBAS3.SA"
]

INDICES = {
    "S&P500": "^GSPC",
    "Nasdaq": "^IXIC",
    "Dow Jones": "^DJI",
    "IBOV": "^BVSP",
    "EWZ": "EWZ",
    "BTC": "BTC-USD"
}

# ==============================
# INDICADORES
# ==============================

def calcular_rsi(series, period=14):
    delta = series.diff()
    ganho = delta.clip(lower=0)
    perda = -delta.clip(upper=0)

    media_ganho = ganho.rolling(period).mean()
    media_perda = perda.rolling(period).mean()

    rs = media_ganho / media_perda
    rsi = 100 - (100 / (1 + rs))
    return rsi


def baixar_dados(ticker, periodo="3mo"):
    try:
        df = yf.download(
            ticker,
            period=periodo,
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=False
        )
        if df is None or df.empty:
            return None

        df = df.dropna()
        return df
    except:
        return None


# ==============================
# ANÁLISE TÉCNICA
# ==============================

def analisar_ativo(ticker):

    df = baixar_dados(ticker)

    if df is None or len(df) < 30:
        return "Sem dados suficientes"

    close = df["Close"]

    ema9 = close.ewm(span=9).mean()
    ema21 = close.ewm(span=21).mean()
    rsi = calcular_rsi(close)

    rsi_atual = float(rsi.iloc[-1])

    if ema9.iloc[-1] > ema21.iloc[-1] and rsi_atual > 55:
        sinal = "🟢 COMPRA"
    elif ema9.iloc[-1] < ema21.iloc[-1] and rsi_atual < 45:
        sinal = "🔴 VENDA"
    else:
        sinal = "⚪ NEUTRO"

    return f"{sinal} | RSI {rsi_atual:.1f}"


# ==============================
# VARIAÇÃO DIÁRIA
# ==============================

def variacao_dia(ticker):

    df = baixar_dados(ticker, periodo="5d")

    if df is None or len(df) < 2:
        return "N/D"

    ultimo = df["Close"].iloc[-1]
    anterior = df["Close"].iloc[-2]

    variacao = ((ultimo - anterior) / anterior) * 100

    return f"{variacao:.2f}%"


# ==============================
# RELATÓRIO
# ==============================

def gerar_relatorio():

    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    texto_indices = ""
    for nome, ticker in INDICES.items():
        texto_indices += f"{nome}: {variacao_dia(ticker)}\n"

    texto_top = ""
    for ativo in ATIVOS_TOP:
        nome = ativo.replace(".SA", "")
        texto_top += f"{nome} → {analisar_ativo(ativo)}\n"

    mensagem = f"""
📊 RELATÓRIO INSTITUCIONAL B3
⏰ {agora}

🌎 MERCADO GLOBAL
{texto_indices}

🔥 TOP 5 MAIS LÍQUIDAS (EMA 9x21 + RSI 14)
{texto_top}

📌 Modelo técnico: Cruzamento EMA 9x21 + RSI 14
"""

    return mensagem


# ==============================
# ENVIO AUTOMÁTICO
# ==============================

async def enviar_relatorio(context: ContextTypes.DEFAULT_TYPE):
    mensagem = gerar_relatorio()
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=mensagem
    )


# ==============================
# MAIN (SEM asyncio.run)
# ==============================

def main():

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Envia 1x ao iniciar
    app.job_queue.run_once(enviar_relatorio, when=5)

    # Envia a cada 1 hora
    app.job_queue.run_repeating(
        enviar_relatorio,
        interval=3600,
        first=3600
    )

    print("🚀 Robô institucional rodando estável...")

    app.run_polling()


if __name__ == "__main__":
    main()

import asyncio
import requests
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, time
from telegram import Bot

# ================= CONFIGURAÇÃO =================
TOKEN = "8430351852:AAF50usp88gBEQ9XAlS98pOCVs8aBNztAqc"
CHAT_ID = "8352381582"
ALPHA_KEY = "OYSICYD1972XILCB"

bot = Bot(token=TOKEN)

ACOES_LIQUIDAS = [
    "PETR4.SA","VALE3.SA","ITUB4.SA",
    "BBDC4.SA","BBAS3.SA","WEGE3.SA",
    "ABEV3.SA","MGLU3.SA","SUZB3.SA","RENT3.SA"
]

# ================= FUNÇÕES BÁSICAS =================

def variacao_dia(ticker):
    df = yf.download(ticker, period="2d", interval="1d", progress=False)
    if len(df) < 2:
        return None
    return round(((df["Close"].iloc[-1] / df["Close"].iloc[-2"]) - 1) * 100, 2)

def correlacao(t1, t2, period="1mo"):
    df1 = yf.download(t1, period=period, progress=False)["Close"]
    df2 = yf.download(t2, period=period, progress=False)["Close"]
    df = pd.concat([df1, df2], axis=1).dropna()
    if len(df) < 10:
        return None
    return round(df.corr().iloc[0,1], 2)

# ================= MÓDULOS =================

def ewz_vs_ibov():
    ewz = variacao_dia("EWZ")
    ibov = variacao_dia("^BVSP")
    corr = correlacao("EWZ","^BVSP")
    return ewz, ibov, corr

def fluxo_estrangeiro():
    df = yf.download("EWZ", period="5d", progress=False)
    if len(df) < 2:
        return "Indefinido"
    volume = df["Volume"].iloc[-1]
    media = df["Volume"].mean()
    if volume > media * 1.3:
        return "Entrada forte"
    elif volume < media * 0.7:
        return "Saída forte"
    else:
        return "Fluxo normal"

def moedas():
    brl = variacao_dia("BRL=X")
    eur = variacao_dia("EURUSD=X")
    jpy = variacao_dia("JPY=X")
    return brl, eur, jpy

def btc_vs_sp():
    corr = correlacao("BTC-USD","^GSPC")
    btc = variacao_dia("BTC-USD")
    return btc, corr

def pre_market_usa():
    sp500 = variacao_dia("^GSPC")
    dow = variacao_dia("^DJI")
    nasdaq = variacao_dia("^IXIC")
    return sp500, dow, nasdaq

def noticias():
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&apikey={ALPHA_KEY}"
    r = requests.get(url)
    data = r.json()
    if "feed" not in data:
        return ["Sem notícias disponíveis"]
    # Filtrar notícias de interesse: Petrobras, Vale, bancos
    noticias_filtro = []
    for item in data["feed"][:10]:
        title = item["title"]
        if any(p in title.lower() for p in ["petrobras","vale","itau","banco","bbas"]):
            noticias_filtro.append(title)
    if not noticias_filtro:
        noticias_filtro = ["Sem notícias relevantes sobre Petrobras, Vale ou bancos"]
    return noticias_filtro

# ================= ALERTAS DE AÇÕES =================

def analisar_acao(ticker):
    df = yf.download(ticker, period="3mo", progress=False)
    if len(df) < 30:
        return None

    close = df["Close"]
    mm21 = close.rolling(21).mean().iloc[-1]
    preco = close.iloc[-1]

    delta = close.diff()
    ganho = delta.clip(lower=0).rolling(14).mean()
    perda = -delta.clip(upper=0).rolling(14).mean()
    rs = ganho / perda
    rsi = 100 - (100 / (1 + rs))
    rsi_atual = rsi.iloc[-1]

    if preco > mm21 and rsi_atual > 55:
        return "COMPRA"
    elif preco < mm21 and rsi_atual < 45:
        return "VENDA"
    return None

def top_5_acoes():
    resultados = []
    for acao in ACOES_LIQUIDAS:
        sinal = analisar_acao(acao)
        if sinal:
            var = variacao_dia(acao)
            resultados.append({"acao": acao.replace(".SA",""), "sinal": sinal, "variacao": var})
    resultados = sorted(resultados, key=lambda x: abs(x["variacao"]), reverse=True)
    return resultados[:5]

# ================= RELATÓRIO GLOBAL =================

async def enviar_relatorio():
    msg = "📊 *RELATÓRIO GLOBAL + B3 ALEX*\n\n"

    ewz, ibov, corr = ewz_vs_ibov()
    fluxo = fluxo_estrangeiro()
    brl, eur, jpy = moedas()
    btc, btc_corr = btc_vs_sp()
    sp500, dow, nasdaq = pre_market_usa()

    msg += "🌐 *Pre-market EUA*\n"
    msg += f"S&P500: {sp500}% | Dow: {dow}% | Nasdaq: {nasdaq}%\n\n"

    msg += "📌 EWZ vs IBOV\n"
    msg += f"EWZ: {ewz}% | IBOV: {ibov}% | Correlação: {corr}\n"
    msg += f"Fluxo Estrangeiro: {fluxo}\n\n"

    msg += "💱 Moedas vs USD\n"
    msg += f"BRL: {brl}% | EUR: {eur}% | JPY: {jpy}%\n\n"

    msg += "🪙 Bitcoin\n"
    msg += f"BTC: {btc}% | Correlação S&P500: {btc_corr}\n\n"

    msg += "📰 Notícias Relevantes\n"
    for n in noticias():
        msg += f"• {n}\n"

    # Top 5 ações mais fortes
    top5 = top_5_acoes()
    if top5:
        msg += "\n🔥 *TOP 5 AÇÕES COM SINAL* 🔥\n"
        for t in top5:
            msg += f"{t['acao']} | {t['sinal']} | {t['variacao']}%\n"
    else:
        msg += "\nNenhuma ação com sinal forte no momento"

    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")

# ================= ALERTAS HORÁRIOS =================

async def alertas_horarios():
    mensagens = []
    for acao in ACOES_LIQUIDAS:
        sinal = analisar_acao(acao)
        if sinal:
            nome = acao.replace(".SA","")
            var = variacao_dia(acao)
            mensagens.append(f"{nome}: {sinal} ({var}%)")
    if mensagens:
        texto = "🚨 *ALERTAS DO MOMENTO*\n\n" + "\n".join(mensagens)
        await bot.send_message(chat_id=CHAT_ID, text=texto, parse_mode="Markdown")

# ================= LOOP PRINCIPAL =================

async def scheduler():
    print("🚀 Robô Global iniciado com sucesso")
    primeira_execucao = True

    while True:
        try:
            agora = datetime.now().time()

            # 🔥 TESTE IMEDIATO AO INICIAR
            if primeira_execucao:
                await enviar_relatorio()
                primeira_execucao = False

            # 🚨 ALERTAS HORÁRIOS - 1h
            await alertas_horarios()
            await asyncio.sleep(3600)

        except Exception as e:
            print("Erro no loop:", e)
            await asyncio.sleep(60)

# ================= EXECUÇÃO =================

if __name__ == "__main__":
    asyncio.run(scheduler())

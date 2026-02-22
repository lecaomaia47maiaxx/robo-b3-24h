import asyncio
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, time
from telegram import Bot

# ================= CONFIGURAÇÃO =================
TOKEN = "8430351852:AAF50usp88gBEQ9XAlS98pOCVs8aBNztAqc"
CHAT_ID = "8352381582"
ALPHA_KEY = "OYSICYD1972XILCB"

bot = Bot(token=TOKEN)

ACOES_LIQUIDAS = [
    "PETR4.SA","VALE3.SA","ITUB4.SA",
    "BBDC4.SA","BBAS3.SA","WEGE3.SA"
]

# ================= FUNÇÕES BÁSICAS =================

def variacao_dia(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="1d", progress=False)
        if len(df) < 2:
            return None
        return round(((df["Close"].iloc[-1] / df["Close"].iloc[-2]) - 1) * 100, 2)
    except:
        return None

def correlacao(t1, t2):
    try:
        df1 = yf.download(t1, period="1mo", progress=False)["Close"]
        df2 = yf.download(t2, period="1mo", progress=False)["Close"]
        df = pd.concat([df1, df2], axis=1).dropna()
        if len(df) < 10:
            return None
        return round(df.corr().iloc[0,1], 2)
    except:
        return None

# ================= INDICADORES GLOBAIS =================

def mercados_globais():
    mercados = {
        "Dow Jones": "^DJI",
        "S&P500": "^GSPC",
        "Nasdaq": "^IXIC",
        "DAX": "^GDAXI",
        "FTSE": "^FTSE",
        "CAC": "^FCHI",
        "Nikkei": "^N225",
        "Hang Seng": "^HSI"
    }
    resultados = {}
    for nome, ticker in mercados.items():
        var = variacao_dia(ticker)
        resultados[nome] = var
    return resultados

def commodities():
    ativos = {
        "Petróleo WTI": "CL=F",
        "Ouro": "GC=F",
        "Minério de ferro": "VALE3.SA"  # proxy para minério
    }
    resultados = {}
    for nome, ticker in ativos.items():
        var = variacao_dia(ticker)
        resultados[nome] = var
    return resultados

def ewz_vs_ibov():
    ewz = variacao_dia("EWZ")
    ibov = variacao_dia("^BVSP")
    corr = correlacao("EWZ", "^BVSP")
    tendencia = "Alta 📈" if ibov and ibov > 0 else "Baixa 📉"
    return ewz, ibov, corr, tendencia

def fluxo_estrangeiro():
    try:
        df = yf.download("EWZ", period="5d", progress=False)
        if len(df) < 2:
            return "Indefinido"
        volume = df["Volume"].iloc[-1]
        media = df["Volume"].mean()
        if volume > media * 1.3:
            return "Entrada estrangeira forte 📈"
        elif volume < media * 0.7:
            return "Saída estrangeira forte 📉"
        else:
            return "Fluxo neutro"
    except:
        return "Indefinido"

def moedas():
    brl = variacao_dia("BRL=X")
    eur = variacao_dia("EURUSD=X")
    jpy = variacao_dia("JPY=X")
    return brl, eur, jpy

def btc_vs_sp():
    btc = variacao_dia("BTC-USD")
    corr = correlacao("BTC-USD", "^GSPC")
    return btc, corr

def noticias():
    try:
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&apikey={ALPHA_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()
        if "feed" not in data:
            return ["Sem notícias relevantes"]
        return [item["title"] for item in data["feed"][:5]]
    except:
        return ["Erro ao buscar notícias"]

# ================= ANÁLISE DAS AÇÕES =================

def analisar_acao(ticker):
    try:
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
            return "COMPRA 🔥"
        elif preco < mm21 and rsi_atual < 45:
            return "VENDA 🔻"
        else:
            return "NEUTRA 🟡"
    except:
        return None

# ================= RELATÓRIO GLOBAL =================

async def enviar_relatorio():
    msg = "📊 *RELATÓRIO GLOBAL + B3 INSTITUCIONAL*\n\n"

    # Mercados globais
    globais = mercados_globais()
    msg += "🌎 *Mercados Globais*\n"
    for m, v in globais.items():
        if v is not None:
            sinal = "📈 Positivo" if v > 0 else "📉 Negativo"
            msg += f"{m}: {v}% ({sinal})\n"
        else:
            msg += f"{m}: Dados indisponíveis\n"
    msg += "\n"

    # Commodities
    com = commodities()
    msg += "⛏️ *Commodities*\n"
    for c, v in com.items():
        if v is not None:
            sinal = "📈 Positivo" if v > 0 else "📉 Negativo"
            msg += f"{c}: {v}% ({sinal})\n"
        else:
            msg += f"{c}: Dados indisponíveis\n"
    msg += "\n"

    # IBOV e EWZ
    ewz, ibov, corr, tendencia = ewz_vs_ibov()
    fluxo = fluxo_estrangeiro()
    msg += f"🇧🇷 *B3 / EWZ*\nIBOV: {ibov}% | EWZ: {ewz}%\nTendência IBOV: {tendencia}\nCorrelação EWZ x IBOV: {corr}\nFluxo estrangeiro: {fluxo}\n\n"

    # Moedas
    brl, eur, jpy = moedas()
    msg += f"💱 *Moedas vs USD*\nBRL: {brl}% | EUR: {eur}% | JPY: {jpy}%\n\n"

    # Bitcoin
    btc, btc_corr = btc_vs_sp()
    msg += f"🪙 *Bitcoin*\nBTC: {btc}% | Correlação BTC x S&P500: {btc_corr}\n\n"

    # Notícias
    msg += "📰 *Notícias relevantes do dia:*\n"
    for n in noticias():
        msg += f"• {n}\n"
    msg += "\n"

    # Ações líquidas B3
    msg += "📈 *Análise das ações mais líquidas*\n"
    for acao in ACOES_LIQUIDAS:
        sinal = analisar_acao(acao)
        msg += f"{acao.replace('.SA','')}: {sinal}\n"

    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")

# ================= ALERTAS HORÁRIOS =================

async def alertas_horarios():
    mensagens = []
    for acao in ACOES_LIQUIDAS:
        sinal = analisar_acao(acao)
        if sinal in ["COMPRA 🔥","VENDA 🔻"]:
            nome = acao.replace(".SA","")
            mensagens.append(f"{nome}: {sinal}")

    if mensagens:
        texto = "🚨 *ALERTAS DO MOMENTO*\n\n" + "\n".join(mensagens)
        await bot.send_message(chat_id=CHAT_ID, text=texto, parse_mode="Markdown")

# ================= LOOP PRINCIPAL =================

async def scheduler():
    print("🚀 Robô Institucional Máximo Ativo")

    primeira_execucao = True

    while True:
        try:
            agora = datetime.now().time()

            # 🔥 TESTE IMEDIATO
            if primeira_execucao:
                await bot.send_message(chat_id=CHAT_ID, text="🚀 Robô Global iniciado com sucesso")
                await enviar_relatorio()
                primeira_execucao = False

            # 📊 RELATÓRIO 09:00
            if time(9,0) <= agora <= time(9,5):
                await enviar_relatorio()
                await asyncio.sleep(3600)

            # 🚨 ALERTAS HORÁRIOS
            await alertas_horarios()
            await asyncio.sleep(3600)

        except Exception as e:
            print("Erro no loop:", e)
            await asyncio.sleep(60)

# ================= START =================

if __name__ == "__main__":
    asyncio.run(scheduler())

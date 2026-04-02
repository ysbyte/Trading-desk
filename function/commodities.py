import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import matplotlib.pyplot as plt

def get_oil_data(start="2010-01-01"):
    tickers = ["BZ=F","CL=F"]
    
    data = yf.download(tickers, start=start, auto_adjust=False)
    
    prices = data["Close"]
    prices.columns = ["Brent", "WTI"]
    
    return prices.dropna()

def compute_returns(df):
    return df.pct_change().dropna()

def annual_return(r):
    return r.mean() * 252

def annual_vol(r):
    return r.std() * (252 ** 0.5)

def sharpe(r):
    return annual_return(r) / annual_vol(r)

def compute_spread(df):
    return df["Brent"] - df["WTI"]

def compute_momentum(prices, window=20):
    return ((prices.iloc[-1] / prices.iloc[-window]) - 1) * 100

def max_drawdown(prices):
    rolling_max = prices.cummax()
    drawdowns = (prices - rolling_max) / rolling_max
    return drawdowns.min() * 100

def zscore(series, window=30):
    mean = series.rolling(window).mean()
    std = series.rolling(window).std()
    return (series - mean) / std

def signal(z, threshold=2):
    s = pd.Series(0, index=z.index)
    
    s[z > threshold] = -1
    s[z < -threshold] = 1
    
    return s

def log_returns(df):
    df = df[df > 0]
    return np.log(df).diff().dropna()

def backtest(df, signal):
    r = log_returns(df)
    
    spread_r = r["Brent"] - r["WTI"]
    
    signal = signal.shift(1).loc[spread_r.index]
    
    strat_r = signal * spread_r
    
    pnl = strat_r.cumsum()
    
    sharpe = (strat_r.mean() / strat_r.std()) * np.sqrt(252)
    
    drawdown = pnl - pnl.cummax()
    
    return pnl, strat_r, sharpe, drawdown.min()

def get_eia_inventory(api_key):
    url = f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={api_key}&frequency=weekly&data[0]=value&facets[series][]=WCESTUS1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=500"
    
    try:
        response = requests.get(url)
        data = response.json()["response"]["data"]
        df_inv = pd.DataFrame(data)
        df_inv["date"] = pd.to_datetime(df_inv["period"])
        df_inv["inventory"] = df_inv["value"].astype(float) / 1000 
        df_inv = df_inv.sort_values("date").set_index("date")
        
        df_inv["variation"] = df_inv["inventory"].diff()
        
        return df_inv[["inventory", "variation"]].dropna()
    except Exception as e:
        print(f"Erreur EIA: {e}")
        return pd.DataFrame()
    
def futures_curve(symbol="WTI", months=6):
    ticker_map = {"WTI": "CL", "Brent": "BZ"}
    s = ticker_map.get(symbol, "CL")
    
    codes_mois = "FGHJKMNQUVXZ"
    today = datetime.now()
    current_month = today.month
    current_year = today.year % 100

    tickers = []
    labels = []
    
    if symbol == "WTI":
        start_offset = 1 if today.day < 20 else 2
    elif symbol == "Brent":
        start_offset = 2 if today.day < 25 else 3

    for i in range(start_offset, months + start_offset):
        idx = (current_month + i - 1) % 12
        letter = codes_mois[idx]
        year = current_year + (current_month + i - 1) // 12
    
        ticker = f"{s}{letter}{year:02d}.NYM"
        tickers.append(ticker)
        labels.append(f"{letter}{year}")

    data_futures = yf.download(tickers, period="5d", progress=False, auto_adjust=False)['Close']
    
    if data_futures.empty:
        return None

    last_row = data_futures.iloc[-1]
    
    prices = [last_row[t] for t in tickers if t in last_row.index]
    valid_labels = [l for t, l in zip(tickers, labels) if t in last_row.index]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(valid_labels, prices, marker='o', linestyle='-', color='#007acc', linewidth=2)
    ax.set_title(f"{symbol} Term Structure", fontsize=12, fontweight='bold')
    ax.set_ylabel("Price (USD / bbl)")
    ax.grid(True, alpha=0.3)

    spread = prices[-1] - prices[0]
    
    if spread < 0:
        status = "Backwardation"
        color_msg = "red"
    else:
        status = "Contango"
        color_msg = "green"

    ax.text(0.5, 0.05, f"Market Status: {status} (Spread: ${spread:.2f})", 
            transform=ax.transAxes, ha="center", fontsize=10, 
            fontweight='bold', color=color_msg)
    plt.tight_layout()
    return fig
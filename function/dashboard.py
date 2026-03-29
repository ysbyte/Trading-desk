import requests
import pandas as pd

FRED_KEY = "cc0333f48969a440321a367c6b410cf3"

FRED_URL = "https://api.stlouisfed.org/fred/series/observations"
YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart/"

def get_fred(series):

    params = {
        "series_id": series,
        "api_key": FRED_KEY,
        "file_type": "json"
    }

    r = requests.get(FRED_URL, params=params)
    data = r.json()

    df = pd.DataFrame(data["observations"])

    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df


def get_yahoo(ticker):

    params = {
        "interval": "1d",
        "range": "1y"
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(YAHOO_URL + ticker, params=params, headers=headers)

    data = r.json()

    timestamps = data["chart"]["result"][0]["timestamp"]
    prices = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]

    df = pd.DataFrame({
        "date": pd.to_datetime(timestamps, unit="s"),
        "value": prices
    })
    return df

def latest_value(df):
    return df["value"].dropna().iloc[-1]



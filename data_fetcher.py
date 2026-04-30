import requests
import pandas as pd
import time
from config import API_KEY, INTERVAL, OUTPUTSIZE, CALL_INTERVAL_SECONDS

BASE_URL = "https://api.twelvedata.com/time_series"

last_call_time = 0
cached_df = None


def fetch_data(symbol):
    global last_call_time, cached_df

    now = time.time()

    # ✅ Prevent over-calling API
    if cached_df is not None and (now - last_call_time < CALL_INTERVAL_SECONDS):
        return cached_df

    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "outputsize": OUTPUTSIZE,
        "apikey": API_KEY,
        "timezone": "UTC"
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if "values" not in data:
        print("API Error:", data)
        return cached_df

    df = pd.DataFrame(data["values"])

    df.rename(columns={"datetime": "time"}, inplace=True)

    df["time"] = pd.to_datetime(df["time"])
    df[["open", "high", "low", "close"]] = df[
        ["open", "high", "low", "close"]
    ].astype(float)

    df.sort_values("time", inplace=True)
    df.reset_index(drop=True, inplace=True)

    cached_df = df
    last_call_time = now

    return df
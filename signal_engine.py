import time
from datetime import datetime

from data_fetcher import fetch_data
from indicators import calculate_indicators
from strategy import generate_signal
from risk_management import calculate_levels
from config import SYMBOLS, CALL_INTERVAL_SECONDS

last_trade_time = None
TRADE_COOLDOWN = 600


def is_trading_session():
    hour = datetime.utcnow().hour
    return 7 <= hour <= 16


def run_engine():

    print("🚀 BOT STARTED (API SAFE MODE)")

    global last_trade_time

    while True:

        df = fetch_data(SYMBOLS["gold"])

        if df is None or len(df) < 200:
            print("Waiting data...")
            time.sleep(30)
            continue

        df = calculate_indicators(df)

        if not is_trading_session():
            print("Outside session")
            time.sleep(CALL_INTERVAL_SECONDS)
            continue

        signal, conf = generate_signal(df)

        print("\n---")
        print("TIME:", df.iloc[-1]["time"])
        print("SIGNAL:", signal, "| CONF:", conf)

        now = time.time()

        if last_trade_time and (now - last_trade_time < TRADE_COOLDOWN):
            print("Cooldown active")
            time.sleep(CALL_INTERVAL_SECONDS)
            continue

        if signal in ["BUY", "SELL"]:

            entry, sl, tp, lot = calculate_levels(df, signal, 100, conf)

            print("ENTRY:", entry)
            print("SL:", sl)
            print("TP:", tp)
            print("LOT:", lot)

            last_trade_time = now

        else:
            print("NO TRADE")

        time.sleep(CALL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_engine()
from data_fetcher import fetch_data
from indicators import calculate_indicators
from strategy import generate_signal
from risk_management import calculate_levels

INITIAL_BALANCE = 100


def backtest():

    df = fetch_data("XAU/USD")
    df = calculate_indicators(df)

    balance = INITIAL_BALANCE
    trades = wins = losses = 0

    trade = None

    for i in range(200, len(df)):

        current = df.iloc[:i+1]
        candle = df.iloc[i]

        if trade:

            high = candle["high"]
            low = candle["low"]

            # 🔥 SMART BREAK-EVEN (FIXED)
            if trade["type"] == "BUY":

                trigger = trade["entry"] + (trade["tp"] - trade["entry"]) * 0.7

                if high >= trigger:
                    trade["sl"] = trade["entry"]

                if low <= trade["sl"]:
                    balance -= trade["risk"]
                    losses += 1
                    trade = None

                elif high >= trade["tp"]:
                    balance += trade["reward"]
                    wins += 1
                    trade = None

            else:

                trigger = trade["entry"] - (trade["entry"] - trade["tp"]) * 0.7

                if low <= trigger:
                    trade["sl"] = trade["entry"]

                if high >= trade["sl"]:
                    balance -= trade["risk"]
                    losses += 1
                    trade = None

                elif low <= trade["tp"]:
                    balance += trade["reward"]
                    wins += 1
                    trade = None
                    
        if trade is None:
            signal, conf = generate_signal(current)

            if signal in ["BUY", "SELL"]:
                entry, sl, tp, lot = calculate_levels(current, signal, balance, conf)

                if entry is None:
                    continue

                stop_distance = abs(entry - sl)
                tp_distance = abs(tp - entry)

                risk = balance * 0.01
                reward = risk * (tp_distance / stop_distance)

                trade = {
                    "type": signal,
                    "entry": entry,
                    "sl": sl,
                    "tp": tp,
                    "risk": risk,
                    "reward": reward
                }

                trades += 1

    print("\nRESULTS")
    print("Balance:", round(balance, 2))
    print("Trades:", trades)
    print("Wins:", wins)
    print("Losses:", losses)


if __name__ == "__main__":
    backtest()
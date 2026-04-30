def calculate_levels(df, signal, balance=100, conf=60):

    latest = df.iloc[-1]
    price = latest["close"]
    atr = df["atr"].iloc[-1]

    recent_low = df["low"].rolling(10).min().iloc[-2]
    recent_high = df["high"].rolling(10).max().iloc[-2]

    buffer = atr * 0.3

    if signal == "BUY":
        sl = recent_low - buffer
    else:
        sl = recent_high + buffer

    entry = price
    stop_distance = abs(entry - sl)

    if stop_distance == 0:
        return None, None, None, 0

    # ✅ TIERED RISK
    risk_percent = 0.01 if conf >= 65 else 0.005
    risk_amount = balance * risk_percent

    lot = risk_amount / stop_distance

    tp = entry + (stop_distance * 2) if signal == "BUY" else entry - (stop_distance * 2)

    return round(entry, 2), round(sl, 2), round(tp, 2), round(lot, 4)
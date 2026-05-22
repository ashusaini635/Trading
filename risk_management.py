def calculate_levels(df, signal, balance=100, conf=60):

    latest = df.iloc[-1]
    price = latest["close"]
    atr = df["atr"].iloc[-1]

    # Include current candle (-1) so we don't place SL above a pinbar's wick!
    recent_low = df["low"].rolling(10).min().iloc[-1]
    recent_high = df["high"].rolling(10).max().iloc[-1]

    # Increased buffer to survive XAU/USD volatility (wicks)
    buffer = atr * 1.0

    if signal == "BUY":
        sl = recent_low - buffer
    else:
        sl = recent_high + buffer

    entry = price

    # Prevent the SL from being too tight (minimum 1.5 ATR)
    if abs(entry - sl) < atr * 1.5:
        if signal == "BUY":
            sl = entry - (atr * 1.5)
        else:
            sl = entry + (atr * 1.5)

    stop_distance = abs(entry - sl)

    if stop_distance == 0:
        return None, None, None, 0

    # ✅ TIERED RISK
    risk_percent = 0.01 if conf >= 65 else 0.005
    risk_amount = balance * risk_percent

    lot = risk_amount / stop_distance

    # Lower R:R to 1:1.2 for a highly consistent base-hit win rate
    tp = entry + (stop_distance * 1.2) if signal == "BUY" else entry - (stop_distance * 1.2)

    return round(entry, 2), round(sl, 2), round(tp, 2), round(lot, 4)
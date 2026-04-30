import numpy as np

def generate_signal(df):

    if len(df) < 120:
        return "HOLD", 0

    latest = df.iloc[-1]
    price = latest["close"]

    # =====================
    # ATR
    # =====================
    df["tr"] = np.maximum(
        df["high"] - df["low"],
        np.maximum(
            abs(df["high"] - df["close"].shift()),
            abs(df["low"] - df["close"].shift())
        )
    )
    atr = df["tr"].rolling(14).mean().iloc[-1]

    # Block low-quality market
    if (latest["high"] - latest["low"]) < atr * 0.6:
        return "HOLD", 0

    # =====================
    # TREND FILTER (CRITICAL)
    # =====================
    ema50 = df["close"].ewm(span=50).mean().iloc[-1]
    ema100 = df["close"].ewm(span=100).mean().iloc[-1]

    trend_up = ema50 > ema100
    trend_down = ema50 < ema100

    trend_strength = abs(ema50 - ema100)

    # ONLY TRADE STRONG TREND OR SKIP
    if trend_strength < atr * 0.8:
        return "HOLD", 0

    # =====================
    # STRUCTURE
    # =====================
    bos_up = latest["close"] > df["high"].rolling(20).max().iloc[-2]
    bos_down = latest["close"] < df["low"].rolling(20).min().iloc[-2]

    # =====================
    # LIQUIDITY SWEEP
    # =====================
    swing_high = df["high"].rolling(10).max().iloc[-2]
    swing_low = df["low"].rolling(10).min().iloc[-2]

    sweep_low = latest["low"] < swing_low and latest["close"] > swing_low
    sweep_high = latest["high"] > swing_high and latest["close"] < swing_high

    # =====================
    # PULLBACK
    # =====================
    pullback = abs(price - ema50) < atr * 0.4

    # =====================
    # MARKET STATE CLASSIFICATION
    # =====================
    trending_market = abs(ema50 - ema100) > atr * 0.8

    # =====================
    # FINAL RULE: ONLY 1 TYPE OF TRADE
    # =====================
    buy = 0
    sell = 0

    # 🔵 MODE 1: TREND CONTINUATION ONLY
    if trending_market:

        if trend_up and bos_up and pullback:
            buy += 7

        if trend_down and bos_down and pullback:
            sell += 7

    # 🔵 MODE 2: REVERSAL (ONLY WHEN EXTREME SWEEP)
    else:

        if sweep_low:
            buy += 6

        if sweep_high:
            sell += 6

    # =====================
    # MOMENTUM
    # =====================
    momentum = df["close"].iloc[-1] - df["close"].iloc[-5]

    if momentum > 0:
        buy += 2
    elif momentum < 0:
        sell += 2

    # =====================
    # FINAL SCORE
    # =====================
    max_score = 10

    buy_conf = (buy / max_score) * 100
    sell_conf = (sell / max_score) * 100

    # STRICTER ENTRY (IMPORTANT FIX)
    if buy_conf > 60 and buy > sell:
        return "BUY", round(buy_conf, 2)

    if sell_conf > 60 and sell > buy:
        return "SELL", round(sell_conf, 2)

    return "HOLD", 0
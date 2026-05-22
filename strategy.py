import numpy as np

def generate_signal(df):

    if len(df) < 150:
        return "HOLD", 0

    latest = df.iloc[-1]
    price = latest["close"]

    # =========================
    # MACD & ADX (Trend & Momentum)
    # =========================
    macd = df["macd"].iloc[-1]
    macd_signal = df["macd_signal"].iloc[-1]
    adx = df["adx"].iloc[-1]

    # =========================
    # ATR (volatility baseline)
    # =========================
    atr = df["atr"].iloc[-1]

    # =========================
    # EMA 9 & 21 (Short-Term Trend Baseline)
    # =========================
    ema_9 = df["ema_9"].iloc[-1]
    ema_21 = df["ema_21"].iloc[-1]

    # =========================
    # TREND (Price Action Structure)
    # =========================
    recent_highs = df["high"].rolling(20).max()
    recent_lows = df["low"].rolling(20).min()

    curr_swing_high = recent_highs.iloc[-2]
    prev_swing_high = recent_highs.iloc[-22]

    curr_swing_low = recent_lows.iloc[-2]
    prev_swing_low = recent_lows.iloc[-22]

    trend_up = (curr_swing_high > prev_swing_high) and (curr_swing_low > prev_swing_low)
    trend_down = (curr_swing_high < prev_swing_high) and (curr_swing_low < prev_swing_low)

    # =========================
    # CANDLESTICK PATTERNS (Price Action)
    # =========================
    prev_candle = df.iloc[-2]
    body_size = abs(latest["close"] - latest["open"])
    
    upper_wick = latest["high"] - max(latest["open"], latest["close"])
    lower_wick = min(latest["open"], latest["close"]) - latest["low"]

    bullish_pinbar = (lower_wick > 2 * body_size) and (upper_wick <= body_size)
    bearish_pinbar = (upper_wick > 2 * body_size) and (lower_wick <= body_size)

    bullish_engulfing = (prev_candle["close"] < prev_candle["open"]) and \
                        (latest["close"] > latest["open"]) and \
                        (latest["close"] >= prev_candle["open"]) and \
                        (latest["open"] <= prev_candle["close"])

    bearish_engulfing = (prev_candle["close"] > prev_candle["open"]) and \
                        (latest["close"] < latest["open"]) and \
                        (latest["close"] <= prev_candle["open"]) and \
                        (latest["open"] >= prev_candle["close"])

    # =========================
    # LIQUIDITY (SMC CORE)
    # =========================
    equal_highs = abs(df["high"].iloc[-2] - df["high"].iloc[-3]) < atr * 0.2
    equal_lows = abs(df["low"].iloc[-2] - df["low"].iloc[-3]) < atr * 0.2

    sweep_high = latest["high"] > df["high"].iloc[-2] and latest["close"] < df["high"].iloc[-2]
    sweep_low = latest["low"] < df["low"].iloc[-2] and latest["close"] > df["low"].iloc[-2]

    # =========================
    # FAIR VALUE GAP (FVG)
    # =========================
    fvg_up = df["low"].iloc[-1] > df["high"].iloc[-3]
    fvg_down = df["high"].iloc[-1] < df["low"].iloc[-3]

    # =========================
    # ORDER BLOCK (simplified)
    # =========================
    last_bearish_candle = df[df["close"] < df["open"]].iloc[-1]
    last_bullish_candle = df[df["close"] > df["open"]].iloc[-1]

    # A bullish OB is the last down-candle. We buy when price pulls back into its range.
    near_bull_ob = last_bearish_candle["low"] < price < last_bearish_candle["high"]
    # A bearish OB is the last up-candle. We sell when price pulls back into its range.
    near_bear_ob = last_bullish_candle["low"] < price < last_bullish_candle["high"]

    # =========================
    # PREMIUM / DISCOUNT
    # =========================
    range_high = df["high"].rolling(50).max().iloc[-1]
    range_low = df["low"].rolling(50).min().iloc[-1]

    equilibrium = (range_high + range_low) / 2

    discount_zone = price < equilibrium
    premium_zone = price > equilibrium

    # =========================
    # MOMENTUM
    # =========================
    momentum = df["close"].iloc[-1] - df["close"].iloc[-5]

    # =========================
    # SCORING ENGINE
    # =========================
    buy = 0
    sell = 0

    # 1. BASELINE TREND (EMA 9 & 21) - Strict Filter
    if ema_9 > ema_21 and price > ema_9:
        buy += 4
    elif ema_9 < ema_21 and price < ema_9:
        sell += 4

    # 2. PRICE ACTION TREND
    if trend_up:
        buy += 3
    if trend_down:
        sell += 3

    # 3. PULLBACK ZONES (Discount/Premium)
    if discount_zone:
        buy += 3
    if premium_zone:
        sell += 3

    # 4. SMART MONEY (Liquidity / OB / FVG)
    if sweep_low or near_bull_ob or fvg_up:
        buy += 3
    if sweep_high or near_bear_ob or fvg_down:
        sell += 3

    # 5. CANDLESTICK REJECTION
    if bullish_pinbar or bullish_engulfing:
        buy += 3
    if bearish_pinbar or bearish_engulfing:
        sell += 3

    # 6. MOMENTUM & VOLATILITY
    if macd > macd_signal:
        buy += 2
    elif macd < macd_signal:
        sell += 2
        
    if adx > 25:
        if ema_9 > ema_21:
            buy += 2
        if ema_9 < ema_21:
            sell += 2

    # 7. RSI PULLBACK CONFLUENCE
    if 35 < df["rsi"].iloc[-1] < 50:
        buy += 2
    if 50 < df["rsi"].iloc[-1] < 65:
        sell += 2

    # =========================
    # FINAL DECISION
    # =========================
    max_score = 22

    buy_conf = (buy / max_score) * 100
    sell_conf = (sell / max_score) * 100

    if buy_conf >= 50 and buy > sell:
        return "BUY", round(buy_conf, 2)

    if sell_conf >= 50 and sell > buy:
        return "SELL", round(sell_conf, 2)

    return "HOLD", 0
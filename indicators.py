import ta

def calculate_indicators(df):

    df["rsi"] = ta.momentum.rsi(df["close"], window=14)

    df["atr"] = ta.volatility.average_true_range(
        df["high"], df["low"], df["close"], window=14
    )

    df["macd"] = ta.trend.macd(df["close"])
    df["macd_signal"] = ta.trend.macd_signal(df["close"])
    
    df["adx"] = ta.trend.adx(df["high"], df["low"], df["close"], window=14)

    df["ema_9"] = ta.trend.ema_indicator(df["close"], window=9)
    df["ema_21"] = ta.trend.ema_indicator(df["close"], window=21)

    df.bfill(inplace=True)
    df.ffill(inplace=True)

    return df
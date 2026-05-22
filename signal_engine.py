import time
from datetime import datetime, timedelta, timezone

from data_fetcher import fetch_data
from indicators import calculate_indicators
from strategy import generate_signal
from risk_management import calculate_levels
from config import SYMBOLS

# ============================================
# SETTINGS
# ============================================

last_trade_time = None

# 1 hour cooldown
TRADE_COOLDOWN = 0

# UTC+3 timezone
UTC_PLUS_3 = timezone(timedelta(hours=3))


# ============================================
# WAIT FOR NEXT CANDLE
# ============================================

def wait_until_next_candle(last_candle_time=None):

    now = datetime.now(UTC_PLUS_3)

    if last_candle_time is not None:
        if last_candle_time.tzinfo is None:
            last_candle_time = last_candle_time.replace(tzinfo=UTC_PLUS_3)
            
        # Exactly 1 hour after the last candle's open time
        target_time = (last_candle_time + timedelta(hours=1)).replace(
            second=2,
            microsecond=0
        )

        # If data is stale or market was closed, sync to next 1h clock interval
        if target_time <= now:
            mins_to_add = 60 - now.minute
            target_time = (now + timedelta(minutes=mins_to_add)).replace(
                second=2, microsecond=0
            )
    else:
        # Fallback if no last_candle_time provided
        mins_to_add = 60 - now.minute
        target_time = (now + timedelta(minutes=mins_to_add)).replace(
            second=2,
            microsecond=0
        )

    print(f"\nNext candle at: {target_time}\n")

    while True:

        now = datetime.now(UTC_PLUS_3)

        remaining = (target_time - now).total_seconds()

        if remaining <= 0:
            break

        mins, secs = divmod(int(remaining), 60)
        hours, mins = divmod(mins, 60)

        print(
            f"\rWaiting for next candle: "
            f"{hours:02}:{mins:02}:{secs:02}",
            end=""
        )

        time.sleep(1)

    print("\n\nNew candle detected!\n")


# ============================================
# MAIN ENGINE
# ============================================

def run_engine():

    global last_trade_time

    print("🚀 BOT STARTED (1H CANDLE MODE UTC+3)")

    while True:

        try:

            print("\nFetching fresh candle data...")

            # ====================================
            # FETCH DATA
            # ====================================

            df = fetch_data(SYMBOLS["gold"])

            if df is None or len(df) < 200:

                print("Insufficient data received")
                wait_until_next_candle()
                continue

            # ====================================
            # CALCULATE INDICATORS
            # ====================================

            df = calculate_indicators(df)

            # ====================================
            # GENERATE SIGNAL
            # ====================================

            signal, conf = generate_signal(df)

            print("\n==============================")
            print("CURRENT TIME :", datetime.now(UTC_PLUS_3))
            print("LAST CANDLE  :", df.iloc[-1]["time"])
            print("SIGNAL       :", signal)
            print("CONFIDENCE   :", conf)

            now_ts = time.time()

            # ====================================
            # COOLDOWN CHECK
            # ====================================

            if (
                last_trade_time
                and (now_ts - last_trade_time < TRADE_COOLDOWN)
            ):

                remaining = int(
                    TRADE_COOLDOWN - (now_ts - last_trade_time)
                )

                mins, secs = divmod(remaining, 60)

                print(
                    f"Cooldown active "
                    f"({mins}m {secs}s remaining)"
                )

            else:

                # ====================================
                # EXECUTE TRADE LOGIC
                # ====================================

                if signal in ["BUY", "SELL"]:

                    entry, sl, tp, lot = calculate_levels(
                        df,
                        signal,
                        100,
                        conf
                    )

                    print("\n========= TRADE =========")
                    print("TYPE  :", signal)
                    print("ENTRY :", entry)
                    print("SL    :", sl)
                    print("TP    :", tp)
                    print("LOT   :", lot)
                    print("Confidence : ", conf)
                    print("=========================\n")

                    last_trade_time = now_ts

                else:

                    print("\nNO TRADE SETUP FOUND\n")

            # ====================================
            # WAIT FOR NEXT CANDLE
            # ====================================

            wait_until_next_candle(df.iloc[-1]["time"])

        except KeyboardInterrupt:

            print("\nBot stopped manually")
            break

        except Exception as e:

            print("\nENGINE ERROR:", e)

            # Prevent crash loop
            time.sleep(10)


# ============================================
# START BOT
# ============================================

if __name__ == "__main__":

    run_engine()
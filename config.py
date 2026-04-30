from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("TWELVE_API_KEY")

SYMBOLS = {
    "gold": "XAU/USD",
}

INTERVAL = "5min"
OUTPUTSIZE = 5000

INITIAL_BALANCE = 100
RISK_PER_TRADE = 0.01

# ✅ API LIMIT CONTROL
MAX_CALLS_PER_DAY = 800
CALL_INTERVAL_SECONDS = 300  # 5 min (IMPORTANT)
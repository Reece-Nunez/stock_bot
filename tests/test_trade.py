import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.data_fetcher import DataFetcher
from trading.order_manager import OrderManager

# Environment variables for Alpaca Paper Trading
API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = os.getenv("APCA_API_BASE_URL")

# Initialize DataFetcher and OrderManager
fetcher = DataFetcher(API_KEY, API_SECRET, BASE_URL)
order_manager = OrderManager(api=fetcher.api, fetcher=fetcher)

# Place a test trade
symbol = "AAPL"
try:
    order = order_manager.place_market_order(
        symbol=symbol,
        qty=1,
        side="buy",
        time_in_force="gtc"  # Good 'Til Canceled
    )
    print(f"Test Trade Order Placed: {order}")
except Exception as e:
    print(f"Error placing test trade: {e}")

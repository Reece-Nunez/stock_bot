import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.data_fetcher import DataFetcher


API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = os.getenv("APCA_API_BASE_URL")

fetcher = DataFetcher(API_KEY, API_SECRET, BASE_URL)
data = fetcher.get_historical_data("AAPL", "minute", limit=100)
print(data)

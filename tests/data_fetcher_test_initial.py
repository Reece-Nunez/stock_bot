from data.data_fetcher import DataFetcher
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = os.getenv("APCA_API_BASE_URL")

fetcher = DataFetcher(API_KEY, API_SECRET, BASE_URL)
account_info = fetcher.get_account_info()
print("Account Info:", account_info)
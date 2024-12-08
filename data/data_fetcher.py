from alpaca_trade_api import REST
import pandas as pd
import logging

logging.basicConfig(
    filename="stock_bot_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class DataFetcher:
    def __init__(self, api_key, api_secret, base_url):
        self.api = REST(api_key, api_secret, base_url)

    def get_historical_data(self, symbol, timeframe, limit=1000, retries=3):
        """Fetch historical data for the given symbol with retry logic."""
        attempt = 0
        while attempt < retries:
            try:
                bars = self.api.get_bars(symbol, timeframe, limit=limit)
                df = pd.DataFrame({
                    'time': [bar.t for bar in bars],
                    'open': [bar.o for bar in bars],
                    'high': [bar.h for bar in bars],
                    'low': [bar.l for bar in bars],
                    'close': [bar.c for bar in bars],
                    'volume': [bar.v for bar in bars]
                })
                return df
            except Exception as e:
                logging.warning(f"Retrying {symbol} historical data fetch... Attempt {attempt + 1}")
                attempt += 1
                sleep(2 ** attempt)  # Exponential backoff
        logging.error(f"Failed to fetch historical data for {symbol} after {retries} attempts.")
        return pd.DataFrame()

    def get_realtime_price(self, symbol):
        """Fetch real-time price for a symbol."""
        try:
            quote = self.api.get_last_trade(symbol)
            return quote.price
        except Exception as e:
            logging.error(f"Failed to fetch real-time price for {symbol}: {e}")
            return None

    def get_all_assets(self):
        """Retrieve a list of all US equity assets."""
        try:
            assets = self.api.list_assets(asset_class="us_equity")
            filtered_assets = [
                {
                    "symbol": asset.symbol,
                    "name": asset.name,
                    "status": asset.status,
                    "tradable": asset.tradable,
                }
                for asset in assets
            ]
            return pd.DataFrame(filtered_assets)
        except Exception as e:
            logging.error(f"Failed to fetch assets: {e}")
            return pd.DataFrame()

    def check_asset_tradable(self, symbol):
        """Check if a particular asset is tradable."""
        try:
            asset = self.api.get_asset(symbol)
            return {
                "symbol": asset.symbol,
                "name": asset.name,
                "tradable": asset.tradable,
                "status": asset.status,
            }
        except Exception as e:
            logging.error(f"Failed to check tradability for {symbol}: {e}")
            return None

    def get_account_info(self):
        """Fetch account info."""
        try:
            account = self.api.get_account()
            return {
                "status": "Restricted" if account.trading_blocked else "Active",
                "buying_power": float(account.buying_power),
            }
        except Exception as e:
            logging.error(f"Failed to fetch account info: {e}")
            return {}

    def get_portfolio_gain_loss(self):
        """Fetch portfolio gain/loss."""
        try:
            account = self.api.get_account()
            balance_change = float(account.equity) - float(account.last_equity)
            return {
                "current_equity": float(account.equity),
                "previous_close_equity": float(account.last_equity),
                "balance_change": balance_change,
            }
        except Exception as e:
            logging.error(f"Failed to fetch portfolio gain/loss: {e}")
            return {}

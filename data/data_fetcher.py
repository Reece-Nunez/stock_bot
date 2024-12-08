# data_fetcher.py
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

    def get_historical_data(self, symbol, timeframe, limit=1000):
        """Fetch historical data for the given symbol."""
        barset = self.api.get_barset(symbol, timeframe, limit=limit)
        data = barset[symbol]
        df = pd.DataFrame({
            'time': [bar.t for bar in data],
            'open': [bar.o for bar in data],
            'high': [bar.h for bar in data],
            'low': [bar.l for bar in data],
            'close': [bar.c for bar in data],
            'volume': [bar.v for bar in data]
        })
        return df

    def get_realtime_price(self, symbol):
        """Fetch real-time price for a symbol."""
        quote = self.api.get_last_trade(symbol)
        return quote.price

    def get_all_assets(self):
        """Retrieve a list of all US equity assets."""
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

    def check_asset_tradable(self, symbol):
        """Check if a particular asset is tradable."""
        asset = self.api.get_asset(symbol)
        return {
            "symbol": asset.symbol,
            "name": asset.name,
            "tradable": asset.tradable,
            "status": asset.status,
        }

    def get_account_info(self):
        """Fetch account info."""
        account = self.api.get_account()
        return {
            "status": "Restricted" if account.trading_blocked else "Active",
            "buying_power": float(account.buying_power),
        }

    def get_portfolio_gain_loss(self):
        """Fetch portfolio gain/loss."""
        account = self.api.get_account()
        balance_change = float(account.equity) - float(account.last_equity)
        return {
            "current_equity": float(account.equity),
            "previous_close_equity": float(account.last_equity),
            "balance_change": balance_change,
        }
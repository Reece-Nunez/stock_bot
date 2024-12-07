import alpaca_trade_api as tradeapi
import pandas as pd

class DataFetcher:
    def __init__(self, api_key, api_secret, base_url):
        self.api = tradeapi.REST(api_key, api_secret, base_url)

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

import os
from time import sleep
from alpaca_trade_api import REST
import pandas as pd
from logger_config import logger
import requests
import asyncio

class DataFetcher:
    def __init__(self, api_key, api_secret, base_url):
        self.api = REST(api_key, api_secret, base_url)
        
    def get_sector_analysis(self):
        """Fetch sector performance data from Alpha Vantage."""
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        url = f"https://www.alphavantage.co/query?function=SECTOR&apikey={api_key}"
        try:
            response = requests.get(url)
            data = response.json()
            return data["Rank A: Real-Time Performance"]
        except Exception as e:
            logger.error(f"Failed to fetch sector performance: {e}")
            return {}

    async def get_historical_data(self, symbol, timeframe, limit=1000, retries=3):
        """Fetch historical data for the given symbol with retry logic."""
        # Define valid timeframes for Alpaca API
        valid_timeframes = {
            "minute": "1Min",
            "5minute": "5Min",
            "15minute": "15Min",
            "hour": "1Hour",
            "day": "1Day"
        }

        # Translate the timeframe to Alpaca-compatible format
        alpaca_timeframe = valid_timeframes.get(timeframe.lower())
        if not alpaca_timeframe:
            logger.error(f"Invalid timeframe '{timeframe}' provided. Valid options are: {list(valid_timeframes.keys())}")
            return pd.DataFrame()
        
        attempt = 0
        while attempt < retries:
            try:
                logger.info(f"Fetching data for {symbol} with timeframe {alpaca_timeframe}, limit {limit}. Attempt {attempt + 1}")
                
                # Use Alpaca-compatible timeframe
                bars = list(self.api.get_bars_iter(symbol, alpaca_timeframe, limit=limit))
                logger.info(f"Raw bars response for {symbol}: {bars}")

                if not bars:
                    logger.warning(f"No data returned for {symbol}. Retrying...")
                    raise ValueError("Empty data response")
                
                # Convert response to DataFrame
                df = pd.DataFrame({
                    'time': [bar.t for bar in bars],
                    'open': [bar.o for bar in bars],
                    'high': [bar.h for bar in bars],
                    'low': [bar.l for bar in bars],
                    'close': [bar.c for bar in bars],
                    'volume': [bar.v for bar in bars]
                })
                logger.info(f"Successfully fetched historical data for {symbol}")
                return df
            
            except Exception as e:
                logger.warning(f"Retrying {symbol} historical data fetch... Attempt {attempt + 1}. Error: {e}")
                attempt += 1
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
        logger.error(f"Failed to fetch historical data for {symbol} after {retries} attempts.")
        return pd.DataFrame()

    def get_realtime_price(self, symbol):
        """Fetch real-time price for a symbol."""
        try:
            quote = self.api.get_last_trade(symbol)
            return quote.price
        except Exception as e:
            logger.error(f"Failed to fetch real-time price for {symbol}: {e}")
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
            logger.error(f"Failed to fetch assets: {e}")
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
            logger.error(f"Failed to check tradability for {symbol}: {e}")
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
            logger.error(f"Failed to fetch account info: {e}")
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
            logger.error(f"Failed to fetch portfolio gain/loss: {e}")
            return {}
        
    def place_trailing_stop_order(self, symbol, qty, side, trail_percent):
        try:
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type="trailing_stop",
                trail_percent=trail_percent,
                time_in_force="gtc",
            )
            logger.info(f"Trailing stop order placed: {order}")
            return order
        except Exception as e:
            logger.error(f"Failed to place trailing stop order: {e}")
            raise


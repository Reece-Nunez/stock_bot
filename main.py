import os
from logger_config import logger
import asyncio
from dotenv import load_dotenv
from alerts.alerts import send_alert
from data.data_fetcher import DataFetcher
from strategies.rsi_strategy import RSIStrategy
from strategies.macd_strategy import MACDStrategy
from strategies.bollinger_strategy import BollingerBandsStrategy
from trading.order_manager import OrderManager
from analytics.analytics import Analytics
from backtest.backtester import Backtester

# Load environment variables
load_dotenv()

# Config
API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = os.getenv("APCA_API_BASE_URL")

if not API_KEY or not API_SECRET or not BASE_URL:
    logger.error("API credentials or BASE_URL are not set.")
    raise EnvironmentError("API credentials or BASE_URL are not set.")

# Initialize Analytics
analytics = Analytics()

# Initialize modules
fetcher = DataFetcher(API_KEY, API_SECRET, BASE_URL)
order_manager = OrderManager(api=fetcher.api, fetcher=fetcher)

# Strategies
strategies = {
    "rsi": RSIStrategy(overbought=70, oversold=30),
    "macd": MACDStrategy(),
    "bollinger": BollingerBandsStrategy(window=20, num_std_dev=2),
}
default_strategy = "rsi"  # Default active strategy

# Log active strategy at the start of the loop
logger.info(f"Active strategy: {default_strategy}")

# Parameters
risk_per_trade = 0.02
stop_loss_pct = 0.02
take_profit_pct = 0.05
symbol = "AAPL"

async def execute_trades(current_strategy: str = "rsi"):
    """
    Execute trades based on the current active strategy in real-time.
    """
    last_signal = None

    while True:
        try:
            # Fetch historical data
            data = await fetcher.get_historical_data(symbol, "minute", limit=100)
            if data.empty:
                logger.warning(f"No data available for {symbol}. Retrying in 60 seconds.")
                await asyncio.sleep(60)
                continue

            # Generate signal
            strategy = strategies[current_strategy]
            signal = data["signal"].iloc[-1]

            # Execute trades based on signal
            if signal != last_signal:
                if signal == 1:  # Buy
                    await order_manager.place_dynamic_bracket_order(
                        symbol=symbol,
                        side="buy",
                        risk_per_trade=risk_per_trade,
                        stop_loss_pct=stop_loss_pct,
                        take_profit_pct=take_profit_pct,
                    )
                elif signal == -1:  # Sell
                    await order_manager.place_dynamic_bracket_order(
                        symbol=symbol,
                        side="sell",
                        risk_per_trade=risk_per_trade,
                        stop_loss_pct=stop_loss_pct,
                        take_profit_pct=take_profit_pct,
                    )
                last_signal = signal

        except Exception as e:
            logger.error(f"Error in trade execution loop for {symbol}: {e}")

        await asyncio.sleep(60)  # Wait a minute before fetching new data

if __name__ == "__main__":
    try:
        asyncio.run(execute_trades())
    except KeyboardInterrupt:
        logger.info("Trading bot stopped manually.")
    except Exception as e:
        logger.critical(f"Critical error: {e}")
        send_alert("Critical Error in Trading Bot", str(e))

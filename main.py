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

async def main():
    # Verify API connection and account status
    account_info = fetcher.get_account_info()
    print("Account Info:", account_info)
    if not account_info or account_info["status"] != "Active":
        logger.error("API credentials may be incorrect, or the account is not active.")
        return
    
     # Check if the market is open
    clock = fetcher.api.get_clock()
    if not clock.is_open:
        logger.warning("Market is closed. Exiting.")
        return
    
    # Check if the symbol is tradable
    asset_info = fetcher.check_asset_tradable("AAPL")
    print("Asset Info:", asset_info)
    if not asset_info or not asset_info["tradable"]:
        logger.error(f"The symbol AAPL is not tradable. Exiting.")
        return
    
    # Initialize order manager and strategies
    order_manager = OrderManager(api=fetcher.api, fetcher=fetcher)

    strategies = {
        "rsi": RSIStrategy(overbought=70, oversold=30),
        "macd": MACDStrategy(),
        "bollinger": BollingerBandsStrategy(window=20, num_std_dev=2),
    }
    default_strategy = "rsi"  # Default active strategy
    logger.info(f"Active strategy: {default_strategy}")

    # Backtesting
    logger.info("Starting backtesting...")
    await backtest_strategies(strategies, fetcher, "AAPL")
    logger.info("Backtesting complete.")

    # Start trading bot
    await execute_trades(order_manager, strategies, fetcher, default_strategy)

async def backtest_strategies(strategies, fetcher, symbol):
    """
    Backtest all strategies using historical data.
    """
    try:
        logger.info(f"Fetching historical data for backtesting {symbol}...")
        historical_data = await fetcher.get_historical_data(symbol, "minute", limit=1000)
        if historical_data.empty:
            logger.error(f"No historical data available for {symbol}. Skipping backtesting.")
            return

        for strategy_name, strategy in strategies.items():
            logger.info(f"Backtesting strategy: {strategy_name}")
            backtester = Backtester(strategy)
            results = backtester.run(historical_data)
            logger.info(f"Results for {strategy_name}: {results}")

    except Exception as e:
        logger.error(f"Error during backtesting: {e}")

async def execute_trades(order_manager, strategies, fetcher, current_strategy="rsi", max_iterations=None):
    """
    Execute trades based on the current active strategy in real-time.
    """
    last_signal = None  # Ensure last_signal starts as None
    iteration = 0

    while max_iterations is None or iteration < max_iterations:
        iteration += 1
        try:
            # Fetch historical data
            data = await fetcher.get_historical_data("AAPL", "minute", limit=100)
            if data.empty:
                logger.warning(f"No data available for AAPL. Retrying in 60 seconds.")
                await asyncio.sleep(60)
                continue

            # Generate signal
            strategy = strategies[current_strategy]
            data = strategy.generate_signal(data)
            signal = data["signal"].iloc[-1]

            # Debugging: Log signal values
            logger.debug(f"Iteration {iteration}: Current signal: {signal}, Last signal: {last_signal}")

            # Execute trades based on signal changes
            if signal != last_signal and signal in [1, -1]:  # Only trigger for buy/sell signals
                logger.info(f"Signal changed to {signal}. Triggering trade.")
                if signal == 1:  # Buy
                    await order_manager.place_dynamic_bracket_order(
                        symbol="AAPL",
                        side="buy",
                        risk_per_trade=0.02,
                        stop_loss_pct=0.02,
                        take_profit_pct=0.05,
                    )
                elif signal == -1:  # Sell
                    await order_manager.place_dynamic_bracket_order(
                        symbol="AAPL",
                        side="sell",
                        risk_per_trade=0.02,
                        stop_loss_pct=0.02,
                        take_profit_pct=0.05,
                    )
            else:
                logger.info("No valid signal change. No trade executed.")

            # Update last_signal after processing
            last_signal = signal

        except Exception as e:
            logger.error(f"Error in trade execution loop: {e}")

        await asyncio.sleep(60)  # Wait before fetching new data


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Trading bot stopped manually.")
    except Exception as e:
        logger.critical(f"Critical error: {e}")
        send_alert("Critical Error in Trading Bot", str(e))
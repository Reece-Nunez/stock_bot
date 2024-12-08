import os
import logging
import asyncio
from alerts.alerts import send_alert
from loguru import logger
from data.data_fetcher import DataFetcher
from strategies.rsi_strategy import RSIStrategy
from strategies.macd_strategy import MACDStrategy
from strategies.bollinger_strategy import BollingerBandsStrategy
from trading.order_manager import OrderManager
from analytics.analytics import Analytics
from backtest.backtester import Backtester

# Configure Loguru
logger.add("stock_bot_logs.log", rotation="10 MB")

# Configure Logging
logging.basicConfig(
    filename="stock_bot_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Config
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_API_SECRET")
BASE_URL = os.getenv("ALPACA_BASE_URL")

if not API_KEY or not API_SECRET or not BASE_URL:
    logging.error("API credentials or BASE_URL are not set.")
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
logging.info(f"Active strategy: {default_strategy}")

# Parameters
risk_per_trade = 0.02
stop_loss_pct = 0.02
take_profit_pct = 0.05
symbol = "AAPL"

async def execute_trades(current_strategy: str = default_strategy):
    """
    Execute trades based on the current active strategy in real-time.
    """
    last_signal = None
    while True:
        try:
            # Fetch historical data
            data = fetcher.get_historical_data(symbol, "minute", limit=100)
            if data.empty:
                logging.warning(f"No data available for {symbol}. Retrying in 60 seconds.")
                await asyncio.sleep(60)
                continue

            # Generate signal
            strategy = strategies[current_strategy]
            signal = strategy.generate_signal(data)["signal"].iloc[-1]

            # Execute trades based on signal
            if signal != last_signal:
                if signal == 1:  # Buy
                    order_manager.place_dynamic_bracket_order(
                        symbol,
                        side="buy",
                        risk_per_trade=risk_per_trade,
                        stop_loss_pct=stop_loss_pct,
                        take_profit_pct=take_profit_pct,
                    )
                    analytics.update_trade(100, current_strategy) # Simulate profit/loss
                    logging.info(f"Buy signal triggered for {symbol}.")
                elif signal == -1:  # Sell
                    order_manager.place_dynamic_bracket_order(
                        symbol,
                        side="sell",
                        risk_per_trade=risk_per_trade,
                        stop_loss_pct=stop_loss_pct,
                        take_profit_pct=take_profit_pct,
                    )
                    analytics.update_trade(-50, current_strategy) # Simulate profit/loss
                    logging.info(f"Sell signal triggered for {symbol}.")
                last_signal = signal
                
                # Dynamic strategy switching based on sentiment or analytics
                if analytics.sentiment_scores.get("market_sentiment", 0) < -0.5:
                    default_strategy = "bollinger"
                    logging.info(f"Switched strategy to Bollinger due to negative market sentiment.")
    

        except Exception as e:
            logging.error(f"Error in trade execution loop for {symbol}: {e}")

        await asyncio.sleep(60)  # Run the loop every 60 seconds
        
def backtest_strategy(strategy_name, historical_data):
    """Backtest a given strategy on historical data."""
    strategy = strategies[strategy_name]
    backtester = Backtester(strategy)
    results = backtester.run(historical_data)
    analytics.update_trade(results - fetcher.get_portfolio_gain_loss()["current_equity"], strategy_name)
    logging.info(f"Backtest results for {strategy_name}: {results}")
    return results

if __name__ == "__main__":
    # Backtest before live trading
    historical_data = fetcher.get_historical_data(symbol, "minute", limit=1000)
    for strat in strategies:
        backtest_strategy(strat, historical_data)
        
     # Switch to live trading after backtesting
    try:
        asyncio.run(execute_trades())
    except KeyboardInterrupt:
        logger.info("Trading bot stopped manually.")
    except Exception as e:
        logger.critical(f"Critical error: {e}")
        send_alert("Critical Error in Trading Bot", str(e))

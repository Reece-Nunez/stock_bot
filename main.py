import os
import logging
import asyncio
from data.data_fetcher import DataFetcher
from strategies.rsi_strategy import RSIStrategy
from strategies.macd_strategy import MACDStrategy
from strategies.bollinger_strategy import BollingerBandsStrategy
from trading.order_manager import OrderManager

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

# Initialize modules
fetcher = DataFetcher(API_KEY, API_SECRET, BASE_URL)
order_manager = OrderManager(fetcher.api)

# Strategies
strategies = {
    "rsi": RSIStrategy(overbought=70, oversold=30),
    "macd": MACDStrategy(),
    "bollinger": BollingerBandsStrategy(window=20, num_std_dev=2),
}
default_strategy = "rsi"  # Default active strategy

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
                    logging.info(f"Buy signal triggered for {symbol}.")
                elif signal == -1:  # Sell
                    order_manager.place_dynamic_bracket_order(
                        symbol,
                        side="sell",
                        risk_per_trade=risk_per_trade,
                        stop_loss_pct=stop_loss_pct,
                        take_profit_pct=take_profit_pct,
                    )
                    logging.info(f"Sell signal triggered for {symbol}.")
                last_signal = signal

        except Exception as e:
            logging.error(f"Error in trade execution loop for {symbol}: {e}")

        await asyncio.sleep(60)  # Run the loop every 60 seconds

if __name__ == "__main__":
    try:
        asyncio.run(execute_trades())  # Use asyncio.run() for better loop management
    except KeyboardInterrupt:
        logging.info("Trading bot stopped manually.")
    except Exception as e:
        logging.critical(f"Critical error in trading bot: {e}")

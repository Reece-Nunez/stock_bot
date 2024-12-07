from data.data_fetcher import DataFetcher
from strategies.ma_crossover import MovingAverageCrossover
from trading.order_manager import OrderManager
from backtest.backtester import Backtester

# Config
API_KEY = CK59BIB075IWXZMCOH11
API_SECRET = cNzVJJogHJkr0oMtsEnBIjxZuCjQSck4rATj7eLW
BASE_URL = 'https://paper-api.alpaca.markets'

# Initialize modules
fetcher = DataFetcher(API_KEY, API_SECRET, BASE_URL)
strategy = MovingAverageCrossover(short_window=10, long_window=50)
backtester = Backtester(strategy)
order_manager = OrderManager(fetcher.api)

# Fetch historical data
symbol = 'AAPL'
data = fetcher.get_historical_data(symbol, 'minute', limit=1000)

# Backtest the strategy
final_balance = backtester.run(data)
print(f"Final Balance after Backtesting: ${final_balance:.2f}")

# Example live trading loop
import time
while True:
    price = fetcher.get_realtime_price(symbol)
    print(f"Current Price: ${price}")
    signal = strategy.generate_signal(data)
    if signal == 1:
        order_manager.place_order(symbol, qty=1, side='buy')
    elif signal == -1:
        order_manager.place_order(symbol, qty=1, side='sell')
    time.sleep(60)

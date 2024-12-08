from logger_config import logger
import pandas as pd

class Backtester:
    def __init__(self, strategy, initial_balance=10000, transaction_fee=0.001):
        self.strategy = strategy
        self.initial_balance = initial_balance
        self.transaction_fee = transaction_fee

    def run(self, data):
        """Backtest the strategy on historical data."""
        logger.info("Starting backtesting...")
        data = self.strategy.generate_signal(data)
        balance = self.initial_balance
        position = 0
        trade_log = []

        for _, row in data.iterrows():
            if row['signal'] == 1:  # Buy
                position += (balance * (1 - self.transaction_fee)) / row['close']
                balance = 0
                logger.info(f"Buy at {row['close']}")
            elif row['signal'] == -1 and position > 0:  # Sell
                balance += (position * row['close']) * (1 - self.transaction_fee)
                trade_log.append(balance)
                position = 0
                logger.info(f"Sell at {row['close']}")

        final_balance = balance + (position * data['close'].iloc[-1])
        cumulative_returns = pd.Series(trade_log).pct_change().dropna().sum()
        logger.info(f"Final Balance: ${final_balance:.2f}, Cumulative Returns: {cumulative_returns:.2f}")
        return final_balance

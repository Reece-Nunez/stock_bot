class Backtester:
    def __init__(self, strategy, initial_balance=10000):
        self.strategy = strategy
        self.initial_balance = initial_balance

    def run(self, data):
        """Backtest the strategy on historical data."""
        data = self.strategy.generate_signal(data)
        balance = self.initial_balance
        position = 0
        for _, row in data.iterrows():
            if row['signal'] == 1:  # Buy
                position += balance / row['close']
                balance = 0
            elif row['signal'] == -1 and position > 0:  # Sell
                balance += position * row['close']
                position = 0
        return balance

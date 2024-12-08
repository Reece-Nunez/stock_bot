import pandas as pd
from strategies.base_strategy import BaseStrategy

class MACDStrategy(BaseStrategy):
    def __init__(self, short_window=12, long_window=26, signal_window=9):
        self.short_window = short_window
        self.long_window = long_window
        self.signal_window = signal_window

    def generate_signal(self, data):
        """
        Generates buy/sell signals based on MACD.
        Buy when MACD crosses above the signal line.
        Sell when MACD crosses below the signal line.
        """
        data['ema_short'] = data['close'].ewm(span=self.short_window, adjust=False).mean()
        data['ema_long'] = data['close'].ewm(span=self.long_window, adjust=False).mean()
        data['macd'] = data['ema_short'] - data['ema_long']
        data['signal_line'] = data['macd'].ewm(span=self.signal_window, adjust=False).mean()

        # Generate signals
        data['signal'] = 0
        data.loc[data['macd'] > data['signal_line'], 'signal'] = 1  # Buy
        data.loc[data['macd'] < data['signal_line'], 'signal'] = -1  # Sell
        return data

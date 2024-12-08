import pandas as pd
from strategies.base_strategy import BaseStrategy

class RSIStrategy(BaseStrategy):
    def __init__(self, period=14, overbought=70, oversold=30):
        self.period = period
        self.overbought = overbought
        self.oversold = oversold

    def generate_signal(self, data):
        """
        Generates buy/sell signals based on RSI.
        Buy when RSI < oversold.
        Sell when RSI > overbought.
        """
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.period).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))

        # Generate signals
        data['signal'] = 0
        data.loc[data['rsi'] < self.oversold, 'signal'] = 1  # Buy
        data.loc[data['rsi'] > self.overbought, 'signal'] = -1  # Sell
        return data

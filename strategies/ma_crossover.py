import pandas as pd
from strategies.base_strategy import BaseStrategy

class MovingAverageCrossover(BaseStrategy):
    def __init__(self, short_window=10, long_window=50):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signal(self, data):
        data['short_ma'] = data['close'].rolling(self.short_window).mean()
        data['long_ma'] = data['close'].rolling(self.long_window).mean()
        
        # Signal: Buy when short MA crosses above long MA, sell when below
        data['signal'] = 0
        data.loc[data['short_ma'] > data['long_ma'], 'signal'] = 1
        data.loc[data['short_ma'] < data['long_ma'], 'signal'] = -1
        return data

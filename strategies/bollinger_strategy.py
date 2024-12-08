import pandas as pd
from strategies.base_strategy import BaseStrategy

class BollingerBandsStrategy(BaseStrategy):
    def __init__(self, window=20, num_std_dev=2):
        self.window = window
        self.num_std_dev = num_std_dev

    def generate_signal(self, data):
        """
        Generates buy/sell signals based on Bollinger Bands.
        Buy when price crosses below the lower band.
        Sell when price crosses above the upper band.
        """
        data['sma'] = data['close'].rolling(self.window).mean()
        data['std_dev'] = data['close'].rolling(self.window).std()
        data['upper_band'] = data['sma'] + (self.num_std_dev * data['std_dev'])
        data['lower_band'] = data['sma'] - (self.num_std_dev * data['std_dev'])

        # Generate signals
        data['signal'] = 0
        data.loc[data['close'] < data['lower_band'], 'signal'] = 1  # Buy
        data.loc[data['close'] > data['upper_band'], 'signal'] = -1  # Sell
        return data

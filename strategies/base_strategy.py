from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    @abstractmethod
    def generate_signal(self, data):
        """Generate buy/sell/hold signals based on data."""
        pass

class OrderManager:
    def __init__(self, api):
        self.api = api

    def place_order(self, symbol, qty, side, order_type='market'):
        """Place a buy or sell order."""
        self.api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type=order_type,
            time_in_force='gtc'
        )

import logging
from alpaca_trade_api import REST

# Configure logging
logging.basicConfig(
    filename="order_manager_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class OrderManager:
    def __init__(self, api: REST, fetcher):
        self.api = api
        self.fetcher = fetcher  # Store the fetcher instance

    def place_market_order(self, symbol: str, qty: int, side: str, time_in_force="day"):
        """Place a market order."""
        try:
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type="market",
                time_in_force=time_in_force,
            )
            logging.info(f"Market order placed: {order}")
            return order
        except Exception as e:
            logging.error(f"Failed to place market order: {e}")
            raise

    def place_dynamic_bracket_order(self, symbol, side, risk_per_trade, stop_loss_pct, take_profit_pct):
        """Place a dynamic bracket order with a portfolio exposure cap."""
        current_equity = self.fetcher.get_portfolio_gain_loss()["current_equity"]  # Use fetcher instance
        max_exposure = current_equity * 0.2  # Limit to 20% of total equity

        # Calculate position size based on risk
        risk_amount = current_equity * risk_per_trade
        position_size = min(risk_amount / stop_loss_pct, max_exposure)
        if position_size <= 0:
            logging.warning(f"Position size for {symbol} is zero or negative. Skipping order.")
            return

        self.place_bracket_order(symbol, position_size, side, take_profit_pct, stop_loss_pct)

    def place_bracket_order(
        self, symbol: str, qty: int, side: str, take_profit_pct: float, stop_loss_pct: float
    ):
        """Place a bracket order with dynamic stop-loss and take-profit percentages."""
        try:
            current_price = self.api.get_last_trade(symbol).price
            take_profit_price = current_price * (1 + take_profit_pct)
            stop_loss_price = current_price * (1 - stop_loss_pct)

            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type="market",
                time_in_force="day",
                order_class="bracket",
                take_profit={"limit_price": take_profit_price},
                stop_loss={"stop_price": stop_loss_price},
            )
            logging.info(f"Bracket order placed: {order}")
            return order
        except Exception as e:
            logging.error(f"Failed to place bracket order: {e}")
            raise

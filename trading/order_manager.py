import logging
from alpaca_trade_api import REST
from typing import List
import pandas as pd

# Configure logging
logging.basicConfig(
    filename="order_manager_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class OrderManager:
    def __init__(self, api: REST):
        self.api = api

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
    
    def calculate_position_size(self, risk_per_trade: float, stop_loss_pct: float) -> int:
        """Calculate position size based on account balance and risk percentage."""
        try:
            account = self.api.get_account()
            equity = float(account.equity)
            risk_amount = equity * risk_per_trade
            position_size = int(risk_amount / (stop_loss_pct * equity))
            logging.info(f"Calculated position size: {position_size} shares.")
            return position_size
        except Exception as e:
            logging.error(f"Failed to calculate position size: {e}")
            raise

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

    def fetch_portfolio(self):
        """Fetch current portfolio positions."""
        try:
            positions = self.api.list_positions()
            portfolio = [
                {
                    "symbol": position.symbol,
                    "qty": position.qty,
                    "market_value": position.market_value,
                    "unrealized_pl": position.unrealized_pl,
                }
                for position in positions
            ]
            logging.info(f"Fetched portfolio: {portfolio}")
            return portfolio
        except Exception as e:
            logging.error(f"Failed to fetch portfolio: {e}")
            raise
    
    def place_dynamic_bracket_order(
        self, symbol: str, side: str, risk_per_trade: float, stop_loss_pct: float, take_profit_pct: float
    ):
        """Place a bracket order with dynamic position sizing."""
        try:
            current_price = self.api.get_last_trade(symbol).price
            stop_loss_price = current_price * (1 - stop_loss_pct)
            take_profit_price = current_price * (1 + take_profit_pct)
            qty = self.calculate_position_size(risk_per_trade, stop_loss_pct)

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
            logging.info(f"Dynamic bracket order placed: {order}")
            return order
        except Exception as e:
            logging.error(f"Failed to place dynamic bracket order: {e}")
            raise


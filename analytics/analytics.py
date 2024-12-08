import logging
import numpy as np

class Analytics:
    def __init__(self):
        self.total_trades = 0
        self.win_rate = 0
        self.total_profit = 0
        self.trade_history = []
        self.current_strategy = "rsi"

    def update_trade(self, profit_loss):
        self.total_trades += 1
        self.trade_history.append(profit_loss)
        wins = len([trade for trade in self.trade_history if trade > 0])
        self.win_rate = (wins / self.total_trades) * 100
        self.total_profit += profit_loss
        logging.info(f"Trade updated. Profit/Loss: {profit_loss}, Total Profit: {self.total_profit}")

    def get_sharpe_ratio(self):
        """Calculate the Sharpe ratio."""
        if len(self.trade_history) < 2:
            return 0
        returns = np.array(self.trade_history)
        mean_return = np.mean(returns)
        std_dev = np.std(returns)
        sharpe_ratio = mean_return / std_dev if std_dev != 0 else 0
        return round(sharpe_ratio, 2)

    def get_max_drawdown(self):
        """Calculate maximum drawdown."""
        if not self.trade_history:
            return 0
        cumulative_returns = np.cumsum(self.trade_history)
        peak = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - peak) / peak
        max_drawdown = np.min(drawdown)
        return round(max_drawdown * 100, 2)  # As percentage

    def get_analytics(self):
        return {
            "total_trades": self.total_trades,
            "win_rate": round(self.win_rate, 2),
            "total_profit": round(self.total_profit, 2),
            "sharpe_ratio": self.get_sharpe_ratio(),
            "max_drawdown": self.get_max_drawdown(),
            "current_strategy": self.current_strategy,
        }

    def get_real_time_updates(self):
        """Simulated real-time updates."""
        return {"recent_trades": self.trade_history[-5:]}  # Return last 5 trades

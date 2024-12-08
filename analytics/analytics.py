import logging
import numpy as np
import pandas as pd
from datetime import datetime

class Analytics:
    def __init__(self):
        self.total_trades = 0
        self.win_rate = 0
        self.total_profit = 0
        self.trade_history = []
        self.strategy_performance = {}
        self.sentiment_scores = {}  # For external sentiment analysis
        self.last_update_time = datetime.now()

    def update_trade(self, profit_loss, strategy):
        """
        Update analytics when a trade is executed.
        """
        self.total_trades += 1
        self.trade_history.append({
            "timestamp": datetime.now(),
            "profit_loss": profit_loss,
            "strategy": strategy
        })
        wins = len([trade for trade in self.trade_history if trade["profit_loss"] > 0])
        self.win_rate = (wins / self.total_trades) * 100
        self.total_profit += profit_loss

        # Update performance by strategy
        if strategy not in self.strategy_performance:
            self.strategy_performance[strategy] = {"trades": 0, "profit": 0}
        self.strategy_performance[strategy]["trades"] += 1
        self.strategy_performance[strategy]["profit"] += profit_loss

        logging.info(f"Trade updated. Profit/Loss: {profit_loss}, Strategy: {strategy}, Total Profit: {self.total_profit}")

    def get_sharpe_ratio(self):
        """Calculate the Sharpe ratio."""
        if len(self.trade_history) < 2:
            return 0
        returns = np.array([trade["profit_loss"] for trade in self.trade_history])
        mean_return = np.mean(returns)
        std_dev = np.std(returns)
        sharpe_ratio = mean_return / std_dev if std_dev != 0 else 0
        logging.info(f"Sharpe Ratio calculated: {round(sharpe_ratio, 2)}")
        return round(sharpe_ratio, 2)

    def get_max_drawdown(self):
        """Calculate maximum drawdown."""
        if not self.trade_history:
            return 0
        cumulative_returns = np.cumsum([trade["profit_loss"] for trade in self.trade_history])
        peak = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - peak) / peak
        max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0
        logging.info(f"Max Drawdown calculated: {round(max_drawdown * 100, 2)}%")
        return round(max_drawdown * 100, 2)  # As percentage

    def get_analytics(self):
        """
        Return analytics as a dictionary.
        """
        return {
            "total_trades": self.total_trades,
            "win_rate": round(self.win_rate, 2),
            "total_profit": round(self.total_profit, 2),
            "strategy_performance": self.strategy_performance,
            "sentiment_scores": self.sentiment_scores,
            "last_update_time": self.last_update_time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def get_real_time_updates(self):
        """Simulated real-time updates."""
        return {"recent_trades": self.trade_history[-5:]}  # Return last 5 trades

    def update_sentiment_scores(self, sentiment_data):
        """
        Update sentiment scores from external APIs.
        """
        self.sentiment_scores = sentiment_data
        self.last_update_time = datetime.now()
        logging.info(f"Sentiment scores updated: {self.sentiment_scores}")

    def get_heatmap_data(self):
        """
        Generate heatmap data for strategy performance.
        """
        strategies = self.strategy_performance.keys()
        trades = [self.strategy_performance[strategy]["trades"] for strategy in strategies]
        profits = [self.strategy_performance[strategy]["profit"] for strategy in strategies]

        # Generate heatmap-friendly DataFrame
        heatmap_data = pd.DataFrame({
            "Strategy": strategies,
            "Trades": trades,
            "Profit": profits
        })
        return heatmap_data

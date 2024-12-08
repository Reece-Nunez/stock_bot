import os
import pytest
import asyncio
import pandas as pd
from unittest.mock import Mock, patch
from main import execute_trades, backtest_strategies
from data.data_fetcher import DataFetcher
from trading.order_manager import OrderManager
from strategies.rsi_strategy import RSIStrategy

# Mock environment variables
os.environ["APCA_API_KEY_ID"] = "test_api_key"
os.environ["APCA_API_SECRET_KEY"] = "test_api_secret"
os.environ["APCA_API_BASE_URL"] = "https://paper-api.alpaca.markets"

@pytest.mark.asyncio
async def test_backtesting_with_mock_data():
    # Mock DataFetcher
    with patch("data.data_fetcher.DataFetcher.get_historical_data", new_callable=Mock) as mock_historical_data:
        mock_historical_data.return_value = pd.DataFrame({
            "time": ["2024-12-01", "2024-12-02", "2024-12-03"],
            "open": [100, 101, 102],
            "high": [105, 106, 107],
            "low": [95, 96, 97],
            "close": [102, 103, 104],
            "volume": [1000, 1200, 1500],
        })

        # Mock strategies
        strategies = {"rsi": RSIStrategy(overbought=70, oversold=30)}

        # Run backtesting
        fetcher = DataFetcher("api_key", "api_secret", "http://mock.api")
        await backtest_strategies(strategies, fetcher, "AAPL")


@pytest.mark.asyncio
async def test_execute_trades_with_mock_data():
    # Mock DataFetcher and OrderManager
    with patch("data.data_fetcher.DataFetcher.get_historical_data", new_callable=Mock) as mock_historical_data, \
         patch("trading.order_manager.OrderManager.place_dynamic_bracket_order", new_callable=Mock) as mock_place_order, \
         patch("strategies.rsi_strategy.RSIStrategy.generate_signal", new_callable=Mock) as mock_generate_signal:

        # Mock historical data with signals to trigger trades
        mock_historical_data.return_value = pd.DataFrame({
            "time": ["2024-12-01", "2024-12-02", "2024-12-03"],
            "open": [100, 101, 102],
            "high": [105, 106, 107],
            "low": [95, 96, 97],
            "close": [102, 103, 104],
            "volume": [1000, 1200, 1500],
            "signal": [0, 1, -1],  # Mocked signals to trigger buy/sell
        })

        # Mock the generate_signal method to return the same DataFrame
        mock_generate_signal.return_value = pd.DataFrame({
            "time": ["2024-12-01", "2024-12-02", "2024-12-03"],
            "signal": [0, 1, -1],  # Ensure signals trigger trades
        })

        # Initialize mock fetcher and order manager
        fetcher = DataFetcher("api_key", "api_secret", "http://mock.api")
        order_manager = OrderManager(fetcher.api, fetcher)

        # Execute trades with mock data
        await execute_trades(order_manager, {"rsi": RSIStrategy(overbought=70, oversold=30)}, fetcher, current_strategy="rsi", max_iterations=3)

        # Assert the historical data was fetched
        mock_historical_data.assert_called_with("AAPL", "minute", limit=100)

        # Debug: Print calls for troubleshooting
        print("Mock Calls:", mock_place_order.call_args_list)

        # Assert the place_dynamic_bracket_order method was called with expected arguments
        assert mock_place_order.call_count == 2, "Expected two trades (buy and sell) to be triggered."
        mock_place_order.assert_any_call(
            symbol="AAPL",
            side="buy",
            risk_per_trade=0.02,
            stop_loss_pct=0.02,
            take_profit_pct=0.05,
        )
        mock_place_order.assert_any_call(
            symbol="AAPL",
            side="sell",
            risk_per_trade=0.02,
            stop_loss_pct=0.02,
            take_profit_pct=0.05,
        )



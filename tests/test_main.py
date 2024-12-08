import os
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from main import execute_trades
import pandas as pd

os.environ["API_KEY"] = "test_api_key"
os.environ["API_SECRET"] = "test_api_secret"
os.environ["BASE_URL"] = "https://paper-api.alpaca.markets"

@pytest.mark.asyncio
async def test_execute_trades():
    # Mock DataFetcher and OrderManager
    with patch("main.fetcher") as mock_fetcher, patch("main.order_manager") as mock_order_manager, patch("asyncio.sleep", new_callable=AsyncMock):
        # Mock `get_historical_data` to alternate signals (buy, sell)
        mock_fetcher.get_historical_data = AsyncMock(
            side_effect=[
                pd.DataFrame({"signal": [1]}),  # Buy signal
                pd.DataFrame({"signal": [-1]}),  # Sell signal
            ]
        )
        # Mock `place_dynamic_bracket_order` to be an AsyncMock
        mock_order_manager.place_dynamic_bracket_order = AsyncMock()

        # Run the trading function with max_iterations to limit execution
        await execute_trades("rsi", max_iterations=2)

        # Verify the mocked methods were called
        assert mock_fetcher.get_historical_data.call_count == 2
        assert mock_order_manager.place_dynamic_bracket_order.call_count == 2

        # Verify the first call was a buy
        mock_order_manager.place_dynamic_bracket_order.assert_any_call(
            symbol="AAPL",
            side="buy",
            risk_per_trade=0.02,
            stop_loss_pct=0.02,
            take_profit_pct=0.05,
        )
        # Verify the second call was a sell
        mock_order_manager.place_dynamic_bracket_order.assert_any_call(
            symbol="AAPL",
            side="sell",
            risk_per_trade=0.02,
            stop_loss_pct=0.02,
            take_profit_pct=0.05,
        )

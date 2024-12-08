import pytest
import pandas as pd
from unittest.mock import AsyncMock, MagicMock, patch
from data.data_fetcher import DataFetcher
from main import backtest_strategies
from strategies.rsi_strategy import RSIStrategy

@pytest.mark.asyncio
async def test_backtesting_with_mock_data():
    # Mock DataFetcher
    with patch("data.data_fetcher.DataFetcher.get_historical_data", new_callable=AsyncMock) as mock_historical_data:
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


def test_get_realtime_price(mocker):
    # Mock Alpaca API response
    mock_api = MagicMock()
    mock_api.get_last_trade.return_value.price = 105

    fetcher = DataFetcher("api_key", "api_secret", "https://paper-api.alpaca.markets")
    fetcher.api = mock_api  # Replace API with mock

    price = fetcher.get_realtime_price("AAPL")
    assert price == 105

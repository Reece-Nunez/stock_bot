import pytest
import pandas as pd
from unittest.mock import MagicMock
from data.data_fetcher import DataFetcher

def test_get_historical_data(mocker):
    # Mock Alpaca API response
    mock_api = MagicMock()
    mock_api.get_bars.return_value = [
        MagicMock(t="2024-01-01", o=100, h=110, l=90, c=105, v=1000)
    ]
    
    fetcher = DataFetcher("api_key", "api_secret", "https://paper-api.alpaca.markets")
    fetcher.api = mock_api  # Replace API with mock

    data = fetcher.get_historical_data("AAPL", "minute", limit=1)
    assert isinstance(data, pd.DataFrame)
    assert len(data) == 1
    assert data.iloc[0]['close'] == 105

def test_get_realtime_price(mocker):
    # Mock Alpaca API response
    mock_api = MagicMock()
    mock_api.get_last_trade.return_value.price = 105

    fetcher = DataFetcher("api_key", "api_secret", "https://paper-api.alpaca.markets")
    fetcher.api = mock_api  # Replace API with mock

    price = fetcher.get_realtime_price("AAPL")
    assert price == 105

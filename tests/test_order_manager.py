from unittest.mock import MagicMock
from trading.order_manager import OrderManager

def test_place_market_order(mocker):
    mock_api = MagicMock()
    mock_fetcher = MagicMock()
    mock_fetcher.get_portfolio_gain_loss.return_value = {"current_equity": 10000}

    order_manager = OrderManager(mock_api, mock_fetcher)

    order = order_manager.place_market_order("AAPL", 1, "buy")
    assert order is not None

def test_place_bracket_order(mocker):
    mock_api = MagicMock()
    mock_fetcher = MagicMock()
    mock_fetcher.get_portfolio_gain_loss.return_value = {"current_equity": 10000}

    order_manager = OrderManager(mock_api, mock_fetcher)

    order = order_manager.place_bracket_order("AAPL", 1, "buy", 0.05, 0.02)
    assert order is not None

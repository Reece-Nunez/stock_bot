from analytics.analytics import Analytics

def test_update_trade():
    analytics = Analytics()
    analytics.update_trade(100, "rsi")
    assert analytics.total_trades == 1
    assert analytics.total_profit == 100
    assert analytics.win_rate == 100

def test_get_sharpe_ratio():
    analytics = Analytics()
    analytics.update_trade(100, "rsi")
    analytics.update_trade(-50, "rsi")
    sharpe_ratio = analytics.get_sharpe_ratio()
    assert sharpe_ratio > 0

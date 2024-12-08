from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from data.data_fetcher import DataFetcher
from strategies.rsi_strategy import RSIStrategy
from strategies.macd_strategy import MACDStrategy
from strategies.bollinger_strategy import BollingerBandsStrategy
from trading.order_manager import OrderManager
from analytics.analytics import Analytics
import os
from logger_config import logger
from threading import Thread

# Flask App Initialization
app = Flask(__name__)

# Initialize SocketIO
socketio = SocketIO(app)

# Configure logger
logger.basicConfig(
    filename="app_logs.log",
    level=logger.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize API Credentials
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_API_SECRET")
BASE_URL = os.getenv("ALPACA_BASE_URL")

if not API_KEY or not API_SECRET or not BASE_URL:
    logger.error("API credentials or BASE_URL are not set.")
    raise EnvironmentError("API credentials or BASE_URL are not set.")

# Initialize Modules
data_fetcher = DataFetcher(API_KEY, API_SECRET, BASE_URL)
order_manager = OrderManager(data_fetcher.api)
analytics = Analytics()

# Strategies
strategies = {
    "rsi": RSIStrategy(period=14, overbought=70, oversold=30),
    "macd": MACDStrategy(short_window=12, long_window=26, signal_window=9),
    "bollinger": BollingerBandsStrategy(window=20, num_std_dev=2),
}
current_strategy = "rsi"  # Default strategy


@app.route("/")
def dashboard():
    """
    Render the main dashboard with account info, portfolio metrics, and performance analytics.
    """
    try:
        account_info = data_fetcher.get_account_info()
        portfolio_info = data_fetcher.get_portfolio_gain_loss()
        bot_analytics = analytics.get_analytics()

        return render_template(
            "dashboard.html",
            account=account_info,
            portfolio=portfolio_info,
            analytics=bot_analytics,
            current_strategy=current_strategy
        )
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        return "An error occurred while loading the dashboard."


@app.route("/update-strategy", methods=["POST"])
def update_strategy():
    """
    Update the active trading strategy.
    """
    global current_strategy
    try:
        strategy = request.form.get("strategy")
        if strategy in strategies:
            current_strategy = strategy
            analytics.update_current_strategy(strategy)
            logger.info(f"Updated trading strategy to: {strategy}")
            return jsonify({"status": "success", "message": f"Strategy updated to {strategy}"}), 200
        else:
            logger.warning(f"Invalid strategy update attempt: {strategy}")
            return jsonify({"status": "error", "message": "Invalid strategy selected."}), 400
    except Exception as e:
        logger.error(f"Failed to update strategy: {e}")
        return jsonify({"status": "error", "message": "Error updating strategy."}), 500


@socketio.on("connect")
def handle_connect():
    logger.info("Client connected to WebSocket.")


def broadcast_real_time_data():
    """Send real-time updates to the WebSocket clients."""
    while True:
        try:
            portfolio = data_fetcher.get_portfolio_gain_loss()
            analytics_data = analytics.get_analytics()
            socketio.emit("real_time_data", {"portfolio": portfolio, "analytics": analytics_data})
        except Exception as e:
            logger.error(f"Error in broadcasting real-time data: {e}")


if __name__ == "__main__":
    # Start broadcasting thread
    thread = Thread(target=broadcast_real_time_data, daemon=True)
    thread.start()

    # Run the app with WebSocket support
    socketio.run(app, debug=True)

from flask import Flask, render_template, jsonify, request
from data_fetcher import DataFetcher

# Flask app
app = Flask(__name__)

# Initialize DataFetcher
api_key = "your_api_key"
api_secret = "your_api_secret"
base_url = "https://paper-api.alpaca.markets"
data_fetcher = DataFetcher(api_key, api_secret, base_url)

@app.route("/")
def dashboard():
    """Render the dashboard."""
    account_info = data_fetcher.get_account_info()
    portfolio_info = data_fetcher.get_portfolio_gain_loss()
    return render_template("dashboard.html", account=account_info, portfolio=portfolio_info)

@app.route("/assets")
def assets():
    """Render the assets page."""
    assets = data_fetcher.get_all_assets()
    return render_template("assets.html", assets=assets.to_dict(orient="records"))

@app.route("/check-asset", methods=["POST"])
def check_asset():
    """Check if a specific asset is tradable."""
    symbol = request.form.get("symbol")
    result = data_fetcher.check_asset_tradable(symbol)
    return jsonify(result)

@app.route("/api/account")
def account_api():
    """API endpoint for account information."""
    return jsonify(data_fetcher.get_account_info())

@app.route("/api/portfolio")
def portfolio_api():
    """API endpoint for portfolio gain/loss."""
    return jsonify(data_fetcher.get_portfolio_gain_loss())

if __name__ == "__main__":
    app.run(debug=True)

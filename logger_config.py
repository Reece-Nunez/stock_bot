from loguru import logger
import sys
import os

# Log file configuration
LOG_FILE = os.getenv("LOG_FILE", "stock_bot.log")  # Default log file

# Configure logger
logger.remove()  # Remove default handler
logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")  # Console logs
logger.add(
    LOG_FILE,
    rotation="10 MB",  # Rotate log files at 10 MB
    retention="7 days",  # Keep logs for 7 days
    compression="zip",  # Compress old logs
    level="DEBUG",
    format="{time} {level} {message}",
)

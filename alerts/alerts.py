import os
import smtplib
from email.message import EmailMessage
from loguru import logger  # Replacing logging with loguru

def send_alert(subject, body):
    """Send an email alert."""
    email = os.getenv("ALERT_EMAIL")
    password = os.getenv("ALERT_PASSWORD")
    recipient = os.getenv("RECIPIENT_EMAIL")
    try:
        if not email or not password or not recipient:
            logger.error("Email credentials or recipient are not set in environment variables.")
            return

        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = email
        msg["To"] = recipient

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(email, password)
            server.send_message(msg)
        logger.info("Alert sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send alert: {e}")

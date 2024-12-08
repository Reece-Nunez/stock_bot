import os
import smtplib
from email.message import EmailMessage
import logging

def send_alert(subject, body):
    """Send an email alert."""
    email = os.getenv("ALERT_EMAIL")
    password = os.getenv("ALERT_PASSWORD")
    recipient = os.getenv("RECIPIENT_EMAIL")
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = email
        msg["To"] = recipient

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(email, password)
            server.send_message(msg)
        logging.info("Alert sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send alert: {e}")

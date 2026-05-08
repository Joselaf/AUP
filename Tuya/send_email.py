import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Credentials are loaded from Tuya/.env:
#   SMTP_USER     - your email address
#   SMTP_PASSWORD - your email password

SMTP_HOST = "smtp.aup.pt"
SMTP_PORT = 25
RECIPIENT = "luis.faria@aup.pt"

def send_email(subject: str, body: str):
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    if not user or not password:
        raise RuntimeError("SMTP_USER and SMTP_PASSWORD environment variables must be set.")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"Alertas casa ganso <{user}>"
    msg["To"] = RECIPIENT
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.ehlo()
        smtp.login(user, password)
        smtp.send_message(msg)
    print(f"Email sent to {RECIPIENT}")


if __name__ == "__main__":
    send_email(
        subject="Test email",
        body="This is a test email sent from send_email.py.",
    )

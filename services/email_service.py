import os
import json
import smtplib
import logging
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

RECIPIENTS_FILE = Path(__file__).resolve().parent.parent / "recipients.json"


def _load_recipients() -> list[str]:
    """Load recipient email addresses from recipients.json."""
    if not RECIPIENTS_FILE.exists():
        logger.error("Recipients file not found: %s", RECIPIENTS_FILE)
        raise FileNotFoundError(f"Missing {RECIPIENTS_FILE}")

    with open(RECIPIENTS_FILE, "r") as f:
        recipients = json.load(f)

    if not isinstance(recipients, list) or not recipients:
        raise ValueError("recipients.json must be a non-empty JSON array of email strings.")

    logger.info("Loaded %d recipient(s) from %s", len(recipients), RECIPIENTS_FILE.name)
    return recipients


def send_news_email(html_content: str) -> None:
    """Send an HTML email with the provided content via Gmail SMTP."""
    sender = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_PASSWORD")

    if not all([sender, password]):
        logger.error("Email credentials missing — check SENDER_EMAIL, SENDER_PASSWORD")
        raise ValueError("One or more email environment variables are not set.")

    recipients = _load_recipients()

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📰 Your Daily News Digest"
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(html_content, "html"))

    try:
        logger.info("Connecting to smtp.gmail.com:465 …")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipients, msg.as_string())
        logger.info("Email sent successfully to %s", ", ".join(recipients))
    except smtplib.SMTPAuthenticationError:
        logger.exception("SMTP authentication failed — check SENDER_PASSWORD (must be a Gmail App Password)")
        raise
    except smtplib.SMTPException:
        logger.exception("SMTP error while sending email")
        raise
    except Exception:
        logger.exception("Unexpected error while sending email")
        raise

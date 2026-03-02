import logging

from services.news_service import fetch_and_format_news
from services.email_service import send_news_email

logger = logging.getLogger(__name__)


def run_pipeline() -> None:
    """Orchestrate the full fetch-news → send-email pipeline.

    Catches all exceptions so that a single failure never crashes
    the scheduler or the running server.
    """
    logger.info("Pipeline started")
    try:
        html = fetch_and_format_news()
        send_news_email(html)
        logger.info("Pipeline completed successfully")
    except Exception:
        logger.exception("Pipeline failed")

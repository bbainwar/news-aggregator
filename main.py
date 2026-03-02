import os
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from services.pipeline import run_pipeline

# ---------------------------------------------------------------------------
# Environment & Logging
# ---------------------------------------------------------------------------
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Scheduler configuration (all optional, with sensible defaults)
# ---------------------------------------------------------------------------
SCHEDULE_HOUR = int(os.getenv("SCHEDULE_HOUR", "8"))
SCHEDULE_MINUTE = int(os.getenv("SCHEDULE_MINUTE", "0"))
SCHEDULE_TZ = os.getenv("SCHEDULE_TZ", "Asia/Kolkata")

scheduler = AsyncIOScheduler(timezone=SCHEDULE_TZ)


# ---------------------------------------------------------------------------
# FastAPI lifespan (modern approach — replaces on_event)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        run_pipeline,
        trigger="cron",
        hour=SCHEDULE_HOUR,
        minute=SCHEDULE_MINUTE,
        id="daily_news_email",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "Scheduler started — daily email job at %02d:%02d %s",
        SCHEDULE_HOUR,
        SCHEDULE_MINUTE,
        SCHEDULE_TZ,
    )
    yield
    scheduler.shutdown()
    logger.info("Scheduler shut down")


app = FastAPI(
    title="Daily News Aggregator",
    description="Fetches top news via Gemini + Google Search and emails a daily digest.",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Manual trigger endpoint (for testing)
# ---------------------------------------------------------------------------
@app.post("/trigger-email", status_code=202)
async def trigger_email(background_tasks: BackgroundTasks):
    """Manually trigger the news-fetch-and-email pipeline in the background."""
    background_tasks.add_task(run_pipeline)
    logger.info("Manual trigger received — pipeline queued")
    return {"message": "Email pipeline triggered. Check logs for progress."}

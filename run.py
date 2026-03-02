"""Standalone entry point for the news pipeline.

Used by GitHub Actions and for local testing:
    python run.py
"""

import logging
from dotenv import load_dotenv

from services.pipeline import run_pipeline

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

if __name__ == "__main__":
    run_pipeline()

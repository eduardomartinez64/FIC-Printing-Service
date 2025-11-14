#!/usr/bin/env python3
"""Main entry point for the Gmail email processor service."""

import logging
import time
import signal
import sys
import schedule

from src.utils.logger import setup_logging
from src.config import Config
from src.email_processor import EmailProcessor
from src.services.gmail_service import GmailService
from src.services.daily_report import DailyReportService

logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
running = True


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global running
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    running = False


def main():
    """Main entry point for the service."""
    global running

    # Setup logging
    setup_logging()
    logger.info("=" * 60)
    logger.info("Gmail Email Processor Service Starting")
    logger.info("=" * 60)

    # Validate configuration
    try:
        Config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    # Initialize email processor
    try:
        processor = EmailProcessor()
    except Exception as e:
        logger.error(f"Failed to initialize email processor: {e}", exc_info=True)
        sys.exit(1)

    # Verify setup
    if not processor.verify_setup():
        logger.error("Service setup verification failed. Please check configuration.")
        sys.exit(1)

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Schedule processing to run every minute
    interval_seconds = Config.CHECK_INTERVAL_SECONDS
    logger.info(f"Scheduling email processing every {interval_seconds} seconds")

    schedule.every(interval_seconds).seconds.do(processor.run_once)

    # Schedule daily report if configured
    if Config.DAILY_REPORT_EMAIL:
        try:
            gmail_service = GmailService()
            daily_report = DailyReportService(gmail_service, Config.DAILY_REPORT_EMAIL)

            # Schedule for weekdays only at configured time
            report_time = Config.DAILY_REPORT_TIME
            schedule.every().monday.at(report_time).do(daily_report.send_daily_report)
            schedule.every().tuesday.at(report_time).do(daily_report.send_daily_report)
            schedule.every().wednesday.at(report_time).do(daily_report.send_daily_report)
            schedule.every().thursday.at(report_time).do(daily_report.send_daily_report)
            schedule.every().friday.at(report_time).do(daily_report.send_daily_report)

            logger.info(f"Daily report scheduled for weekdays at {report_time} EST to {Config.DAILY_REPORT_EMAIL}")
        except Exception as e:
            logger.error(f"Failed to setup daily report service: {e}")
            logger.info("Continuing without daily reports")

    # Run immediately on startup
    logger.info("Running initial email processing cycle...")
    processor.run_once()

    # Main loop
    logger.info("Service is now running. Press Ctrl+C to stop.")
    logger.info("=" * 60)

    while running:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
            time.sleep(5)

    logger.info("Service stopped")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()

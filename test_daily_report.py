#!/usr/bin/env python3
"""Test script for daily report generation."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.gmail_service import GmailService
from src.services.daily_report import DailyReportService
from src.config import Config

def main():
    """Test daily report generation and sending."""
    print("=" * 60)
    print("Testing Daily Report Generation")
    print("=" * 60)

    # Check configuration
    if not Config.DAILY_REPORT_EMAIL:
        print("\n❌ ERROR: DAILY_REPORT_EMAIL not configured in .env")
        print("Please set DAILY_REPORT_EMAIL in your .env file")
        return 1

    print(f"\nReport recipient: {Config.DAILY_REPORT_EMAIL}")
    print(f"Scheduled time: {Config.DAILY_REPORT_TIME} EST")

    try:
        # Initialize services
        print("\nInitializing Gmail service...")
        gmail_service = GmailService()

        print("Initializing daily report service...")
        daily_report = DailyReportService(gmail_service, Config.DAILY_REPORT_EMAIL)

        # Send test report
        print("\nGenerating and sending daily report...")
        print("(This will send an actual email to the configured address)")

        success = daily_report.send_daily_report()

        if success:
            print("\n✓ Daily report sent successfully!")
            print(f"Check {Config.DAILY_REPORT_EMAIL} for the email.")
        else:
            print("\n✗ Failed to send daily report")
            print("Check the logs for error details")
            return 1

    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        return 0
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n" + "=" * 60)
    print("Test complete")
    print("=" * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())

"""Configuration management for the email processor service."""

import os
import re
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration."""

    # Base paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    CREDENTIALS_FILE = BASE_DIR / "credentials.json"
    TOKEN_FILE = BASE_DIR / "token.json"

    # Gmail API settings
    GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    EMAIL_SUBJECT_FILTER = os.getenv('EMAIL_SUBJECT_FILTER', 'Batch Order Shipment Report')

    # PrintNode settings
    PRINTNODE_API_KEY = os.getenv('PRINTNODE_API_KEY')
    PRINTNODE_PRINTER_ID = os.getenv('PRINTNODE_PRINTER_ID')
    PRINTNODE_API_URL = 'https://api.printnode.com'

    # Service settings
    CHECK_INTERVAL_SECONDS = int(os.getenv('CHECK_INTERVAL_SECONDS', '60'))

    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = BASE_DIR / os.getenv('LOG_FILE', 'logs/email_processor.log')
    LOG_DIR = LOG_FILE.parent

    # Processed emails tracking
    PROCESSED_EMAILS_FILE = BASE_DIR / "processed_emails.txt"

    # Error notification settings
    _error_emails = os.getenv('ERROR_NOTIFICATION_EMAIL', '')
    ERROR_NOTIFICATION_EMAILS = [email.strip() for email in _error_emails.split(',') if email.strip()]

    # Daily report settings
    DAILY_REPORT_EMAIL = os.getenv('DAILY_REPORT_EMAIL', '')
    DAILY_REPORT_TIME = os.getenv('DAILY_REPORT_TIME', '18:00')  # Default 6 PM

    # Email validation regex
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        errors = []

        if not cls.CREDENTIALS_FILE.exists():
            errors.append(f"Gmail credentials file not found: {cls.CREDENTIALS_FILE}")

        if not cls.PRINTNODE_API_KEY:
            errors.append("PRINTNODE_API_KEY not set in environment")

        if not cls.PRINTNODE_PRINTER_ID:
            errors.append("PRINTNODE_PRINTER_ID not set in environment")

        # Validate error notification email addresses
        if cls.ERROR_NOTIFICATION_EMAILS:
            invalid_emails = [e for e in cls.ERROR_NOTIFICATION_EMAILS
                            if not cls.EMAIL_REGEX.match(e)]
            if invalid_emails:
                errors.append(f"Invalid error notification email addresses: {', '.join(invalid_emails)}")

        # Validate daily report email address
        if cls.DAILY_REPORT_EMAIL and not cls.EMAIL_REGEX.match(cls.DAILY_REPORT_EMAIL):
            errors.append(f"Invalid daily report email address: {cls.DAILY_REPORT_EMAIL}")

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

        # Create necessary directories
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)

        return True

"""Configuration management for the email processor service."""

import os
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
    ERROR_NOTIFICATION_EMAIL = os.getenv('ERROR_NOTIFICATION_EMAIL')

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

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

        # Create necessary directories
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)

        return True

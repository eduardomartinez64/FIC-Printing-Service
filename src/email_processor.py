"""Main email processor service orchestrator."""

import logging
import time
from pathlib import Path
from typing import Set

from src.config import Config
from src.services.gmail_service import GmailService
from src.services.csv_parser import CSVParser
from src.services.printnode_service import PrintNodeService

logger = logging.getLogger(__name__)


class EmailProcessor:
    """Main service for processing emails and printing PDFs."""

    def __init__(self):
        """Initialize the email processor service."""
        self.gmail = GmailService()
        self.printnode = PrintNodeService()
        self.csv_parser = CSVParser()
        self.processed_emails: Set[str] = self._load_processed_emails()

    def _load_processed_emails(self) -> Set[str]:
        """Load set of already processed email IDs from file."""
        if Config.PROCESSED_EMAILS_FILE.exists():
            content = Config.PROCESSED_EMAILS_FILE.read_text()
            return set(line.strip() for line in content.splitlines() if line.strip())
        return set()

    def _save_processed_email(self, message_id: str):
        """Save processed email ID to file."""
        self.processed_emails.add(message_id)
        with Config.PROCESSED_EMAILS_FILE.open('a') as f:
            f.write(f"{message_id}\n")

    def process_emails(self):
        """
        Main processing loop: scan emails, extract PDFs, and print.

        This method:
        1. Searches for emails with the configured subject filter
        2. Extracts CSV attachments
        3. Parses PDF links from column C
        4. Prints PDFs via PrintNode
        5. Tracks processed emails to avoid duplicates
        """
        try:
            logger.info("=" * 60)
            logger.info("Starting email processing cycle")
            logger.info("=" * 60)

            # Search for matching emails
            emails = self.gmail.search_emails(
                subject_filter=Config.EMAIL_SUBJECT_FILTER,
                max_results=20
            )

            if not emails:
                logger.info("No new emails found")
                return

            # Process each email
            processed_count = 0
            printed_count = 0

            for email in emails:
                message_id = email['id']

                # Skip already processed emails
                if message_id in self.processed_emails:
                    logger.debug(f"Email {message_id} already processed, skipping")
                    continue

                logger.info(f"Processing email ID: {message_id}")

                # Get attachments
                attachments = self.gmail.get_attachments(email)
                csv_attachments = [
                    att for att in attachments
                    if att['filename'].lower().endswith('.csv')
                ]

                if not csv_attachments:
                    logger.warning(f"No CSV attachments found in email {message_id}")
                    self._save_processed_email(message_id)
                    continue

                # Process first CSV attachment
                csv_attachment = csv_attachments[0]
                logger.info(f"Processing CSV attachment: {csv_attachment['filename']}")

                # Download CSV
                csv_data = self.gmail.download_attachment(
                    message_id,
                    csv_attachment['attachment_id']
                )

                if not csv_data:
                    logger.error("Failed to download CSV attachment")
                    self._save_processed_email(message_id)
                    continue

                # Extract PDF link from column C (last row)
                pdf_link = self.csv_parser.extract_pdf_link(csv_data, column='C')

                if not pdf_link:
                    logger.error("No PDF link found in CSV column C")
                    self._save_processed_email(message_id)
                    continue

                # Print PDF
                logger.info(f"Printing PDF: {pdf_link}")
                job_id = self.printnode.print_pdf_from_url(
                    pdf_link,
                    title=f"Batch Order Report - {csv_attachment['filename']}"
                )

                if job_id:
                    logger.info(f"✓ Successfully printed PDF. Job ID: {job_id}")
                    printed_count += 1
                else:
                    logger.error("Failed to print PDF")

                # Mark as processed regardless of print success
                self._save_processed_email(message_id)
                processed_count += 1

                # Optional: Mark email as read
                self.gmail.mark_as_read(message_id)

            logger.info("=" * 60)
            logger.info(f"Processing complete: {processed_count} emails processed, {printed_count} PDFs printed")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Error during email processing: {e}", exc_info=True)

    def run_once(self):
        """Run a single processing cycle."""
        try:
            self.process_emails()
        except Exception as e:
            logger.error(f"Unexpected error in processing cycle: {e}", exc_info=True)

    def verify_setup(self) -> bool:
        """
        Verify that all services are configured correctly.

        Returns:
            True if all services are working, False otherwise
        """
        logger.info("Verifying service setup...")

        # Test PrintNode connection
        if not self.printnode.test_connection():
            logger.error("PrintNode connection failed")
            return False

        # Verify printer exists
        if not self.printnode.verify_printer_exists():
            logger.error("Configured printer not found")
            return False

        # Gmail service is verified during initialization
        logger.info("✓ All services verified successfully")
        return True

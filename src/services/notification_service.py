"""Email notification service for sending error alerts."""

import base64
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional

from googleapiclient.errors import HttpError

from src.config import Config

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending email notifications."""

    def __init__(self, gmail_service):
        """
        Initialize notification service.

        Args:
            gmail_service: Authenticated GmailService instance
        """
        self.gmail_service = gmail_service
        self.notification_emails = Config.ERROR_NOTIFICATION_EMAILS

    def send_error_notification(
        self,
        error_message: str,
        email_id: str,
        attachment_filename: Optional[str] = None,
        attachment_data: Optional[bytes] = None
    ) -> bool:
        """
        Send error notification email with optional attachment.

        Args:
            error_message: Description of the error
            email_id: Gmail message ID that caused the error
            attachment_filename: Name of the problematic attachment
            attachment_data: Binary data of the attachment

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.notification_emails:
            logger.warning("No notification emails configured, skipping error notification")
            return False

        try:
            # Create message
            message = MIMEMultipart()
            message['to'] = ', '.join(self.notification_emails)
            message['subject'] = f'FIC Printing Service Error - Email ID: {email_id}'

            # Create email body
            body = f"""
An error occurred while processing an email in the FIC Printing Service.

Error Details:
--------------
{error_message}

Email ID: {email_id}

The problematic email attachment is included with this notification (if available).

---
This is an automated notification from the FIC Printing Service.
"""

            message.attach(MIMEText(body, 'plain'))

            # Attach the problematic file if provided
            if attachment_filename and attachment_data:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment_data)
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {attachment_filename}'
                )
                message.attach(part)
                logger.debug(f"Attached file: {attachment_filename}")

            # Encode and send
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            send_message = {'raw': raw_message}

            self.gmail_service.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()

            logger.info(f"Error notification sent to {', '.join(self.notification_emails)}")
            return True

        except HttpError as error:
            logger.error(f"Failed to send error notification: {error}")
            return False
        except Exception as error:
            logger.error(f"Unexpected error sending notification: {error}")
            return False

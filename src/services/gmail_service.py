"""Gmail API service for scanning and processing emails."""

import base64
import logging
from typing import List, Dict, Optional
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.config import Config

logger = logging.getLogger(__name__)


class GmailService:
    """Service for interacting with Gmail API."""

    def __init__(self):
        """Initialize Gmail service with authentication."""
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authenticate with Gmail API using OAuth2."""
        creds = None

        # Load existing token if available
        if Config.TOKEN_FILE.exists():
            creds = Credentials.from_authorized_user_file(
                str(Config.TOKEN_FILE), Config.GMAIL_SCOPES
            )

        # Refresh or create new credentials if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing Gmail API credentials")
                creds.refresh(Request())
            else:
                logger.info("Performing initial Gmail API authentication")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(Config.CREDENTIALS_FILE), Config.GMAIL_SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for future use
            Config.TOKEN_FILE.write_text(creds.to_json())

        # Build Gmail API service
        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Gmail API service initialized successfully")

    def search_emails(self, subject_filter: str, max_results: int = 10) -> List[Dict]:
        """
        Search for emails with specific subject.

        Args:
            subject_filter: Subject text to filter emails
            max_results: Maximum number of emails to return

        Returns:
            List of email message objects
        """
        try:
            # Build search query
            query = f'subject:"{subject_filter}" has:attachment'
            logger.debug(f"Searching emails with query: {query}")

            # Search for messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} emails matching filter")

            # Get full message details
            full_messages = []
            for msg in messages:
                full_msg = self.get_message(msg['id'])
                if full_msg:
                    full_messages.append(full_msg)

            return full_messages

        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return []

    def get_message(self, message_id: str) -> Optional[Dict]:
        """
        Get full message details by ID.

        Args:
            message_id: Gmail message ID

        Returns:
            Full message object or None
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            return message
        except HttpError as error:
            logger.error(f"Error fetching message {message_id}: {error}")
            return None

    def get_attachments(self, message: Dict) -> List[Dict]:
        """
        Extract attachments from a message.

        Args:
            message: Gmail message object

        Returns:
            List of attachment details (filename, data, mime_type)
        """
        attachments = []

        if 'parts' not in message['payload']:
            return attachments

        for part in message['payload']['parts']:
            if part.get('filename') and part.get('body', {}).get('attachmentId'):
                attachment = {
                    'filename': part['filename'],
                    'mime_type': part['mimeType'],
                    'attachment_id': part['body']['attachmentId'],
                    'message_id': message['id']
                }
                attachments.append(attachment)

        return attachments

    def download_attachment(self, message_id: str, attachment_id: str) -> Optional[bytes]:
        """
        Download attachment data.

        Args:
            message_id: Gmail message ID
            attachment_id: Attachment ID

        Returns:
            Attachment data as bytes or None
        """
        try:
            attachment = self.service.users().messages().attachments().get(
                userId='me',
                messageId=message_id,
                id=attachment_id
            ).execute()

            data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
            return data

        except HttpError as error:
            logger.error(f"Error downloading attachment: {error}")
            return None

    def mark_as_read(self, message_id: str) -> bool:
        """
        Mark a message as read.

        Args:
            message_id: Gmail message ID

        Returns:
            True if successful, False otherwise
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            logger.debug(f"Marked message {message_id} as read")
            return True
        except HttpError as error:
            logger.error(f"Error marking message as read: {error}")
            return False

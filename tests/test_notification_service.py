"""Tests for notification service."""

import pytest
import base64
from unittest.mock import Mock, patch, MagicMock
from email.mime.multipart import MIMEMultipart

from src.services.notification_service import NotificationService


@pytest.fixture
def mock_gmail_service():
    """Create a mock Gmail service."""
    mock_service = Mock()
    mock_service.service = Mock()
    return mock_service


@pytest.fixture
def notification_service(mock_gmail_service):
    """Create a NotificationService instance with mocked Gmail service."""
    with patch('src.services.notification_service.Config') as mock_config:
        mock_config.ERROR_NOTIFICATION_EMAILS = ['test@example.com']
        service = NotificationService(mock_gmail_service)
    return service


def test_send_notification_without_attachment(mock_gmail_service):
    """Test sending notification without attachment."""
    with patch('src.services.notification_service.Config') as mock_config:
        mock_config.ERROR_NOTIFICATION_EMAILS = ['test@example.com']
        service = NotificationService(mock_gmail_service)

        # Mock the Gmail API send method with proper chaining
        mock_execute = Mock(return_value={'id': 'message123'})
        mock_send = Mock(return_value=Mock(execute=mock_execute))
        mock_gmail_service.service.users().messages().send = mock_send

        # Send notification
        result = service.send_error_notification(
            error_message="Test error message",
            email_id="email123"
        )

        # Verify
        assert result is True
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert call_args[1]['userId'] == 'me'
        assert 'body' in call_args[1]


def test_send_notification_with_attachment(mock_gmail_service):
    """Test sending notification with attachment."""
    with patch('src.services.notification_service.Config') as mock_config:
        mock_config.ERROR_NOTIFICATION_EMAILS = ['test@example.com']
        service = NotificationService(mock_gmail_service)

        # Mock the Gmail API send method with proper chaining
        mock_execute = Mock(return_value={'id': 'message123'})
        mock_send = Mock(return_value=Mock(execute=mock_execute))
        mock_gmail_service.service.users().messages().send = mock_send

        # Send notification with attachment
        test_data = b"test file content"
        result = service.send_error_notification(
            error_message="Test error message",
            email_id="email123",
            attachment_filename="test.csv",
            attachment_data=test_data
        )

        # Verify
        assert result is True
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        raw_message = call_args[1]['body']['raw']

        # Decode and verify the message contains attachment
        decoded = base64.urlsafe_b64decode(raw_message)
        assert b'test.csv' in decoded
        assert b'application' in decoded


def test_filename_sanitization(mock_gmail_service):
    """Test that filenames with newlines and quotes are sanitized."""
    with patch('src.services.notification_service.Config') as mock_config:
        mock_config.ERROR_NOTIFICATION_EMAILS = ['test@example.com']
        service = NotificationService(mock_gmail_service)

        # Mock the Gmail API send method with proper chaining
        mock_execute = Mock(return_value={'id': 'message123'})
        mock_send = Mock(return_value=Mock(execute=mock_execute))
        mock_gmail_service.service.users().messages().send = mock_send

        # Send notification with malicious filename
        malicious_filename = 'test\nInjection:\r\nBcc: attacker@evil.com\r\n"file".csv'
        result = service.send_error_notification(
            error_message="Test error",
            email_id="email123",
            attachment_filename=malicious_filename,
            attachment_data=b"test"
        )

        # Verify
        assert result is True
        call_args = mock_send.call_args
        raw_message = call_args[1]['body']['raw']
        decoded = base64.urlsafe_b64decode(raw_message).decode('utf-8', errors='ignore')

        # Verify sanitization prevented header injection
        # The filename should not create a new "Bcc:" header separate from Content-Disposition
        lines = decoded.split('\n')
        bcc_headers = [line for line in lines if line.strip().startswith('Bcc:')]
        # There should be no Bcc header in the email headers section
        assert len(bcc_headers) == 0 or 'attacker@evil.com' not in bcc_headers[0]

        # Verify that the malicious characters were removed
        assert 'testInjection:Bcc: attacker@evil.comfile.csv' in decoded or 'testInjectionBcc attacker@evil.comfilecsv' in decoded


def test_no_emails_configured(mock_gmail_service):
    """Test graceful handling when no notification emails are configured."""
    with patch('src.services.notification_service.Config') as mock_config:
        mock_config.ERROR_NOTIFICATION_EMAILS = []
        service = NotificationService(mock_gmail_service)

        # Send notification
        result = service.send_error_notification(
            error_message="Test error",
            email_id="email123"
        )

        # Verify
        assert result is False
        # Gmail API should not be called
        mock_gmail_service.service.users().messages().send.assert_not_called()


def test_multiple_recipients(mock_gmail_service):
    """Test sending notification to multiple recipients."""
    with patch('src.services.notification_service.Config') as mock_config:
        mock_config.ERROR_NOTIFICATION_EMAILS = ['user1@example.com', 'user2@example.com', 'user3@example.com']
        service = NotificationService(mock_gmail_service)

        # Mock the Gmail API send method with proper chaining
        mock_execute = Mock(return_value={'id': 'message123'})
        mock_send = Mock(return_value=Mock(execute=mock_execute))
        mock_gmail_service.service.users().messages().send = mock_send

        # Send notification
        result = service.send_error_notification(
            error_message="Test error",
            email_id="email123"
        )

        # Verify
        assert result is True
        call_args = mock_send.call_args
        raw_message = call_args[1]['body']['raw']
        decoded = base64.urlsafe_b64decode(raw_message).decode('utf-8', errors='ignore')

        # Verify all recipients are in the message
        assert 'user1@example.com' in decoded
        assert 'user2@example.com' in decoded
        assert 'user3@example.com' in decoded


def test_gmail_api_http_error_handling(mock_gmail_service):
    """Test handling of Gmail API HTTP errors."""
    from googleapiclient.errors import HttpError

    with patch('src.services.notification_service.Config') as mock_config:
        mock_config.ERROR_NOTIFICATION_EMAILS = ['test@example.com']
        service = NotificationService(mock_gmail_service)

        # Mock the Gmail API to raise HttpError
        mock_response = Mock()
        mock_response.status = 500
        mock_error = HttpError(mock_response, b'Server error')

        mock_send = Mock(side_effect=mock_error)
        mock_gmail_service.service.users().messages().send = mock_send

        # Send notification
        result = service.send_error_notification(
            error_message="Test error",
            email_id="email123"
        )

        # Verify error is handled gracefully
        assert result is False


def test_unexpected_exception_handling(mock_gmail_service):
    """Test handling of unexpected exceptions."""
    with patch('src.services.notification_service.Config') as mock_config:
        mock_config.ERROR_NOTIFICATION_EMAILS = ['test@example.com']
        service = NotificationService(mock_gmail_service)

        # Mock the Gmail API to raise unexpected error
        mock_send = Mock(side_effect=RuntimeError("Unexpected error"))
        mock_gmail_service.service.users().messages().send = mock_send

        # Send notification
        result = service.send_error_notification(
            error_message="Test error",
            email_id="email123"
        )

        # Verify error is handled gracefully
        assert result is False


def test_email_body_contains_error_details(mock_gmail_service):
    """Test that notification body contains all expected information."""
    with patch('src.services.notification_service.Config') as mock_config:
        mock_config.ERROR_NOTIFICATION_EMAILS = ['test@example.com']
        service = NotificationService(mock_gmail_service)

        # Mock the Gmail API send method with proper chaining
        mock_execute = Mock(return_value={'id': 'message123'})
        mock_send = Mock(return_value=Mock(execute=mock_execute))
        mock_gmail_service.service.users().messages().send = mock_send

        error_msg = "Failed to parse CSV file"
        email_id = "test_email_123"

        # Send notification
        result = service.send_error_notification(
            error_message=error_msg,
            email_id=email_id
        )

        # Verify
        assert result is True
        call_args = mock_send.call_args
        raw_message = call_args[1]['body']['raw']
        decoded = base64.urlsafe_b64decode(raw_message).decode('utf-8', errors='ignore')

        # Verify body contains error message and email ID
        assert error_msg in decoded
        assert email_id in decoded
        assert "FIC Printing Service" in decoded


def test_email_subject_format(mock_gmail_service):
    """Test that notification subject has correct format."""
    with patch('src.services.notification_service.Config') as mock_config:
        mock_config.ERROR_NOTIFICATION_EMAILS = ['test@example.com']
        service = NotificationService(mock_gmail_service)

        # Mock the Gmail API send method with proper chaining
        mock_execute = Mock(return_value={'id': 'message123'})
        mock_send = Mock(return_value=Mock(execute=mock_execute))
        mock_gmail_service.service.users().messages().send = mock_send

        email_id = "email456"

        # Send notification
        result = service.send_error_notification(
            error_message="Test error",
            email_id=email_id
        )

        # Verify
        assert result is True
        call_args = mock_send.call_args
        raw_message = call_args[1]['body']['raw']
        decoded = base64.urlsafe_b64decode(raw_message).decode('utf-8', errors='ignore')

        # Verify subject contains email ID
        expected_subject = f"FIC Printing Service Error - Email ID: {email_id}"
        assert expected_subject in decoded


def test_base64_encoding_of_message(mock_gmail_service):
    """Test that message is properly base64 encoded."""
    with patch('src.services.notification_service.Config') as mock_config:
        mock_config.ERROR_NOTIFICATION_EMAILS = ['test@example.com']
        service = NotificationService(mock_gmail_service)

        # Mock the Gmail API send method with proper chaining
        mock_execute = Mock(return_value={'id': 'message123'})
        mock_send = Mock(return_value=Mock(execute=mock_execute))
        mock_gmail_service.service.users().messages().send = mock_send

        # Send notification
        result = service.send_error_notification(
            error_message="Test error",
            email_id="email123"
        )

        # Verify
        assert result is True
        call_args = mock_send.call_args
        raw_message = call_args[1]['body']['raw']

        # Verify raw_message is valid base64
        try:
            decoded = base64.urlsafe_b64decode(raw_message)
            # Should not raise exception
            assert len(decoded) > 0
        except Exception as e:
            pytest.fail(f"Message is not properly base64 encoded: {e}")


def test_attachment_data_without_filename(mock_gmail_service):
    """Test that attachment is not included if filename is missing."""
    with patch('src.services.notification_service.Config') as mock_config:
        mock_config.ERROR_NOTIFICATION_EMAILS = ['test@example.com']
        service = NotificationService(mock_gmail_service)

        # Mock the Gmail API send method with proper chaining
        mock_execute = Mock(return_value={'id': 'message123'})
        mock_send = Mock(return_value=Mock(execute=mock_execute))
        mock_gmail_service.service.users().messages().send = mock_send

        # Send notification with data but no filename
        result = service.send_error_notification(
            error_message="Test error",
            email_id="email123",
            attachment_filename=None,
            attachment_data=b"test data"
        )

        # Verify
        assert result is True
        call_args = mock_send.call_args
        raw_message = call_args[1]['body']['raw']
        decoded = base64.urlsafe_b64decode(raw_message).decode('utf-8', errors='ignore')

        # Attachment should not be included
        assert 'Content-Disposition' not in decoded

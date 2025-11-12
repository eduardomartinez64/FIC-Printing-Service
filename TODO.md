# FIC Printing Service - TODO List

**Last Updated**: 2025-11-12

## Priority 1: Must Fix (Security & Critical)

### 🔴 1. Add Filename Sanitization
**File**: `src/services/notification_service.py:85`
**Status**: ✅ Completed (2025-11-12)
**Priority**: CRITICAL
**Estimated Effort**: 15 minutes

**Issue**: Email attachment filenames are not sanitized, allowing potential header injection attacks.

**Implementation**:
```python
# In notification_service.py, line 79-88
if attachment_filename and attachment_data:
    # Sanitize filename to prevent header injection
    safe_filename = attachment_filename.replace('\n', '').replace('\r', '').replace('"', '')

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment_data)
    encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition',
        f'attachment; filename="{safe_filename}"'
    )
    message.attach(part)
    logger.debug(f"Attached file: {safe_filename}")
```

---

### 🟡 2. Add Email Address Validation
**File**: `src/config.py:40-41`
**Status**: ✅ Completed (2025-11-12)
**Priority**: HIGH
**Estimated Effort**: 30 minutes

**Issue**: Configuration accepts invalid email addresses without validation, leading to silent failures.

**Implementation**:
```python
# Add to config.py at top
import re

class Config:
    # ... existing code ...

    # Error notification settings
    _error_emails = os.getenv('ERROR_NOTIFICATION_EMAIL', '')
    ERROR_NOTIFICATION_EMAILS = [email.strip() for email in _error_emails.split(',') if email.strip()]
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        errors = []

        # ... existing validations ...

        # Validate error notification emails
        if cls.ERROR_NOTIFICATION_EMAILS:
            invalid_emails = [e for e in cls.ERROR_NOTIFICATION_EMAILS
                            if not cls.EMAIL_REGEX.match(e)]
            if invalid_emails:
                errors.append(f"Invalid error notification email addresses: {', '.join(invalid_emails)}")

        # ... rest of validation ...
```

**Test Cases Needed**:
- Valid single email
- Valid multiple emails (comma-separated)
- Invalid email format
- Empty email list
- Emails with spaces

---

## Priority 2: Should Fix (Testing & Documentation)

### 📝 3. Add Unit Tests for NotificationService
**File**: New file `tests/test_notification_service.py`
**Status**: ✅ Completed (2025-11-12)
**Priority**: MEDIUM
**Estimated Effort**: 2 hours

**Test Coverage Needed**:
- ✅ Send notification without attachment
- ✅ Send notification with attachment
- ✅ Handle missing configuration (no emails configured)
- ✅ Handle Gmail API errors
- ✅ Verify email formatting (MIME structure)
- ✅ Verify base64 encoding of attachments
- ✅ Test multiple recipients

**Example Test Structure**:
```python
import pytest
from unittest.mock import Mock, patch
from src.services.notification_service import NotificationService

class TestNotificationService:
    def test_send_notification_without_attachment(self):
        # Test basic notification sending
        pass

    def test_send_notification_with_attachment(self):
        # Test attachment encoding and inclusion
        pass

    def test_no_emails_configured(self):
        # Verify graceful handling when no emails set
        pass

    def test_gmail_api_error_handling(self):
        # Test error handling for API failures
        pass
```

---

### 📝 4. Improve Error Context in Messages
**File**: `src/email_processor.py:104-110`
**Status**: ✅ Completed (2025-11-12)
**Priority**: MEDIUM
**Estimated Effort**: 1 hour

**Issue**: Generic error messages don't include underlying cause or HTTP status codes.

**Implementation**:
```python
# In gmail_service.py - modify download_attachment method
def download_attachment(self, message_id: str, attachment_id: str) -> Optional[bytes]:
    try:
        attachment = self.service.users().messages().attachments().get(
            userId='me',
            messageId=message_id,
            id=attachment_id
        ).execute()

        data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
        return data

    except HttpError as error:
        logger.error(f"Error downloading attachment: {error.status_code} - {error.reason}")
        raise  # Re-raise to allow caller to handle
    except Exception as error:
        logger.error(f"Unexpected error downloading attachment: {error}")
        raise

# In email_processor.py - update error handling
try:
    csv_data = self.gmail.download_attachment(
        message_id,
        csv_attachment['attachment_id']
    )
except Exception as e:
    error_msg = f"Failed to download CSV attachment: {str(e)}"
    logger.error(error_msg)
    self.notification.send_error_notification(
        error_message=error_msg,
        email_id=message_id,
        attachment_filename=csv_attachment['filename']
    )
    self._save_processed_email(message_id)
    continue
```

---

### 📝 5. Document Re-authentication Requirement
**Files**: `README.md`, `SETUP_GUIDE.md`
**Status**: ✅ Completed (2025-11-12)
**Priority**: MEDIUM
**Estimated Effort**: 15 minutes

**Issue**: Scope change from `gmail.readonly` to `gmail.modify` requires users to re-authenticate.

**Add to SETUP_GUIDE.md**:
```markdown
## Upgrading from Previous Versions

### Gmail API Scope Change
If you're upgrading from a version that used `gmail.readonly` scope:

1. Delete your existing token file:
   ```bash
   rm token.json
   ```

2. Run the service to trigger re-authentication:
   ```bash
   python main.py
   ```

3. Complete the OAuth flow in your browser with the new permissions

**Why?** The service now requires `gmail.modify` scope to:
- Mark processed emails as read
- Send error notification emails from your account
```

---

## Priority 3: Nice to Have (Enhancements)

### 💡 6. Add Rate Limiting for Error Notifications
**File**: `src/services/notification_service.py`
**Status**: ⏳ Pending
**Priority**: LOW
**Estimated Effort**: 2 hours

**Rationale**: Prevent notification spam if many errors occur in rapid succession.

**Implementation Approach**:
```python
from datetime import datetime, timedelta
from collections import deque

class NotificationService:
    def __init__(self, gmail_service):
        self.gmail_service = gmail_service
        self.notification_emails = Config.ERROR_NOTIFICATION_EMAILS

        # Rate limiting: max 5 notifications per 5 minutes
        self.notification_times = deque(maxlen=5)
        self.rate_limit_window = timedelta(minutes=5)

    def _should_send_notification(self) -> bool:
        """Check if we're within rate limits."""
        now = datetime.now()

        # Remove old timestamps outside the window
        while self.notification_times and \
              now - self.notification_times[0] > self.rate_limit_window:
            self.notification_times.popleft()

        # Check if we've hit the limit
        if len(self.notification_times) >= 5:
            logger.warning("Rate limit reached for error notifications")
            return False

        return True

    def send_error_notification(self, ...):
        if not self._should_send_notification():
            logger.warning("Skipping notification due to rate limiting")
            return False

        # ... existing send logic ...

        # Track successful send
        self.notification_times.append(datetime.now())
```

---

### 💡 7. Make Notification Email Templates Configurable
**Files**: `src/config.py`, `src/services/notification_service.py`
**Status**: ⏳ Pending
**Priority**: LOW
**Estimated Effort**: 1 hour

**Enhancement**: Allow customization of notification subject and body via environment variables.

**Implementation**:
```python
# In config.py
ERROR_NOTIFICATION_SUBJECT = os.getenv(
    'ERROR_NOTIFICATION_SUBJECT',
    'FIC Printing Service Error - Email ID: {email_id}'
)

ERROR_NOTIFICATION_BODY_TEMPLATE = os.getenv(
    'ERROR_NOTIFICATION_BODY_TEMPLATE',
    '''An error occurred while processing an email in the FIC Printing Service.

Error Details:
--------------
{error_message}

Email ID: {email_id}

The problematic email attachment is included with this notification (if available).

---
This is an automated notification from the FIC Printing Service.'''
)

# In notification_service.py
message['subject'] = Config.ERROR_NOTIFICATION_SUBJECT.format(email_id=email_id)
body = Config.ERROR_NOTIFICATION_BODY_TEMPLATE.format(
    error_message=error_message,
    email_id=email_id
)
```

---

### 💡 8. Implement Async Notification Sending
**File**: `src/services/notification_service.py`, `src/email_processor.py`
**Status**: ⏳ Pending
**Priority**: LOW
**Estimated Effort**: 3 hours

**Rationale**: Improve performance by not blocking email processing while sending notifications.

**Implementation Approach**:
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class EmailProcessor:
    def __init__(self):
        # ... existing init ...
        self.notification_executor = ThreadPoolExecutor(max_workers=2)

    def _send_notification_async(self, error_message, email_id, **kwargs):
        """Send notification asynchronously without blocking."""
        self.notification_executor.submit(
            self.notification.send_error_notification,
            error_message=error_message,
            email_id=email_id,
            **kwargs
        )

    def process_emails(self):
        # Replace synchronous calls with async:
        # self.notification.send_error_notification(...)
        # with:
        self._send_notification_async(...)
```

**Trade-offs**:
- ✅ Pro: Better performance for email processing
- ✅ Pro: Non-blocking for high error scenarios
- ❌ Con: Harder to test
- ❌ Con: Less immediate feedback on notification failures

---

## Future Enhancements (Not from Code Review)

### 🚀 9. Add Retry Logic for Print Failures
**Status**: 💡 Idea
**Priority**: LOW

Consider implementing retry logic for transient print failures (network issues, printer offline).

---

### 🚀 10. Add Metrics/Dashboard
**Status**: 💡 Idea
**Priority**: LOW

Track and visualize:
- Emails processed per day
- Print success rate
- Error types and frequency
- Processing time metrics

---

### 🚀 11. Support Multiple Printers
**Status**: 💡 Idea
**Priority**: LOW

Allow configuration of multiple printers with routing rules based on email content or sender.

---

## Completed Items

✅ **Filename sanitization in notification_service.py** - Completed 2025-11-12
✅ **Email address validation in config.py** - Completed 2025-11-12
✅ **Unit tests for NotificationService** - Completed 2025-11-12 (11 tests, all passing)
✅ **Improved error context with HTTP status codes** - Completed 2025-11-12
✅ **Re-authentication documentation** - Completed 2025-11-12
✅ **Gmail API scope upgrade** - Completed in commit 84e1380
✅ **Partial subject matching** - Completed in commit 0d73184
✅ **Mark emails as read** - Completed in commit 0d73184
✅ **Error notification system** - Completed in commit 84e1380
✅ **Add stephen@sugarbearpro.com to recipients** - Completed in commit b920a5e

---

## Notes

- Priority levels: 🔴 CRITICAL | 🟡 HIGH | 📝 MEDIUM | 💡 LOW | 🚀 FUTURE
- Status indicators: ⏳ Pending | 🔄 In Progress | ✅ Completed | ❌ Blocked
- When starting a task, update status to 🔄 In Progress
- When completing a task, update status to ✅ Completed and move to "Completed Items" section

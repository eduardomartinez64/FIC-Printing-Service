# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gmail Email Processor Service - An automated service that:
1. Scans Gmail inbox every minute for **unread** emails with subject **containing** "Batch Order Shipment Report"
2. Extracts CSV attachments from matching emails
3. Parses PDF links from column C (last row) of the CSV
4. Automatically prints PDFs to remote printer via PrintNode API
5. Marks processed emails as read to prevent reprocessing

## Architecture

### Core Components

- **EmailProcessor** (`src/email_processor.py`) - Main orchestrator that coordinates all services
- **GmailService** (`src/services/gmail_service.py`) - Handles Gmail API authentication, email search, and attachment download
- **CSVParser** (`src/services/csv_parser.py`) - Extracts PDF links from CSV column C (last row)
- **PrintNodeService** (`src/services/printnode_service.py`) - Manages PrintNode API integration for remote printing
- **Config** (`src/config.py`) - Centralized configuration management using environment variables

### Key Design Patterns

- Service-oriented architecture with separate concerns
- Processed emails tracking to prevent duplicate processing (stored in `processed_emails.txt`)
- Comprehensive logging for all operations
- Graceful shutdown handling with signal handlers
- Scheduled execution using `schedule` library

## Development Commands

### Setup Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials:
# - PRINTNODE_API_KEY
# - PRINTNODE_PRINTER_ID
# - EMAIL_SUBJECT_FILTER (default: "Batch Order Shipment Report")
# - CHECK_INTERVAL_SECONDS (default: 60)
```

### Running the Service
```bash
# Run service (requires credentials.json for Gmail API)
python main.py

# Stop with Ctrl+C (graceful shutdown)
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_filename.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src tests/
```

### Monitoring Logs
```bash
# Real-time log monitoring
tail -f logs/email_processor.log

# View all logs
cat logs/email_processor.log
```

## Important Implementation Details

### Gmail API Authentication
- Uses OAuth2 flow (requires `credentials.json` from Google Cloud Console)
- Token cached in `token.json` after first authentication
- Automatically refreshes expired tokens

### Email Processing Flow
1. Search for unread emails with subject containing the filter text (partial match)
2. Skip already processed emails (tracked by message ID)
3. Download CSV attachments (filters for .csv extension)
4. Parse column C last row for PDF URL
5. Download and print PDF via PrintNode
6. Mark email as processed (saves ID to `processed_emails.txt`)
7. Mark email as read in Gmail

### CSV Parsing Logic
- Converts column letter (e.g., 'C') to zero-based index (2)
- Reads last row using pandas: `df.iloc[-1][column_name]`
- Validates URL format (must start with http:// or https://)
- Handles empty cells and missing columns gracefully

### PrintNode Integration
- Base64 encodes PDF content for API submission
- Submits print jobs with contentType: "pdf_base64"
- Returns job ID for tracking
- Includes printer verification on startup

## File References

- Main entry: `main.py:1`
- Service orchestrator: `src/email_processor.py:1`
- Gmail integration: `src/services/gmail_service.py:1`
- CSV parsing: `src/services/csv_parser.py:1`
- PrintNode API: `src/services/printnode_service.py:1`
- Configuration: `src/config.py:1`
- Logging setup: `src/utils/logger.py:1`

## Common Tasks

### Adding New CSV Column Support
Modify `src/services/csv_parser.py:20` - change column parameter in `extract_pdf_link()` method

### Changing Email Subject Filter
Update `.env` file: `EMAIL_SUBJECT_FILTER=New Subject Text`

### Adjusting Scan Interval
Update `.env` file: `CHECK_INTERVAL_SECONDS=120` (for 2 minutes)

### Debugging Print Issues
1. Check PrintNode connection: `PrintNodeService.test_connection()`
2. List available printers: `PrintNodeService.get_printers()`
3. Verify printer ID matches configuration

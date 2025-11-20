# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains two main tools for Sugar Bear's FIC (FedEx International Connect) operations:

### 1. Gmail Email Processor Service
An automated service that:
1. Scans Gmail inbox every minute for **unread** emails with subject **containing** "Batch Order Shipment Report"
2. Extracts CSV attachments from matching emails
3. Parses PDF links from column C (last row) of the CSV
4. Automatically prints PDFs to remote printer via PrintNode API
5. Marks processed emails as read to prevent reprocessing

### 2. Shopify Shipping Export Tool
A standalone tool that:
1. Connects to Shopify Admin API to fetch all shipping data
2. Exports 200+ shipping zones, rates, countries, and carrier services
3. Creates formatted Excel file with multiple analysis sheets
4. Helps identify consolidation opportunities and duplicate zones
5. Provides comprehensive documentation for zone restructuring

## Architecture

### Core Components

#### Email Processor Service
- **EmailProcessor** (`src/email_processor.py`) - Main orchestrator that coordinates all services
- **GmailService** (`src/services/gmail_service.py`) - Handles Gmail API authentication, email search, and attachment download
- **NotificationService** (`src/services/notification_service.py`) - Sends error notifications with attachments
- **CSVParser** (`src/services/csv_parser.py`) - Extracts PDF links from CSV column C (last row)
- **PrintNodeService** (`src/services/printnode_service.py`) - Manages PrintNode API integration for remote printing

#### Shopify Export Tool
- **ShopifyService** (`src/services/shopify_service.py`) - Shopify Admin API integration for fetching shipping data
- **ShippingExporter** (`src/exporters/shipping_exporter.py`) - Excel formatting and export logic with multiple sheets

#### Shared Components
- **Config** (`src/config.py`) - Centralized configuration management using environment variables
- **Logger** (`src/utils/logger.py`) - Logging setup for all services

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
# Email Processor Service:
# - PRINTNODE_API_KEY
# - PRINTNODE_PRINTER_ID
# - EMAIL_SUBJECT_FILTER (default: "Batch Order Shipment Report")
# - CHECK_INTERVAL_SECONDS (default: 60)
# - ERROR_NOTIFICATION_EMAIL (comma-separated emails)

# Shopify Export Tool:
# - SHOPIFY_STORE_URL (your-store.myshopify.com)
# - SHOPIFY_ACCESS_TOKEN (shpat_...)
# - SHOPIFY_API_VERSION (default: 2024-10)
# - EXPORT_OUTPUT_DIR (default: exports)
```

### Running the Services

#### Email Processor Service
```bash
# Run email processor (requires credentials.json for Gmail API)
python main.py

# Stop with Ctrl+C (graceful shutdown)
```

#### Shopify Export Tool
```bash
# Export Shopify shipping data to Excel
python export_shopify_shipping.py

# Output: exports/shopify_shipping_export_YYYYMMDD_HHMMSS.xlsx
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

### Email Processor Service
- Main entry: `main.py:1`
- Service orchestrator: `src/email_processor.py:1`
- Gmail integration: `src/services/gmail_service.py:1`
- Error notifications: `src/services/notification_service.py:1`
- CSV parsing: `src/services/csv_parser.py:1`
- PrintNode API: `src/services/printnode_service.py:1`

### Shopify Export Tool
- Main export script: `export_shopify_shipping.py:1`
- Shopify API integration: `src/services/shopify_service.py:1`
- Excel exporter: `src/exporters/shipping_exporter.py:1`

### Shared Components
- Configuration: `src/config.py:1`
- Logging setup: `src/utils/logger.py:1`

## Project Documentation

- **CODE_REVIEW.md** - Latest code review findings and security analysis
- **TODO.md** - Task tracking for improvements and enhancements
- **SETUP_GUIDE.md** - Detailed setup and deployment instructions (Email Processor)
- **SHOPIFY_EXPORT_GUIDE.md** - Complete guide for Shopify shipping export tool (15+ pages)

## Common Tasks

### Email Processor Service

#### Adding New CSV Column Support
Modify `src/services/csv_parser.py:20` - change column parameter in `extract_pdf_link()` method

#### Changing Email Subject Filter
Update `.env` file: `EMAIL_SUBJECT_FILTER=New Subject Text`

#### Adjusting Scan Interval
Update `.env` file: `CHECK_INTERVAL_SECONDS=120` (for 2 minutes)

#### Debugging Print Issues
1. Check PrintNode connection: `PrintNodeService.test_connection()`
2. List available printers: `PrintNodeService.get_printers()`
3. Verify printer ID matches configuration

### Shopify Export Tool

#### Running an Export
```bash
python export_shopify_shipping.py
```
Output: `exports/shopify_shipping_export_YYYYMMDD_HHMMSS.xlsx`

#### Setting Up Shopify API Access
1. Go to Shopify Admin → Settings → Apps → Develop apps
2. Create custom app with `read_shipping` scope
3. Copy access token (starts with `shpat_`)
4. Add to `.env` file as `SHOPIFY_ACCESS_TOKEN`
5. See [SHOPIFY_EXPORT_GUIDE.md](SHOPIFY_EXPORT_GUIDE.md) for detailed setup

#### Analyzing Export Data
1. Open Excel file from `exports/` directory
2. Review "Overview" sheet for summary statistics
3. Use "Zones" sheet to find zones with similar rate counts
4. Use "Rates" sheet to compare pricing structures
5. Use "Countries" sheet for geographic analysis
6. See [SHOPIFY_EXPORT_GUIDE.md](SHOPIFY_EXPORT_GUIDE.md) for analysis strategies

#### Troubleshooting Export Issues
- Connection failed: Verify `SHOPIFY_STORE_URL` and `SHOPIFY_ACCESS_TOKEN`
- Permission denied: Ensure custom app has `read_shipping` scope
- Rate limiting: Normal for 200+ zones, tool handles automatically
- See [SHOPIFY_EXPORT_GUIDE.md](SHOPIFY_EXPORT_GUIDE.md) troubleshooting section

## Code Review & Quality Assurance

### Recent Code Review (2025-11-12)
A comprehensive code review was performed covering commits d73a75f through b920a5e. Key findings:

**Security Issues Identified:**
1. **CRITICAL**: Filename sanitization needed in notification service to prevent header injection
2. **HIGH**: Email address validation missing in configuration

**Features Added:**
- Error notification system with attachment forwarding
- Partial subject matching for more flexible email filtering
- Automatic marking of processed emails as read
- Gmail API scope upgraded to `gmail.modify`

**Overall Assessment**: ⭐⭐⭐⭐☆ (4/5)
- Well-implemented following project conventions
- Good error handling and logging
- Security issues require attention before production

**Action Items**: See [TODO.md](TODO.md) for prioritized task list with implementation details.

### Code Review Process
When reviewing code changes:
1. Use `/review` command or examine git diffs directly
2. Focus on security, performance, testing, and documentation
3. Document findings in [CODE_REVIEW.md](CODE_REVIEW.md)
4. Create actionable tasks in [TODO.md](TODO.md) with:
   - Priority levels (Critical, High, Medium, Low)
   - Estimated effort
   - Implementation examples
   - Test cases needed

### Known Issues & Improvements
See [TODO.md](TODO.md) for current task tracking including:
- **Priority 1**: Security fixes (filename sanitization, email validation)
- **Priority 2**: Testing and documentation improvements
- **Priority 3**: Performance enhancements (rate limiting, async notifications)

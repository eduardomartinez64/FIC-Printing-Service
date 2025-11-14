# FIC Printing Service

Automated service that scans Gmail inbox for **unread** emails with subject containing "Batch Order Shipment Report", extracts PDF links from CSV attachments (column C, last row), and prints them to a remote printer via PrintNode.

## Features

- Scans Gmail inbox every minute for unread emails containing specific subject text
- Extracts CSV attachments from matching emails
- Parses PDF links from column C (last row) in CSV files
- Automatically prints PDFs to remote PrintNode printer
- Comprehensive logging of all processing attempts
- Tracks processed emails to avoid duplicates
- Marks processed emails as read
- Graceful shutdown handling
- Print history tracking with statistics and CSV export
- Automated daily email reports with print statistics (weekdays at 6 PM EST)

## Prerequisites

- Python 3.8 or higher
- Gmail account with API access
- PrintNode account with API key
- Remote printer configured in PrintNode

## Setup

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable Gmail API for your project
4. Create OAuth 2.0 credentials (Desktop application)
5. Download credentials and save as `credentials.json` in project root
6. On first run, you'll be prompted to authorize the application

### 3. Configure PrintNode

1. Sign up at [PrintNode](https://www.printnode.com/)
2. Get your API key from account settings
3. Note your printer ID (you can list printers using the service)

### 4. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:

```
PRINTNODE_API_KEY=your_actual_api_key
PRINTNODE_PRINTER_ID=your_printer_id
EMAIL_SUBJECT_FILTER=Batch Order Shipment Report
CHECK_INTERVAL_SECONDS=60
LOG_LEVEL=INFO
ERROR_NOTIFICATION_EMAIL=your_email@example.com
DAILY_REPORT_EMAIL=your_email@example.com
DAILY_REPORT_TIME=18:00  # 6 PM EST
```

## Usage

### Run the Service

```bash
python main.py
```

The service will:
1. Verify configuration and connections
2. Run an initial email scan
3. Continue scanning every minute
4. Log all activity to `logs/email_processor.log`
5. Send automated daily reports (if configured) at 6 PM EST on weekdays

### Stop the Service

Press `Ctrl+C` for graceful shutdown

### Run as Background Service (Linux)

Using systemd:

```bash
sudo cp fic-printing-service.service /etc/systemd/system/
sudo systemctl enable fic-printing-service
sudo systemctl start fic-printing-service
sudo systemctl status fic-printing-service
```

### View Logs

```bash
# Real-time monitoring
tail -f logs/email_processor.log

# View all logs
cat logs/email_processor.log
```

### Print History and Reports

View print history and statistics:

```bash
# Show statistics
python print_history.py stats

# List recent print jobs
python print_history.py list --limit 20

# List failed prints only
python print_history.py list --status failed

# Export to CSV
python print_history.py export --output reports/my_report.csv
```

Test daily report (sends actual email):

```bash
python test_daily_report.py
```

See [PRINT_HISTORY_GUIDE.md](PRINT_HISTORY_GUIDE.md) for detailed documentation.

## Testing

Run tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=src tests/
```

## Project Structure

```
FIC-Printing-Service/
├── main.py                          # Service entry point
├── credentials.json                 # Gmail API credentials (not in repo)
├── token.json                       # Gmail OAuth token (auto-generated)
├── processed_emails.txt             # Tracking file (auto-generated)
├── .env                            # Environment config (not in repo)
├── requirements.txt                # Python dependencies
├── logs/                           # Log files
│   └── email_processor.log
├── src/
│   ├── config.py                   # Configuration management
│   ├── email_processor.py          # Main orchestrator
│   ├── services/
│   │   ├── gmail_service.py        # Gmail API integration
│   │   ├── csv_parser.py           # CSV parsing logic
│   │   └── printnode_service.py    # PrintNode integration
│   └── utils/
│       └── logger.py               # Logging configuration
└── tests/                          # Test files
```

## Troubleshooting

### Gmail Authentication Issues

- **Upgrading?** If you previously used an older version with `gmail.readonly` scope, delete `token.json` and re-authenticate to grant the new `gmail.modify` permissions (required for marking emails as read and sending error notifications)
- Delete `token.json` and re-authenticate if having auth issues
- Ensure Gmail API is enabled in Google Cloud Console
- Check that `credentials.json` is valid

### PrintNode Connection Failed

- Verify API key is correct
- Check printer ID exists: use `get_printers()` method
- Ensure printer is online in PrintNode dashboard

### No Emails Found

- Check email subject filter matches exactly
- Verify emails have CSV attachments
- Check Gmail API quota limits

### CSV Parsing Errors

- Ensure CSV has at least 3 columns (A, B, C)
- Verify column C in last row contains a valid URL
- Check CSV encoding is UTF-8

## Security Notes

- Never commit `credentials.json`, `token.json`, or `.env` files
- Keep PrintNode API key secure
- Use environment variables for sensitive data
- Regularly rotate API keys

## License

MIT License

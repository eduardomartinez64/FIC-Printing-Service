# Print History Guide

The FIC Printing Service now includes comprehensive print history tracking and reporting.

## Features

- **Automatic Tracking**: Every print job (successful or failed) is automatically logged
- **Detailed Records**: Tracks timestamp, email ID, CSV filename, PDF URL, size, and PrintNode job ID
- **Statistics**: View summary statistics of all printing activity
- **CSV Export**: Export complete history to CSV for analysis in Excel or other tools
- **Filtering**: Filter by success/failure status

## Files Created

- `print_history.json` - JSON database of all print records
- `reports/` - Directory where CSV exports are saved

## Using the Print History Utility

### View Statistics

Show overall statistics about printing activity:

```bash
python print_history.py stats
```

Output:
```
============================================================
 Print History Statistics
============================================================
Total Prints:       25
Successful Prints:  23 (92.0%)
Failed Prints:      2 (8.0%)
Total PDF Size:     45.6 MB

Earliest Print:     2025-11-13 09:15:30
Latest Print:       2025-11-13 21:05:42
============================================================
```

### List Print History

List all print jobs in a formatted table:

```bash
python print_history.py list
```

List only the last 10 prints:

```bash
python print_history.py list --limit 10
```

List only successful prints:

```bash
python print_history.py list --status success
```

List only failed prints:

```bash
python print_history.py list --status failed
```

Output in JSON format:

```bash
python print_history.py list --format json
```

### Export to CSV

Export complete history to CSV:

```bash
python print_history.py export
```

Export to a specific file:

```bash
python print_history.py export --output reports/my_report.csv
```

Export only successful prints:

```bash
python print_history.py export --status success
```

Export only failed prints:

```bash
python print_history.py export --status failed --output reports/failures.csv
```

## Print Record Fields

Each print record contains:

| Field | Description |
|-------|-------------|
| `timestamp` | ISO 8601 timestamp when print was submitted |
| `email_id` | Gmail message ID that triggered the print |
| `csv_filename` | Name of the CSV attachment |
| `pdf_url` | URL of the PDF that was printed |
| `pdf_size_bytes` | Size of PDF in bytes |
| `printnode_job_id` | PrintNode job ID (0 for failed prints) |
| `status` | `success` or `failed` |
| `error_message` | Error details (only for failed prints) |

## Example CSV Export

The exported CSV can be opened in Excel or Google Sheets:

```csv
timestamp,email_id,csv_filename,pdf_url,pdf_size_bytes,printnode_job_id,status,error_message
2025-11-13T13:25:53.123456,193f8e6a5ca80ed0,shipment_report.csv,https://example.com/doc.pdf,186676,7359023115,success,
2025-11-13T14:30:12.654321,194a9f7b6db91fe1,order_batch.csv,https://example.com/doc2.pdf,245123,7359023116,success,
2025-11-13T15:45:33.987654,195b0g8c7ec02gf2,failed_order.csv,https://example.com/bad.pdf,0,0,failed,Error downloading PDF from URL
```

## Querying History Programmatically

You can also use the Python API directly:

```python
from src.services.print_history import PrintHistoryService

# Initialize service
history = PrintHistoryService()

# Get last 20 records
records = history.get_history(limit=20)

# Get only failed prints
failed = history.get_history(status_filter='failed')

# Get statistics
stats = history.get_statistics()
print(f"Success rate: {stats['successful_prints'] / stats['total_prints'] * 100:.1f}%")

# Export to CSV
csv_path = history.export_to_csv(output_file='my_report.csv')
```

## Integration with Monitoring Tools

The JSON format makes it easy to integrate with monitoring tools:

```bash
# Get failed prints count in last hour (requires jq)
python print_history.py list --format json | \
  jq '[.[] | select(.status=="failed" and (.timestamp | fromdateiso8601) > (now - 3600))] | length'

# Get total MB printed today
python print_history.py list --format json | \
  jq '[.[] | select(.timestamp | startswith("2025-11-13"))] |
      map(.pdf_size_bytes) | add / 1048576'
```

## Maintenance

### Backup Print History

```bash
# Backup the JSON file
cp print_history.json print_history_backup_$(date +%Y%m%d).json

# Or export to CSV for archival
python print_history.py export --output archives/history_$(date +%Y%m%d).csv
```

### Clear Old Records

If you need to archive and clear old records, you can manually edit `print_history.json` or write a script to filter by date.

## Troubleshooting

### No history showing

If no history shows up, check that:
1. The service has successfully printed at least one PDF
2. The `print_history.json` file exists in the project root
3. You're running the command from the project directory

### Export fails

Make sure the `reports/` directory exists:

```bash
mkdir -p reports
```

## See Also

- [README.md](README.md) - Main project documentation
- [logs/email_processor.log](logs/email_processor.log) - Detailed service logs
- [processed_emails.txt](processed_emails.txt) - List of processed email IDs

#!/usr/bin/env python3
"""Print history query and export utility."""

import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.print_history import PrintHistoryService


def main():
    """Main entry point for print history utility."""
    parser = argparse.ArgumentParser(
        description='Query and export FIC Printing Service print history'
    )

    parser.add_argument(
        'command',
        choices=['list', 'stats', 'export'],
        help='Command to execute'
    )

    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of records (for list command)'
    )

    parser.add_argument(
        '--status',
        choices=['success', 'failed'],
        help='Filter by status'
    )

    parser.add_argument(
        '--output',
        '-o',
        type=Path,
        help='Output file path (for export command)'
    )

    parser.add_argument(
        '--format',
        choices=['table', 'json'],
        default='table',
        help='Output format for list command'
    )

    args = parser.parse_args()

    # Initialize service
    history_service = PrintHistoryService()

    if args.command == 'list':
        list_history(history_service, args)
    elif args.command == 'stats':
        show_statistics(history_service)
    elif args.command == 'export':
        export_history(history_service, args)


def list_history(service: PrintHistoryService, args):
    """List print history."""
    history = service.get_history(
        limit=args.limit,
        status_filter=args.status
    )

    if not history:
        print("No print history found")
        return

    if args.format == 'json':
        import json
        print(json.dumps(history, indent=2))
    else:
        # Table format
        print("\n" + "=" * 120)
        print(f"{'Timestamp':<20} {'Status':<10} {'Job ID':<12} {'PDF Size':<12} {'CSV Filename':<30}")
        print("=" * 120)

        for record in history:
            timestamp = record.get('timestamp', '')[:19]  # Trim microseconds
            status = record.get('status', 'unknown')
            job_id = str(record.get('printnode_job_id', 'N/A'))
            size_bytes = record.get('pdf_size_bytes', 0)
            size_kb = round(size_bytes / 1024, 1) if size_bytes else 0
            csv_file = record.get('csv_filename', 'N/A')[:30]

            # Color code status
            if status == 'success':
                status_display = f"\033[92m{status}\033[0m"  # Green
            else:
                status_display = f"\033[91m{status}\033[0m"  # Red

            print(f"{timestamp:<20} {status_display:<19} {job_id:<12} {size_kb:<11} KB {csv_file:<30}")

            # Show PDF URL on next line
            pdf_url = record.get('pdf_url', '')
            if pdf_url:
                print(f"  → {pdf_url}")

            # Show error message if failed
            error_msg = record.get('error_message')
            if error_msg:
                print(f"  ✗ Error: {error_msg}")

            print()

        print("=" * 120)
        print(f"Total records: {len(history)}\n")


def show_statistics(service: PrintHistoryService):
    """Show print statistics."""
    stats = service.get_statistics()

    print("\n" + "=" * 60)
    print(" Print History Statistics")
    print("=" * 60)
    print(f"Total Prints:       {stats['total_prints']}")
    print(f"Successful Prints:  {stats['successful_prints']} ({_calc_percentage(stats['successful_prints'], stats['total_prints'])}%)")
    print(f"Failed Prints:      {stats['failed_prints']} ({_calc_percentage(stats['failed_prints'], stats['total_prints'])}%)")
    print(f"Total PDF Size:     {stats['total_pdf_size_mb']} MB")
    print()
    print(f"Earliest Print:     {_format_timestamp(stats['earliest_print'])}")
    print(f"Latest Print:       {_format_timestamp(stats['latest_print'])}")
    print("=" * 60 + "\n")


def export_history(service: PrintHistoryService, args):
    """Export print history to CSV."""
    output_path = service.export_to_csv(
        output_file=args.output,
        status_filter=args.status
    )

    print(f"\n✓ Print history exported to: {output_path}\n")


def _calc_percentage(part: int, total: int) -> str:
    """Calculate percentage as string."""
    if total == 0:
        return "0.0"
    return f"{(part / total * 100):.1f}"


def _format_timestamp(timestamp: str) -> str:
    """Format ISO timestamp for display."""
    if not timestamp:
        return "N/A"
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return timestamp


if __name__ == '__main__':
    main()

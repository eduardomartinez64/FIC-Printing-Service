"""Print history tracking service."""

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

from src.config import Config

logger = logging.getLogger(__name__)


@dataclass
class PrintRecord:
    """Record of a print job."""
    timestamp: str
    email_id: str
    csv_filename: str
    pdf_url: str
    pdf_size_bytes: int
    printnode_job_id: int
    status: str  # 'success' or 'failed'
    error_message: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


class PrintHistoryService:
    """Service for tracking and reporting print history."""

    def __init__(self):
        """Initialize print history service."""
        self.history_file = Config.BASE_DIR / "print_history.json"
        self.csv_export_dir = Config.BASE_DIR / "reports"
        self.csv_export_dir.mkdir(exist_ok=True)

    def log_print_job(
        self,
        email_id: str,
        csv_filename: str,
        pdf_url: str,
        pdf_size_bytes: int,
        printnode_job_id: int,
        status: str = 'success',
        error_message: Optional[str] = None
    ) -> None:
        """
        Log a print job to history.

        Args:
            email_id: Gmail message ID
            csv_filename: Name of CSV attachment
            pdf_url: URL of printed PDF
            pdf_size_bytes: Size of PDF in bytes
            printnode_job_id: PrintNode job ID
            status: 'success' or 'failed'
            error_message: Error message if failed
        """
        try:
            record = PrintRecord(
                timestamp=datetime.now().isoformat(),
                email_id=email_id,
                csv_filename=csv_filename,
                pdf_url=pdf_url,
                pdf_size_bytes=pdf_size_bytes,
                printnode_job_id=printnode_job_id,
                status=status,
                error_message=error_message
            )

            # Load existing history
            history = self._load_history()

            # Append new record
            history.append(record.to_dict())

            # Save updated history
            self._save_history(history)

            logger.debug(f"Logged print job: {printnode_job_id} for {pdf_url}")

        except Exception as e:
            logger.error(f"Failed to log print job to history: {e}")

    def get_history(
        self,
        limit: Optional[int] = None,
        status_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Get print history.

        Args:
            limit: Maximum number of records to return (most recent first)
            status_filter: Filter by status ('success' or 'failed')

        Returns:
            List of print records
        """
        history = self._load_history()

        # Filter by status if requested
        if status_filter:
            history = [r for r in history if r.get('status') == status_filter]

        # Sort by timestamp (most recent first)
        history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        # Apply limit if specified
        if limit:
            history = history[:limit]

        return history

    def export_to_csv(
        self,
        output_file: Optional[Path] = None,
        status_filter: Optional[str] = None
    ) -> Path:
        """
        Export print history to CSV file.

        Args:
            output_file: Output file path (default: reports/print_history_YYYYMMDD.csv)
            status_filter: Filter by status ('success' or 'failed')

        Returns:
            Path to created CSV file
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.csv_export_dir / f"print_history_{timestamp}.csv"

        history = self.get_history(status_filter=status_filter)

        if not history:
            logger.warning("No print history to export")
            return output_file

        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if history:
                fieldnames = history[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(history)

        logger.info(f"Exported {len(history)} print records to {output_file}")
        return output_file

    def get_statistics(self) -> Dict:
        """
        Get print statistics.

        Returns:
            Dictionary with statistics
        """
        history = self._load_history()

        if not history:
            return {
                'total_prints': 0,
                'successful_prints': 0,
                'failed_prints': 0,
                'total_pdf_size_mb': 0.0,
                'earliest_print': None,
                'latest_print': None
            }

        successful = [r for r in history if r.get('status') == 'success']
        failed = [r for r in history if r.get('status') == 'failed']

        total_size_bytes = sum(r.get('pdf_size_bytes', 0) for r in history)
        total_size_mb = total_size_bytes / (1024 * 1024)

        timestamps = [r.get('timestamp') for r in history if r.get('timestamp')]
        timestamps.sort()

        return {
            'total_prints': len(history),
            'successful_prints': len(successful),
            'failed_prints': len(failed),
            'total_pdf_size_mb': round(total_size_mb, 2),
            'earliest_print': timestamps[0] if timestamps else None,
            'latest_print': timestamps[-1] if timestamps else None
        }

    def _load_history(self) -> List[Dict]:
        """Load print history from file."""
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load print history: {e}")
            return []

    def _save_history(self, history: List[Dict]) -> None:
        """Save print history to file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save print history: {e}")

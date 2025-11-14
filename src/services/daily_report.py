"""Daily statistics report service."""

import logging
from datetime import datetime, timedelta
from typing import List, Dict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

from googleapiclient.errors import HttpError

from src.services.print_history import PrintHistoryService

logger = logging.getLogger(__name__)


class DailyReportService:
    """Service for generating and sending daily print statistics reports."""

    def __init__(self, gmail_service, recipient_email: str):
        """
        Initialize daily report service.

        Args:
            gmail_service: Authenticated GmailService instance
            recipient_email: Email address to send reports to
        """
        self.gmail_service = gmail_service
        self.recipient_email = recipient_email
        self.print_history = PrintHistoryService()

    def send_daily_report(self) -> bool:
        """
        Send daily statistics report email.

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Get today's date range
            today = datetime.now().date()
            start_time = datetime.combine(today, datetime.min.time()).isoformat()
            end_time = datetime.now().isoformat()

            # Get all history and filter for today
            all_history = self.print_history.get_history()
            today_history = [
                r for r in all_history
                if r.get('timestamp', '').startswith(str(today))
            ]

            # Get overall statistics
            overall_stats = self.print_history.get_statistics()

            # Generate report HTML
            report_html = self._generate_report_html(
                today_history,
                overall_stats,
                today
            )

            # Send email
            return self._send_email(report_html, today)

        except Exception as e:
            logger.error(f"Failed to send daily report: {e}", exc_info=True)
            return False

    def _generate_report_html(
        self,
        today_history: List[Dict],
        overall_stats: Dict,
        report_date: datetime.date
    ) -> str:
        """Generate HTML report content."""

        # Calculate today's stats
        today_successful = sum(1 for r in today_history if r.get('status') == 'success')
        today_failed = sum(1 for r in today_history if r.get('status') == 'failed')
        today_total = len(today_history)

        today_size_bytes = sum(r.get('pdf_size_bytes', 0) for r in today_history)
        today_size_mb = round(today_size_bytes / (1024 * 1024), 2)

        # Calculate success rate
        if today_total > 0:
            success_rate = round((today_successful / today_total) * 100, 1)
        else:
            success_rate = 0.0

        # Get failed prints for details
        failed_prints = [r for r in today_history if r.get('status') == 'failed']

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 8px 8px 0 0;
            text-align: center;
        }}
        .content {{
            background-color: white;
            padding: 30px;
            border-radius: 0 0 8px 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-box {{
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-box.success {{
            background-color: #d4edda;
            border-left: 4px solid #28a745;
        }}
        .stat-box.failed {{
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
        }}
        .stat-number {{
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
        }}
        .section {{
            margin: 30px 0;
        }}
        .section-title {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th {{
            background-color: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .footer {{
            text-align: center;
            color: #7f8c8d;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 12px;
        }}
        .success-badge {{
            color: #28a745;
            font-weight: bold;
        }}
        .failed-badge {{
            color: #dc3545;
            font-weight: bold;
        }}
        .no-data {{
            text-align: center;
            padding: 40px;
            color: #95a5a6;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 FIC Printing Service Daily Report</h1>
        <p>{report_date.strftime('%A, %B %d, %Y')}</p>
    </div>

    <div class="content">
        <div class="section">
            <h2 class="section-title">Today's Summary</h2>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-label">Total Prints</div>
                    <div class="stat-number">{today_total}</div>
                </div>
                <div class="stat-box success">
                    <div class="stat-label">Successful</div>
                    <div class="stat-number">{today_successful}</div>
                    <div class="stat-label">{success_rate}% Success Rate</div>
                </div>
                <div class="stat-box failed">
                    <div class="stat-label">Failed</div>
                    <div class="stat-number">{today_failed}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Total Size</div>
                    <div class="stat-number">{today_size_mb}</div>
                    <div class="stat-label">MB</div>
                </div>
            </div>
        </div>
"""

        # Add recent prints section
        if today_history:
            html += """
        <div class="section">
            <h2 class="section-title">Today's Print Jobs</h2>
            <table>
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Status</th>
                        <th>CSV File</th>
                        <th>Size (KB)</th>
                    </tr>
                </thead>
                <tbody>
"""
            for record in today_history[:20]:  # Limit to 20 most recent
                timestamp = record.get('timestamp', '')[:19].split('T')[1] if 'T' in record.get('timestamp', '') else 'N/A'
                status = record.get('status', 'unknown')
                status_class = 'success-badge' if status == 'success' else 'failed-badge'
                csv_file = record.get('csv_filename', 'N/A')[:40]
                size_kb = round(record.get('pdf_size_bytes', 0) / 1024, 1)

                html += f"""
                    <tr>
                        <td>{timestamp}</td>
                        <td class="{status_class}">{status.upper()}</td>
                        <td>{csv_file}</td>
                        <td>{size_kb}</td>
                    </tr>
"""

            html += """
                </tbody>
            </table>
        </div>
"""
        else:
            html += """
        <div class="section">
            <div class="no-data">
                No print jobs today
            </div>
        </div>
"""

        # Add failed prints details if any
        if failed_prints:
            html += """
        <div class="section">
            <h2 class="section-title">⚠️ Failed Prints Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>CSV File</th>
                        <th>Error Message</th>
                    </tr>
                </thead>
                <tbody>
"""
            for record in failed_prints:
                timestamp = record.get('timestamp', '')[:19].split('T')[1] if 'T' in record.get('timestamp', '') else 'N/A'
                csv_file = record.get('csv_filename', 'N/A')[:40]
                error_msg = record.get('error_message', 'Unknown error')[:100]

                html += f"""
                    <tr>
                        <td>{timestamp}</td>
                        <td>{csv_file}</td>
                        <td>{error_msg}</td>
                    </tr>
"""

            html += """
                </tbody>
            </table>
        </div>
"""

        # Add overall statistics
        html += f"""
        <div class="section">
            <h2 class="section-title">Overall Statistics (All Time)</h2>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-label">Total Prints</div>
                    <div class="stat-number">{overall_stats['total_prints']}</div>
                </div>
                <div class="stat-box success">
                    <div class="stat-label">Successful</div>
                    <div class="stat-number">{overall_stats['successful_prints']}</div>
                </div>
                <div class="stat-box failed">
                    <div class="stat-label">Failed</div>
                    <div class="stat-number">{overall_stats['failed_prints']}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Total Size</div>
                    <div class="stat-number">{overall_stats['total_pdf_size_mb']}</div>
                    <div class="stat-label">MB</div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>FIC Printing Service - Automated Daily Report</p>
            <p>Generated at {datetime.now().strftime('%I:%M %p EST')}</p>
        </div>
    </div>
</body>
</html>
"""
        return html

    def _send_email(self, html_content: str, report_date: datetime.date) -> bool:
        """
        Send the report email.

        Args:
            html_content: HTML content of the report
            report_date: Date of the report

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['to'] = self.recipient_email
            message['subject'] = f'FIC Printing Service Daily Report - {report_date.strftime("%B %d, %Y")}'

            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)

            # Encode and send
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            send_message = {'raw': raw_message}

            self.gmail_service.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()

            logger.info(f"Daily report sent successfully to {self.recipient_email}")
            return True

        except HttpError as error:
            logger.error(f"Failed to send daily report: {error}")
            return False
        except Exception as error:
            logger.error(f"Unexpected error sending daily report: {error}")
            return False

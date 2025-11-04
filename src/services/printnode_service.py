"""PrintNode service for remote printing."""

import logging
import requests
from typing import Optional, Dict
from base64 import b64encode

from src.config import Config

logger = logging.getLogger(__name__)


class PrintNodeService:
    """Service for printing documents via PrintNode API."""

    def __init__(self):
        """Initialize PrintNode service."""
        self.api_key = Config.PRINTNODE_API_KEY
        self.printer_id = Config.PRINTNODE_PRINTER_ID
        self.base_url = Config.PRINTNODE_API_URL
        self.session = requests.Session()
        self.session.auth = (self.api_key, '')

    def test_connection(self) -> bool:
        """
        Test PrintNode API connection and credentials.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/whoami")
            response.raise_for_status()
            user_info = response.json()
            logger.info(f"PrintNode connection successful. User: {user_info.get('firstname', 'Unknown')}")
            return True
        except requests.RequestException as e:
            logger.error(f"PrintNode connection failed: {e}")
            return False

    def get_printers(self) -> list:
        """
        Get list of available printers.

        Returns:
            List of printer objects
        """
        try:
            response = self.session.get(f"{self.base_url}/printers")
            response.raise_for_status()
            printers = response.json()
            logger.info(f"Found {len(printers)} printers")
            return printers
        except requests.RequestException as e:
            logger.error(f"Error fetching printers: {e}")
            return []

    def print_pdf_from_url(self, pdf_url: str, title: str = "Batch Order Report") -> Optional[int]:
        """
        Print a PDF from URL.

        Args:
            pdf_url: URL of the PDF to print
            title: Title for the print job

        Returns:
            Print job ID if successful, None otherwise
        """
        try:
            logger.info(f"Attempting to print PDF from URL: {pdf_url}")

            # Download PDF content
            pdf_response = requests.get(pdf_url, timeout=30)
            pdf_response.raise_for_status()
            pdf_content = pdf_response.content

            logger.info(f"Downloaded PDF ({len(pdf_content)} bytes)")

            # Print using PDF content
            return self.print_pdf(pdf_content, title)

        except requests.RequestException as e:
            logger.error(f"Error downloading PDF from {pdf_url}: {e}")
            return None

    def print_pdf(self, pdf_content: bytes, title: str = "Document") -> Optional[int]:
        """
        Print PDF content to PrintNode printer.

        Args:
            pdf_content: PDF file content as bytes
            title: Title for the print job

        Returns:
            Print job ID if successful, None otherwise
        """
        try:
            # Encode PDF content to base64
            pdf_base64 = b64encode(pdf_content).decode('utf-8')

            # Prepare print job
            print_job = {
                "printerId": int(self.printer_id),
                "title": title,
                "contentType": "pdf_base64",
                "content": pdf_base64,
                "source": "Gmail Email Processor"
            }

            # Submit print job
            response = self.session.post(
                f"{self.base_url}/printjobs",
                json=print_job
            )
            response.raise_for_status()
            job_id = response.json()

            logger.info(f"Print job submitted successfully. Job ID: {job_id}")
            return job_id

        except requests.RequestException as e:
            logger.error(f"Error submitting print job: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during printing: {e}")
            return None

    def get_print_job_status(self, job_id: int) -> Optional[Dict]:
        """
        Get status of a print job.

        Args:
            job_id: PrintNode job ID

        Returns:
            Job status dict or None
        """
        try:
            response = self.session.get(f"{self.base_url}/printjobs/{job_id}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching job status: {e}")
            return None

    def verify_printer_exists(self) -> bool:
        """
        Verify that configured printer exists and is available.

        Returns:
            True if printer exists, False otherwise
        """
        try:
            printers = self.get_printers()
            printer_ids = [str(p.get('id')) for p in printers]

            if self.printer_id in printer_ids:
                printer = next(p for p in printers if str(p.get('id')) == self.printer_id)
                logger.info(f"Printer '{printer.get('name')}' is available (ID: {self.printer_id})")
                return True
            else:
                logger.error(f"Printer ID {self.printer_id} not found. Available IDs: {printer_ids}")
                return False

        except Exception as e:
            logger.error(f"Error verifying printer: {e}")
            return False

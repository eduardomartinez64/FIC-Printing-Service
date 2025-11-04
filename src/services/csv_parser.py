"""CSV parser for extracting PDF links from email attachments."""

import io
import logging
from typing import Optional
import pandas as pd

logger = logging.getLogger(__name__)


class CSVParser:
    """Parser for extracting PDF links from CSV files."""

    @staticmethod
    def extract_pdf_link(csv_data: bytes, column: str = 'C') -> Optional[str]:
        """
        Extract PDF link from the last row of specified column in CSV.

        Args:
            csv_data: CSV file data as bytes
            column: Column letter to extract from (default: 'C')

        Returns:
            PDF link URL or None if not found
        """
        try:
            # Convert bytes to string for pandas
            csv_string = csv_data.decode('utf-8')
            df = pd.read_csv(io.StringIO(csv_string))

            # Convert column letter to index (A=0, B=1, C=2, etc.)
            column_index = ord(column.upper()) - ord('A')

            if column_index >= len(df.columns):
                logger.error(f"Column {column} does not exist in CSV (only {len(df.columns)} columns found)")
                return None

            # Get the column name by index
            column_name = df.columns[column_index]
            logger.debug(f"Reading from column: {column_name}")

            # Check if DataFrame is empty
            if df.empty:
                logger.warning("CSV file is empty")
                return None

            # Get the last row value from the specified column
            last_row_value = df.iloc[-1][column_name]

            # Check if the value is a valid string
            if pd.isna(last_row_value):
                logger.warning(f"Last row in column {column} is empty")
                return None

            pdf_link = str(last_row_value).strip()

            # Basic validation that it looks like a URL
            if not pdf_link.startswith(('http://', 'https://')):
                logger.warning(f"Value in last row doesn't look like a URL: {pdf_link}")
                return None

            logger.info(f"Successfully extracted PDF link from column {column}: {pdf_link}")
            return pdf_link

        except pd.errors.EmptyDataError:
            logger.error("CSV file is empty or invalid")
            return None
        except Exception as e:
            logger.error(f"Error parsing CSV: {e}")
            return None

    @staticmethod
    def extract_pdf_links_all_rows(csv_data: bytes, column: str = 'C') -> list:
        """
        Extract all PDF links from specified column in CSV.

        Args:
            csv_data: CSV file data as bytes
            column: Column letter to extract from (default: 'C')

        Returns:
            List of PDF link URLs
        """
        try:
            csv_string = csv_data.decode('utf-8')
            df = pd.read_csv(io.StringIO(csv_string))

            column_index = ord(column.upper()) - ord('A')

            if column_index >= len(df.columns):
                logger.error(f"Column {column} does not exist in CSV")
                return []

            column_name = df.columns[column_index]

            # Filter for valid URLs
            links = []
            for value in df[column_name]:
                if pd.notna(value):
                    link = str(value).strip()
                    if link.startswith(('http://', 'https://')):
                        links.append(link)

            logger.info(f"Found {len(links)} PDF links in column {column}")
            return links

        except Exception as e:
            logger.error(f"Error parsing CSV: {e}")
            return []

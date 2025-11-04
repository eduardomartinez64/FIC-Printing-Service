"""Tests for CSV parser service."""

import pytest
from src.services.csv_parser import CSVParser


def test_extract_pdf_link_from_valid_csv():
    """Test extracting PDF link from valid CSV."""
    csv_data = b"""Header1,Header2,PDF_Link
Row1A,Row1B,https://example.com/doc1.pdf
Row2A,Row2B,https://example.com/doc2.pdf
Row3A,Row3B,https://example.com/final.pdf"""

    parser = CSVParser()
    result = parser.extract_pdf_link(csv_data, column='C')

    assert result == "https://example.com/final.pdf"


def test_extract_pdf_link_empty_csv():
    """Test handling of empty CSV."""
    csv_data = b"Header1,Header2,Header3\n"

    parser = CSVParser()
    result = parser.extract_pdf_link(csv_data, column='C')

    assert result is None


def test_extract_pdf_link_missing_column():
    """Test handling when column doesn't exist."""
    csv_data = b"Header1,Header2\nRow1A,Row1B"

    parser = CSVParser()
    result = parser.extract_pdf_link(csv_data, column='C')

    assert result is None


def test_extract_pdf_link_invalid_url():
    """Test handling of non-URL value."""
    csv_data = b"Header1,Header2,Header3\nRow1A,Row1B,not_a_url"

    parser = CSVParser()
    result = parser.extract_pdf_link(csv_data, column='C')

    assert result is None


def test_extract_all_pdf_links():
    """Test extracting all PDF links from column."""
    csv_data = b"""Header1,Header2,PDF_Link
Row1A,Row1B,https://example.com/doc1.pdf
Row2A,Row2B,https://example.com/doc2.pdf
Row3A,Row3B,not_a_url
Row4A,Row4B,https://example.com/doc3.pdf"""

    parser = CSVParser()
    result = parser.extract_pdf_links_all_rows(csv_data, column='C')

    assert len(result) == 3
    assert "https://example.com/doc1.pdf" in result
    assert "https://example.com/doc2.pdf" in result
    assert "https://example.com/doc3.pdf" in result

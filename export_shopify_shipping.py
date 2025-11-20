#!/usr/bin/env python3
"""
Shopify Shipping Export Tool

This script exports your Shopify shipping zones, rates, countries, and carrier services
to a formatted Excel file for analysis.

Usage:
    python export_shopify_shipping.py

Configuration:
    Set the following in your .env file:
    - SHOPIFY_STORE_URL=your-store.myshopify.com
    - SHOPIFY_ACCESS_TOKEN=shpat_your_token_here
    - SHOPIFY_API_VERSION=2024-10 (optional)
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.shopify_service import ShopifyService
from src.exporters.shipping_exporter import ShippingExporter
from src.utils.logger import setup_logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


def validate_config():
    """Validate required configuration."""
    errors = []

    store_url = os.getenv('SHOPIFY_STORE_URL')
    access_token = os.getenv('SHOPIFY_ACCESS_TOKEN')

    if not store_url:
        errors.append("SHOPIFY_STORE_URL not set in .env file")

    if not access_token:
        errors.append("SHOPIFY_ACCESS_TOKEN not set in .env file")

    if access_token and not access_token.startswith('shpat_'):
        errors.append("SHOPIFY_ACCESS_TOKEN appears invalid (should start with 'shpat_')")

    if errors:
        logger.error("Configuration errors:")
        for error in errors:
            logger.error(f"  - {error}")
        return False

    return True


def main():
    """Main execution function."""
    # Setup logging
    setup_logging()

    logger.info("=" * 70)
    logger.info("Shopify Shipping Data Export Tool")
    logger.info("=" * 70)

    # Validate configuration
    if not validate_config():
        logger.error("\nPlease configure your .env file with Shopify credentials.")
        logger.error("See SHOPIFY_EXPORT_GUIDE.md for setup instructions.")
        return 1

    # Get configuration
    store_url = os.getenv('SHOPIFY_STORE_URL')
    access_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
    api_version = os.getenv('SHOPIFY_API_VERSION', '2024-10')
    output_dir = os.getenv('EXPORT_OUTPUT_DIR', 'exports')

    logger.info(f"Store URL: {store_url}")
    logger.info(f"API Version: {api_version}")
    logger.info(f"Output Directory: {output_dir}")
    logger.info("")

    try:
        # Initialize services
        logger.info("Initializing Shopify service...")
        shopify = ShopifyService(store_url, access_token, api_version)

        # Test connection
        if not shopify.test_connection():
            logger.error("\nFailed to connect to Shopify. Please check:")
            logger.error("  1. Your store URL is correct")
            logger.error("  2. Your access token is valid")
            logger.error("  3. The token has 'read_shipping' scope")
            return 1

        logger.info("")

        # Fetch all shipping data
        data = shopify.get_all_shipping_data()

        # Export to Excel
        logger.info("")
        exporter = ShippingExporter(output_dir=output_dir)
        filepath = exporter.export_to_excel(data)

        # Success message
        logger.info("")
        logger.info("=" * 70)
        logger.info("Export completed successfully!")
        logger.info("=" * 70)
        logger.info(f"Excel file: {filepath}")
        logger.info("")
        logger.info("Next steps:")
        logger.info("  1. Open the Excel file")
        logger.info("  2. Review the 'Overview' sheet for summary statistics")
        logger.info("  3. Analyze zones and rates for consolidation opportunities")
        logger.info("  4. See SHOPIFY_EXPORT_GUIDE.md for analysis tips")
        logger.info("=" * 70)

        return 0

    except KeyboardInterrupt:
        logger.warning("\n\nExport cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"\n\nUnexpected error during export: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())

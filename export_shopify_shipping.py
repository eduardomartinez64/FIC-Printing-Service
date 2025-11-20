#!/usr/bin/env python3
"""
Shopify Shipping Data Export Tool

Exports shipping profiles, zones, rates, and countries from a Shopify store
to a structured Excel file for analysis and consolidation.

Usage:
    python export_shopify_shipping.py

Configuration:
    Set the following environment variables in .env:
    - SHOPIFY_STORE_URL: Your Shopify store URL (e.g., your-store.myshopify.com)
    - SHOPIFY_ACCESS_TOKEN: Your Shopify Admin API access token
    - SHOPIFY_API_VERSION: (Optional) API version (default: 2024-10)
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.shopify_service import ShopifyService
from exporters.shipping_exporter import ShippingExporter
from utils.logger import setup_logging


def main():
    """Main execution function."""
    # Load environment variables
    load_dotenv()

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("Shopify Shipping Data Export Tool")
    logger.info("=" * 60)

    # Get configuration from environment
    store_url = os.getenv('SHOPIFY_STORE_URL')
    access_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
    api_version = os.getenv('SHOPIFY_API_VERSION', '2024-10')

    # Validate configuration
    if not store_url:
        logger.error("SHOPIFY_STORE_URL not set in environment variables")
        print("\n[ERROR] Error: SHOPIFY_STORE_URL not configured")
        print("Please set this in your .env file")
        return 1

    if not access_token:
        logger.error("SHOPIFY_ACCESS_TOKEN not set in environment variables")
        print("\n[ERROR] Error: SHOPIFY_ACCESS_TOKEN not configured")
        print("Please set this in your .env file")
        return 1

    try:
        # Initialize services
        print(f"\n Connecting to Shopify store: {store_url}")
        shopify = ShopifyService(store_url, access_token, api_version)

        # Test connection
        if not shopify.test_connection():
            logger.error("Failed to connect to Shopify")
            print("[ERROR] Failed to connect to Shopify. Check your credentials.")
            return 1

        print("[OK] Successfully connected to Shopify")

        # Fetch shipping data
        print("\n Fetching shipping data...")
        print("   - Shipping zones...")
        shipping_data = shopify.get_all_shipping_data()

        zones_count = len(shipping_data['shipping_zones'])
        countries_count = len(shipping_data['countries'])
        services_count = len(shipping_data['carrier_services'])

        print(f"   [OK] Found {zones_count} shipping zones")
        print(f"   [OK] Found {countries_count} countries")
        print(f"   [OK] Found {services_count} carrier services")

        # Calculate total rates
        total_rates = 0
        for zone in shipping_data['shipping_zones']:
            total_rates += len(zone.get('weight_based_shipping_rates', []))
            total_rates += len(zone.get('price_based_shipping_rates', []))
            total_rates += len(zone.get('carrier_shipping_rate_providers', []))

        print(f"   [OK] Found {total_rates} total shipping rates")

        # Export to Excel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"shopify_shipping_export_{timestamp}.xlsx"

        print(f"\n Exporting to Excel: {output_file}")
        exporter = ShippingExporter()
        exporter.export_to_excel(shipping_data, output_file)

        print(f"\n[OK] Export completed successfully!")
        print(f"\n File saved: {output_file}")
        print("\n Excel sheets created:")
        print("   - Overview - Summary and statistics")
        print("   - Zones - All shipping zones")
        print("   - Rates - Detailed rate breakdown")
        print("   - Countries - Countries and provinces per zone")
        print("   - Carrier Services - Third-party carrier configuration")
        print("\nTip: Tip: Use Excel filters and pivot tables to analyze and consolidate your zones")

        logger.info(f"Export completed successfully: {output_file}")
        return 0

    except KeyboardInterrupt:
        print("\n\n[WARNING]  Export cancelled by user")
        logger.warning("Export cancelled by user")
        return 1

    except Exception as e:
        logger.error(f"Export failed: {e}", exc_info=True)
        print(f"\n[ERROR] Export failed: {e}")
        print("Check logs/shopify_export.log for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())

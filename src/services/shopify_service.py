"""Shopify Admin API service for fetching shipping data."""

import logging
import requests
from typing import List, Dict, Optional
from time import sleep

logger = logging.getLogger(__name__)


class ShopifyService:
    """Service for interacting with Shopify Admin API."""

    def __init__(self, store_url: str, access_token: str, api_version: str = "2024-10"):
        """
        Initialize Shopify service.

        Args:
            store_url: Your Shopify store URL (e.g., 'your-store.myshopify.com')
            access_token: Shopify Admin API access token
            api_version: Shopify API version (default: 2024-10)
        """
        self.store_url = store_url.replace('https://', '').replace('http://', '')
        self.access_token = access_token
        self.api_version = api_version
        self.base_url = f"https://{self.store_url}/admin/api/{api_version}"
        self.headers = {
            'X-Shopify-Access-Token': access_token,
            'Content-Type': 'application/json'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make a request to Shopify API with rate limiting.

        Args:
            endpoint: API endpoint (e.g., '/shipping_zones.json')
            params: Query parameters

        Returns:
            Response JSON or None on error
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            # Check rate limits
            if 'X-Shopify-Shop-Api-Call-Limit' in response.headers:
                call_limit = response.headers['X-Shopify-Shop-Api-Call-Limit']
                logger.debug(f"API call limit: {call_limit}")

                # If approaching limit, slow down
                current, limit = map(int, call_limit.split('/'))
                if current / limit > 0.8:  # 80% of limit
                    logger.warning("Approaching rate limit, adding delay")
                    sleep(1)

            return response.json()

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching {endpoint}: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching {endpoint}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {endpoint}: {e}")
            return None

    def test_connection(self) -> bool:
        """
        Test connection to Shopify API.

        Returns:
            True if connection successful, False otherwise
        """
        logger.info("Testing Shopify API connection...")

        result = self._make_request('/shop.json')

        if result and 'shop' in result:
            shop = result['shop']
            logger.info(f"Connected to Shopify store: {shop.get('name')}")
            logger.info(f"  Store URL: {shop.get('domain')}")
            logger.info(f"  Currency: {shop.get('currency')}")
            return True
        else:
            logger.error("Failed to connect to Shopify API")
            return False

    def get_shipping_zones(self) -> List[Dict]:
        """
        Fetch all shipping zones.

        Returns:
            List of shipping zone objects
        """
        logger.info("Fetching shipping zones...")

        result = self._make_request('/shipping_zones.json')

        if result and 'shipping_zones' in result:
            zones = result['shipping_zones']
            logger.info(f"Found {len(zones)} shipping zones")
            return zones
        else:
            logger.warning("No shipping zones found")
            return []

    def get_countries_for_zone(self, zone_id: int) -> List[Dict]:
        """
        Fetch countries for a specific shipping zone.

        Args:
            zone_id: Shipping zone ID

        Returns:
            List of country objects with provinces
        """
        logger.debug(f"Fetching countries for zone {zone_id}")

        result = self._make_request(f'/shipping_zones/{zone_id}.json')

        if result and 'shipping_zone' in result:
            countries = result['shipping_zone'].get('countries', [])
            logger.debug(f"  Found {len(countries)} countries in zone {zone_id}")
            return countries
        else:
            return []

    def get_carrier_services(self) -> List[Dict]:
        """
        Fetch all carrier services (third-party shipping).

        Returns:
            List of carrier service objects
        """
        logger.info("Fetching carrier services...")

        result = self._make_request('/carrier_services.json')

        if result and 'carrier_services' in result:
            services = result['carrier_services']
            logger.info(f"Found {len(services)} carrier services")
            return services
        else:
            logger.info("No carrier services configured")
            return []

    def get_all_shipping_data(self) -> Dict:
        """
        Fetch all shipping-related data.

        Returns:
            Dictionary containing zones, rates, countries, and carrier services
        """
        logger.info("=" * 60)
        logger.info("Starting comprehensive shipping data fetch")
        logger.info("=" * 60)

        data = {
            'zones': [],
            'rates': [],
            'countries': [],
            'carrier_services': []
        }

        # Fetch zones
        zones = self.get_shipping_zones()
        data['zones'] = zones

        # Process each zone (zones already contain all data we need)
        for i, zone in enumerate(zones, 1):
            zone_id = zone['id']
            zone_name = zone['name']

            if i % 50 == 0:
                logger.info(f"Processing zone {i}/{len(zones)}: {zone_name}")

            # Extract rates from zone data
            for rate in zone.get('weight_based_shipping_rates', []):
                rate_data = {
                    'zone_id': zone_id,
                    'zone_name': zone_name,
                    'rate_type': 'weight_based',
                    'name': rate.get('name'),
                    'price': rate.get('price'),
                    'weight_low': rate.get('weight_low'),
                    'weight_high': rate.get('weight_high')
                }
                data['rates'].append(rate_data)

            for rate in zone.get('price_based_shipping_rates', []):
                rate_data = {
                    'zone_id': zone_id,
                    'zone_name': zone_name,
                    'rate_type': 'price_based',
                    'name': rate.get('name'),
                    'price': rate.get('price'),
                    'min_order_subtotal': rate.get('min_order_subtotal'),
                    'max_order_subtotal': rate.get('max_order_subtotal')
                }
                data['rates'].append(rate_data)

            for rate in zone.get('carrier_shipping_rate_providers', []):
                rate_data = {
                    'zone_id': zone_id,
                    'zone_name': zone_name,
                    'rate_type': 'carrier',
                    'carrier_service_id': rate.get('carrier_service_id'),
                    'flat_modifier': rate.get('flat_modifier'),
                    'percent_modifier': rate.get('percent_modifier')
                }
                data['rates'].append(rate_data)

            # Extract countries from zone data (already included)
            for country in zone.get('countries', []):
                country_data = {
                    'zone_id': zone_id,
                    'zone_name': zone_name,
                    'country_id': country.get('id'),
                    'country_code': country.get('code'),
                    'country_name': country.get('name'),
                    'tax': country.get('tax'),
                    'provinces': []
                }

                # Add provinces if any
                for province in country.get('provinces', []):
                    province_data = {
                        'province_id': province.get('id'),
                        'province_code': province.get('code'),
                        'province_name': province.get('name'),
                        'tax': province.get('tax')
                    }
                    country_data['provinces'].append(province_data)

                data['countries'].append(country_data)

        # Fetch carrier services
        data['carrier_services'] = self.get_carrier_services()

        logger.info("=" * 60)
        logger.info(f"Data fetch complete!")
        logger.info(f"  Zones: {len(data['zones'])}")
        logger.info(f"  Rates: {len(data['rates'])}")
        logger.info(f"  Countries: {len(data['countries'])}")
        logger.info(f"  Carrier Services: {len(data['carrier_services'])}")
        logger.info("=" * 60)

        return data

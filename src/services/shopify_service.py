"""
Shopify API Service for fetching shipping profiles, zones, and rates.
Handles authentication and data retrieval from Shopify Admin API.
"""

import requests
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ShopifyService:
    """Service for interacting with Shopify Admin API to fetch shipping data."""

    def __init__(self, shop_url: str, access_token: str, api_version: str = "2024-10"):
        """
        Initialize Shopify service.

        Args:
            shop_url: Shopify store URL (e.g., 'your-store.myshopify.com')
            access_token: Shopify Admin API access token
            api_version: Shopify API version (default: 2024-10)
        """
        self.shop_url = shop_url.replace('https://', '').replace('http://', '')
        self.access_token = access_token
        self.api_version = api_version
        self.base_url = f"https://{self.shop_url}/admin/api/{api_version}"

        self.headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }

        logger.info(f"Initialized Shopify service for store: {self.shop_url}")

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make GET request to Shopify API.

        Args:
            endpoint: API endpoint (e.g., '/shipping_zones.json')
            params: Optional query parameters

        Returns:
            JSON response as dictionary

        Raises:
            requests.HTTPError: If API request fails
        """
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"Making request to: {url}")

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Shopify API request failed: {e}")
            raise

    def test_connection(self) -> bool:
        """
        Test connection to Shopify API.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self._make_request('/shop.json')
            shop_name = response.get('shop', {}).get('name', 'Unknown')
            logger.info(f"Successfully connected to Shopify store: {shop_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Shopify: {e}")
            return False

    def get_shipping_zones(self) -> List[Dict]:
        """
        Fetch all shipping zones from Shopify.

        Returns:
            List of shipping zone dictionaries
        """
        logger.info("Fetching shipping zones...")

        try:
            response = self._make_request('/shipping_zones.json')
            zones = response.get('shipping_zones', [])
            logger.info(f"Retrieved {len(zones)} shipping zones")
            return zones
        except Exception as e:
            logger.error(f"Failed to fetch shipping zones: {e}")
            raise

    def get_countries(self) -> List[Dict]:
        """
        Fetch all countries configured in Shopify.

        Returns:
            List of country dictionaries
        """
        logger.info("Fetching countries...")

        try:
            response = self._make_request('/countries.json')
            countries = response.get('countries', [])
            logger.info(f"Retrieved {len(countries)} countries")
            return countries
        except Exception as e:
            logger.error(f"Failed to fetch countries: {e}")
            raise

    def get_carrier_services(self) -> List[Dict]:
        """
        Fetch carrier services configured in Shopify.

        Returns:
            List of carrier service dictionaries
        """
        logger.info("Fetching carrier services...")

        try:
            response = self._make_request('/carrier_services.json')
            services = response.get('carrier_services', [])
            logger.info(f"Retrieved {len(services)} carrier services")
            return services
        except Exception as e:
            logger.error(f"Failed to fetch carrier services: {e}")
            raise

    def get_delivery_profiles(self) -> List[Dict]:
        """
        Fetch all delivery profiles (shipping profiles) from Shopify.
        Each profile contains multiple shipping zones.

        Returns:
            List of delivery profile dictionaries with zones
        """
        logger.info("Fetching delivery profiles...")

        try:
            # Note: Delivery profiles endpoint might not be available in all Shopify plans
            # If it fails, we'll fall back to grouping zones
            try:
                response = self._make_request('/delivery_profiles.json')
                profiles = response.get('delivery_profiles', [])
                logger.info(f"Retrieved {len(profiles)} delivery profiles")
                return profiles
            except:
                # Fallback: Create a single "default" profile with all zones
                logger.warning("Delivery profiles endpoint not available, using zones grouping")
                zones = self.get_shipping_zones()

                # Group zones by profile_id if available, otherwise create default profile
                profiles_dict = {}
                for zone in zones:
                    profile_id = zone.get('profile_id', 'default')
                    if profile_id not in profiles_dict:
                        profiles_dict[profile_id] = {
                            'id': profile_id,
                            'name': f"Shipping Profile {profile_id}" if profile_id != 'default' else "Default Shipping",
                            'zones': []
                        }
                    profiles_dict[profile_id]['zones'].append(zone)

                profiles = list(profiles_dict.values())
                logger.info(f"Grouped zones into {len(profiles)} profile(s)")
                return profiles

        except Exception as e:
            logger.error(f"Failed to fetch delivery profiles: {e}")
            raise

    def get_all_shipping_data(self) -> Dict[str, Any]:
        """
        Fetch comprehensive shipping configuration data organized by profiles.

        Returns:
            Dictionary containing profiles (with zones), countries, and carrier services
        """
        logger.info("Fetching all shipping data...")

        data = {
            'profiles': self.get_delivery_profiles(),
            'shipping_zones': self.get_shipping_zones(),  # Keep for backward compatibility
            'countries': self.get_countries(),
            'carrier_services': self.get_carrier_services()
        }

        logger.info("Successfully retrieved all shipping data")
        return data

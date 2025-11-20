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

    def _extract_profile_name(self, profile: Dict) -> str:
        """
        Extract a clean, human-readable name from a delivery profile.

        Args:
            profile: Profile dictionary from API

        Returns:
            Clean profile name string
        """
        # Try to get the profile name
        name = profile.get('name', '')

        # If name is a GID (gid://shopify/DeliveryProfile/...), extract a cleaner version
        if name.startswith('gid://'):
            # Try to get profile_id or id
            profile_id = profile.get('profile_id') or profile.get('id', 'Unknown')
            # Clean up the profile_id if it's also a GID
            if isinstance(profile_id, str) and 'DeliveryProfile/' in profile_id:
                # Extract just the number after DeliveryProfile/
                parts = profile_id.split('DeliveryProfile/')
                if len(parts) > 1:
                    numeric_id = parts[1].split('/')[0].split('?')[0]
                    name = f"Shipping Profile {numeric_id}"
                else:
                    name = f"Profile {profile_id}"
            else:
                name = f"Shipping Profile {profile_id}"

        # If still no good name, try other fields
        if not name or name.startswith('gid://'):
            # Check if there's a legible_name field
            name = profile.get('legible_name') or profile.get('title') or 'Unnamed Profile'

        return name

    def _get_profile_product_count(self, profile_id: str) -> int:
        """
        Get the number of products/variants assigned to a delivery profile.

        Args:
            profile_id: The profile ID (can be numeric or GID format)

        Returns:
            Number of products assigned to this profile, or -1 if unable to determine
        """
        try:
            # Extract numeric ID if it's a GID
            if isinstance(profile_id, str) and 'DeliveryProfile/' in profile_id:
                numeric_id = profile_id.split('DeliveryProfile/')[-1].split('/')[0].split('?')[0]
            else:
                numeric_id = str(profile_id)

            # Try to get profile details which may include product count
            try:
                endpoint = f'/delivery_profiles/{numeric_id}.json'
                response = self._make_request(endpoint)
                profile_data = response.get('delivery_profile', {})

                # Check for product variant IDs or product count
                variant_ids = profile_data.get('product_variant_ids', [])
                if variant_ids:
                    return len(variant_ids)

                # Some Shopify versions may have a location_groups with product info
                location_groups = profile_data.get('location_groups', [])
                for group in location_groups:
                    locations = group.get('locations', [])
                    if locations:
                        return 1  # Has locations, likely has products

            except:
                pass

            # Fallback: If profile_id is 'default' or appears to be default, assume it has products
            if profile_id == 'default' or 'default' in str(profile_id).lower():
                return 1  # Default profile usually has products

            # Unable to determine, return -1 to indicate unknown
            return -1

        except Exception as e:
            logger.debug(f"Could not determine product count for profile {profile_id}: {e}")
            return -1

    def get_delivery_profiles(self, filter_active_only: bool = True) -> List[Dict]:
        """
        Fetch all delivery profiles (shipping profiles) from Shopify.
        Each profile contains multiple shipping zones.

        Args:
            filter_active_only: If True, only return profiles with products assigned

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
                logger.info(f"Retrieved {len(profiles)} delivery profiles from API")

                # Enhance profiles with better names and product counts
                enhanced_profiles = []
                for profile in profiles:
                    # Extract clean name
                    clean_name = self._extract_profile_name(profile)
                    profile['display_name'] = clean_name

                    # Get product count
                    profile_id = profile.get('id') or profile.get('profile_id', '')
                    product_count = self._get_profile_product_count(profile_id)
                    profile['product_count'] = product_count

                    # Filter if requested
                    if filter_active_only:
                        # Include profile if: has products, is default, or count unknown
                        if product_count != 0:  # Keep if has products or unknown (-1)
                            enhanced_profiles.append(profile)
                            logger.info(f"Including profile '{clean_name}' (products: {product_count if product_count >= 0 else 'unknown'})")
                        else:
                            logger.info(f"Skipping profile '{clean_name}' (no products assigned)")
                    else:
                        enhanced_profiles.append(profile)

                logger.info(f"Returning {len(enhanced_profiles)} active delivery profiles")
                return enhanced_profiles

            except Exception as api_error:
                # Fallback: Create a single "default" profile with all zones
                logger.warning(f"Delivery profiles endpoint not available ({api_error}), using zones grouping")
                zones = self.get_shipping_zones()

                # Group zones by profile_id if available, otherwise create default profile
                profiles_dict = {}
                for zone in zones:
                    profile_id = zone.get('profile_id', 'default')
                    if profile_id not in profiles_dict:
                        clean_name = self._extract_profile_name({'id': profile_id, 'name': ''})
                        profiles_dict[profile_id] = {
                            'id': profile_id,
                            'name': clean_name,
                            'display_name': clean_name,
                            'zones': [],
                            'product_count': 1  # Assume fallback profiles have products
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

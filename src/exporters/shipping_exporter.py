"""
Excel Exporter for Shopify Shipping Data.
Exports shipping zones, profiles, and rates to structured Excel workbook.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

logger = logging.getLogger(__name__)


class ShippingExporter:
    """Exports Shopify shipping data to Excel with multiple sheets."""

    def __init__(self):
        """Initialize the exporter."""
        self.workbook = Workbook()
        self.workbook.remove(self.workbook.active)  # Remove default sheet

        # Define styles
        self.header_font = Font(bold=True, color="FFFFFF")
        self.header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        self.header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    def _style_header_row(self, sheet, row_num: int = 1):
        """Apply styling to header row."""
        for cell in sheet[row_num]:
            cell.font = self.header_font
            cell.fill = self.header_fill
            cell.alignment = self.header_alignment

    def _auto_adjust_columns(self, sheet):
        """Auto-adjust column widths based on content."""
        for column in sheet.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)

            for cell in column:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass

            adjusted_width = min(max_length + 2, 50)  # Cap at 50
            sheet.column_dimensions[column_letter].width = adjusted_width

    def export_to_excel(self, shipping_data: Dict[str, Any], output_file: str) -> str:
        """
        Export shipping data to Excel file.

        Args:
            shipping_data: Dictionary containing shipping zones and related data
            output_file: Output file path

        Returns:
            Path to created Excel file
        """
        logger.info(f"Starting export to: {output_file}")

        try:
            # Create sheets
            self._create_overview_sheet(shipping_data)
            self._create_zones_sheet(shipping_data['shipping_zones'])
            self._create_rates_sheet(shipping_data['shipping_zones'])
            self._create_countries_sheet(shipping_data['shipping_zones'])
            self._create_carrier_services_sheet(shipping_data.get('carrier_services', []))

            # Save workbook
            self.workbook.save(output_file)
            logger.info(f"Successfully exported data to: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            raise

    def _create_overview_sheet(self, shipping_data: Dict[str, Any]):
        """Create overview/summary sheet."""
        sheet = self.workbook.create_sheet("Overview", 0)

        # Add title
        sheet['A1'] = "Shopify Shipping Configuration Export"
        sheet['A1'].font = Font(size=16, bold=True)

        # Add metadata
        row = 3
        sheet[f'A{row}'] = "Export Date:"
        sheet[f'B{row}'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row += 1
        sheet[f'A{row}'] = "Total Shipping Zones:"
        sheet[f'B{row}'] = len(shipping_data.get('shipping_zones', []))

        row += 1
        sheet[f'A{row}'] = "Total Countries:"
        sheet[f'B{row}'] = len(shipping_data.get('countries', []))

        row += 1
        sheet[f'A{row}'] = "Total Carrier Services:"
        sheet[f'B{row}'] = len(shipping_data.get('carrier_services', []))

        # Calculate total rates
        total_rates = 0
        for zone in shipping_data.get('shipping_zones', []):
            for rate in zone.get('weight_based_shipping_rates', []):
                total_rates += 1
            for rate in zone.get('price_based_shipping_rates', []):
                total_rates += 1
            for rate in zone.get('carrier_shipping_rate_providers', []):
                total_rates += 1

        row += 1
        sheet[f'A{row}'] = "Total Shipping Rates:"
        sheet[f'B{row}'] = total_rates

        # Add instructions
        row += 3
        sheet[f'A{row}'] = "Sheet Descriptions:"
        sheet[f'A{row}'].font = Font(bold=True)

        row += 1
        sheet[f'A{row}'] = "• Zones: All shipping zones with basic information"
        row += 1
        sheet[f'A{row}'] = "• Rates: Detailed breakdown of all shipping rates by zone"
        row += 1
        sheet[f'A{row}'] = "• Countries: Countries and provinces included in each zone"
        row += 1
        sheet[f'A{row}'] = "• Carrier Services: Third-party carrier services configured"

        # Style the overview
        for cell in sheet['A']:
            cell.font = Font(bold=True)

        self._auto_adjust_columns(sheet)

    def _create_zones_sheet(self, zones: List[Dict]):
        """Create shipping zones summary sheet."""
        sheet = self.workbook.create_sheet("Zones")

        # Headers
        headers = [
            "Zone ID",
            "Zone Name",
            "# of Countries",
            "# of Weight Rates",
            "# of Price Rates",
            "# of Carrier Rates",
            "Total Rates"
        ]
        sheet.append(headers)
        self._style_header_row(sheet)

        # Data rows
        for zone in zones:
            zone_id = zone.get('id', '')
            zone_name = zone.get('name', '')
            num_countries = len(zone.get('countries', []))
            num_weight_rates = len(zone.get('weight_based_shipping_rates', []))
            num_price_rates = len(zone.get('price_based_shipping_rates', []))
            num_carrier_rates = len(zone.get('carrier_shipping_rate_providers', []))
            total_rates = num_weight_rates + num_price_rates + num_carrier_rates

            sheet.append([
                zone_id,
                zone_name,
                num_countries,
                num_weight_rates,
                num_price_rates,
                num_carrier_rates,
                total_rates
            ])

        self._auto_adjust_columns(sheet)
        logger.info(f"Created Zones sheet with {len(zones)} zones")

    def _create_rates_sheet(self, zones: List[Dict]):
        """Create detailed shipping rates sheet."""
        sheet = self.workbook.create_sheet("Rates")

        # Headers
        headers = [
            "Zone ID",
            "Zone Name",
            "Rate Type",
            "Rate Name",
            "Min Value",
            "Max Value",
            "Price",
            "Carrier Service"
        ]
        sheet.append(headers)
        self._style_header_row(sheet)

        # Data rows
        total_rates = 0
        for zone in zones:
            zone_id = zone.get('id', '')
            zone_name = zone.get('name', '')

            # Weight-based rates
            for rate in zone.get('weight_based_shipping_rates', []):
                sheet.append([
                    zone_id,
                    zone_name,
                    "Weight-Based",
                    rate.get('name', ''),
                    rate.get('weight_low', ''),
                    rate.get('weight_high', ''),
                    rate.get('price', ''),
                    ''
                ])
                total_rates += 1

            # Price-based rates
            for rate in zone.get('price_based_shipping_rates', []):
                sheet.append([
                    zone_id,
                    zone_name,
                    "Price-Based",
                    rate.get('name', ''),
                    rate.get('min_order_subtotal', ''),
                    rate.get('max_order_subtotal', ''),
                    rate.get('price', ''),
                    ''
                ])
                total_rates += 1

            # Carrier rates
            for rate in zone.get('carrier_shipping_rate_providers', []):
                carrier_service = rate.get('carrier_service_id', '')
                sheet.append([
                    zone_id,
                    zone_name,
                    "Carrier Service",
                    rate.get('service_filter', {}).get('*', 'All Services'),
                    '',
                    '',
                    '',
                    carrier_service
                ])
                total_rates += 1

        self._auto_adjust_columns(sheet)
        logger.info(f"Created Rates sheet with {total_rates} rates")

    def _create_countries_sheet(self, zones: List[Dict]):
        """Create countries/regions breakdown sheet."""
        sheet = self.workbook.create_sheet("Countries")

        # Headers
        headers = [
            "Zone ID",
            "Zone Name",
            "Country Code",
            "Country Name",
            "Province Code",
            "Province Name",
            "Tax"
        ]
        sheet.append(headers)
        self._style_header_row(sheet)

        # Data rows
        total_entries = 0
        for zone in zones:
            zone_id = zone.get('id', '')
            zone_name = zone.get('name', '')

            for country in zone.get('countries', []):
                country_code = country.get('code', '')
                country_name = country.get('name', '')
                tax = country.get('tax', 0)

                provinces = country.get('provinces', [])
                if provinces:
                    # If has provinces, list each province
                    for province in provinces:
                        sheet.append([
                            zone_id,
                            zone_name,
                            country_code,
                            country_name,
                            province.get('code', ''),
                            province.get('name', ''),
                            tax
                        ])
                        total_entries += 1
                else:
                    # No provinces, just list country
                    sheet.append([
                        zone_id,
                        zone_name,
                        country_code,
                        country_name,
                        '',
                        '',
                        tax
                    ])
                    total_entries += 1

        self._auto_adjust_columns(sheet)
        logger.info(f"Created Countries sheet with {total_entries} entries")

    def _create_carrier_services_sheet(self, carrier_services: List[Dict]):
        """Create carrier services configuration sheet."""
        sheet = self.workbook.create_sheet("Carrier Services")

        # Headers
        headers = [
            "Service ID",
            "Service Name",
            "Active",
            "Service Discovery",
            "Carrier Name",
            "Admin Graphql API ID",
            "Format"
        ]
        sheet.append(headers)
        self._style_header_row(sheet)

        # Data rows
        for service in carrier_services:
            sheet.append([
                service.get('id', ''),
                service.get('name', ''),
                service.get('active', False),
                service.get('service_discovery', False),
                service.get('carrier_name', ''),
                service.get('admin_graphql_api_id', ''),
                service.get('format', '')
            ])

        self._auto_adjust_columns(sheet)
        logger.info(f"Created Carrier Services sheet with {len(carrier_services)} services")

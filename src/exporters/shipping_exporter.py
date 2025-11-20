"""Excel exporter for Shopify shipping data."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

logger = logging.getLogger(__name__)


class ShippingExporter:
    """Exports Shopify shipping data to formatted Excel files."""

    def __init__(self, output_dir: str = "exports"):
        """
        Initialize the exporter.

        Args:
            output_dir: Directory to save export files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_to_excel(self, data: Dict, filename: str = None) -> str:
        """
        Export shipping data to formatted Excel file.

        Args:
            data: Dictionary containing zones, rates, countries, carrier_services
            filename: Optional custom filename

        Returns:
            Path to created Excel file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"shopify_shipping_export_{timestamp}.xlsx"

        filepath = self.output_dir / filename

        logger.info(f"Creating Excel export: {filepath}")

        # Create workbook
        wb = Workbook()
        wb.remove(wb.active)  # Remove default sheet

        # Create sheets
        self._create_overview_sheet(wb, data)
        self._create_zones_sheet(wb, data['zones'])
        self._create_rates_sheet(wb, data['rates'])
        self._create_countries_sheet(wb, data['countries'])
        self._create_carrier_services_sheet(wb, data['carrier_services'])

        # Save workbook
        wb.save(filepath)
        logger.info(f"Excel file created: {filepath}")

        return str(filepath)

    def _create_overview_sheet(self, wb: Workbook, data: Dict):
        """Create overview summary sheet."""
        ws = wb.create_sheet("Overview", 0)

        # Title
        ws['A1'] = "Shopify Shipping Data Export"
        ws['A1'].font = Font(size=16, bold=True)

        # Export metadata
        row = 3
        ws[f'A{row}'] = "Export Date:"
        ws[f'B{row}'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        row += 2
        ws[f'A{row}'] = "Summary Statistics"
        ws[f'A{row}'].font = Font(size=14, bold=True)

        # Statistics
        stats = [
            ("Total Shipping Zones", len(data['zones'])),
            ("Total Shipping Rates", len(data['rates'])),
            ("Total Countries Covered", len(set(c['country_code'] for c in data['countries']))),
            ("Total Countries/Provinces Entries", len(data['countries'])),
            ("Total Carrier Services", len(data['carrier_services']))
        ]

        row += 2
        for label, value in stats:
            ws[f'A{row}'] = label
            ws[f'B{row}'] = value
            ws[f'A{row}'].font = Font(bold=True)
            row += 1

        # Rate type breakdown
        row += 2
        ws[f'A{row}'] = "Rate Types Breakdown"
        ws[f'A{row}'].font = Font(size=14, bold=True)

        rate_types = {}
        for rate in data['rates']:
            rate_type = rate['rate_type']
            rate_types[rate_type] = rate_types.get(rate_type, 0) + 1

        row += 2
        for rate_type, count in rate_types.items():
            ws[f'A{row}'] = f"{rate_type.replace('_', ' ').title()} Rates"
            ws[f'B{row}'] = count
            ws[f'A{row}'].font = Font(bold=True)
            row += 1

        # Adjust column widths
        ws.column_dimensions['A'].width = 35
        ws.column_dimensions['B'].width = 20

    def _create_zones_sheet(self, wb: Workbook, zones: List[Dict]):
        """Create shipping zones sheet."""
        ws = wb.create_sheet("Zones")

        # Headers
        headers = [
            'Zone ID', 'Zone Name', 'Profile ID', 'Profile Name',
            'Weight-Based Rates', 'Price-Based Rates', 'Carrier Rates'
        ]
        self._write_header_row(ws, headers)

        # Data rows
        for idx, zone in enumerate(zones, start=2):
            ws[f'A{idx}'] = zone.get('id')
            ws[f'B{idx}'] = zone.get('name')
            ws[f'C{idx}'] = zone.get('profile_id')
            ws[f'D{idx}'] = zone.get('profile_name')
            ws[f'E{idx}'] = len(zone.get('weight_based_shipping_rates', []))
            ws[f'F{idx}'] = len(zone.get('price_based_shipping_rates', []))
            ws[f'G{idx}'] = len(zone.get('carrier_shipping_rate_providers', []))

        # Auto-adjust column widths
        self._auto_adjust_columns(ws)

        logger.debug(f"Created Zones sheet with {len(zones)} zones")

    def _create_rates_sheet(self, wb: Workbook, rates: List[Dict]):
        """Create shipping rates sheet."""
        ws = wb.create_sheet("Rates")

        # Headers
        headers = [
            'Zone ID', 'Zone Name', 'Rate Type', 'Rate Name', 'Price',
            'Weight Low', 'Weight High', 'Min Order Subtotal', 'Max Order Subtotal',
            'Carrier Service ID', 'Flat Modifier', 'Percent Modifier'
        ]
        self._write_header_row(ws, headers)

        # Data rows
        for idx, rate in enumerate(rates, start=2):
            ws[f'A{idx}'] = rate.get('zone_id')
            ws[f'B{idx}'] = rate.get('zone_name')
            ws[f'C{idx}'] = rate.get('rate_type', '').replace('_', ' ').title()
            ws[f'D{idx}'] = rate.get('name', '')
            ws[f'E{idx}'] = rate.get('price', '')

            # Weight-based fields
            if rate.get('rate_type') == 'weight_based':
                ws[f'F{idx}'] = rate.get('weight_low', '')
                ws[f'G{idx}'] = rate.get('weight_high', '')

            # Price-based fields
            elif rate.get('rate_type') == 'price_based':
                ws[f'H{idx}'] = rate.get('min_order_subtotal', '')
                ws[f'I{idx}'] = rate.get('max_order_subtotal', '')

            # Carrier fields
            elif rate.get('rate_type') == 'carrier':
                ws[f'J{idx}'] = rate.get('carrier_service_id', '')
                ws[f'K{idx}'] = rate.get('flat_modifier', '')
                ws[f'L{idx}'] = rate.get('percent_modifier', '')

        # Auto-adjust column widths
        self._auto_adjust_columns(ws)

        logger.debug(f"Created Rates sheet with {len(rates)} rates")

    def _create_countries_sheet(self, wb: Workbook, countries: List[Dict]):
        """Create countries/provinces sheet."""
        ws = wb.create_sheet("Countries")

        # Headers
        headers = [
            'Zone ID', 'Zone Name', 'Country Code', 'Country Name',
            'Country Tax', 'Province Code', 'Province Name', 'Province Tax'
        ]
        self._write_header_row(ws, headers)

        # Data rows
        row = 2
        for country in countries:
            if country.get('provinces'):
                # Write row for each province
                for province in country['provinces']:
                    ws[f'A{row}'] = country.get('zone_id')
                    ws[f'B{row}'] = country.get('zone_name')
                    ws[f'C{row}'] = country.get('country_code')
                    ws[f'D{row}'] = country.get('country_name')
                    ws[f'E{row}'] = country.get('tax', 0)
                    ws[f'F{row}'] = province.get('province_code', '')
                    ws[f'G{row}'] = province.get('province_name', '')
                    ws[f'H{row}'] = province.get('tax', 0)
                    row += 1
            else:
                # Write country-only row
                ws[f'A{row}'] = country.get('zone_id')
                ws[f'B{row}'] = country.get('zone_name')
                ws[f'C{row}'] = country.get('country_code')
                ws[f'D{row}'] = country.get('country_name')
                ws[f'E{row}'] = country.get('tax', 0)
                row += 1

        # Auto-adjust column widths
        self._auto_adjust_columns(ws)

        logger.debug(f"Created Countries sheet with {len(countries)} entries")

    def _create_carrier_services_sheet(self, wb: Workbook, carrier_services: List[Dict]):
        """Create carrier services sheet."""
        ws = wb.create_sheet("Carrier Services")

        # Headers
        headers = [
            'Service ID', 'Name', 'Active', 'Service Discovery',
            'Carrier Service Type', 'Admin Graphql API ID', 'Format'
        ]
        self._write_header_row(ws, headers)

        # Data rows
        for idx, service in enumerate(carrier_services, start=2):
            ws[f'A{idx}'] = service.get('id')
            ws[f'B{idx}'] = service.get('name')
            ws[f'C{idx}'] = 'Yes' if service.get('active') else 'No'
            ws[f'D{idx}'] = 'Yes' if service.get('service_discovery') else 'No'
            ws[f'E{idx}'] = service.get('carrier_service_type', '')
            ws[f'F{idx}'] = service.get('admin_graphql_api_id', '')
            ws[f'G{idx}'] = service.get('format', '')

        # Auto-adjust column widths
        self._auto_adjust_columns(ws)

        logger.debug(f"Created Carrier Services sheet with {len(carrier_services)} services")

    def _write_header_row(self, ws, headers: List[str]):
        """Write and format header row."""
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        header_alignment = Alignment(horizontal="center", vertical="center")

        for col_num, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment

        # Freeze header row
        ws.freeze_panes = 'A2'

    def _auto_adjust_columns(self, ws):
        """Auto-adjust column widths based on content."""
        for column_cells in ws.columns:
            max_length = 0
            column = column_cells[0].column_letter

            for cell in column_cells:
                try:
                    if cell.value:
                        cell_length = len(str(cell.value))
                        if cell_length > max_length:
                            max_length = cell_length
                except:
                    pass

            adjusted_width = min(max_length + 2, 50)  # Max width of 50
            ws.column_dimensions[column].width = adjusted_width

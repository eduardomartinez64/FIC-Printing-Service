# Shopify Shipping Export Tool - Complete Guide

**Version**: 1.0
**Last Updated**: 2025-11-20

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Shopify API Setup](#shopify-api-setup)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [Understanding the Export](#understanding-the-export)
8. [Analysis Strategies](#analysis-strategies)
9. [Troubleshooting](#troubleshooting)
10. [Security Best Practices](#security-best-practices)

---

## Overview

The Shopify Shipping Export Tool is designed to help you analyze and consolidate your Shopify shipping profiles by exporting all shipping data to a formatted Excel file.

### What It Does

- Fetches all shipping zones from your Shopify store (200+ zones supported)
- Exports weight-based, price-based, and carrier shipping rates
- Maps geographic coverage (countries and provinces)
- Documents carrier service configurations
- Creates a professionally formatted Excel file with multiple sheets

### Use Cases

- **Zone Consolidation**: Identify duplicate or similar zones to merge
- **Rate Analysis**: Compare pricing across different zones
- **Geographic Review**: Understand which regions are covered by which zones
- **Audit & Documentation**: Create a snapshot of your current shipping configuration

---

## Prerequisites

### System Requirements

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection
- Shopify store with Admin access

### Required Permissions

You'll need admin access to your Shopify store to:
- Create a custom app
- Generate an Admin API access token
- Grant `read_shipping` scope

---

## Installation

### 1. Install Python Dependencies

From your project directory:

```bash
pip install -r requirements.txt
```

This will install:
- `requests` - For Shopify API communication
- `openpyxl` - For Excel file creation
- `python-dotenv` - For environment configuration

### 2. Verify Installation

Check that all dependencies are installed:

```bash
python -c "import requests, openpyxl, dotenv; print('All dependencies installed!')"
```

---

## Shopify API Setup

### Step 1: Access Shopify Admin

1. Log in to your Shopify store admin panel
2. Navigate to: **Settings** → **Apps and sales channels**
3. Click **Develop apps** (at the bottom of the page)

### Step 2: Create Custom App

1. Click **Create an app**
2. Enter app details:
   - **App name**: "Shipping Data Export" (or your preferred name)
   - **App developer**: Your email address
3. Click **Create app**

### Step 3: Configure API Scopes

1. Click **Configure Admin API scopes**
2. Scroll down to find **Shipping** section
3. Check the box for: `read_shipping`
   - This grants read-only access to shipping data
   - No write permissions are granted (safe for export)
4. Click **Save**

### Step 4: Install the App

1. Click the **API credentials** tab
2. Click **Install app**
3. Confirm the installation

### Step 5: Get Access Token

1. In the **API credentials** tab, find **Admin API access token**
2. Click **Reveal token once**
3. **IMPORTANT**: Copy this token immediately
   - It starts with `shpat_`
   - You won't be able to see it again
   - Store it securely

### Step 6: Get Your Store URL

Your store URL is typically: `your-store-name.myshopify.com`

Example: If your store is `sugarbearpro.myshopify.com`, that's your store URL.

---

## Configuration

### 1. Create Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

### 2. Edit Configuration

Open `.env` in your text editor and update the Shopify section:

```bash
# Shopify Configuration (for shipping export tool)
SHOPIFY_STORE_URL=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_your_actual_access_token_here
SHOPIFY_API_VERSION=2024-10
EXPORT_OUTPUT_DIR=exports
```

**Configuration Options:**

- **SHOPIFY_STORE_URL**: Your store's myshopify.com URL (required)
- **SHOPIFY_ACCESS_TOKEN**: The access token from Step 5 above (required)
- **SHOPIFY_API_VERSION**: Shopify API version (optional, default: 2024-10)
- **EXPORT_OUTPUT_DIR**: Where to save Excel files (optional, default: exports)

### 3. Verify Configuration

The tool will validate your configuration when you run it.

---

## Usage

### Basic Usage

Run the export tool:

```bash
python export_shopify_shipping.py
```

### What Happens

1. **Connection Test**: Verifies API credentials
2. **Data Fetch**: Retrieves all shipping zones, rates, countries
3. **Excel Export**: Creates formatted Excel file
4. **Output**: File saved to `exports/shopify_shipping_export_YYYYMMDD_HHMMSS.xlsx`

### Example Output

```
======================================================================
Shopify Shipping Data Export Tool
======================================================================
Store URL: sugarbearpro.myshopify.com
API Version: 2024-10
Output Directory: exports

Initializing Shopify service...
Testing Shopify API connection...
✓ Connected to Shopify store: Sugar Bear Pro
  Store URL: sugarbearpro.com
  Currency: USD

======================================================================
Starting comprehensive shipping data fetch
======================================================================
Fetching shipping zones...
✓ Found 203 shipping zones
Processing zone: United States
Processing zone: Canada
...

======================================================================
Data fetch complete!
  Zones: 203
  Rates: 1,847
  Countries: 421
  Carrier Services: 3
======================================================================

Creating Excel export: exports/shopify_shipping_export_20251120_143022.xlsx
✓ Excel file created: exports/shopify_shipping_export_20251120_143022.xlsx

======================================================================
✓ Export completed successfully!
======================================================================
Excel file: exports/shopify_shipping_export_20251120_143022.xlsx

Next steps:
  1. Open the Excel file
  2. Review the 'Overview' sheet for summary statistics
  3. Analyze zones and rates for consolidation opportunities
  4. See SHOPIFY_EXPORT_GUIDE.md for analysis tips
======================================================================
```

### Custom Output Location

To specify a custom output directory:

```bash
# In .env file
EXPORT_OUTPUT_DIR=/path/to/custom/directory
```

---

## Understanding the Export

The Excel file contains 5 sheets with different data views:

### Sheet 1: Overview

**Purpose**: High-level summary and statistics

**Contents**:
- Export date and timestamp
- Total counts (zones, rates, countries, carrier services)
- Rate type breakdown (weight-based, price-based, carrier)

**Use For**: Quick assessment of your shipping configuration scope

---

### Sheet 2: Zones

**Purpose**: List of all shipping zones

**Columns**:
- **Zone ID**: Unique identifier
- **Zone Name**: Zone display name
- **Profile ID**: Associated shipping profile
- **Profile Name**: Profile display name
- **Weight-Based Rates**: Count of weight-based rates
- **Price-Based Rates**: Count of price-based rates
- **Carrier Rates**: Count of carrier service rates

**Use For**:
- Finding zones with similar rate counts
- Identifying zones to merge
- Sorting by profile to group related zones

---

### Sheet 3: Rates

**Purpose**: Detailed shipping rate information

**Columns**:
- **Zone ID/Name**: Which zone this rate belongs to
- **Rate Type**: Weight Based | Price Based | Carrier
- **Rate Name**: Display name for the rate
- **Price**: Shipping cost
- **Weight Low/High**: For weight-based rates (in kg or lbs)
- **Min/Max Order Subtotal**: For price-based rates
- **Carrier Service ID**: For carrier-calculated rates
- **Flat/Percent Modifier**: Carrier rate adjustments

**Use For**:
- Comparing pricing across zones
- Finding duplicate rate structures
- Analyzing weight/price thresholds
- Identifying consolidation candidates

---

### Sheet 4: Countries

**Purpose**: Geographic coverage mapping

**Columns**:
- **Zone ID/Name**: Which zone covers this geography
- **Country Code**: ISO country code (US, CA, GB, etc.)
- **Country Name**: Full country name
- **Country Tax**: Tax percentage for country
- **Province Code**: State/province code (if applicable)
- **Province Name**: State/province name
- **Province Tax**: Tax percentage for province

**Use For**:
- Understanding geographic coverage
- Finding overlapping coverage
- Regional analysis
- Tax rate review

---

### Sheet 5: Carrier Services

**Purpose**: Third-party carrier configuration

**Columns**:
- **Service ID**: Unique identifier
- **Name**: Carrier service name
- **Active**: Yes/No status
- **Service Discovery**: Enabled/disabled
- **Carrier Service Type**: Type of carrier
- **Admin GraphQL API ID**: For API reference
- **Format**: Data format type

**Use For**:
- Documenting carrier integrations
- Reviewing active services
- API reference

---

## Analysis Strategies

### Finding Duplicate Zones

#### Strategy 1: Sort by Rate Counts

1. Open the **Zones** sheet
2. Sort by **Weight-Based Rates** column (ascending)
3. Look for zones with identical rate counts
4. Cross-reference with **Rates** sheet to compare actual rates

#### Strategy 2: Compare Rate Structures

1. Open the **Rates** sheet
2. Filter by **Zone Name** for first zone
3. Note the rate structure (prices, weights, thresholds)
4. Filter by **Zone Name** for second zone
5. Compare the structures side-by-side

**Example**: If "Zone A" and "Zone B" both have:
- Same number of weight-based rates
- Same price points
- Same weight thresholds
→ They are candidates for merging

---

### Identifying Mergeable Zones

#### Geographic Analysis

1. Open the **Countries** sheet
2. Create a pivot table:
   - Rows: Country Name
   - Columns: Zone Name
   - Values: Count of entries
3. Look for countries appearing in multiple zones with similar rates

#### Rate Similarity Analysis

1. Open the **Rates** sheet
2. Sort by **Price** column
3. Look for identical pricing patterns across different zones
4. Check if geographic coverage differs

**Consolidation Rule**: If two zones have:
- Identical rate structures
- Similar geographic coverage
- Same shipping profile
→ They can likely be merged

---

### Using Pivot Tables

#### Create Rate Summary by Zone

1. Select all data in **Rates** sheet
2. Insert → Pivot Table
3. Configuration:
   - Rows: Zone Name
   - Columns: Rate Type
   - Values: Count of Rates, Average of Price
4. Analyze for patterns

#### Geographic Coverage Summary

1. Select all data in **Countries** sheet
2. Insert → Pivot Table
3. Configuration:
   - Rows: Country Name
   - Columns: Zone Name
   - Values: Count of Provinces
4. Find overlapping coverage

---

### Excel Formulas for Analysis

#### Find Duplicate Rate Prices

```excel
=COUNTIF(E:E, E2) > 1
```
(Where E is the Price column)

#### Calculate Rate Variance

```excel
=STDEV(E2:E100)
```
(Shows price variation across rates)

#### Identify Gaps in Weight Ranges

```excel
=IF(G2<>F3, "Gap", "")
```
(Where F is Weight Low, G is Weight High of previous row)

---

## Troubleshooting

### Connection Issues

#### Error: "Failed to connect to Shopify API"

**Possible Causes**:
1. Incorrect store URL
2. Invalid access token
3. Token lacks required scope
4. Network/firewall issues

**Solutions**:
```bash
# Verify store URL format
SHOPIFY_STORE_URL=your-store.myshopify.com  # ✓ Correct
SHOPIFY_STORE_URL=https://your-store.myshopify.com  # ✓ Also works
SHOPIFY_STORE_URL=your-store.com  # ✗ Wrong

# Verify token format
SHOPIFY_ACCESS_TOKEN=shpat_abc123...  # ✓ Correct
SHOPIFY_ACCESS_TOKEN=abc123...  # ✗ Missing prefix
```

#### Error: "Token appears invalid"

**Solution**: Regenerate your access token:
1. Go to Shopify Admin → Apps → Your custom app
2. Uninstall and reinstall the app
3. Get a new access token
4. Update `.env` file

---

### Permission Issues

#### Error: "Access denied" or "403 Forbidden"

**Cause**: Missing `read_shipping` scope

**Solution**:
1. Go to your custom app settings
2. Configure Admin API scopes
3. Ensure `read_shipping` is checked
4. Save and reinstall the app
5. Get a new access token

---

### Rate Limiting

#### Warning: "Approaching rate limit, adding delay"

**What It Means**: The tool is automatically slowing down to respect Shopify's rate limits (2 requests/second)

**Normal Behavior**: This is expected for large stores with 100+ zones

**If It Takes Too Long**:
- The tool is working correctly
- For 200 zones, expect 5-10 minutes
- Do not interrupt the process

---

### Export Issues

#### Error: "Permission denied" when creating export file

**Solution**:
```bash
# Create exports directory manually
mkdir exports

# Or specify a different directory in .env
EXPORT_OUTPUT_DIR=/home/user/Documents/shopify_exports
```

#### Excel file is empty or corrupted

**Cause**: Data fetch failed silently

**Solution**:
1. Check the log file: `logs/shopify_export.log`
2. Look for API errors
3. Verify all data was fetched (zones, rates, countries)
4. Re-run the export

---

### Data Issues

#### Some zones are missing

**Possible Causes**:
1. Zones belong to different shipping profiles
2. API rate limiting caused incomplete fetch
3. Zones were created after initial fetch

**Solution**:
1. Check which profile you're exporting from
2. Re-run the export (it fetches all zones)
3. Check logs for any skipped zones

#### Countries/provinces are incomplete

**Solution**: The tool fetches detailed country data for each zone. If missing:
1. Verify the zone has countries assigned in Shopify
2. Check API permissions
3. Look for errors in `logs/shopify_export.log`

---

## Security Best Practices

### Protecting Your Access Token

#### Never Commit Tokens to Git

```bash
# Ensure .env is in .gitignore
echo ".env" >> .gitignore

# Verify it's ignored
git status  # Should not show .env
```

#### Use Environment Variables for Production

```bash
# Instead of .env file, set environment variables:
export SHOPIFY_STORE_URL="your-store.myshopify.com"
export SHOPIFY_ACCESS_TOKEN="shpat_your_token"
```

#### Rotate Tokens Regularly

1. Create a new access token every 90 days
2. Delete old tokens immediately
3. Update `.env` with new token

---

### Access Token Storage

#### On Ubuntu/Linux

```bash
# Restrict .env file permissions
chmod 600 .env

# Only owner can read/write
ls -l .env
# Output: -rw------- 1 user user ... .env
```

#### On Windows

1. Right-click `.env` file
2. Properties → Security
3. Advanced → Disable inheritance
4. Remove all users except yourself

---

### Audit Trail

#### Log All Exports

The tool automatically logs to `logs/shopify_export.log`:

```bash
# Review export history
cat logs/shopify_export.log

# Find exports from specific date
grep "2025-11-20" logs/shopify_export.log
```

#### Track Who Exports Data

If multiple team members use the tool:
1. Each should have their own Shopify custom app
2. Use different app names to identify who exported
3. Review app access in Shopify Admin regularly

---

## Advanced Usage

### Automating Exports

#### Weekly Export Script

```bash
#!/bin/bash
# weekly_export.sh

cd /path/to/FIC-Printing-Service
source venv/bin/activate
python export_shopify_shipping.py

# Archive old exports (keep last 4 weeks)
find exports/ -name "*.xlsx" -mtime +28 -delete
```

Add to crontab:
```bash
# Run every Monday at 9 AM
0 9 * * 1 /path/to/weekly_export.sh
```

---

### Custom Analysis Scripts

#### Example: Find Zones with Identical Rates

```python
import pandas as pd

# Read the export
excel_file = "exports/shopify_shipping_export_20251120_143022.xlsx"
rates_df = pd.read_excel(excel_file, sheet_name="Rates")

# Group by zone and create rate fingerprint
def create_fingerprint(group):
    return tuple(sorted(group['Price'].tolist()))

fingerprints = rates_df.groupby('Zone Name').apply(create_fingerprint)

# Find duplicates
duplicates = fingerprints[fingerprints.duplicated(keep=False)]
print("Zones with identical rate structures:")
print(duplicates)
```

---

## Appendix

### File Structure

```
FIC-Printing-Service/
├── export_shopify_shipping.py      # Main export script
├── src/
│   ├── services/
│   │   └── shopify_service.py      # Shopify API integration
│   └── exporters/
│       └── shipping_exporter.py    # Excel export logic
├── exports/                         # Export output directory
│   └── shopify_shipping_export_*.xlsx
├── logs/
│   └── shopify_export.log          # Export logs
├── .env                            # Configuration (not in git)
├── .env.example                    # Configuration template
└── requirements.txt                # Python dependencies
```

### API Rate Limits

Shopify API rate limits:
- **REST Admin API**: 2 requests/second
- **Burst**: Up to 40 requests
- **Retry**: 0.5 seconds between retries

The tool automatically handles rate limiting.

### Shopify API Documentation

- [Shopify Admin API](https://shopify.dev/docs/api/admin-rest)
- [Shipping Zones API](https://shopify.dev/docs/api/admin-rest/2024-10/resources/shipping-zone)
- [Authentication](https://shopify.dev/docs/apps/auth/admin-app-access-tokens)

---

## Support

### Getting Help

1. Check this guide's [Troubleshooting](#troubleshooting) section
2. Review logs in `logs/shopify_export.log`
3. Consult [TODO.md](TODO.md) for known issues
4. Check [CLAUDE.md](CLAUDE.md) for project context

### Reporting Issues

When reporting issues, include:
- Python version: `python --version`
- Error message from console
- Relevant log entries from `logs/shopify_export.log`
- Your configuration (with token redacted)

---

**End of Guide**

*Last Updated: 2025-11-20*
*Version: 1.0*

# Shopify Shipping Data Export Guide

## Overview

This tool exports your Shopify store's shipping configuration (zones, rates, countries) to a structured Excel file. This is particularly useful for:

- **Auditing** your current shipping setup
- **Consolidating** multiple zones (e.g., reducing from 200+ zones)
- **Analyzing** shipping costs and coverage
- **Documenting** your shipping configuration
- **Planning** changes before implementing them in Shopify

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install `openpyxl` (for Excel export) and other required packages.

### 2. Get Shopify API Credentials

You need to create a **Custom App** in your Shopify Admin to get API access:

#### Step-by-Step:

1. **Log into your Shopify Admin**
   - Go to: `https://your-store.myshopify.com/admin`

2. **Create a Custom App**
   - Navigate to: `Settings` → `Apps and sales channels` → `Develop apps`
   - Click: `Create an app`
   - Name it: "Shipping Data Exporter" (or any name you prefer)

3. **Configure API Scopes**
   - Go to: `Configuration` tab
   - Under "Admin API access scopes", enable:
     - ✅ `read_shipping` - Read shipping rates and zones
     - ✅ `read_locations` - Read store locations
   - Click: `Save`

4. **Install the App**
   - Go to: `API credentials` tab
   - Click: `Install app`
   - Confirm installation

5. **Get Your Access Token**
   - After installation, you'll see: **Admin API access token**
   - Click: `Reveal token once`
   - **⚠️ IMPORTANT**: Copy this token immediately! You can only see it once.
   - Save it securely in your `.env` file

### 3. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your Shopify credentials:

```bash
# Shopify Configuration
SHOPIFY_STORE_URL=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_your_access_token_here
SHOPIFY_API_VERSION=2024-10
```

**Notes:**
- Replace `your-store` with your actual store name
- Paste the access token you copied earlier
- API version `2024-10` is recommended (latest stable)

### 4. Run the Export

```bash
python export_shopify_shipping.py
```

Expected output:

```
🔗 Connecting to Shopify store: your-store.myshopify.com
✅ Successfully connected to Shopify

📦 Fetching shipping data...
   - Shipping zones...
   ✅ Found 200 shipping zones
   ✅ Found 15 countries
   ✅ Found 3 carrier services
   ✅ Found 450 total shipping rates

📊 Exporting to Excel: shopify_shipping_export_20241120_143022.xlsx

✅ Export completed successfully!

📁 File saved: shopify_shipping_export_20241120_143022.xlsx
```

## Excel Output Structure

The exported Excel file contains **5 sheets**:

### 1. Overview Sheet
- Export timestamp
- Summary statistics (total zones, rates, countries)
- Sheet descriptions

### 2. Zones Sheet
All shipping zones with counts:
- Zone ID
- Zone Name
- Number of Countries
- Number of Weight-Based Rates
- Number of Price-Based Rates
- Number of Carrier Rates
- Total Rates

**Use this to:** Identify zones with similar configurations that can be merged.

### 3. Rates Sheet
Detailed breakdown of ALL shipping rates:
- Zone ID & Name
- Rate Type (Weight-Based, Price-Based, or Carrier Service)
- Rate Name
- Min/Max Values (weight or price thresholds)
- Price
- Carrier Service (if applicable)

**Use this to:**
- Compare pricing across zones
- Find duplicate rate structures
- Identify consolidation opportunities

### 4. Countries Sheet
Countries and provinces included in each zone:
- Zone ID & Name
- Country Code & Name
- Province Code & Name (if specific provinces)
- Tax percentage

**Use this to:**
- See which countries/states are in which zones
- Identify overlapping geographic coverage
- Plan zone consolidation based on geography

### 5. Carrier Services Sheet
Third-party shipping carriers configured:
- Service ID & Name
- Active status
- Service Discovery enabled
- Carrier Name
- Format

**Use this to:** Understand which carrier services are integrated.

## Analyzing Your Data

### Finding Consolidation Opportunities

#### 1. Sort by Rate Count (Zones sheet)
- Zones with 1-2 rates might be candidates for merging
- Look for zones with identical rate counts

#### 2. Compare Rate Structures (Rates sheet)
- Use Excel's filter/sort to group by "Rate Type" and "Price"
- Find zones with identical pricing → can likely be merged
- Example: If Zone A and Zone B both have "$5 for 0-5 lbs", they might be mergeable

#### 3. Geographic Analysis (Countries sheet)
- Filter by country to see all zones covering that country
- Look for overlapping coverage that could be consolidated
- Example: Multiple zones for different US states could potentially become one zone

#### 4. Pivot Table Analysis
Create a pivot table to summarize:
- **Rows**: Zone Name
- **Values**: Count of Rates, Count of Countries
- **Filter**: Rate Type

This helps visualize which zones have similar characteristics.

### Example Consolidation Workflow

```
1. Open Excel file
2. Go to "Rates" sheet
3. Add Filter (Data → Filter)
4. Sort by "Price" column
5. Identify zones with same pricing structure
6. Check "Countries" sheet to verify geographic coverage doesn't conflict
7. Document zones to merge
8. Test consolidation in Shopify (start with 2-3 zones)
9. Re-export to verify changes
```

## Troubleshooting

### Error: "Failed to connect to Shopify"

**Possible causes:**
1. **Incorrect Store URL**
   - Verify format: `your-store.myshopify.com` (no https://)
   - Check for typos

2. **Invalid Access Token**
   - Regenerate token in Shopify Admin
   - Make sure you copied the entire token (starts with `shpat_`)

3. **Insufficient API Scopes**
   - Verify your app has `read_shipping` scope enabled
   - Reinstall the app after changing scopes

### Error: "SHOPIFY_STORE_URL not configured"

- Check your `.env` file exists
- Verify the variable names match exactly
- No spaces around the `=` sign

### Empty Excel File

- Your store might not have any shipping zones configured
- Check the logs: `logs/shopify_export.log`
- Verify in Shopify Admin: `Settings` → `Shipping and delivery`

### Rate Limiting

Shopify has API rate limits:
- **Standard**: 2 requests/second
- **Plus**: 4 requests/second

The tool makes minimal API calls (typically 3-4 total), so rate limiting is unlikely. If you see rate limit errors, wait 60 seconds and retry.

## Security Best Practices

1. **Never commit `.env` file to git**
   - It's already in `.gitignore`
   - Contains sensitive API tokens

2. **Rotate access tokens periodically**
   - Recommended: Every 90 days
   - Immediately if compromised

3. **Use minimum required scopes**
   - Only `read_shipping` is needed
   - Don't enable write permissions unless necessary

4. **Restrict app access**
   - Only install on stores you manage
   - Remove app access when no longer needed

## Advanced Usage

### Scheduled Exports

To automatically export weekly:

```bash
# Linux/Mac crontab
0 0 * * 0 cd /path/to/FIC-Printing-Service && python export_shopify_shipping.py

# This runs every Sunday at midnight
```

### Custom Output Filename

Modify `export_shopify_shipping.py` line 72:

```python
# Instead of timestamp, use custom name
output_file = "my_custom_export.xlsx"
```

### Export Specific API Version

Change in `.env`:

```bash
SHOPIFY_API_VERSION=2024-07  # Use older API version
```

## API Reference

### Shopify Admin API Endpoints Used

1. **GET `/admin/api/{version}/shop.json`**
   - Tests connection
   - Gets shop name

2. **GET `/admin/api/{version}/shipping_zones.json`**
   - Fetches all shipping zones with rates

3. **GET `/admin/api/{version}/countries.json`**
   - Fetches configured countries

4. **GET `/admin/api/{version}/carrier_services.json`**
   - Fetches carrier service integrations

### Rate Limit Headers

The tool respects Shopify's rate limiting. Each response includes:
- `X-Shopify-Shop-Api-Call-Limit`: Current usage (e.g., "2/40")

## Files Reference

- **Main script**: `export_shopify_shipping.py:1`
- **Shopify API service**: `src/services/shopify_service.py:1`
- **Excel exporter**: `src/exporters/shipping_exporter.py:1`
- **Configuration**: `.env` (create from `.env.example`)
- **Logs**: `logs/shopify_export.log`

## Support

### Common Questions

**Q: Will this modify my Shopify store?**
A: No. This tool only **reads** data. It cannot modify zones, rates, or any store settings.

**Q: How often can I run this?**
A: As often as needed. Each export is independent and doesn't affect your store.

**Q: Can I export from multiple stores?**
A: Yes. Change the credentials in `.env` between runs, or create multiple `.env` files.

**Q: What if I have 200+ zones?**
A: The tool handles any number of zones. Large exports may take 30-60 seconds.

**Q: Is my data secure?**
A: Yes. All data stays local on your machine. Nothing is sent to external services.

### Getting Help

1. Check logs: `logs/shopify_export.log`
2. Verify Shopify API credentials
3. Test connection in Shopify Admin: `Settings` → `Apps and sales channels` → `Develop apps`
4. Review this guide's Troubleshooting section

## Next Steps

After exporting:

1. **Analyze the data** using Excel filters and pivot tables
2. **Identify zones to consolidate** based on similar rates/geography
3. **Test in Shopify** - Start with merging 2-3 zones
4. **Re-export and verify** - Confirm changes worked as expected
5. **Iterate** - Gradually consolidate remaining zones

---

**Pro Tip**: Before making major changes to your Shopify shipping configuration, always export first to have a backup record of your current setup!

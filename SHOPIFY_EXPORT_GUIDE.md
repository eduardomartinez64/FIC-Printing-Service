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

The exported Excel file is organized **by shipping profile**, with each profile having its own tab. This makes it easy for your logistics team to review and optimize rates.

### Overview Sheet

The first sheet provides a summary:
- **Export timestamp** and date
- **Summary statistics**: Total profiles, zones, rates, carrier services
- **Profile breakdown table**: Shows each profile with its zone count, rate count, and sheet name
- **Navigation instructions**: How to use the export

### Profile Sheets (One per Shipping Profile)

Each shipping profile gets its own dedicated sheet with a **hierarchical, easy-to-read layout**:

#### Profile Sheet Structure:

```
[Profile Name]

📍 Zone Name 1
   Countries Served:
      • United States (All regions), Canada (Ontario, Quebec, ...)
      • United Kingdom (All regions)

   Shipping Rates (5 total):
      ┌─────────────────────────────┬─────────┬──────────────┬────────────────────────────┐
      │ Rate Name                   │ Price   │ Type         │ Rule / Description         │
      ├─────────────────────────────┼─────────┼──────────────┼────────────────────────────┤
      │ Standard Shipping           │ $5.00   │ Weight-Based │ Weight: 0 - 5 lbs         │
      │ Heavy Package               │ $15.00  │ Weight-Based │ Weight: 5 - 20 lbs        │
      │ Free Shipping               │ $0.00   │ Price-Based  │ Order value: $50+         │
      │ Express Shipping            │ $12.00  │ Weight-Based │ Weight: 0 - 10 lbs        │
      │ Carrier Calculated          │ Calc.   │ Carrier      │ Carrier: All services     │
      └─────────────────────────────┴─────────┴──────────────┴────────────────────────────┘

📍 Zone Name 2
   Countries Served:
      • Mexico (All regions), Brazil (Sao Paulo, Rio de Janeiro)

   Shipping Rates (3 total):
      [... rate table ...]
```

#### What Makes This Format Perfect for Review:

1. **Profile-Based Organization**: Each profile is isolated in its own sheet - no need to filter or search
2. **Visual Hierarchy**: Color-coded headers (blue for zones, green for sections) make scanning easy
3. **Clear Geographic Coverage**: See at a glance which countries/regions each zone serves
4. **Detailed Rate Information**:
   - **Rate Name**: What customers see
   - **Price**: Exact shipping cost
   - **Type**: Weight-Based, Price-Based, or Carrier Service
   - **Rule/Description**: Human-readable conditions (e.g., "Weight: 0-5 lbs", "Order value: $50+")
5. **Grouped by Zone**: All related information for each zone is together

#### Rate Description Examples:

The **Rule / Description** column automatically formats rate conditions for easy understanding:

- **Weight-Based**:
  - `Weight: 0 - 5 lbs`
  - `Weight: 10+ lbs`
- **Price-Based**:
  - `Order value: $0 - $50`
  - `Order value: $100+`
  - `All order values`
- **Carrier Service**:
  - `Carrier: All services (ID: 12345)`
  - `Carrier: Express, Overnight (ID: 67890)`

## Analyzing Your Data for Consolidation

### Step-by-Step Consolidation Workflow

#### Step 1: Review Each Profile

Start with the **Overview sheet** to see all your profiles:
1. Note which profiles have the most zones (prime candidates for consolidation)
2. Click through to each profile's sheet to review

#### Step 2: Identify Duplicate Rate Structures

Within each profile sheet:

**Method A - Visual Comparison:**
1. Scroll through zones in the profile
2. Look for zones with identical rate tables
3. Compare the "Price" and "Rule/Description" columns
4. If two zones have the same rates, they're merge candidates

**Example:**
```
Zone: US East Coast
  Standard: $5.00 (Weight: 0-5 lbs)
  Express: $12.00 (Weight: 0-10 lbs)

Zone: US West Coast
  Standard: $5.00 (Weight: 0-5 lbs)  ← Same rates!
  Express: $12.00 (Weight: 0-10 lbs) ← Same rates!
```
✅ These zones can likely be merged!

**Method B - Excel Analysis:**
1. Copy all rate data from a profile sheet
2. Paste into a new sheet
3. Sort by "Price" column
4. Use conditional formatting to highlight duplicates
5. Group zones with matching prices and rules

#### Step 3: Check Geographic Compatibility

Before merging zones with identical rates, verify their geographic coverage doesn't conflict:

1. Look at the **Countries Served** section for each zone
2. Ensure there's no overlap (same country in multiple zones)
3. If no overlap → safe to merge
4. If overlap → investigate why separate zones exist (might be intentional)

**Example - Safe to Merge:**
```
Zone A: United States, Canada
Zone B: United Kingdom, France
→ No overlap, can merge if rates are identical
```

**Example - Investigate First:**
```
Zone A: United States (California, New York)
Zone B: United States (Texas, Florida)
→ Same country, different states - might be intentional
```

#### Step 4: Document Consolidation Opportunities

Create a consolidation plan:

1. Open a new Excel sheet or document
2. For each merge opportunity, note:
   - Profile name
   - Zones to merge (list their names)
   - New zone name suggestion
   - Countries that will be covered
   - Rate structure (confirm all zones have same rates)
   - Estimated savings (number of zones reduced)

**Template:**
```
Profile: International Shipping
Merge: "Europe Zone 1" + "Europe Zone 2" + "Europe Zone 3"
Into: "Europe - All Countries"
Countries: UK, France, Germany, Italy, Spain, Netherlands
Rates: Standard $15 (0-5 lbs), Express $25 (0-10 lbs)
Savings: 3 zones → 1 zone (67% reduction)
```

#### Step 5: Prioritize by Impact

Focus on high-impact consolidations first:

1. **Large profile with many zones**: Start with profiles that have 50+ zones
2. **Simple rate structures**: Merge zones with 1-2 rates first (less risk)
3. **Geographic groups**: Merge regional zones (e.g., all European countries)
4. **Identical rates across zones**: These are the safest merges

### Example Consolidation Scenario

**Before:** 200 shipping zones across 3 profiles

**Analysis findings:**
- Profile 1 "Domestic Shipping": 150 zones for US states
  - 120 zones have identical rates: $5 (0-5 lbs), $10 (5-15 lbs)
  - Each state is a separate zone
  - **Consolidation**: Merge into 5 regional zones (Northeast, Southeast, Midwest, Southwest, West)
  - **Result**: 150 → 5 zones (97% reduction!)

- Profile 2 "International": 40 zones for different countries
  - 15 European zones all have same rates
  - 10 Asian zones have same rates
  - **Consolidation**: Create "Europe" and "Asia" zones
  - **Result**: 40 → 17 zones (58% reduction)

- Profile 3 "Express Shipping": 10 zones
  - Already optimized, no changes needed

**After:** 22 shipping zones total (89% reduction!)

### Common Patterns to Look For

When reviewing your 200 zones, look for these common over-segmentation patterns:

1. **State-by-state zones**: Most stores don't need separate zones per US state
2. **Duplicate international zones**: Multiple zones for same country with identical rates
3. **Historical zones**: Zones created for one-off promotions that are no longer used
4. **Test zones**: Zones created during setup but never removed
5. **Over-granular weight tiers**: Too many weight brackets (consolidate if possible)

### Quick Review Workflow

**For a 200-zone consolidation project:**

1. **Day 1**: Export data and review Overview sheet (30 min)
   - Identify which profiles have the most zones
   - Set consolidation targets (e.g., reduce by 75%)

2. **Day 2-3**: Profile-by-profile analysis (2-4 hours)
   - Open each profile sheet
   - Scroll through and mark zones with identical rates
   - Create consolidation plan document

3. **Day 4**: Geographic verification (1-2 hours)
   - Review countries served for each merge candidate
   - Confirm no conflicts

4. **Day 5**: Test in Shopify (2 hours)
   - Start with 5-10 zone merges
   - Verify functionality
   - Check customer checkout experience

5. **Week 2**: Full implementation (4-6 hours)
   - Execute consolidation plan in batches
   - Re-export after each batch to verify
   - Update documentation

6. **Week 3**: Monitor and optimize
   - Watch for any customer shipping issues
   - Fine-tune rates if needed
   - Re-export final configuration

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

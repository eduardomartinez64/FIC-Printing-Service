#!/usr/bin/env python3
"""Helper script to list available PrintNode printers."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if requests is available
try:
    import requests
except ImportError:
    print("Error: requests library not installed")
    print("Please install dependencies first:")
    print("  pip install requests python-dotenv")
    sys.exit(1)

# Get API key from environment
api_key = os.getenv('PRINTNODE_API_KEY')

if not api_key or api_key == 'your_printnode_api_key_here':
    print("Error: PRINTNODE_API_KEY not set in .env file")
    print("Please edit .env and add your PrintNode API key")
    sys.exit(1)

print("Connecting to PrintNode...")
print(f"API Key: {api_key[:10]}..." if len(api_key) > 10 else "API Key: [short key]")
print()

try:
    # Test connection
    response = requests.get(
        "https://api.printnode.com/whoami",
        auth=(api_key, '')
    )
    response.raise_for_status()
    user_info = response.json()
    print(f"✓ Connected as: {user_info.get('firstname', 'Unknown')} {user_info.get('lastname', '')}")
    print(f"  Email: {user_info.get('email', 'N/A')}")
    print()

    # Get printers
    response = requests.get(
        "https://api.printnode.com/printers",
        auth=(api_key, '')
    )
    response.raise_for_status()
    printers = response.json()

    if not printers:
        print("No printers found.")
        print()
        print("Make sure:")
        print("  1. PrintNode client is installed and running")
        print("  2. Your printer is connected and turned on")
        print("  3. The printer is visible in PrintNode dashboard")
        sys.exit(0)

    print(f"Found {len(printers)} printer(s):")
    print("=" * 80)

    for printer in printers:
        print(f"\nPrinter Name: {printer.get('name', 'Unknown')}")
        print(f"Printer ID:   {printer.get('id', 'N/A')} ← Use this in .env file")
        print(f"Computer:     {printer.get('computer', {}).get('name', 'N/A')}")
        print(f"Status:       {printer.get('state', 'unknown')}")
        print(f"Description:  {printer.get('description', 'N/A')}")

    print("\n" + "=" * 80)
    print("\nTo use a printer, copy its ID to your .env file:")
    print("  PRINTNODE_PRINTER_ID=<printer_id>")

except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("✗ Authentication failed")
        print("  Your API key is invalid")
        print("  Please check your PrintNode API key in .env file")
    else:
        print(f"✗ HTTP Error: {e}")
except requests.exceptions.RequestException as e:
    print(f"✗ Connection Error: {e}")
    print("  Check your internet connection")
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    sys.exit(1)

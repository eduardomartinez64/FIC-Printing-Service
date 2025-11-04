# Quick Setup Guide

Follow these steps to get the Gmail Email Processor Service running.

## Step 1: Install Python Virtual Environment Package

```bash
sudo apt install python3.12-venv
```

## Step 2: Create Virtual Environment and Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Set Up Gmail API Credentials

### 3.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name (e.g., "Gmail Email Processor")
4. Click "Create"

### 3.2 Enable Gmail API

1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click on "Gmail API"
4. Click "Enable"

### 3.3 Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" user type
   - Fill in required fields (app name, user support email)
   - Add your email to test users
   - Save and continue through all steps
4. Back at "Create OAuth client ID":
   - Application type: **Desktop app**
   - Name: "Gmail Email Processor"
   - Click "Create"
5. Download the credentials file
6. Rename it to `credentials.json`
7. Move it to the project root directory: `/home/emartinez/FIC-Printing-Service/credentials.json`

### 3.4 First-Time Authentication

When you first run the service:
1. It will open a browser window
2. Sign in with your Gmail account
3. Grant the requested permissions
4. The token will be saved to `token.json` for future use

## Step 4: Set Up PrintNode Account

### 4.1 Create PrintNode Account

1. Go to [PrintNode.com](https://www.printnode.com/)
2. Sign up for an account (free trial available)
3. Download and install the PrintNode client on the computer connected to your printer
4. The client will automatically detect your printers

### 4.2 Get API Key

1. Log in to PrintNode dashboard
2. Go to "Account" → "API Keys"
3. Click "Create API Key"
4. Copy the API key

### 4.3 Get Printer ID

1. In PrintNode dashboard, go to "Printers"
2. Find your desired printer
3. Note the Printer ID (it's a number)

OR use this Python script to list printers:

```python
import requests

api_key = "your_api_key_here"
response = requests.get(
    "https://api.printnode.com/printers",
    auth=(api_key, '')
)
printers = response.json()

for printer in printers:
    print(f"Name: {printer['name']}, ID: {printer['id']}")
```

### 4.4 Update .env File

Edit `/home/emartinez/FIC-Printing-Service/.env`:

```
PRINTNODE_API_KEY=your_actual_api_key_from_step_4.2
PRINTNODE_PRINTER_ID=your_printer_id_from_step_4.3
EMAIL_SUBJECT_FILTER=Batch Order Shipment Report
CHECK_INTERVAL_SECONDS=60
LOG_LEVEL=INFO
```

## Step 5: Run the Service

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the service
python main.py
```

You should see:
- Configuration validation
- Gmail authentication (first time only)
- PrintNode connection test
- Service starting and running checks every minute

## Step 6: Test the Service

Send yourself a test email with:
- Subject: "Batch Order Shipment Report"
- Attached CSV file with a PDF URL in column C, last row

Example CSV content:
```
Column A,Column B,Column C
Data 1,Data 2,https://www.example.com/sample.pdf
```

The service should:
1. Detect the email
2. Download the CSV
3. Extract the PDF URL
4. Print the PDF to your configured printer

## Troubleshooting

### "credentials.json not found"
- Make sure you downloaded the OAuth credentials from Google Cloud Console
- Rename it to `credentials.json`
- Place it in `/home/emartinez/FIC-Printing-Service/credentials.json`

### "PRINTNODE_API_KEY not set"
- Edit `.env` file and add your actual PrintNode API key
- Don't use quotes around the value

### "Printer not found"
- Verify the printer ID is correct
- Check that PrintNode client is running and printer is online
- Use the Python script above to list available printers

### "No emails found"
- Check the subject filter matches exactly
- Ensure Gmail API has the right permissions
- Check Gmail API quota in Google Cloud Console

## Running as a Service (Optional)

To run continuously in the background on Linux:

```bash
# Edit fic-printing-service.service file with correct paths
sudo nano fic-printing-service.service

# Copy to systemd
sudo cp fic-printing-service.service /etc/systemd/system/

# Enable and start service
sudo systemctl enable fic-printing-service
sudo systemctl start fic-printing-service

# Check status
sudo systemctl status fic-printing-service

# View logs
sudo journalctl -u fic-printing-service -f
```

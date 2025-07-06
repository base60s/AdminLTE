# Polymarket Price Monitoring Agent

An automated agent that monitors Polymarket prediction market prices and logs them to a Google Sheet at regular intervals.

## Features

- ✅ Fetches real-time prices from Polymarket API
- ✅ Automatically updates Google Sheets with price data
- ✅ Configurable update intervals (default: 10 minutes)
- ✅ Comprehensive logging and error handling
- ✅ Service account authentication for Google Sheets
- ✅ Easy configuration via environment variables

## Prerequisites

1. **Python 3.7+** installed on your system
2. **Google Cloud Project** with Sheets API enabled
3. **Google Service Account** with credentials JSON file
4. **Google Sheet** created and shared with the service account
5. **Polymarket Market ID** of the market you want to monitor

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Google Cloud Setup

#### Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"

#### Create a Service Account
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details
4. Click "Create and Continue"
5. Skip the optional steps and click "Done"

#### Download Credentials
1. Click on the created service account
2. Go to the "Keys" tab
3. Click "Add Key" > "Create New Key"
4. Choose "JSON" format
5. Download the file and save it as `credentials.json` in your project directory

### 3. Google Sheets Setup

#### Create a Google Sheet
1. Go to [Google Sheets](https://sheets.google.com/)
2. Create a new spreadsheet
3. Note the Sheet ID from the URL (the long string between `/d/` and `/edit`)

#### Share the Sheet
1. Click "Share" in your Google Sheet
2. Add the service account email (found in your `credentials.json` file)
3. Give it "Editor" permissions

### 4. Find Polymarket Event or Market Slug

1. Go to [Polymarket](https://polymarket.com/)
2. Navigate to the event or specific market you want to monitor
3. Copy the slug from the URL:
   - For events: `https://polymarket.com/event/will-trump-win-2024` → slug is `will-trump-win-2024`
   - For specific markets: `https://polymarket.com/event/will-trump-win-2024/will-trump-get-over-270-electoral-votes` → slug is `will-trump-get-over-270-electoral-votes`

### 5. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your configuration:
   ```env
   POLYMARKET_EVENT_SLUG=will-trump-win-2024
   POLYMARKET_MARKET_SLUG=will-trump-get-over-270-electoral-votes
   GOOGLE_SHEET_ID=your_actual_sheet_id
   GOOGLE_SHEET_NAME=Polymarket Prices
   GOOGLE_CREDENTIALS_FILE=credentials.json
   UPDATE_INTERVAL_MINUTES=10
   LOG_LEVEL=INFO
   LOG_FILE=polymarket_agent.log
   ```
   
   **Note:** You only need to set either `POLYMARKET_EVENT_SLUG` OR `POLYMARKET_MARKET_SLUG`, not both. Use `POLYMARKET_MARKET_SLUG` for a specific market, or `POLYMARKET_EVENT_SLUG` to monitor the first market in an event.

## Usage

### Start the Agent

Run the agent in continuous monitoring mode:

```bash
python polymarket_agent.py
```

The agent will:
1. Run an initial price update
2. Schedule updates every 10 minutes (or your configured interval)
3. Log all activities to the console and log file

### Test Your Configuration

Before running the full agent, test your configuration:

```bash
python test_configuration.py
```

This will verify that:
- Your environment variables are set correctly
- You can connect to the Polymarket API
- You can connect to Google Sheets
- The end-to-end data flow works

### Run a Single Update (Testing)

To test the setup, you can run a single update:

1. Edit `polymarket_agent.py` and comment/uncomment the appropriate lines in the `main()` function:
   ```python
   # Option 1: Run continuous monitoring (recommended for production)
   # agent.start_monitoring()
   
   # Option 2: Run a single update (useful for testing)
   agent.run_single_update()
   ```

2. Run the script:
   ```bash
   python polymarket_agent.py
   ```

### Check Agent Status

To check the agent status:

1. Edit `polymarket_agent.py` and use the status option:
   ```python
   # Option 3: Get status
   status = agent.get_status()
   print(f"Agent Status: {status}")
   ```

## File Structure

```
polymarket-agent/
├── polymarket_agent.py         # Main agent script
├── config.py                   # Configuration management
├── polymarket_client.py        # Polymarket API client
├── google_sheets_client.py     # Google Sheets API client
├── test_configuration.py       # Configuration test script
├── setup.py                   # Setup and installation helper
├── requirements.txt           # Python dependencies
├── .env.example              # Example environment file
├── .env                      # Your environment configuration (create this)
├── credentials.json          # Google service account credentials (download this)
├── polymarket_agent.log      # Log file (created automatically)
└── README_POLYMARKET_AGENT.md # This file
```

## Configuration Options

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `POLYMARKET_EVENT_SLUG` | Event slug from Polymarket URL | One of event/market slug | - |
| `POLYMARKET_MARKET_SLUG` | Market slug from Polymarket URL | One of event/market slug | - |
| `GOOGLE_SHEET_ID` | Google Sheet ID from URL | Yes | - |
| `GOOGLE_SHEET_NAME` | Name of the sheet tab | No | "Polymarket Prices" |
| `GOOGLE_CREDENTIALS_FILE` | Path to service account JSON | No | "credentials.json" |
| `UPDATE_INTERVAL_MINUTES` | Update frequency in minutes | No | 10 |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No | INFO |
| `LOG_FILE` | Path to log file | No | "polymarket_agent.log" |

## Google Sheets Output Format

The agent will create a Google Sheet with the following columns:

| Column | Description |
|--------|-------------|
| timestamp | ISO format timestamp of the update |
| market_title | Title/question of the Polymarket market |
| market_slug | Polymarket market slug |
| condition_id | Market condition ID (internal identifier) |
| category | Market category (e.g., "Politics", "Sports") |
| end_date | Market end date |
| active | Whether the market is currently active |
| closed | Whether the market is closed |
| [Outcome]_price | Price/probability for each outcome (e.g., "Yes_price", "No_price") |

## Troubleshooting

### Common Issues

1. **"Configuration validation failed"**
   - Check that all required environment variables are set
   - Verify that the credentials.json file exists

2. **"Failed to authenticate with Google Sheets API"**
   - Verify that the credentials.json file is valid
   - Check that the Google Sheets API is enabled in your project

3. **"Error writing to sheet"**
   - Ensure the service account has edit permissions on the sheet
   - Verify the Google Sheet ID is correct

4. **"Error fetching market data"**
   - Check that the Polymarket event or market slug is correct
   - Verify the slug exists in the URL when you visit the market
   - Verify internet connectivity

### Enable Debug Logging

Set `LOG_LEVEL=DEBUG` in your `.env` file for more detailed logs.

### Check Logs

Monitor the log file for detailed information:

```bash
tail -f polymarket_agent.log
```

## Running in Production

### Using Screen (Linux/macOS)

```bash
screen -S polymarket-agent
python polymarket_agent.py
# Press Ctrl+A, then D to detach
```

To reattach:
```bash
screen -r polymarket-agent
```

### Using systemd (Linux)

Create a service file `/etc/systemd/system/polymarket-agent.service`:

```ini
[Unit]
Description=Polymarket Price Monitoring Agent
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/your/polymarket-agent
ExecStart=/usr/bin/python3 polymarket_agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable polymarket-agent
sudo systemctl start polymarket-agent
```

## Security Considerations

- Keep your `credentials.json` file secure and never commit it to version control
- Store your `.env` file securely and don't share it publicly
- Regularly rotate your service account keys
- Monitor the logs for any unusual activity

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the log files for error messages
3. Verify your configuration matches the setup instructions
4. Ensure all prerequisites are properly installed

## License

This project is open source and available under the MIT License.
# OSRS Grand Exchange Price Monitor

A modern, professional Python application for monitoring Old School RuneScape Grand Exchange prices and alerting on significant price deviations.

## Features

- **Real-time Price Monitoring**: Fetches prices from the official OSRS Wiki API every 15 minutes (configurable)
- **Statistical Analysis**: Calculates mean, standard deviation, and tracks price deviations
- **Smart Alerts**: Alerts when prices deviate beyond a threshold (default: 1 standard deviation)
- **Windows Toast Notifications**: Desktop notifications for price alerts
- **Item Search**: Search from 20,000+ tradeable OSRS items
- **Sortable Table**: View and sort monitored items by any column
- **Persistent Data**: Saves watchlist, price history, and settings between sessions
- **Modern UI**: Dark-themed, professional interface using CustomTkinter

## Screenshots

The application provides:
- A searchable item database
- Real-time price tracking table with sorting
- Configurable monitoring settings
- Visual and toast notifications for alerts

## Installation

### Prerequisites

- Python 3.8 or higher
- Windows OS (for toast notifications - optional on other platforms)

### Setup

1. **First Time Installation**:
   ```bash
   # Run the installer (Windows)
   install.bat
   
   # Or manually:
   pip install -r requirements.txt
   python download_items.py
   ```

2. **Run the application**:
   ```bash
   # Windows
   run.bat
   
   # Or manually
   python osrs_price_monitor.py
   ```

Note: `install.bat` only needs to be run once. After that, use `run.bat` to start the app quickly.

## Usage

### First Launch

On first launch, the application will:
1. Download the item database from OSRSBox (~1MB, cached locally)
2. Create necessary data files in the same directory

### Adding Items to Monitor

1. Type an item name in the search box (e.g., "Shark", "Saradomin brew")
2. Click on the item from the search results, or
3. Type the exact name and click "Add to Watchlist"

**Example Items**:
- Shark (ID: 385)
- Saradomin brew(4) (ID: 6685)
- Abyssal whip (ID: 4151)
- Nature rune (ID: 561)

### Monitoring

1. **Configure Settings**:
   - **Threshold (σ)**: Standard deviations for alerts (default: 1.0)
   - **Interval (min)**: How often to check prices (default: 15 minutes)
   - Click "Save Settings" to persist changes

2. **Start Monitoring**:
   - Click "Start Monitoring" to begin automatic price checks
   - Click "Check Now" for an immediate price check
   - Click "Stop Monitoring" to pause

3. **View Results**:
   - The table shows: Item name, current price, average, standard deviation, deviation in σ, percentage change, and status
   - Click column headers to sort
   - Items with alerts show "⚠️ ALERT!" status

4. **Remove Items**:
   - Right-click on any item in the table
   - Select "Remove from Watchlist"

### Alerts

When a price deviates beyond the threshold:
- Visual indicator appears in the table (⚠️ ALERT!)
- Windows toast notification appears (if available)
- Notification shows current price, average price, and deviation

## How It Works

### Statistical Analysis

1. **Price Collection**: Every check interval, the app fetches current prices from the OSRS Wiki API
2. **Historical Tracking**: Prices are stored locally (up to 1000 entries per item)
3. **Mean Calculation**: Average price across all collected data points
4. **Standard Deviation**: Measures price volatility
5. **Deviation Score**: (Current Price - Mean) / Standard Deviation
6. **Alert Trigger**: When |Deviation| >= Threshold

### Data Storage

The application creates these files:
- `item_mapping.json`: Cached item database (ID to name mapping)
- `watchlist.json`: Your monitored items list
- `price_history.json`: Historical price data
- `settings.json`: Your preferences (threshold, interval)

All data persists between sessions.

## Item IDs

The application uses item IDs from the OSRS game. To find item IDs:

1. **Search in the app**: Type the item name to find its ID
2. **OSRS Wiki**: Visit [oldschool.runescape.wiki](https://oldschool.runescape.wiki)
3. **OSRSBox**: Browse [OSRSBox Item Database](https://www.osrsbox.com/osrsbox-db/)

### Common Item IDs

| Item | ID |
|------|-----|
| Shark | 385 |
| Saradomin brew(4) | 6685 |
| Abyssal whip | 4151 |
| Twisted bow | 20997 |
| Dragon bones | 536 |
| Nature rune | 561 |
| Cannonball | 2 |

## API Information

This application uses:
- **OSRS Wiki Prices API**: `https://prices.runescape.wiki/api/v1/osrs/latest`
  - Real-time price data from the Grand Exchange
  - Requires User-Agent header
  
- **OSRSBox Database**: `https://osrsbox.github.io/osrsbox-db/items-summary.json`
  - Item ID to name mappings
  - Cached locally after first download

## Configuration

### Threshold

The threshold determines how sensitive alerts are:
- **0.5**: Very sensitive (many alerts)
- **1.0**: Balanced (recommended)
- **2.0**: Only major price swings
- **3.0**: Only extreme changes

### Update Interval

- Minimum: 1 minute (not recommended - may strain API)
- Recommended: 15 minutes
- For casual monitoring: 30-60 minutes

## Troubleshooting

### "Loaded 0 items" or search not working

If the app shows "Loaded 0 tradeable items" or search doesn't show results:

**Solution 1: Download items manually**
```bash
python download_items.py
```
This will download the complete item database (~4000 items) and save it as `item_mapping.json`.

**Solution 2: Use the fallback list**
The app includes ~100 popular items as a fallback. Just restart the app and it will use these automatically if the download fails.

**Solution 3: Provide your own mapping file**
1. Download the item mapping from: `https://prices.runescape.wiki/api/v1/osrs/mapping`
2. Save it as `osrs_items_manual.json` in the same folder as the app
3. Restart the app

### "Error fetching item database"
- Check internet connection
- OSRSBox API might be down
- Application will use fallback common items

### "Error fetching prices"
- Check internet connection
- OSRS Wiki API might be rate-limiting
- Verify User-Agent header compliance

### Toast notifications not working
- Ensure `winotify` is installed: `pip install winotify`
- Notifications only work on Windows
- Check Windows notification settings

### Price history not persisting
- Check write permissions in application directory
- Ensure `price_history.json` is not read-only

## Performance

- Memory usage: ~50-100 MB
- Network usage: ~10 KB per price check
- Disk usage: ~1-5 MB for all data files

## Limitations

- Only tracks tradeable items (non-tradeable items not available via API)
- Price accuracy depends on OSRS Wiki API data
- Requires at least 2 data points to calculate statistics
- Toast notifications are Windows-only

## Credits

- **OSRS Wiki**: Price data API
- **OSRSBox**: Item database
- **CustomTkinter**: Modern UI framework
- **winotify**: Windows toast notifications

## License

This is a personal-use monitoring tool. Please comply with:
- OSRS Wiki API terms of use
- OSRSBox data usage guidelines
- Jagex's rules regarding third-party tools

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Ensure you have Python 3.8+

## Disclaimer

This tool is for personal use only. It does not interact with the OSRS game client and only reads publicly available price data. Use responsibly and in accordance with Jagex's rules.

# OSRS Price Tracker

A Python application that monitors Old School RuneScape item prices with a modern dark-themed GUI. Automatically fetches current prices from the official OSRS website and tracks changes.

## Features

- **Real-time Price Tracking** — Fetch current prices directly from the OSRS website
- **Persistent Storage** — All data automatically saves to `osrs_tracker_data.json`
- **Item Management** — Add, remove, edit, and reorder tracked items
- **Quantity Tracking** — Calculate total portfolio value (price × quantity)
- **Price Changes** — View percentage changes with color-coded indicators
- **Clean UI** — Dark theme with threaded updates for smooth responsiveness
- **Editable Fields** — Double-click any item to modify details

## Installation

1. Ensure Python 3.6+ is installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

**Launch the application:**
```bash
python osrs_price_tracker.pyw
```

**Core Operations:**
- **Update Prices** — Click "Update Prices" to fetch latest prices from OSRS
- **Add Item** — Provide item name, OSRS item URL, reference price, and quantity
- **Edit Item** — Double-click any row to modify details
- **Remove Item** — Select item and confirm deletion
- **Reorder** — Use "Move Up" / "Move Down" buttons to rearrange

**Tips:**
- Find OSRS item URLs at: `https://secure.runescape.com/m=itemdb_oldschool/`
- Reference price is your baseline for comparison
- All changes save automatically
- Prices update with threaded requests for a responsive interface

## Data Format

Tracked data is stored in `osrs_tracker_data.json` with the following per-item structure:
```json
{
  "name": "Item Name",
  "url": "https://secure.runescape.com/...",
  "reference_price": 1000,
  "quantity": 10,
  "current_price": 0,
  "change_1m": 0,
  "last_updated": "2025-01-01 12:00:00"
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Prices show "N/A" or "Loading..." | Check internet connection; OSRS website may be temporarily unavailable |
| Items not saving | Ensure write permissions in application directory |
| Prices not updating | Verify OSRS item URLs are correct; check network connectivity |

## Requirements

- Python 3.6+
- `requests` library (for HTTP requests)
- `tkinter` (included with Python)

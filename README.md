# OSRS Price Tracker

A modern Python application that tracks Old School RuneScape (OSRS) item prices with a clean, dark-themed GUI.

## Features

- **Real-time Price Tracking**: Scrapes current prices from the official OSRS website
- **Persistent Data**: All settings, reference prices, and quantities are saved between sessions
- **Item Management**: Add, remove, and reorder items in your tracking list
- **Editable Fields**: Double-click any item to edit its name, URL, reference price, or quantity
- **Percentage Change**: Shows price changes with color-coded indicators (green for positive, red for negative)
- **Total Value Calculation**: Displays total value based on current price × quantity
- **Modern UI**: Dark theme with intuitive controls and visual feedback

## Installation

1. Make sure you have Python 3.6 or higher installed
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python osrs_price_tracker.py
   ```

2. **Update Prices**: Click the "Update Prices" button to fetch current prices from the OSRS website

3. **Add Items**: Click "Add Item" to add new items to track. You'll need:
   - Item name (as you want it displayed)
   - OSRS website URL for that item
   - Reference price (your target/comparison price)
   - Quantity (how many you're tracking)

4. **Edit Items**: Double-click any item in the list to edit its details

5. **Remove Items**: Select an item and click "Remove Item" (with confirmation)

6. **Reorder Items**: Select an item and use "Move Up" or "Move Down" buttons

## Data Storage

The application saves all your data in `osrs_tracker_data.json` in the same directory as the script. This includes:
- Item names and URLs
- Reference prices and quantities
- Current prices and last update times
- Item order in the list

## Default Items

The application comes pre-loaded with popular OSRS items including:
- Torstol Seed
- Dragon Pickaxe
- Anglerfish
- Blighted Ice Sack
- Dragon Arrow
- Bond
- Spirit Shield
- Black Chinchompa

## Price Scraping

The application uses the same robust price extraction logic as the original AHK script, with multiple fallback patterns to ensure reliable price detection from the OSRS website.

## UI Features

- **Dark Theme**: Easy on the eyes with a modern dark color scheme
- **Color-coded Changes**: Green for price increases, red for decreases
- **Status Updates**: Real-time status updates during price fetching
- **Threaded Updates**: Price updates run in background threads to keep UI responsive
- **Formatted Numbers**: All prices display with comma separators for readability

## Troubleshooting

- If prices show as "Loading..." or "N/A", the website might be temporarily unavailable
- Make sure you have an internet connection for price updates
- The application includes error handling for network issues and invalid responses
- Data is automatically saved after any changes

## Key Improvements Over AHK Version

- **Interactive GUI**: Full mouse and keyboard interaction
- **Persistent Settings**: All data saves automatically
- **Item Management**: Easy add/remove/edit functionality
- **Quantity Tracking**: Track multiple quantities of items
- **Total Value**: See total portfolio value
- **Better Error Handling**: Graceful handling of network issues
- **Modern Design**: Clean, professional appearance

# OSRS Price Monitor - Quick Start Guide

## Installation (Windows)

1. **First Time Setup**: Double-click `install.bat`
   - This installs all dependencies
   - Downloads the item database (~4000 items)
   - Only needs to be run once

2. **Running the App**: Double-click `run.bat`
   - Use this every time you want to start the app
   - Much faster than install.bat

3. **Manual Method**:
   ```bash
   # First time only
   pip install -r requirements.txt
   python download_items.py
   
   # Every time
   python osrs_price_monitor.py
   ```

## First Time Setup

1. **Download Item Database** (if needed)
   - If search doesn't work, run: `python download_items.py`
   - This downloads ~4000 OSRS items from the official API
   - If download fails, the app has ~100 popular items as fallback

2. **Add Items to Monitor**
   - Type an item name in the search box (e.g., "Shark")
   - Click the item from the dropdown results
   - Repeat for all items you want to track

3. **Configure Settings** (optional)
   - **Threshold**: How many standard deviations trigger an alert (default: 1.0)
   - **Interval**: Minutes between price checks (default: 15)
   - Click "Save Settings"

4. **Start Monitoring**
   - Click the green "Start Monitoring" button
   - Price checks will run automatically every 15 minutes
   - Use "Check Now" for immediate updates

## Understanding the Display

### Table Columns
- **Item**: Item name  
- **Current Price**: Latest price from API
- **Average**: Mean price from YOUR collected data (this session)
- **Std Dev**: Standard deviation in GP (absolute price volatility)
- **Volatility %**: Std Dev as percentage of average (relative volatility)
- **Deviation (σ)**: How many standard deviations from average
- **Change %**: Percentage change from YOUR session average
- **Status**: "Collecting data...", "Normal", or "⚠️ ALERT!"

### Understanding "Average" and "Change %"

**Important:** These values are calculated from the prices YOU'VE collected while running the app, NOT from historical API data.

**Why this is useful:**
- Shows how items perform during YOUR active monitoring session
- Detects deviations from YOUR observed baseline  
- Perfect for active trading/flipping sessions
- Not misleading - it's clear these are YOUR collected data points

**For long-term historical comparison:**
- **Double-click any item** to see full historical price charts
- Choose from: 30 hours, 15 days, 90 days, or 1 year
- Uses official OSRS Wiki historical timeseries data

### Price History Charts (Double-Click Feature)

**Double-click any item in the table** to open an interactive price chart!

**Time Period Options:**
- **30 Hours** (5-min intervals) - Intraday trading patterns
- **15 Days** (1-hour intervals) - Weekly trends
- **90 Days** (6-hour intervals) - Quarterly view
- **1 Year** (24-hour intervals) - Long-term analysis

**Chart Shows:**
- Green line: High (buy) prices over time
- Red line: Low (sell) prices over time
- Yellow fill: Spread between high/low
- Dashed lines: Period averages
- Stats box: Average prices, spread, current price

This historical data comes directly from the OSRS Wiki API and shows REAL trading activity (not your local data).

### Understanding Volatility %

This shows how volatile an item is **relative to its price**:
- **< 2%**: Very stable (e.g., cheap, commonly traded items)
- **2-5%**: Moderate volatility (normal for most items)
- **5-10%**: High volatility (good for flipping)
- **> 10%**: Extreme volatility (high risk/reward)

**Example:**
- Item A: 1000 gp, Std Dev 50 gp → Volatility = 5.0%
- Item B: 100M gp, Std Dev 5M gp → Volatility = 5.0%

Both have the same **relative** volatility (5%), even though Item B swings by millions!

This helps you compare how "active" different items are, regardless of their price.

## Trading Insights

### Finding Good Flip Opportunities

**Sort by Volatility %** to find active items:
- High volatility (>5%) = more price movement = more flip opportunities
- But also higher risk!

**Sort by Deviation (σ)** to find current deals:
- Large negative deviation (like -2.0σ) = price is unusually LOW → possible buy opportunity
- Large positive deviation (like +2.0σ) = price is unusually HIGH → possible sell opportunity

**Sort by Change %** to see current movers:
- Items with large % changes are moving NOW
- Combine with volatility to understand if it's normal or unusual

### Strategy Tips

1. **Stable Items** (low volatility): Good for consistent, small margins
2. **Volatile Items** (high volatility): Higher risk but bigger potential profits
3. **Alert on 1.0σ**: Catches most significant moves without too many false alarms
4. **Alert on 0.5σ**: More sensitive, catches smaller moves (more alerts)
5. **Alert on 2.0σ**: Only extreme moves (fewer alerts, bigger opportunities)

### Example Scenarios

**Scenario 1: Buy Low**
- Item shows -1.5σ deviation
- Price is 15% below average
- High volatility (6%) means it often bounces back
- → Consider buying

**Scenario 2: Sell High**
- Item shows +2.0σ deviation  
- Price is 20% above average
- Moderate volatility (3%) suggests this is unusual
- → Consider selling

**Scenario 3: Avoid**
- Item shows +1.0σ deviation
- But volatility is 15% (very unstable)
- Could go higher OR crash down
- → Too risky for most traders

### Status Meanings

**"Collecting data..."**
- First price check for this item
- Need at least 2 data points to calculate statistics
- Click "Check Now" again in a few minutes to get statistics

**"Normal"**
- Price is within threshold (default: 1.0σ)
- No alert needed

**"⚠️ ALERT!"**
- Price has deviated beyond threshold
- Check the Deviation column to see how far off it is

### When Do Alerts Trigger?

An alert triggers when: `|Deviation| >= Threshold`

**Example**: 
- Threshold set to 1.0
- Item average price: 10,000 gp
- Item std dev: 500 gp
- Alert triggers when price goes below 9,500 or above 10,500

### Sorting
- Click any column header to sort by that column
- Click again to reverse the sort (▲ ascending, ▼ descending)

### Removing Items
Right-click on any item → "Remove from Watchlist"

## Recommended Items to Monitor

### High-Value Items (Large price swings)
- Twisted bow
- Scythe of vitur
- Avernic defender hilt

### Commonly Traded
- Shark
- Dragon bones
- Nature rune
- Cannonball

### Potions
- Saradomin brew(4)
- Super restore(4)
- Prayer potion(4)

## Tips

1. **Let it collect data**: The app needs at least 2 price points to calculate statistics. The more data it has, the better the analysis.

2. **Use the price charts**: Double-click any item to see historical trends. This helps you:
   - Identify if current prices are historically high or low
   - Spot seasonal patterns or trends
   - Decide if a deviation is a real opportunity or normal fluctuation

3. **Adjust threshold**: 
   - Start with 1.0
   - If too many alerts: increase to 1.5 or 2.0
   - If missing opportunities: decrease to 0.5

3. **Check interval**: 
   - 15 minutes is recommended
   - Don't set too low (< 5 minutes) to avoid API rate limits
   - For casual monitoring, 30-60 minutes works well

4. **Windows notifications**:
   - Make sure Windows notifications are enabled
   - Check the notification appears in bottom-right corner
   - Sound alerts help when app is in background

## Troubleshooting

**No items showing in search?**
- Wait for item database to download
- Check console for errors
- Try restarting the app

**"Error fetching prices"?**
- Check internet connection
- API might be temporarily down
- Wait a few minutes and try again

**No toast notifications?**
- Windows only feature
- Check Windows notification settings
- Ensure winotify is installed

**Data not saving?**
- Check folder permissions
- Don't run from read-only location (like CD/DVD)
- Ensure you have disk space

## File Structure

After running, these files are created:
```
osrs_price_monitor.py     # Main application
requirements.txt          # Dependencies
README.md                 # Full documentation
run.bat                   # Easy launcher
item_mapping.json         # Item database cache
watchlist.json           # Your monitored items
price_history.json       # Historical prices
settings.json            # Your preferences
```

## Support

See README.md for full documentation, troubleshooting, and advanced features.

Happy flipping! 📈
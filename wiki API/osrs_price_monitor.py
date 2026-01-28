"""
OSRS Grand Exchange Price Monitor
Tracks item prices and alerts on significant deviations
"""

import requests
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
import statistics
from typing import Dict, List, Optional
import customtkinter as ctk
from tkinter import messagebox
import tkinter.ttk as ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates

try:
    from winotify import Notification, audio
    TOAST_AVAILABLE = True
except ImportError:
    TOAST_AVAILABLE = False
    print("Warning: winotify not available. Install with: pip install winotify")


class PriceMonitor:
    """Handles price data fetching and statistical analysis"""
    
    def __init__(self):
        self.api_url = "https://prices.runescape.wiki/api/v1/osrs/latest"
        self.headers = {'User-Agent': 'OSRS Price Monitor - Personal Use'}
        self.price_history: Dict[int, List[int]] = {}
        
    def fetch_current_prices(self) -> Optional[Dict]:
        """Fetch latest prices from OSRS Wiki API"""
        try:
            response = requests.get(self.api_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()['data']
        except Exception as e:
            print(f"Error fetching prices: {e}")
            return None
    
    def fetch_timeseries(self, item_id: int, timestep: str = '6h') -> Optional[List[Dict]]:
        """
        Fetch historical price data for an item
        
        Args:
            item_id: Item ID to fetch data for
            timestep: Time interval - '5m', '1h', '6h', or '24h'
                     5m = ~30 hours of data
                     1h = ~15 days of data  
                     6h = ~90 days of data
                     24h = ~1 year of data (365 data points max)
        
        Returns:
            List of price data points with timestamps
        """
        try:
            url = f"https://prices.runescape.wiki/api/v1/osrs/timeseries"
            params = {
                'timestep': timestep,
                'id': item_id
            }
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()
            return response.json()['data']
        except Exception as e:
            print(f"Error fetching timeseries for item {item_id}: {e}")
            return None
    
    def update_price_history(self, item_id: int, price: int):
        """Add price to historical data"""
        if item_id not in self.price_history:
            self.price_history[item_id] = []
        self.price_history[item_id].append(price)
    
    def calculate_statistics(self, item_id: int) -> Optional[Dict]:
        """
        Calculate mean, std dev, and current deviation
        
        NOTE: Average and Change % are calculated from YOUR LOCAL price history
        (prices collected while the app is running). This is intentional because:
        1. Shows how the item is performing in YOUR monitoring session
        2. Detects deviations from YOUR observed baseline
        3. Not misleading - clearly based on your data collection
        
        For long-term historical comparison, use the chart (double-click item)
        which shows API's full historical timeseries data.
        """
        if item_id not in self.price_history or len(self.price_history[item_id]) < 2:
            return None
        
        prices = self.price_history[item_id]
        mean_price = statistics.mean(prices)
        
        if len(prices) < 2:
            return {'mean': mean_price, 'std_dev': 0, 'current_deviation': 0}
        
        std_dev = statistics.stdev(prices)
        current_price = prices[-1]
        
        if std_dev > 0:
            deviation = (current_price - mean_price) / std_dev
        else:
            deviation = 0
        
        return {
            'mean': mean_price,
            'std_dev': std_dev,
            'current_deviation': deviation,
            'current_price': current_price
        }


class ItemDatabase:
    """Manages item ID to name mappings"""
    
    def __init__(self):
        self.item_map: Dict[int, str] = {}
        self.name_to_id: Dict[str, int] = {}
        self.data_file = Path("item_mapping.json")
        self.manual_file = Path("osrs_items_manual.json")  # User can provide this
        self.load_or_fetch_items()
    
    def load_or_fetch_items(self):
        """Load item mapping from cache, manual file, or fetch from OSRS Wiki"""
        # First, try manual file if provided
        if self.manual_file.exists():
            try:
                print("Loading item database from manual file...")
                with open(self.manual_file, 'r') as f:
                    data = json.load(f)
                    # Handle both formats: direct mapping or list format
                    if isinstance(data, list):
                        # List format from OSRS Wiki API
                        for item in data:
                            if 'id' in item and 'name' in item:
                                self.item_map[item['id']] = item['name']
                    else:
                        # Dict format
                        self.item_map = {int(k): v for k, v in data.items()}
                
                # Save to cache
                with open(self.data_file, 'w') as f:
                    json.dump(self.item_map, f)
                    
                print(f"Loaded {len(self.item_map)} items from manual file")
                self.name_to_id = {v.lower(): k for k, v in self.item_map.items()}
                print(f"Item database ready with {len(self.item_map)} items")
                return
            except Exception as e:
                print(f"Error loading manual file: {e}")
        
        # Try cache
        if self.data_file.exists():
            try:
                print("Loading item database from cache...")
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.item_map = {int(k): v for k, v in data.items()}
                print(f"Loaded {len(self.item_map)} items from cache")
            except Exception as e:
                print(f"Error loading cache: {e}")
                print("Re-fetching from API...")
                self.fetch_item_mapping()
        else:
            self.fetch_item_mapping()
        
        # Create reverse mapping
        self.name_to_id = {v.lower(): k for k, v in self.item_map.items()}
        print(f"Item database ready with {len(self.item_map)} items")
    
    def fetch_item_mapping(self):
        """Fetch item mapping from OSRS Wiki API"""
        print("Fetching item database from OSRS Wiki...")
        try:
            # Use the OSRS Wiki mapping endpoint
            url = "https://prices.runescape.wiki/api/v1/osrs/mapping"
            headers = {'User-Agent': 'OSRS Price Monitor - Personal Use'}
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Extract items - data is a list of items with 'id' and 'name' fields
            for item in data:
                if 'id' in item and 'name' in item:
                    # Filter out non-tradeable items (they won't have prices anyway)
                    self.item_map[item['id']] = item['name']
            
            # Save to cache
            with open(self.data_file, 'w') as f:
                json.dump(self.item_map, f)
            
            print(f"Loaded {len(self.item_map)} items from OSRS Wiki")
            
        except Exception as e:
            print(f"Error fetching item database: {e}")
            print("Using fallback common items list...")
            # Fallback to common items - extensive list
            self.item_map = {
                # Food
                385: "Shark",
                373: "Swordfish",
                379: "Lobster",
                7946: "Monkfish",
                3144: "Cooked karambwan",
                
                # Potions
                6685: "Saradomin brew(4)",
                3024: "Super restore(4)",
                2436: "Super attack(4)",
                2440: "Super strength(4)",
                2444: "Super defence(4)",
                2452: "Ranging potion(4)",
                2448: "Antifire potion(4)",
                2434: "Prayer potion(4)",
                
                # Runes
                561: "Nature rune",
                560: "Death rune",
                565: "Blood rune",
                566: "Soul rune",
                554: "Fire rune",
                555: "Water rune",
                556: "Air rune",
                557: "Earth rune",
                
                # Weapons
                4151: "Abyssal whip",
                11802: "Armadyl godsword",
                13576: "Dragon warhammer",
                20997: "Twisted bow",
                22804: "Scythe of vitur",
                21021: "Dragon hunter lance",
                
                # Armor
                2577: "Ranger boots",
                6585: "Amulet of fury",
                11773: "Berserker ring",
                6737: "Berserker ring (i)",
                
                # Resources
                536: "Dragon bones",
                532: "Big bones",
                1514: "Magic logs",
                1515: "Yew logs",
                1513: "Magic logs",
                454: "Coal",
                440: "Iron ore",
                453: "Coal",
                
                # Herbs
                207: "Grimy ranarr weed",
                209: "Grimy irit leaf",
                211: "Grimy avantoe",
                213: "Grimy kwuarm",
                3051: "Grimy snapdragon",
                215: "Grimy cadantine",
                2485: "Grimy lantadyme",
                217: "Grimy dwarf weed",
                219: "Grimy torstol",
                
                # Seeds  
                5295: "Ranarr seed",
                5297: "Snapdragon seed",
                5299: "Torstol seed",
                5304: "Spirit seed",
                
                # Other popular
                2: "Cannonball",
                139: "Amulet of glory(4)",
                1755: "Chisel",
                995: "Coins",
                13307: "Abyssal dagger",
                12006: "Abyssal bludgeon",
                19481: "Heavy ballista",
                11235: "Dark bow",
                
                # Barrows items
                4708: "Ahrim's robetop",
                4710: "Ahrim's robeskirt",
                4712: "Ahrim's hood",
                4714: "Ahrim's staff",
                4716: "Dharok's helm",
                4718: "Dharok's platebody",
                4720: "Dharok's platelegs",
                4722: "Dharok's greataxe",
                4724: "Guthan's helm",
                4726: "Guthan's platebody",
                4728: "Guthan's chainskirt",
                4730: "Guthan's warspear",
                4732: "Karil's coif",
                4734: "Karil's leathertop",
                4736: "Karil's leatherskirt",
                4738: "Karil's crossbow",
                4745: "Torag's helm",
                4747: "Torag's platebody",
                4749: "Torag's platelegs",
                4751: "Torag's hammers",
                4753: "Verac's helm",
                4755: "Verac's brassard",
                4757: "Verac's plateskirt",
                4759: "Verac's flail",
                
                # God Wars Dungeon
                11726: "Bandos chestplate",
                11728: "Bandos tassets",
                11724: "Bandos boots",
                11732: "Armadyl helmet",
                11730: "Armadyl chestplate",
                11736: "Armadyl chainskirt",
                
                # Supplies
                314: "Feather",
                1755: "Chisel",
                1925: "Bucket of sand",
                1781: "Molten glass",
                8007: "Cadantine seed",
            }
            # Save fallback to cache
            with open(self.data_file, 'w') as f:
                json.dump(self.item_map, f)
            print(f"Loaded {len(self.item_map)} fallback items")
    
    def search_items(self, query: str) -> List[tuple]:
        """Search for items by name"""
        query = query.lower()
        results = []
        for item_id, name in self.item_map.items():
            if query in name.lower():
                results.append((item_id, name))
        return sorted(results, key=lambda x: x[1])[:50]  # Limit to 50 results
    
    def get_name(self, item_id: int) -> str:
        """Get item name by ID"""
        return self.item_map.get(item_id, f"Unknown Item ({item_id})")
    
    def get_id(self, name: str) -> Optional[int]:
        """Get item ID by name"""
        return self.name_to_id.get(name.lower())


class WatchlistManager:
    """Manages the watchlist of items to monitor"""
    
    def __init__(self, filename="watchlist.json"):
        self.filename = filename
        self.watchlist: List[int] = []
        self.load()
    
    def load(self):
        """Load watchlist from file"""
        path = Path(self.filename)
        if path.exists():
            with open(path, 'r') as f:
                self.watchlist = json.load(f)
    
    def save(self):
        """Save watchlist to file"""
        with open(self.filename, 'w') as f:
            json.dump(self.watchlist, f)
    
    def add_item(self, item_id: int) -> bool:
        """Add item to watchlist"""
        if item_id not in self.watchlist:
            self.watchlist.append(item_id)
            self.save()
            return True
        return False
    
    def remove_item(self, item_id: int) -> bool:
        """Remove item from watchlist"""
        if item_id in self.watchlist:
            self.watchlist.remove(item_id)
            self.save()
            return True
        return False


class PriceHistory:
    """Manages persistent price history"""
    
    def __init__(self, filename="price_history.json"):
        self.filename = filename
        self.history: Dict[str, List[Dict]] = {}
        self.load()
    
    def load(self):
        """Load price history from file"""
        path = Path(self.filename)
        if path.exists():
            with open(path, 'r') as f:
                self.history = json.load(f)
    
    def save(self):
        """Save price history to file"""
        with open(self.filename, 'w') as f:
            json.dump(self.history, f)
    
    def add_price(self, item_id: int, price: int):
        """Add price record"""
        key = str(item_id)
        if key not in self.history:
            self.history[key] = []
        
        self.history[key].append({
            'price': price,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 1000 entries per item
        if len(self.history[key]) > 1000:
            self.history[key] = self.history[key][-1000:]
        
        self.save()
    
    def get_prices(self, item_id: int) -> List[int]:
        """Get price list for an item"""
        key = str(item_id)
        if key in self.history:
            return [entry['price'] for entry in self.history[key]]
        return []


class OSRSPriceMonitorApp:
    """Main application with GUI"""
    
    def __init__(self):
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize components
        self.monitor = PriceMonitor()
        self.item_db = ItemDatabase()
        self.watchlist = WatchlistManager()
        self.price_history = PriceHistory()
        
        # Settings
        self.threshold = 1.0  # Standard deviations
        self.update_interval = 900  # 15 minutes in seconds
        self.monitoring = False
        self.monitor_thread = None
        
        # Sort tracking
        self.sort_column_name = None
        self.sort_reverse = False
        
        # Create GUI
        self.root = ctk.CTk()
        self.root.title("OSRS Grand Exchange Price Monitor")
        self.root.geometry("1000x700")
        
        self.setup_ui()
        self.load_settings()
        self.refresh_watchlist()
        
        # Load historical data
        self.load_historical_data()
    
    def setup_ui(self):
        """Create the user interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="OSRS Price Monitor",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=10)
        
        # Control Panel
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        # Settings
        settings_frame = ctk.CTkFrame(control_frame)
        settings_frame.pack(side="left", padx=5)
        
        ctk.CTkLabel(settings_frame, text="Threshold (σ):").pack(side="left", padx=5)
        self.threshold_entry = ctk.CTkEntry(settings_frame, width=80)
        self.threshold_entry.insert(0, str(self.threshold))
        self.threshold_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(settings_frame, text="Interval (min):").pack(side="left", padx=5)
        self.interval_entry = ctk.CTkEntry(settings_frame, width=80)
        self.interval_entry.insert(0, str(self.update_interval // 60))
        self.interval_entry.pack(side="left", padx=5)
        
        self.save_settings_btn = ctk.CTkButton(
            settings_frame,
            text="Save Settings",
            command=self.save_settings,
            width=100
        )
        self.save_settings_btn.pack(side="left", padx=5)
        
        # Monitoring controls
        monitor_frame = ctk.CTkFrame(control_frame)
        monitor_frame.pack(side="right", padx=5)
        
        self.start_btn = ctk.CTkButton(
            monitor_frame,
            text="Start Monitoring",
            command=self.start_monitoring,
            width=120,
            fg_color="green"
        )
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = ctk.CTkButton(
            monitor_frame,
            text="Stop Monitoring",
            command=self.stop_monitoring,
            width=120,
            fg_color="red",
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=5)
        
        self.check_now_btn = ctk.CTkButton(
            monitor_frame,
            text="Check Now",
            command=self.check_prices_now,
            width=100
        )
        self.check_now_btn.pack(side="left", padx=5)
        
        # Add Item Section
        add_frame = ctk.CTkFrame(main_frame)
        add_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(add_frame, text="Add Item:", font=ctk.CTkFont(size=13)).pack(side="left", padx=5)
        
        self.search_entry = ctk.CTkEntry(
            add_frame, 
            width=350, 
            height=35,
            placeholder_text="Search for items...",
            font=ctk.CTkFont(size=13)
        )
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind('<KeyRelease>', self.on_search)
        
        self.add_btn = ctk.CTkButton(
            add_frame,
            text="Add to Watchlist",
            command=self.add_selected_item,
            width=140,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        self.add_btn.pack(side="left", padx=5)
        
        # Search Results
        self.search_frame = ctk.CTkScrollableFrame(add_frame, height=150)
        self.search_results = []
        
        # Watchlist Table
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(
            table_frame,
            text="Monitored Items",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=5)
        
        # Create custom style for larger fonts
        style = ttk.Style()
        style.theme_use('default')
        
        # Configure Treeview fonts and row height - larger fonts
        style.configure("Treeview",
                       background="#2b2b2b",
                       foreground="white",
                       rowheight=35,
                       fieldbackground="#2b2b2b",
                       font=('Arial', 13))  # Increased from 11 to 13
        style.configure("Treeview.Heading",
                       font=('Arial', 14, 'bold'),  # Increased from 12 to 14
                       background="#1f1f1f",
                       foreground="white")
        style.map('Treeview', background=[('selected', '#4a6ea8')])
        
        # Create Treeview for table
        columns = ('Item', 'Current Price', 'Average', 'Std Dev', 'Volatility %', 'Deviation (σ)', 'Change %', 'Status')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Define headings with better widths
        column_widths = {
            'Item': 180,
            'Current Price': 110,
            'Average': 110,
            'Std Dev': 90,
            'Volatility %': 95,
            'Deviation (σ)': 110,
            'Change %': 90,
            'Status': 120
        }
        
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c))
            self.tree.column(col, width=column_widths[col])
            # Center align all columns except Item
            if col != 'Item':
                self.tree.column(col, anchor='center')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Double-click to show chart
        self.tree.bind("<Double-Button-1>", self.show_price_chart)
        
        # Right-click menu for table
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Status Bar
        self.status_var = ctk.StringVar(value="Ready")
        status_bar = ctk.CTkLabel(
            main_frame,
            textvariable=self.status_var,
            anchor="w"
        )
        status_bar.pack(fill="x", padx=10, pady=5)
    
    def on_search(self, event):
        """Handle search input"""
        query = self.search_entry.get()
        if len(query) < 2:
            if hasattr(self, 'search_frame') and self.search_frame.winfo_manager():
                self.search_frame.pack_forget()
            return
        
        results = self.item_db.search_items(query)
        self.display_search_results(results)
    
    def display_search_results(self, results):
        """Display search results"""
        # Clear previous results
        for widget in self.search_frame.winfo_children():
            widget.destroy()
        
        if not results:
            ctk.CTkLabel(
                self.search_frame, 
                text="No items found",
                font=ctk.CTkFont(size=12)
            ).pack()
            self.search_frame.pack(fill="x", padx=5, pady=5)
            return
        
        self.search_results = results
        for idx, (item_id, name) in enumerate(results[:10]):  # Show top 10
            btn = ctk.CTkButton(
                self.search_frame,
                text=f"{name} (ID: {item_id})",
                command=lambda id=item_id: self.add_item_to_watchlist(id),
                anchor="w",
                height=30,
                font=ctk.CTkFont(size=12)
            )
            btn.pack(fill="x", padx=5, pady=2)
        
        self.search_frame.pack(fill="x", padx=5, pady=5)
    
    def add_selected_item(self):
        """Add item from search entry"""
        query = self.search_entry.get()
        item_id = self.item_db.get_id(query)
        if item_id:
            self.add_item_to_watchlist(item_id)
        else:
            messagebox.showwarning("Not Found", f"Item '{query}' not found")
    
    def add_item_to_watchlist(self, item_id: int):
        """Add item to watchlist"""
        if self.watchlist.add_item(item_id):
            item_name = self.item_db.get_name(item_id)
            self.status_var.set(f"Added {item_name} to watchlist")
            self.refresh_watchlist()
            self.search_entry.delete(0, 'end')
            if hasattr(self, 'search_frame') and self.search_frame.winfo_manager():
                self.search_frame.pack_forget()
        else:
            messagebox.showinfo("Already Added", "Item is already in watchlist")
    
    def refresh_watchlist(self):
        """Refresh the watchlist table"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add items
        for item_id in self.watchlist.watchlist:
            item_name = self.item_db.get_name(item_id)
            self.tree.insert('', 'end', values=(item_name, '-', '-', '-', '-', '-', '-', 'No data'), tags=(str(item_id),))
    
    def show_price_chart(self, event):
        """Show price history chart for selected item"""
        selection = self.tree.selection()
        if not selection:
            return
        
        # Get item ID from tags
        tags = self.tree.item(selection[0])['tags']
        if not tags:
            return
        
        item_id = int(tags[0])
        item_name = self.item_db.get_name(item_id)
        
        # Create chart window
        chart_window = ctk.CTkToplevel(self.root)
        chart_window.title(f"Price History: {item_name}")
        chart_window.geometry("900x650")
        
        # Time period selection frame
        period_frame = ctk.CTkFrame(chart_window)
        period_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(period_frame, text="Time Period:", font=ctk.CTkFont(size=13)).pack(side="left", padx=5)
        
        # Variable to track selected period
        period_var = ctk.StringVar(value="90d")
        
        # Period buttons
        periods = [
            ("30 Hours", "5m"),
            ("15 Days", "1h"),
            ("90 Days", "6h"),
            ("1 Year", "24h")
        ]
        
        # Loading label
        loading_label = ctk.CTkLabel(period_frame, text="", font=ctk.CTkFont(size=12))
        loading_label.pack(side="right", padx=10)
        
        # Chart frame
        chart_frame = ctk.CTkFrame(chart_window)
        chart_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        def load_chart(timestep: str, period_name: str):
            """Load and display chart for given timestep"""
            period_var.set(timestep)
            loading_label.configure(text="Loading...")
            chart_window.update()
            
            # Clear previous chart
            for widget in chart_frame.winfo_children():
                widget.destroy()
            
            # Fetch data
            data = self.monitor.fetch_timeseries(item_id, timestep)
            
            if not data or len(data) == 0:
                loading_label.configure(text="No data available")
                ctk.CTkLabel(
                    chart_frame,
                    text=f"No price history available for {item_name}",
                    font=ctk.CTkFont(size=14)
                ).pack(expand=True)
                return
            
            loading_label.configure(text="")
            
            # Create matplotlib figure
            fig = Figure(figsize=(8, 5), dpi=100)
            fig.patch.set_facecolor('#2b2b2b')
            ax = fig.add_subplot(111)
            ax.set_facecolor('#1f1f1f')
            
            # Extract data
            timestamps = [datetime.fromtimestamp(d['timestamp']) for d in data]
            high_prices = [d.get('avgHighPrice') for d in data]
            low_prices = [d.get('avgLowPrice') for d in data]
            
            # Filter out None values
            valid_data = [(t, h, l) for t, h, l in zip(timestamps, high_prices, low_prices) 
                         if h is not None and l is not None]
            
            if not valid_data:
                loading_label.configure(text="No valid price data")
                return
            
            timestamps, high_prices, low_prices = zip(*valid_data)
            
            # Plot high and low prices
            ax.plot(timestamps, high_prices, label='High Price', color='#4CAF50', linewidth=2)
            ax.plot(timestamps, low_prices, label='Low Price', color='#FF5722', linewidth=2)
            
            # Fill between
            ax.fill_between(timestamps, high_prices, low_prices, alpha=0.2, color='#FFC107')
            
            # Calculate and show average
            avg_high = sum(high_prices) / len(high_prices)
            avg_low = sum(low_prices) / len(low_prices)
            ax.axhline(y=avg_high, color='#4CAF50', linestyle='--', alpha=0.5, linewidth=1)
            ax.axhline(y=avg_low, color='#FF5722', linestyle='--', alpha=0.5, linewidth=1)
            
            # Formatting
            ax.set_xlabel('Date/Time', color='white', fontsize=11)
            ax.set_ylabel('Price (GP)', color='white', fontsize=11)
            ax.set_title(f'{item_name} - Price History ({period_name})', 
                        color='white', fontsize=13, fontweight='bold', pad=15)
            
            # Format x-axis dates
            if timestep == '5m':
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
            elif timestep == '1h':
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            else:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            
            fig.autofmt_xdate()
            
            # Style
            ax.tick_params(colors='white', labelsize=9)
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(True, alpha=0.2, color='white')
            
            # Legend
            legend = ax.legend(loc='upper left', facecolor='#2b2b2b', edgecolor='white')
            for text in legend.get_texts():
                text.set_color('white')
            
            # Add stats text
            stats_text = (
                f"Avg High: {avg_high:,.0f} GP\n"
                f"Avg Low: {avg_low:,.0f} GP\n"
                f"Spread: {avg_high - avg_low:,.0f} GP ({((avg_high - avg_low) / avg_high * 100):.1f}%)\n"
                f"Current: {high_prices[-1]:,.0f} GP"
            )
            ax.text(0.98, 0.98, stats_text,
                   transform=ax.transAxes,
                   verticalalignment='top',
                   horizontalalignment='right',
                   bbox=dict(boxstyle='round', facecolor='#2b2b2b', alpha=0.8, edgecolor='white'),
                   fontsize=9,
                   color='white')
            
            fig.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Create period buttons
        for period_name, timestep in periods:
            btn = ctk.CTkButton(
                period_frame,
                text=period_name,
                command=lambda ts=timestep, pn=period_name: load_chart(ts, pn),
                width=80,
                height=30
            )
            btn.pack(side="left", padx=2)
        
        # Load default view (90 days)
        chart_window.after(100, lambda: load_chart("6h", "90 Days"))
    
    def show_context_menu(self, event):
        """Show context menu for table"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            menu = ctk.CTkToplevel(self.root)
            menu.wm_overrideredirect(True)
            menu.geometry(f"+{event.x_root}+{event.y_root}")
            
            remove_btn = ctk.CTkButton(
                menu,
                text="Remove from Watchlist",
                command=lambda: self.remove_selected_item(item, menu)
            )
            remove_btn.pack(padx=5, pady=5)
            
            # Close menu on focus out
            menu.bind("<FocusOut>", lambda e: menu.destroy())
            menu.focus_set()
    
    def remove_selected_item(self, tree_item, menu):
        """Remove item from watchlist"""
        values = self.tree.item(tree_item)['values']
        item_name = values[0]
        
        # Find item ID from tags
        tags = self.tree.item(tree_item)['tags']
        if tags:
            item_id = int(tags[0])
            self.watchlist.remove_item(item_id)
            self.tree.delete(tree_item)
            self.status_var.set(f"Removed {item_name} from watchlist")
        
        menu.destroy()
    
    def sort_column(self, col):
        """Sort table by column - toggles between ascending and descending"""
        # Check if we're clicking the same column
        if self.sort_column_name == col:
            # Toggle the sort direction
            self.sort_reverse = not self.sort_reverse
        else:
            # New column, start with ascending
            self.sort_column_name = col
            self.sort_reverse = False
        
        # Get all items
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        
        # Custom sort key function
        def sort_key(x):
            val = x[0]
            # Handle empty/placeholder values
            if val in ['-', 'N/A', '']:
                return float('inf') if not self.sort_reverse else float('-inf')
            
            # Try to extract numeric value
            try:
                # Remove common characters and convert to float
                cleaned = val.replace(',', '').replace('σ', '').replace('%', '').replace('⚠️', '').strip()
                # Handle status text
                if 'ALERT' in cleaned or 'Normal' in cleaned or 'Collecting' in cleaned:
                    return float('inf') if not self.sort_reverse else float('-inf')
                return float(cleaned)
            except (ValueError, AttributeError):
                # Fall back to string comparison for non-numeric
                return val.lower()
        
        # Sort with the custom key
        try:
            items.sort(key=sort_key, reverse=self.sort_reverse)
        except Exception as e:
            # Ultimate fallback - just do string sort
            items.sort(key=lambda x: str(x[0]).lower(), reverse=self.sort_reverse)
        
        # Rearrange items
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)
        
        # Update column heading to show sort direction
        for column in self.tree['columns']:
            heading_text = column
            if column == col:
                heading_text = f"{column} {'▼' if self.sort_reverse else '▲'}"
            self.tree.heading(column, text=heading_text, command=lambda c=column: self.sort_column(c))
    
    def load_historical_data(self):
        """Load historical price data into monitor"""
        for item_id in self.watchlist.watchlist:
            prices = self.price_history.get_prices(item_id)
            self.monitor.price_history[item_id] = prices
    
    def save_settings(self):
        """Save user settings"""
        try:
            self.threshold = float(self.threshold_entry.get())
            interval_min = int(self.interval_entry.get())
            self.update_interval = interval_min * 60
            
            settings = {
                'threshold': self.threshold,
                'update_interval': self.update_interval
            }
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
            
            self.status_var.set("Settings saved")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers")
    
    def load_settings(self):
        """Load user settings"""
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                self.threshold = settings.get('threshold', 1.0)
                self.update_interval = settings.get('update_interval', 900)
                
                self.threshold_entry.delete(0, 'end')
                self.threshold_entry.insert(0, str(self.threshold))
                self.interval_entry.delete(0, 'end')
                self.interval_entry.insert(0, str(self.update_interval // 60))
        except FileNotFoundError:
            pass
    
    def start_monitoring(self):
        """Start the monitoring thread"""
        self.monitoring = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_var.set("Monitoring started")
        
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.monitoring = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_var.set("Monitoring stopped")
    
    def monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            self.check_prices()
            
            # Wait for interval
            for _ in range(self.update_interval):
                if not self.monitoring:
                    break
                time.sleep(1)
    
    def check_prices_now(self):
        """Check prices immediately"""
        threading.Thread(target=self.check_prices, daemon=True).start()
    
    def check_prices(self):
        """Fetch prices and update display"""
        self.status_var.set("Checking prices...")
        
        price_data = self.monitor.fetch_current_prices()
        if not price_data:
            self.status_var.set("Error fetching prices")
            return
        
        alerts = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for item_id in self.watchlist.watchlist:
            item_id_str = str(item_id)
            
            # Get item name first
            item_name = self.item_db.get_name(item_id)
            
            if item_id_str not in price_data:
                continue
            
            item_data = price_data[item_id_str]
            
            # Get current price (prefer high price, fall back to low)
            current_price = item_data.get('high')
            if current_price is None:
                current_price = item_data.get('low')
            
            if current_price is None:
                continue
            
            # Update history
            self.monitor.update_price_history(item_id, current_price)
            self.price_history.add_price(item_id, current_price)
            
            # Calculate statistics
            stats = self.monitor.calculate_statistics(item_id)
            
            # Format values - show current price even if no stats yet
            if stats is None or len(self.monitor.price_history.get(item_id, [])) < 2:
                # Not enough data for statistics yet, just show current price
                avg_price = "-"
                std_dev = "-"
                volatility_pct = "-"
                dev_str = "-"
                change_str = "-"
                status = "Collecting data..."
                
                # Update tree with current price
                self.update_tree_item(item_id, item_name, current_price, avg_price, 
                                     std_dev, volatility_pct, dev_str, change_str, status)
                continue
            
            # Have enough data for statistics
            avg_price = f"{stats['mean']:,.0f}"
            std_dev = f"{stats['std_dev']:,.0f}"
            
            # Calculate volatility as percentage of average price
            if stats['mean'] > 0:
                volatility_pct = f"{(stats['std_dev'] / stats['mean']) * 100:.1f}%"
            else:
                volatility_pct = "N/A"
            
            dev_str = f"{stats['current_deviation']:.2f}σ"
            # Have enough data for statistics
            avg_price = f"{stats['mean']:,.0f}"
            std_dev = f"{stats['std_dev']:,.0f}"
            dev_str = f"{stats['current_deviation']:.2f}σ"
            
            # Calculate change percentage
            if stats['mean'] > 0:
                change_pct = ((current_price - stats['mean']) / stats['mean']) * 100
                change_str = f"{change_pct:+.1f}%"
            else:
                change_str = "N/A"
            
            # Determine status and check for alerts
            deviation = stats['current_deviation']
            if abs(deviation) >= self.threshold:
                status = "⚠️ ALERT!"
                alerts.append({
                    'item_name': item_name,
                    'deviation': deviation,
                    'current_price': current_price,
                    'avg_price': stats['mean']
                })
            else:
                status = "Normal"
            
            # Update tree
            self.update_tree_item(item_id, item_name, current_price, avg_price, 
                                 std_dev, volatility_pct, dev_str, change_str, status)
        
        # Show alerts
        if alerts:
            self.show_alerts(alerts)
        
        self.status_var.set(f"Last updated: {timestamp}")
    
    def update_tree_item(self, item_id, name, price, avg, std_dev, volatility_pct, deviation, change, status):
        """Update or add item in tree"""
        # Find existing item
        for item in self.tree.get_children():
            tags = self.tree.item(item)['tags']
            if tags and int(tags[0]) == item_id:
                # Update existing
                self.tree.item(item, values=(name, f"{price:,}", avg, std_dev, volatility_pct, deviation, change, status))
                
                # Color code based on status
                if "ALERT" in status:
                    self.tree.item(item, tags=(str(item_id), 'alert'))
                else:
                    self.tree.item(item, tags=(str(item_id),))
                return
        
        # Add new item
        self.tree.insert('', 'end', values=(name, f"{price:,}", avg, std_dev, volatility_pct, deviation, change, status),
                        tags=(str(item_id),))
    
    def show_alerts(self, alerts):
        """Show alert notifications"""
        for alert in alerts:
            msg = (f"{alert['item_name']}: {alert['deviation']:.2f}σ deviation\n"
                   f"Current: {alert['current_price']:,} gp\n"
                   f"Average: {alert['avg_price']:,.0f} gp")
            
            # Toast notification
            if TOAST_AVAILABLE:
                try:
                    toast = Notification(
                        app_id="OSRS Price Monitor",
                        title=f"Price Alert: {alert['item_name']}",
                        msg=msg,
                        icon=""
                    )
                    toast.set_audio(audio.Default, loop=False)
                    toast.show()
                except Exception as e:
                    print(f"Toast notification error: {e}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    app = OSRSPriceMonitorApp()
    app.run()


if __name__ == "__main__":
    main()
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import requests
import re
import json
import threading
import time
from datetime import datetime
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv

class OSRSPriceTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OSRS Price Tracker")
        self.root.geometry("1100x700")
        self.root.configure(bg='#2b2b2b')
        
        # Data file for persistence
        self.data_file = "osrs_tracker_data.json"
        
        # Load saved data or initialize with default items
        self.load_data()
        
        # Create GUI
        self.create_gui()
        
        # Start price update thread
        self.update_thread = None
        self.stop_updating = False
        
        # Sort variables
        self.sort_column = None
        self.sort_reverse = False
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def load_data(self):
        """Load data from JSON file or initialize with defaults"""
        default_data = {
            "items": [
                {
                    "name": "Torstol Seed",
                    "url": "https://secure.runescape.com/m=itemdb_oldschool/Torstol+seed/viewitem?obj=5304",
                    "reference_price": 13333,
                    "buy_price": 0,
                    "sell_price": 0,
                    "quantity": 1,
                    "current_price": 0,
                    "change_1m": 0,
                    "change_3m": 0,
                    "change_6m": 0,
                    "last_updated": ""
                },
                {
                    "name": "Dragon Pickaxe",
                    "url": "https://secure.runescape.com/m=itemdb_oldschool/Dragon+pickaxe/viewitem?obj=11920",
                    "reference_price": 900000,
                    "buy_price": 0,
                    "sell_price": 0,
                    "quantity": 1,
                    "current_price": 0,
                    "change_1m": 0,
                    "change_3m": 0,
                    "change_6m": 0,
                    "last_updated": ""
                },
                {
                    "name": "Anglerfish",
                    "url": "https://secure.runescape.com/m=itemdb_oldschool/Anglerfish/viewitem?obj=13441",
                    "reference_price": 1440,
                    "buy_price": 0,
                    "sell_price": 0,
                    "quantity": 100,
                    "current_price": 0,
                    "change_1m": 0,
                    "change_3m": 0,
                    "change_6m": 0,
                    "last_updated": ""
                },
                {
                    "name": "Blighted Ice Sack",
                    "url": "https://secure.runescape.com/m=itemdb_oldschool/Blighted+ancient+ice+sack/viewitem?obj=24607",
                    "reference_price": 272,
                    "buy_price": 0,
                    "sell_price": 0,
                    "quantity": 100,
                    "current_price": 0,
                    "change_1m": 0,
                    "change_3m": 0,
                    "change_6m": 0,
                    "last_updated": ""
                },
                {
                    "name": "Dragon Arrow",
                    "url": "https://secure.runescape.com/m=itemdb_oldschool/Dragon+arrow/viewitem?obj=11212",
                    "reference_price": 1400,
                    "buy_price": 0,
                    "sell_price": 0,
                    "quantity": 100,
                    "current_price": 0,
                    "change_1m": 0,
                    "change_3m": 0,
                    "change_6m": 0,
                    "last_updated": ""
                },
                {
                    "name": "Bond",
                    "url": "https://secure.runescape.com/m=itemdb_oldschool/Old+school+bond/viewitem?obj=13190",
                    "reference_price": 12000000,
                    "buy_price": 0,
                    "sell_price": 0,
                    "quantity": 1,
                    "current_price": 0,
                    "change_1m": 0,
                    "change_3m": 0,
                    "change_6m": 0,
                    "last_updated": ""
                },
                {
                    "name": "Spirit Shield",
                    "url": "https://secure.runescape.com/m=itemdb_oldschool/Spirit+shield/viewitem?obj=12829",
                    "reference_price": 55000,
                    "buy_price": 0,
                    "sell_price": 0,
                    "quantity": 1,
                    "current_price": 0,
                    "change_1m": 0,
                    "change_3m": 0,
                    "change_6m": 0,
                    "last_updated": ""
                },
                {
                    "name": "Black Chinchompa",
                    "url": "https://secure.runescape.com/m=itemdb_oldschool/Black+chinchompa/viewitem?obj=11959",
                    "reference_price": 2500,
                    "buy_price": 0,
                    "sell_price": 0,
                    "quantity": 100,
                    "current_price": 0,
                    "change_1m": 0,
                    "change_3m": 0,
                    "change_6m": 0,
                    "last_updated": ""
                }
            ],
            "transactions": []
        }
        
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
                    # Ensure transactions key exists
                    if 'transactions' not in self.data:
                        self.data['transactions'] = []
                    # Migrate items to new schema with buy_price and sell_price
                    for item in self.data.get('items', []):
                        if 'buy_price' not in item:
                            item['buy_price'] = 0
                        if 'sell_price' not in item:
                            item['sell_price'] = 0
                        if 'change_1m' not in item:
                            item['change_1m'] = 0
                        if 'change_3m' not in item:
                            item['change_3m'] = 0
                        if 'change_6m' not in item:
                            item['change_6m'] = 0
            except:
                self.data = default_data
        else:
            self.data = default_data
    
    def save_data(self):
        """Save data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")
    
    def create_gui(self):
        """Create the main GUI"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for dark theme
        style.configure('Treeview',
                        background='#3c3c3c',
                        foreground='white',
                        fieldbackground='#3c3c3c',
                        borderwidth=0)
        style.configure('green', foreground='green')
        style.configure('red', foreground='red')
        style.configure('Treeview.Heading',
                       background='#4a4a4a',
                       foreground='white',
                       borderwidth=1,
                       relief='solid')
        style.map('Treeview', background=[('selected', '#0078d4')])
        
        # Configure custom scrollbar styling
        style.configure('Vertical.TScrollbar',
                       background='#3c3c3c',
                       troughcolor='#2b2b2b',
                       bordercolor='#2b2b2b',
                       darkcolor='#4a4a4a',
                       lightcolor='#4a4a4a',
                       arrowcolor='#00ffff')
        style.map('Vertical.TScrollbar',
                 background=[('active', '#00ffff'), ('pressed', '#0078d4')])
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 10))
        
        # Tab buttons frame (at top)
        top_frame = tk.Frame(main_frame, bg='#2b2b2b')
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Tab buttons on LEFT side
        tab_frame = tk.Frame(top_frame, bg='#2b2b2b')
        tab_frame.pack(side=tk.LEFT, fill=tk.X)
        
        self.prices_btn = tk.Button(tab_frame, text="Prices & Positions", 
                                   command=self.show_prices_tab,
                                   bg='#0078d4', fg='white', font=('Arial', 10, 'bold'))
        self.prices_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.history_btn = tk.Button(tab_frame, text="History", 
                                    command=self.show_history_tab,
                                    bg='#444444', fg='white', font=('Arial', 10, 'bold'))
        self.history_btn.pack(side=tk.LEFT)
        
        # Control buttons frame (RIGHT side)
        self.control_buttons_frame = tk.Frame(top_frame, bg='#2b2b2b')
        self.control_buttons_frame.pack(side=tk.RIGHT, fill=tk.X)
        
        self.update_btn = tk.Button(self.control_buttons_frame, text="Update All Prices", 
                                   command=self.update_prices_thread,
                                   bg='#0078d4', fg='white', font=('Arial', 10, 'bold'))
        self.update_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.update_selected_btn = tk.Button(self.control_buttons_frame, text="Update Selected", 
                                    command=self.update_selected_item,
                                    bg='#0078d4', fg='white', font=('Arial', 10, 'bold'))
        self.update_selected_btn.pack(side=tk.LEFT, padx=(0, 5))

        add_btn = tk.Button(self.control_buttons_frame, text="+ Add Item", 
                           command=self.add_item,
                           bg='#107c10', fg='white', font=('Arial', 10, 'bold'))
        add_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_btn = tk.Button(self.control_buttons_frame, text="Remove Item", 
                              command=self.remove_item,
                              bg='#d13438', fg='white', font=('Arial', 10, 'bold'))
        remove_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.export_prices_btn = tk.Button(self.control_buttons_frame, text="Export", 
                              command=self.export_prices_csv,
                              bg='#006dbf', fg='white', font=('Arial', 10, 'bold'))
        self.export_prices_btn.pack(side=tk.LEFT)
        
        # Content frame (will hold either prices or history view)
        self.content_frame = tk.Frame(main_frame, bg='#2b2b2b')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Notification label in upper right (overlaps header)
        self.notification_label = tk.Label(main_frame, text="",
                                          fg='#00ff00', bg='#2b2b2b', font=('Arial', 9))
        self.notification_label.pack(side=tk.TOP, anchor='ne', padx=(0, 10), pady=(2, 0))
        
        # Create both views but only show prices initially
        self.create_prices_view()
        self.create_history_view()
        self.show_prices_tab()
    
    def create_prices_view(self):
        """Create the prices and positions view"""
        # Treeview for items
        tree_frame = tk.Frame(self.content_frame, bg='#2b2b2b')
        tree_frame.pack(fill=tk.BOTH, expand=True)
        self.tree_frame = tree_frame
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview - columns with Current Price before Reference Price, plus change columns
        columns = ('Item', 'Current Price', '1M Change', '3M Change', '6M Change', 'Reference Price', 'Change %', 'Quantity', 'Portfolio Value')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)

        # Configure columns with sort arrows
        for col in columns:
            self.tree.heading(col, text=f"{col} ↑↓",
                            command=lambda c=col: self.sort_treeview(c))
            self.tree.column(col, anchor='center', width=100)

        self.tree.column('Item', anchor='w', width=150)
        self.tree.column('Current Price', anchor='center', width=120)
        self.tree.column('1M Change', anchor='center', width=100)
        self.tree.column('3M Change', anchor='center', width=100)
        self.tree.column('6M Change', anchor='center', width=100)
        self.tree.column('Reference Price', anchor='center', width=120)
        self.tree.column('Change %', anchor='center', width=90)
        
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.tag_configure('green', foreground='#00FF00')
        self.tree.tag_configure('red', foreground='#FF0000')
        
        # Bind double-click to edit
        self.tree.bind('<Double-1>', self.edit_item)
        
        # Populate tree with initial data
        self.refresh_tree()
    
    def create_history_view(self):
        """Create the transaction history view"""
        self.history_frame = tk.Frame(self.content_frame, bg='#2b2b2b')
        
        # Top frame with summary metrics
        summary_frame = tk.Frame(self.history_frame, bg='#3c3c3c', relief=tk.RAISED, bd=1)
        summary_frame.pack(fill=tk.X, padx=(0, 0), pady=(0, 5))
        
        self.summary_label = tk.Label(summary_frame, text="Portfolio: Current Value: 0 gp | Gain/Loss (Realized): 0 gp (0%) | Unrealized: 0 gp (0%)",
                                     font=('Arial', 10, 'bold'), fg='#00ffff', bg='#3c3c3c')
        self.summary_label.pack(padx=10, pady=5)
        
        # Button frame for history controls
        button_frame = tk.Frame(self.history_frame, bg='#2b2b2b')
        button_frame.pack(fill=tk.X, padx=(0, 0), pady=(0, 5))
        
        delete_selected_btn = tk.Button(button_frame, text="Delete Selected", 
                                       command=self.delete_selected_transaction,
                                       bg='#d13438', fg='white', font=('Arial', 10, 'bold'))
        delete_selected_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        delete_all_btn = tk.Button(button_frame, text="Clear All History", 
                                  command=self.delete_all_history,
                                  bg='#d13438', fg='white', font=('Arial', 10, 'bold'))
        delete_all_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        export_hist_btn = tk.Button(button_frame, text="Export History", 
                                   command=self.export_history_csv,
                                   bg='#006dbf', fg='white', font=('Arial', 10, 'bold'))
        export_hist_btn.pack(side=tk.LEFT)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview for transactions
        columns = ('Date', 'Item', 'Type', 'Quantity', 'Price', 'Total')
        self.history_tree = ttk.Treeview(self.history_frame, columns=columns, show='headings', yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.history_tree.yview)
        
        # Configure columns
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, anchor='center', width=100)
        
        self.history_tree.column('Item', anchor='w', width=150)
        self.history_tree.column('Date', anchor='center', width=140)
        
        self.history_tree.pack(fill=tk.BOTH, expand=True)
        
        self.history_tree.tag_configure('green', foreground='#00FF00')
        self.history_tree.tag_configure('red', foreground='#FF0000')
    
    def show_prices_tab(self):
        """Switch to prices view"""
        self.history_frame.pack_forget()
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        self.prices_btn.config(bg='#0078d4')
        self.history_btn.config(bg='#444444')
        self.control_buttons_frame.pack(side=tk.RIGHT, fill=tk.X)
        self.refresh_tree()
    
    def show_history_tab(self):
        """Switch to history view"""
        self.tree_frame.pack_forget()
        self.history_frame.pack(fill=tk.BOTH, expand=True)
        self.history_btn.config(bg='#0078d4')
        self.prices_btn.config(bg='#444444')
        self.control_buttons_frame.pack_forget()
        self.refresh_history_tree()
    
    def show_notification(self, message, duration=3000, color='#00ff00'):
        """Show a notification in the upper right corner"""
        self.notification_label.config(text=message, fg=color)
        # Auto-hide after duration (in milliseconds)
        self.root.after(duration, lambda: self.notification_label.config(text=""))
    
    def refresh_tree(self):
        """Refresh the treeview with current data"""
        self.tree.delete(*self.tree.get_children())
        
        for idx, item_data in enumerate(self.data['items']):
            reference_price = item_data.get('reference_price', 0)
            current_price = item_data.get('current_price', 0)
            quantity = item_data.get('quantity', 1)
            change_1m = item_data.get('change_1m', 0)
            change_3m = item_data.get('change_3m', 0)
            change_6m = item_data.get('change_6m', 0)

            # Use current_price if available, otherwise use reference_price for display
            display_price = current_price if current_price > 0 else reference_price

            # Calculate change based on current price vs reference price
            change_percent = 0
            if reference_price > 0 and current_price > 0:
                change_percent = ((current_price - reference_price) / reference_price) * 100
                change_str = f"{change_percent:+.2f}%"
            else:
                change_str = "N/A"

            # Format change percentages with color coding
            def format_change(change_val):
                if change_val == 0:
                    return "-"
                change_str = f"{change_val:+.1f}%"
                return change_str

            # Portfolio value based on current price
            portfolio_value = 0
            if quantity == 0:
                portfolio_value_str = "-"
            elif current_price > 0:
                portfolio_value = current_price * quantity
                portfolio_value_str = f"{portfolio_value:,}"
            else:
                portfolio_value_str = "N/A"

            reference_price_str = f"{reference_price:,}"
            current_price_str = f"{display_price:,}" if display_price > 0 else "N/A"
            change_1m_str = format_change(change_1m)
            change_3m_str = format_change(change_3m)
            change_6m_str = format_change(change_6m)

            values = (
                item_data['name'],
                current_price_str,
                change_1m_str,
                change_3m_str,
                change_6m_str,
                reference_price_str,
                change_str,
                quantity,
                portfolio_value_str
            )

            # Store the data index as the item ID
            item_id = self.tree.insert('', 'end', values=values, tags=(f'data_index_{idx}',))
            
            # Color the entire row based on current price vs reference price
            if change_percent > 0:
                self.tree.tag_configure(f'green_{item_id}', foreground='#00FF00')
                self.tree.item(item_id, tags=(f'green_{item_id}', f'data_index_{idx}'))
            elif change_percent < 0:
                self.tree.tag_configure(f'red_{item_id}', foreground='#FF0000')
                self.tree.item(item_id, tags=(f'red_{item_id}', f'data_index_{idx}'))
    
    def scrape_price(self, url):
        """Scrape price and historical changes from OSRS website"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            html = response.text
            
            if len(html) < 100:
                return None, 0, 0, 0
            
            # Extract current price
            price = None
            patterns = [
                r'<h3[^>]*>Current Guide Price[^<]*<span[^>]*title\s*=\s*["\']([0-9,]+)["\'][^>]*>',
                r'Current Guide Price.*?<span[^>]*title\s*=\s*["\']([0-9,]+)["\']',
                r'<span[^>]*title\s*=\s*["\']([0-9,]+)["\'][^>]*>[^<]*</span>',
                r'title\s*=\s*["\']([0-9,]+)["\']'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    price_str = match.group(1).replace(',', '')
                    if price_str.isdigit():
                        price = int(price_str)
                        break
            
            # Extract 1/3/6 month changes from stats__pc-change spans
            changes = [0, 0, 0]  # 1m, 3m, 6m
            change_pattern = r'<span class=["\']stats__pc-change["\']>\s*([-+]?\s*\d+)\s*%?\s*</span>'
            change_matches = re.findall(change_pattern, html)
            
            # The first change is today's, followed by 1m, 3m, 6m
            # We only want the 1m, 3m, 6m changes (skip the first one)
            if len(change_matches) >= 4:
                try:
                    # Skip the first match (today's change), get 1m, 3m, 6m
                    for i in range(3):
                        change_str = change_matches[i + 1].replace(' ', '').replace('%', '')
                        changes[i] = float(change_str)
                except (ValueError, IndexError):
                    pass
            
            return price, changes[0], changes[1], changes[2]
            
        except Exception as e:
            print(f"Error scraping price: {e}")
            return None, 0, 0, 0
    
    def update_prices_thread(self):
        """Start price update in a separate thread"""
        if self.update_thread and self.update_thread.is_alive():
            return
        
        self.update_thread = threading.Thread(target=self.update_prices)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def update_prices(self):
        """Update all item prices concurrently"""
        self.update_btn.config(state='disabled', text='Updating...')
        self.show_notification("Updating prices...", 15000, '#ffff00')
        
        # Store current sort state before update
        current_sort_column = self.sort_column
        current_sort_reverse = self.sort_reverse
        
        total_items = len(self.data['items'])
        updated_count = [0]  # Use list to allow modification in nested function
        
        def update_single_price(item_index):
            """Update price for a single item"""
            if self.stop_updating:
                return
            
            item = self.data['items'][item_index]
            result = self.scrape_price(item['url'])
            if result[0] is not None:
                item['current_price'] = result[0]
                item['change_1m'] = result[1]
                item['change_3m'] = result[2]
                item['change_6m'] = result[3]
                item['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                updated_count[0] += 1
            
            return item_index
        
        # Use ThreadPoolExecutor to fetch all prices concurrently (max 5 threads)
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(update_single_price, i) for i in range(len(self.data['items']))]
            
            # Wait for all to complete
            for future in as_completed(futures):
                if self.stop_updating:
                    break
                future.result()
                self.root.after(0, self.refresh_tree)
        
        # Save data and update GUI
        self.save_data()
        self.root.after(0, self.refresh_tree)
        
        # Restore sort state after refresh
        if current_sort_column:
            self.root.after(0, lambda: self.sort_treeview(current_sort_column))
        
        self.root.after(0, lambda: self.update_btn.config(state='normal', text='Update All Prices'))
        self.root.after(0, lambda: self.show_notification("Update complete", 3000, '#00ff00'))
    
    def update_selected_item(self):
        """Update price for selected item only"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to update.")
            return
        
        # Get the data index from the tag
        item_id = selection[0]
        tags = self.tree.item(item_id, 'tags')
        data_index = None
        for tag in tags:
            if tag.startswith('data_index_'):
                data_index = int(tag.split('_')[-1])
                break
        
        if data_index is None:
            return
        
        item = self.data['items'][data_index]
        
        self.update_selected_btn.config(state='disabled', text='Updating...')
        self.show_notification(f"Updating {item['name']}...", 10000, '#ffff00')
        
        def update():
            result = self.scrape_price(item['url'])
            if result[0] is not None:
                item['current_price'] = result[0]
                item['change_1m'] = result[1]
                item['change_3m'] = result[2]
                item['change_6m'] = result[3]
                item['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_data()
            
            self.refresh_tree()
            self.update_selected_btn.config(state='normal', text='Update Selected')
            self.show_notification("Update complete", 3000, '#00ff00')
        
        thread = threading.Thread(target=update)
        thread.daemon = True
        thread.start()
    
    def add_item(self):
        """Add a new item"""
        dialog = AddItemDialog(self.root)
        if dialog.result:
            name, url, ref_price, buy_price, sell_price, quantity = dialog.result
            new_item = {
                'name': name,
                'url': url,
                'reference_price': ref_price,
                'buy_price': buy_price,
                'sell_price': sell_price,
                'quantity': quantity,
                'current_price': 0,
                'change_1m': 0,
                'change_3m': 0,
                'change_6m': 0,
                'last_updated': ''
            }
            self.data['items'].append(new_item)
            self.save_data()
            self.refresh_tree()
            self.show_notification(f"Added '{name}'", 2000, '#00ff00')
    
    def remove_item(self):
        """Remove selected item"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove.")
            return
        
        # Get the data index from the tag
        item_id = selection[0]
        tags = self.tree.item(item_id, 'tags')
        data_index = None
        for tag in tags:
            if tag.startswith('data_index_'):
                data_index = int(tag.split('_')[-1])
                break
        
        if data_index is None:
            return
        
        item_name = self.data['items'][data_index]['name']
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to remove '{item_name}'?"):
            del self.data['items'][data_index]
            self.save_data()
            self.refresh_tree()
            self.show_notification(f"Removed '{item_name}'", 2000, '#ff9999')
    
    def edit_item(self, event):
        """Edit selected item on double-click"""
        selection = self.tree.selection()
        if not selection:
            return
        
        # Get the data index from the tag instead of tree position
        item_id = selection[0]
        tags = self.tree.item(item_id, 'tags')
        
        # Find the data_index tag
        data_index = None
        for tag in tags:
            if tag.startswith('data_index_'):
                data_index = int(tag.split('_')[-1])
                break
        
        if data_index is None:
            return
        
        item = self.data['items'][data_index]
        old_quantity = item['quantity']
        old_price = item['reference_price']
        
        dialog = EditItemDialog(self.root, item)
        if dialog.result:
            name, url, ref_price, buy_price, sell_price, quantity = dialog.result
            item['name'] = name
            item['url'] = url
            item['reference_price'] = ref_price
            item['buy_price'] = buy_price
            item['sell_price'] = sell_price
            item['quantity'] = quantity
            
            # Log transaction if quantity changed
            if quantity != old_quantity:
                old_buy_price = item.get('buy_price', 0)
                old_sell_price = item.get('sell_price', 0)
                self.log_transaction(name, quantity, buy_price, sell_price, old_quantity, old_buy_price, old_sell_price)
            
            self.save_data()
            self.refresh_tree()
            self.show_notification(f"Updated '{name}'", 2000, '#00ff00')
    
    def sort_treeview(self, col):
        """Sort treeview by column"""
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
            self.sort_column = col

        # Update arrow in column headers
        for column in self.tree['columns']:
            if column == col:
                arrow = " ↓" if self.sort_reverse else " ↑"
            else:
                arrow = " ↑↓"
            self.tree.heading(column, text=f"{column}{arrow}")

        # Get items and sort them based on their data indices
        items_data = []
        for item_id in self.tree.get_children(''):
            value = self.tree.set(item_id, col)
            # Extract data index from tags
            tags = self.tree.item(item_id, 'tags')
            data_index = None
            for tag in tags:
                if tag.startswith('data_index_'):
                    data_index = int(tag.split('_')[-1])
                    break
            items_data.append((value, data_index, item_id))
        
        # Sort based on column type
        if col == 'Item':
            items_data.sort(key=lambda x: x[0], reverse=self.sort_reverse)
        else:
            # Convert values to numbers for numeric sorting
            def convert_value(item):
                try:
                    clean_value = item[0].replace(',', '').replace('+', '').replace('%', '')
                    return float(clean_value)
                except (ValueError, TypeError):
                    return float('-inf')
            
            items_data.sort(key=convert_value, reverse=self.sort_reverse)

        # Rearrange items in sorted order (tree display only, data stays intact)
        for index, (_, _, item_id) in enumerate(items_data):
            self.tree.move(item_id, '', index)
    
    def log_transaction(self, item_name, new_qty, new_buy_price, new_sell_price, old_qty, old_buy_price, old_sell_price):
        """Log a transaction when quantity or prices change"""
        if 'transactions' not in self.data:
            self.data['transactions'] = []
        
        qty_change = new_qty - old_qty
        
        # Only log if there's an actual change
        if qty_change == 0 and new_buy_price == old_buy_price and new_sell_price == old_sell_price:
            return
        
        transaction_type = 'BUY' if qty_change > 0 else 'SELL' if qty_change < 0 else 'PRICE_UPDATE'
        
        # For buys, use buy price; for sells, use sell price
        transaction_qty = abs(qty_change) if qty_change != 0 else 0
        if qty_change > 0:
            transaction_price = new_buy_price
        elif qty_change < 0:
            transaction_price = new_sell_price
        else:
            transaction_price = 0
        
        transaction = {
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'item_name': item_name,
            'type': transaction_type,
            'quantity': transaction_qty,
            'price_per_unit': transaction_price,
            'total_cost': transaction_qty * transaction_price,
            'old_quantity': old_qty,
            'new_quantity': new_qty
        }
        
        self.data['transactions'].append(transaction)
        self.save_data()
    
    def refresh_history_tree(self):
        """Refresh the history treeview"""
        self.history_tree.delete(*self.history_tree.get_children())
        
        if 'transactions' not in self.data or not self.data['transactions']:
            self.summary_label.config(text="Portfolio: Current Value: 0 gp | Gain/Loss (Realized): 0 gp (0%) | Unrealized: 0 gp (0%)")
            return
        
        # Calculate portfolio metrics based on transaction history
        total_cost_of_sold = 0  # Cost basis of items that were sold
        total_proceeds_from_sales = 0  # Revenue from sales
        holdings = {}  # item_name -> {quantity, cost_basis}
        
        for trans in self.data['transactions']:
            trans_type = trans.get('type', '')
            qty = trans.get('quantity', 0)
            price = trans.get('price_per_unit', 0)
            item_name = trans.get('item_name', '')
            
            if trans_type == 'BUY':
                if item_name not in holdings:
                    holdings[item_name] = {'quantity': 0, 'cost_basis': 0}
                holdings[item_name]['quantity'] += qty
                holdings[item_name]['cost_basis'] += qty * price
            elif trans_type == 'SELL':
                if item_name in holdings and holdings[item_name]['quantity'] > 0:
                    # Calculate the cost basis of sold items (FIFO)
                    qty_to_sell = min(qty, holdings[item_name]['quantity'])
                    cost_per_unit = holdings[item_name]['cost_basis'] / holdings[item_name]['quantity']
                    total_cost_of_sold += qty_to_sell * cost_per_unit
                    total_proceeds_from_sales += qty_to_sell * price
                    
                    # Reduce holdings
                    holdings[item_name]['quantity'] -= qty_to_sell
                    holdings[item_name]['cost_basis'] -= qty_to_sell * cost_per_unit
        
        # Calculate current portfolio value and unrealized gains
        current_value = 0
        cost_basis_unrealized = 0
        for item_name, holding in holdings.items():
            if holding['quantity'] > 0:
                # Find the item in the items list to get current price
                for item in self.data['items']:
                    if item['name'] == item_name:
                        current_price = item.get('current_price', 0)
                        sell_price = item.get('sell_price', 0)
                        # Use current_price if available, otherwise use sell_price
                        price_to_use = current_price if current_price > 0 else sell_price
                        if price_to_use > 0:
                            current_value += holding['quantity'] * price_to_use
                        cost_basis_unrealized += holding['cost_basis']
                        break
        
        # Realized gain/loss = proceeds from sales - cost basis of sold items
        realized_gain = total_proceeds_from_sales - total_cost_of_sold
        realized_percent = (realized_gain / total_cost_of_sold * 100) if total_cost_of_sold > 0 else 0
        
        # Unrealized gain/loss = current value of holdings - cost basis of holdings
        unrealized_gain_loss = current_value - cost_basis_unrealized
        unrealized_percent = (unrealized_gain_loss / cost_basis_unrealized * 100) if cost_basis_unrealized > 0 else 0
        
        # Format values
        realized_gain_str = f"{realized_gain:+,}"
        realized_color = '#00FF00' if realized_gain >= 0 else '#FF0000'
        
        unrealized_str = f"{unrealized_gain_loss:+,}"
        
        summary_text = f"Portfolio: Current Value: {current_value:,} gp | Gain/Loss (Realized): {realized_gain_str} gp ({realized_percent:+.2f}%) | Unrealized: {unrealized_str} gp ({unrealized_percent:+.2f}%)"
        self.summary_label.config(text=summary_text, fg=realized_color)
        
        # Sort transactions by date (newest first)
        sorted_transactions = sorted(self.data['transactions'], key=lambda x: x.get('date', ''), reverse=True)
        
        # Build a mapping of sorted transactions to original indices
        trans_index_map = {}
        for idx, trans in enumerate(self.data['transactions']):
            for sort_idx, sorted_trans in enumerate(sorted_transactions):
                if trans is sorted_trans:
                    trans_index_map[sort_idx] = idx
                    break
        
        for sort_idx, trans in enumerate(sorted_transactions):
            date = trans.get('date', '')
            item_name = trans.get('item_name', '')
            trans_type = trans.get('type', '')
            qty = trans.get('quantity', 0)
            price = trans.get('price_per_unit', 0)
            total = trans.get('total_cost', 0)
            
            values = (
                date,
                item_name,
                trans_type,
                qty,
                f"{price:,}",
                f"{total:,}"
            )
            
            # Get the original index in the data array
            original_index = trans_index_map.get(sort_idx, sort_idx)
            item_id = self.history_tree.insert('', 'end', values=values, tags=(f'data_index_{original_index}',))
            
            # Color code transactions
            if trans_type == 'BUY':
                self.history_tree.tag_configure(f'buy_{item_id}', foreground='#00FF00')
                self.history_tree.item(item_id, tags=(f'buy_{item_id}', f'data_index_{original_index}'))
            elif trans_type == 'SELL':
                self.history_tree.tag_configure(f'sell_{item_id}', foreground='#FFD700')
                self.history_tree.item(item_id, tags=(f'sell_{item_id}', f'data_index_{original_index}'))

    def on_closing(self):
        """Handle application closing"""
        self.stop_updating = True
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=2)
        self.root.destroy()
    
    def export_prices_csv(self):
        """Export prices and positions to CSV"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"osrs_prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ['Item', 'Current Price', '1M Change %', '3M Change %', '6M Change %', 'Reference Price', 'Change %', 'Quantity', 'Portfolio Value']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for item in self.data['items']:
                    reference_price = item.get('reference_price', 0)
                    current_price = item.get('current_price', 0)
                    quantity = item.get('quantity', 0)
                    change_1m = item.get('change_1m', 0)
                    change_3m = item.get('change_3m', 0)
                    change_6m = item.get('change_6m', 0)
                    
                    change_percent = 0
                    if reference_price > 0 and current_price > 0:
                        change_percent = ((current_price - reference_price) / reference_price) * 100
                    
                    portfolio_value = 0
                    if quantity > 0 and current_price > 0:
                        portfolio_value = current_price * quantity
                    
                    writer.writerow({
                        'Item': item['name'],
                        'Current Price': current_price,
                        '1M Change %': f"{change_1m:+.2f}" if change_1m != 0 else "",
                        '3M Change %': f"{change_3m:+.2f}" if change_3m != 0 else "",
                        '6M Change %': f"{change_6m:+.2f}" if change_6m != 0 else "",
                        'Reference Price': reference_price,
                        'Change %': f"{change_percent:+.2f}%",
                        'Quantity': quantity,
                        'Portfolio Value': portfolio_value
                    })
            
            self.show_notification("Prices exported", 2000, '#00ff00')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export prices: {str(e)}")
    
    def export_history_csv(self):
        """Export transaction history to CSV"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"osrs_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ['Date', 'Item', 'Type', 'Quantity', 'Price Per Unit', 'Total Cost']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for trans in self.data.get('transactions', []):
                    writer.writerow({
                        'Date': trans.get('date', ''),
                        'Item': trans.get('item_name', ''),
                        'Type': trans.get('type', ''),
                        'Quantity': trans.get('quantity', 0),
                        'Price Per Unit': trans.get('price_per_unit', 0),
                        'Total Cost': trans.get('total_cost', 0)
                    })
            
            self.show_notification("History exported", 2000, '#00ff00')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export history: {str(e)}")
    
    def delete_selected_transaction(self):
        """Delete selected transaction from history"""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a transaction to delete.")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this transaction?"):
            # Get the data index from the tag
            item_id = selection[0]
            tags = self.history_tree.item(item_id, 'tags')
            data_index = None
            for tag in tags:
                if tag.startswith('data_index_'):
                    data_index = int(tag.split('_')[-1])
                    break
            
            if data_index is not None:
                # Delete from data
                del self.data['transactions'][data_index]
                self.save_data()
                self.refresh_history_tree()
                self.show_notification("Transaction deleted", 2000, '#ff9999')
    
    def delete_all_history(self):
        """Delete all transaction history"""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete ALL history?\nThis cannot be undone."):
            self.data['transactions'] = []
            self.save_data()
            self.refresh_history_tree()
            self.show_notification("All history cleared", 2000, '#ff9999')
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


class AddItemDialog:
    def __init__(self, parent):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Item")
        self.dialog.geometry("550x360")
        self.dialog.configure(bg='#2b2b2b')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_widgets(self):
        main_frame = tk.Frame(self.dialog, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Row 1: Item Name label and entry
        row1_label = tk.Frame(main_frame, bg='#2b2b2b')
        row1_label.pack(fill=tk.X, pady=(0, 2))
        tk.Label(row1_label, text="Item Name:", fg='white', bg='#2b2b2b', font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        
        row1_entry = tk.Frame(main_frame, bg='#2b2b2b')
        row1_entry.pack(fill=tk.X, pady=(0, 5))
        self.name_entry = tk.Entry(row1_entry, font=('Arial', 9))
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Row 2: URL label and entry
        row2_label = tk.Frame(main_frame, bg='#2b2b2b')
        row2_label.pack(fill=tk.X, pady=(0, 2))
        tk.Label(row2_label, text="URL:", fg='white', bg='#2b2b2b', font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        
        row2_entry = tk.Frame(main_frame, bg='#2b2b2b')
        row2_entry.pack(fill=tk.X, pady=(0, 5))
        self.url_entry = tk.Entry(row2_entry, font=('Arial', 9))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(row2_entry, text="Open", command=self.open_url,
                 bg='#006dbf', fg='white', font=('Arial', 8), padx=10).pack(side=tk.LEFT, padx=(5, 0))
        
        # Row 3: Quantity label and entry
        row3_label = tk.Frame(main_frame, bg='#2b2b2b')
        row3_label.pack(fill=tk.X, pady=(0, 2))
        tk.Label(row3_label, text="Quantity:", fg='white', bg='#2b2b2b', font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        
        row3_entry = tk.Frame(main_frame, bg='#2b2b2b')
        row3_entry.pack(fill=tk.X, pady=(0, 5))
        self.quantity_entry = tk.Entry(row3_entry, font=('Arial', 9), width=12)
        self.quantity_entry.insert(0, "1")
        self.quantity_entry.pack(side=tk.LEFT)
        
        # Row 4: Reference Price label and entry
        row4_label = tk.Frame(main_frame, bg='#2b2b2b')
        row4_label.pack(fill=tk.X, pady=(0, 2))
        tk.Label(row4_label, text="Reference Price:", fg='white', bg='#2b2b2b', font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        
        row4_entry = tk.Frame(main_frame, bg='#2b2b2b')
        row4_entry.pack(fill=tk.X, pady=(0, 5))
        self.ref_price_entry = tk.Entry(row4_entry, font=('Arial', 9), width=12)
        self.ref_price_entry.pack(side=tk.LEFT)
        
        # Row 5: Buy Price label and entry
        row5_label = tk.Frame(main_frame, bg='#2b2b2b')
        row5_label.pack(fill=tk.X, pady=(0, 2))
        tk.Label(row5_label, text="Buy Price:", fg='#00ff99', bg='#2b2b2b', font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        
        row5_entry = tk.Frame(main_frame, bg='#2b2b2b')
        row5_entry.pack(fill=tk.X, pady=(0, 5))
        self.buy_price_entry = tk.Entry(row5_entry, font=('Arial', 9), width=12)
        self.buy_price_entry.insert(0, "0")
        self.buy_price_entry.pack(side=tk.LEFT)
        
        # Row 6: Sell Price label and entry
        row6_label = tk.Frame(main_frame, bg='#2b2b2b')
        row6_label.pack(fill=tk.X, pady=(0, 2))
        tk.Label(row6_label, text="Sell Price:", fg='#ff6b6b', bg='#2b2b2b', font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        
        row6_entry = tk.Frame(main_frame, bg='#2b2b2b')
        row6_entry.pack(fill=tk.X, pady=(0, 8))
        self.sell_price_entry = tk.Entry(row6_entry, font=('Arial', 9), width=12)
        self.sell_price_entry.insert(0, "0")
        self.sell_price_entry.pack(side=tk.LEFT)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#2b2b2b')
        button_frame.pack(fill=tk.X, pady=(8, 0))
        
        tk.Button(button_frame, text="Add Item", command=self.add_item,
                 bg='#107c10', fg='white', font=('Arial', 9, 'bold'), padx=20).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(button_frame, text="Cancel", command=self.cancel,
                 bg='#d13438', fg='white', font=('Arial', 9, 'bold'), padx=20).pack(side=tk.LEFT)
    
    def add_item(self):
        try:
            name = self.name_entry.get().strip()
            url = self.url_entry.get().strip()
            ref_price = int(self.ref_price_entry.get().strip())
            buy_price = int(self.buy_price_entry.get().strip())
            sell_price = int(self.sell_price_entry.get().strip())
            quantity = int(self.quantity_entry.get().strip())
            
            if not name or not url:
                messagebox.showerror("Error", "Please fill in item name and URL.")
                return
            
            self.result = (name, url, ref_price, buy_price, sell_price, quantity)
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for prices and quantity.")
    
    def cancel(self):
        self.dialog.destroy()
    
    def open_url(self):
        """Open the URL in the default web browser"""
        import webbrowser
        url = self.url_entry.get().strip()
        if url:
            webbrowser.open(url)


class EditItemDialog:
    def __init__(self, parent, item):
        self.result = None
        self.item = item
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Item")
        self.dialog.geometry("550x360")
        self.dialog.configure(bg='#2b2b2b')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_widgets(self):
        main_frame = tk.Frame(self.dialog, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Row 1: Item Name label and entry
        row1_label = tk.Frame(main_frame, bg='#2b2b2b')
        row1_label.pack(fill=tk.X, pady=(0, 2))
        tk.Label(row1_label, text="Item Name:", fg='white', bg='#2b2b2b', font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        
        row1_entry = tk.Frame(main_frame, bg='#2b2b2b')
        row1_entry.pack(fill=tk.X, pady=(0, 5))
        self.name_entry = tk.Entry(row1_entry, font=('Arial', 9))
        self.name_entry.insert(0, self.item['name'])
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Row 2: URL label and entry
        row2_label = tk.Frame(main_frame, bg='#2b2b2b')
        row2_label.pack(fill=tk.X, pady=(0, 2))
        tk.Label(row2_label, text="URL:", fg='white', bg='#2b2b2b', font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        
        row2_entry = tk.Frame(main_frame, bg='#2b2b2b')
        row2_entry.pack(fill=tk.X, pady=(0, 5))
        self.url_entry = tk.Entry(row2_entry, font=('Arial', 9))
        self.url_entry.insert(0, self.item['url'])
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(row2_entry, text="Open", command=self.open_url,
                 bg='#006dbf', fg='white', font=('Arial', 8), padx=10).pack(side=tk.LEFT, padx=(5, 0))
        
        # Row 3: Quantity label and entry
        row3_label = tk.Frame(main_frame, bg='#2b2b2b')
        row3_label.pack(fill=tk.X, pady=(0, 2))
        tk.Label(row3_label, text="Quantity:", fg='white', bg='#2b2b2b', font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        
        row3_entry = tk.Frame(main_frame, bg='#2b2b2b')
        row3_entry.pack(fill=tk.X, pady=(0, 5))
        self.quantity_entry = tk.Entry(row3_entry, font=('Arial', 9), width=12)
        self.quantity_entry.insert(0, str(self.item['quantity']))
        self.quantity_entry.pack(side=tk.LEFT)
        
        # Row 4: Reference Price label and entry
        row4_label = tk.Frame(main_frame, bg='#2b2b2b')
        row4_label.pack(fill=tk.X, pady=(0, 2))
        tk.Label(row4_label, text="Reference Price:", fg='white', bg='#2b2b2b', font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        
        row4_entry = tk.Frame(main_frame, bg='#2b2b2b')
        row4_entry.pack(fill=tk.X, pady=(0, 5))
        self.ref_price_entry = tk.Entry(row4_entry, font=('Arial', 9), width=12)
        self.ref_price_entry.insert(0, str(self.item['reference_price']))
        self.ref_price_entry.pack(side=tk.LEFT)
        
        # Row 5: Buy Price label and entry
        row5_label = tk.Frame(main_frame, bg='#2b2b2b')
        row5_label.pack(fill=tk.X, pady=(0, 2))
        tk.Label(row5_label, text="Buy Price:", fg='#00ff99', bg='#2b2b2b', font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        
        row5_entry = tk.Frame(main_frame, bg='#2b2b2b')
        row5_entry.pack(fill=tk.X, pady=(0, 5))
        self.buy_price_entry = tk.Entry(row5_entry, font=('Arial', 9), width=12)
        self.buy_price_entry.insert(0, str(self.item.get('buy_price', 0)))
        self.buy_price_entry.pack(side=tk.LEFT)
        
        # Row 6: Sell Price label and entry
        row6_label = tk.Frame(main_frame, bg='#2b2b2b')
        row6_label.pack(fill=tk.X, pady=(0, 2))
        tk.Label(row6_label, text="Sell Price:", fg='#ff6b6b', bg='#2b2b2b', font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        
        row6_entry = tk.Frame(main_frame, bg='#2b2b2b')
        row6_entry.pack(fill=tk.X, pady=(0, 8))
        self.sell_price_entry = tk.Entry(row6_entry, font=('Arial', 9), width=12)
        self.sell_price_entry.insert(0, str(self.item.get('sell_price', 0)))
        self.sell_price_entry.pack(side=tk.LEFT)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#2b2b2b')
        button_frame.pack(fill=tk.X, pady=(8, 0))
        
        tk.Button(button_frame, text="Save", command=self.save_item,
                 bg='#107c10', fg='white', font=('Arial', 9, 'bold'), padx=20).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(button_frame, text="Cancel", command=self.cancel,
                 bg='#d13438', fg='white', font=('Arial', 9, 'bold'), padx=20).pack(side=tk.LEFT)
    
    def save_item(self):
        try:
            name = self.name_entry.get().strip()
            url = self.url_entry.get().strip()
            ref_price = int(self.ref_price_entry.get().strip())
            buy_price = int(self.buy_price_entry.get().strip())
            sell_price = int(self.sell_price_entry.get().strip())
            quantity = int(self.quantity_entry.get().strip())
            
            if not name or not url:
                messagebox.showerror("Error", "Please fill in item name and URL.")
                return
            
            self.result = (name, url, ref_price, buy_price, sell_price, quantity)
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for prices and quantity.")
    
    def cancel(self):
        self.dialog.destroy()
    
    def open_url(self):
        """Open the URL in the default web browser"""
        import webbrowser
        url = self.url_entry.get().strip()
        if url:
            webbrowser.open(url)


if __name__ == "__main__":
    app = OSRSPriceTracker()
    app.run()

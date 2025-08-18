import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests
import re
import json
import threading
import time
from datetime import datetime
import os

class OSRSPriceTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OSRS Price Tracker")
        self.root.geometry("1000x700")
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
                    "quantity": 1,
                    "current_price": 0,
                    "last_updated": ""
                },
                {
                    "name": "Dragon Pickaxe",
                    "url": "https://secure.runescape.com/m=itemdb_oldschool/Dragon+pickaxe/viewitem?obj=11920",
                    "reference_price": 900000,
                    "quantity": 1,
                    "current_price": 0,
                    "last_updated": ""
                },
                {
                    "name": "Anglerfish",
                    "url": "https://secure.runescape.com/m=itemdb_oldschool/Anglerfish/viewitem?obj=13441",
                    "reference_price": 1440,
                    "quantity": 100,
                    "current_price": 0,
                    "last_updated": ""
                },
                {
                    "name": "Blighted Ice Sack",
                    "url": "https://secure.runescape.com/m=itemdb_oldschool/Blighted+ancient+ice+sack/viewitem?obj=24607",
                    "reference_price": 272,
                    "quantity": 100,
                    "current_price": 0,
                    "last_updated": ""
                },
                {
                    "name": "Dragon Arrow",
                    "url": "https://secure.runescape.com/m=itemdb_oldschool/Dragon+arrow/viewitem?obj=11212",
                    "reference_price": 1400,
                    "quantity": 100,
                    "current_price": 0,
                    "last_updated": ""
                },
                {
                    "name": "Bond",
                    "url": "https://secure.runescape.com/m=itemdb_oldschool/Old+school+bond/viewitem?obj=13190",
                    "reference_price": 12000000,
                    "quantity": 1,
                    "current_price": 0,
                    "last_updated": ""
                },
                {
                    "name": "Spirit Shield",
                    "url": "https://secure.runescape.com/m=itemdb_oldschool/Spirit+shield/viewitem?obj=12829",
                    "reference_price": 55000,
                    "quantity": 1,
                    "current_price": 0,
                    "last_updated": ""
                },
                {
                    "name": "Black Chinchompa",
                    "url": "https://secure.runescape.com/m=itemdb_oldschool/Black+chinchompa/viewitem?obj=11959",
                    "reference_price": 2500,
                    "quantity": 100,
                    "current_price": 0,
                    "last_updated": ""
                }
            ]
        }
        
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
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
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="OSRS Price Tracker", 
                              font=('Arial', 16, 'bold'), 
                              fg='#00ffff', bg='#2b2b2b')
        title_label.pack(pady=(0, 10))
        
        # Control buttons frame
        control_frame = tk.Frame(main_frame, bg='#2b2b2b')
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        self.update_btn = tk.Button(control_frame, text="Update Prices", 
                                   command=self.update_prices_thread,
                                   bg='#0078d4', fg='white', font=('Arial', 10, 'bold'))
        self.update_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.update_selected_btn = tk.Button(control_frame, text="Update Selected", 
                                    command=self.update_selected_item,
                                    bg='#0078d4', fg='white', font=('Arial', 10, 'bold'))
        self.update_selected_btn.pack(side=tk.LEFT, padx=(0, 5))

        add_btn = tk.Button(control_frame, text="+ Add Item", 
                           command=self.add_item,
                           bg='#107c10', fg='white', font=('Arial', 10, 'bold'))
        add_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_btn = tk.Button(control_frame, text="Remove Item", 
                              command=self.remove_item,
                              bg='#d13438', fg='white', font=('Arial', 10, 'bold'))
        remove_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        move_up_btn = tk.Button(control_frame, text=" Move Up ", 
                               command=self.move_item_up,
                               bg="#444444", fg='white', font=('Arial', 10, 'bold'))
        move_up_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        move_down_btn = tk.Button(control_frame, text="Move Down", 
                                 command=self.move_item_down,
                                 bg='#444444', fg='white', font=('Arial', 10, 'bold'))
        move_down_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Status label
        self.status_label = tk.Label(control_frame, text="Ready", 
                                    fg='#00ff00', bg='#2b2b2b', font=('Arial', 10))
        self.status_label.pack(side=tk.RIGHT)
        
        # Treeview for items
        tree_frame = tk.Frame(main_frame, bg='#2b2b2b')
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ('Item', 'Current Price', 'Reference Price', 'Quantity', 'Change %', 'Net Change')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)

        # Configure columns with sort arrows
        for col in columns:
            self.tree.heading(col, text=f"{col} ↑↓",
                            command=lambda c=col: self.sort_treeview(c))
            self.tree.column(col, anchor='center', width=100)

        self.tree.column('Item', anchor='w', width=150)
        
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.tag_configure('green', foreground='#00FF00')
        self.tree.tag_configure('red', foreground='#FF0000')
        
        # Bind double-click to edit
        self.tree.bind('<Double-1>', self.edit_item)
        
        # Populate tree with initial data
        self.refresh_tree()
    
    def refresh_tree(self):
        """Refresh the treeview with current data"""
        self.tree.delete(*self.tree.get_children())
        
        for item_data in self.data['items']:
            current_price = item_data.get('current_price', 0)
            reference_price = item_data.get('reference_price', 0)
            quantity = item_data.get('quantity', 1)

            change_percent = 0
            if reference_price > 0 and current_price > 0:
                change_percent = ((current_price - reference_price) / reference_price) * 100
                change_str = f"{change_percent:+.2f}%"
            else:
                change_str = "No data"

            net_change = 0
            if quantity == 0:
                net_change_str = "-"
            elif current_price > 0:
                net_change = (current_price - reference_price) * quantity
                net_change_str = f"{net_change:+,}"
            else:
                net_change_str = "No data"

            current_price_str = f"{current_price:,}" if current_price > 0 else "Click Update"
            reference_price_str = f"{reference_price:,}"

            values = (
                item_data['name'],
                current_price_str,
                reference_price_str,
                quantity,
                change_str,
                net_change_str
            )

            item_id = self.tree.insert('', 'end', values=values)
            
            # Color only the change % and net change columns
            if change_percent > 0:
                self.tree.set(item_id, 'Change %', change_str)  # Column name must match exactly
                self.tree.set(item_id, 'Net Change', net_change_str)  # Column name must match exactly
                self.tree.tag_configure(f'green_{item_id}', foreground='#00FF00')
                self.tree.item(item_id, tags=(f'green_{item_id}',))
            elif change_percent < 0:
                self.tree.set(item_id, 'Change %', change_str)
                self.tree.set(item_id, 'Net Change', net_change_str)
                self.tree.tag_configure(f'red_{item_id}', foreground='#FF0000')
                self.tree.item(item_id, tags=(f'red_{item_id}',))
    
    def scrape_price(self, url):
        """Scrape price from OSRS website"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            html = response.text
            
            if len(html) < 100:
                return None
            
            # Multiple regex patterns to extract price (same as AHK script)
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
                        return int(price_str)
            
            return None
            
        except Exception as e:
            print(f"Error scraping price: {e}")
            return None
    
    def update_prices_thread(self):
        """Start price update in a separate thread"""
        if self.update_thread and self.update_thread.is_alive():
            return
        
        self.update_thread = threading.Thread(target=self.update_prices)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def update_prices(self):
        """Update all item prices"""
        self.update_btn.config(state='disabled', text='Updating...')
        self.status_label.config(text="Updating prices...", fg='#ffff00')
        
        total_items = len(self.data['items'])
        
        for i, item in enumerate(self.data['items']):
            if self.stop_updating:
                break
                
            self.status_label.config(text=f"Updating {item['name']} ({i+1}/{total_items})")
            
            price = self.scrape_price(item['url'])
            if price is not None:
                item['current_price'] = price
                item['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Update GUI in main thread
            self.root.after(0, self.refresh_tree)
            
            # Small delay between requests
            time.sleep(1)
        
        # Save data and update GUI
        self.save_data()
        self.root.after(0, self.refresh_tree)
        self.root.after(0, lambda: self.update_btn.config(state='normal', text='Update Prices'))
        self.root.after(0, lambda: self.status_label.config(text="Update complete", fg='#00ff00'))
    
    def update_selected_item(self):
        """Update price for selected item only"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to update.")
            return
        
        item_index = self.tree.index(selection[0])
        item = self.data['items'][item_index]
        
        self.update_selected_btn.config(state='disabled', text='Updating...')
        self.status_label.config(text=f"Updating {item['name']}...", fg='#ffff00')
        
        def update():
            price = self.scrape_price(item['url'])
            if price is not None:
                item['current_price'] = price
                item['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_data()
            
            self.refresh_tree()
            self.update_selected_btn.config(state='normal', text='Update Selected')
            self.status_label.config(text="Update complete", fg='#00ff00')
        
        thread = threading.Thread(target=update)
        thread.daemon = True
        thread.start()
    
    def add_item(self):
        """Add a new item"""
        dialog = AddItemDialog(self.root)
        if dialog.result:
            name, url, ref_price, quantity = dialog.result
            new_item = {
                'name': name,
                'url': url,
                'reference_price': ref_price,
                'quantity': quantity,
                'current_price': 0,
                'last_updated': ''
            }
            self.data['items'].append(new_item)
            self.save_data()
            self.refresh_tree()
    
    def remove_item(self):
        """Remove selected item"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove.")
            return
        
        item_index = self.tree.index(selection[0])
        item_name = self.data['items'][item_index]['name']
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to remove '{item_name}'?"):
            del self.data['items'][item_index]
            self.save_data()
            self.refresh_tree()
    
    def move_item_up(self):
        """Move selected item up"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to move.")
            return
        
        item_index = self.tree.index(selection[0])
        if item_index > 0:
            self.data['items'][item_index], self.data['items'][item_index-1] = \
                self.data['items'][item_index-1], self.data['items'][item_index]
            self.save_data()
            self.refresh_tree()
            # Reselect the moved item
            new_selection = self.tree.get_children()[item_index-1]
            self.tree.selection_set(new_selection)
    
    def move_item_down(self):
        """Move selected item down"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to move.")
            return
        
        item_index = self.tree.index(selection[0])
        if item_index < len(self.data['items']) - 1:
            self.data['items'][item_index], self.data['items'][item_index+1] = \
                self.data['items'][item_index+1], self.data['items'][item_index]
            self.save_data()
            self.refresh_tree()
            # Reselect the moved item
            new_selection = self.tree.get_children()[item_index+1]
            self.tree.selection_set(new_selection)
    
    def edit_item(self, event):
        """Edit selected item on double-click"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item_index = self.tree.index(selection[0])
        item = self.data['items'][item_index]
        
        dialog = EditItemDialog(self.root, item)
        if dialog.result:
            name, url, ref_price, quantity = dialog.result
            item['name'] = name
            item['url'] = url
            item['reference_price'] = ref_price
            item['quantity'] = quantity
            self.save_data()
            self.refresh_tree()
    
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
                arrow = " ↕"
            self.tree.heading(column, text=f"{column}{arrow}")

        # Get items and sort them
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        
        # Sort based on column type
        if col == 'Item':
            items.sort(reverse=self.sort_reverse)
        else:
            # Convert values to numbers for numeric sorting
            def convert_value(value):
                try:
                    # Remove commas and any + or % symbols
                    clean_value = value[0].replace(',', '').replace('+', '').replace('%', '')
                    return float(clean_value)
                except (ValueError, TypeError):
                    return float('-inf')  # Place non-numeric values at the start/end
            
            items.sort(key=convert_value, reverse=self.sort_reverse)

        # Rearrange items in sorted order
        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)

    def on_closing(self):
        """Handle application closing"""
        self.stop_updating = True
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=2)
        self.root.destroy()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


class AddItemDialog:
    def __init__(self, parent):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Item")
        self.dialog.geometry("400x300")
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
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Item name
        tk.Label(main_frame, text="Item Name:", fg='white', bg='#2b2b2b', font=('Arial', 10, 'bold')).pack(anchor='w')
        self.name_entry = tk.Entry(main_frame, font=('Arial', 10), width=50)
        self.name_entry.pack(fill=tk.X, pady=(5, 10))
        
        # URL
        tk.Label(main_frame, text="OSRS Website URL:", fg='white', bg='#2b2b2b', font=('Arial', 10, 'bold')).pack(anchor='w')
        self.url_entry = tk.Entry(main_frame, font=('Arial', 10), width=50)
        self.url_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Reference price
        tk.Label(main_frame, text="Reference Price:", fg='white', bg='#2b2b2b', font=('Arial', 10, 'bold')).pack(anchor='w')
        self.ref_price_entry = tk.Entry(main_frame, font=('Arial', 10), width=50)
        self.ref_price_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Quantity
        tk.Label(main_frame, text="Quantity:", fg='white', bg='#2b2b2b', font=('Arial', 10, 'bold')).pack(anchor='w')
        self.quantity_entry = tk.Entry(main_frame, font=('Arial', 10), width=50)
        self.quantity_entry.insert(0, "1")
        self.quantity_entry.pack(fill=tk.X, pady=(5, 20))
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#2b2b2b')
        button_frame.pack(fill=tk.X)
        
        tk.Button(button_frame, text="Add", command=self.add_item,
                 bg='#107c10', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(button_frame, text="Cancel", command=self.cancel,
                 bg='#d13438', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
    
    def add_item(self):
        try:
            name = self.name_entry.get().strip()
            url = self.url_entry.get().strip()
            ref_price = int(self.ref_price_entry.get().strip())
            quantity = int(self.quantity_entry.get().strip())
            
            if not name or not url:
                messagebox.showerror("Error", "Please fill in all fields.")
                return
            
            self.result = (name, url, ref_price, quantity)
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for price and quantity.")
    
    def cancel(self):
        self.dialog.destroy()


class EditItemDialog:
    def __init__(self, parent, item):
        self.result = None
        self.item = item
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Item")
        self.dialog.geometry("400x300")
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
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Item name
        tk.Label(main_frame, text="Item Name:", fg='white', bg='#2b2b2b', font=('Arial', 10, 'bold')).pack(anchor='w')
        self.name_entry = tk.Entry(main_frame, font=('Arial', 10), width=50)
        self.name_entry.insert(0, self.item['name'])
        self.name_entry.pack(fill=tk.X, pady=(5, 10))
        
        # URL
        tk.Label(main_frame, text="OSRS Website URL:", fg='white', bg='#2b2b2b', font=('Arial', 10, 'bold')).pack(anchor='w')
        self.url_entry = tk.Entry(main_frame, font=('Arial', 10), width=50)
        self.url_entry.insert(0, self.item['url'])
        self.url_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Reference price
        tk.Label(main_frame, text="Reference Price:", fg='white', bg='#2b2b2b', font=('Arial', 10, 'bold')).pack(anchor='w')
        self.ref_price_entry = tk.Entry(main_frame, font=('Arial', 10), width=50)
        self.ref_price_entry.insert(0, str(self.item['reference_price']))
        self.ref_price_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Quantity
        tk.Label(main_frame, text="Quantity:", fg='white', bg='#2b2b2b', font=('Arial', 10, 'bold')).pack(anchor='w')
        self.quantity_entry = tk.Entry(main_frame, font=('Arial', 10), width=50)
        self.quantity_entry.insert(0, str(self.item['quantity']))
        self.quantity_entry.pack(fill=tk.X, pady=(5, 20))
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#2b2b2b')
        button_frame.pack(fill=tk.X)
        
        tk.Button(button_frame, text="Save", command=self.save_item,
                 bg='#107c10', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(button_frame, text="Cancel", command=self.cancel,
                 bg='#d13438', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
    
    def save_item(self):
        try:
            name = self.name_entry.get().strip()
            url = self.url_entry.get().strip()
            ref_price = int(self.ref_price_entry.get().strip())
            quantity = int(self.quantity_entry.get().strip())
            
            if not name or not url:
                messagebox.showerror("Error", "Please fill in all fields.")
                return
            
            self.result = (name, url, ref_price, quantity)
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for price and quantity.")
    
    def cancel(self):
        self.dialog.destroy()


if __name__ == "__main__":
    app = OSRSPriceTracker()
    app.run()

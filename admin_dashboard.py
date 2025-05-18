import tkinter as tk
from tkinter import messagebox, ttk, filedialog, scrolledtext, simpledialog
from ttkbootstrap import Style
import mysql.connector
from mysql.connector import Error
from PIL import Image, ImageTk
from datetime import datetime
from dotenv import load_dotenv
import requests
import random
import os
import shutil
import bcrypt
import re
import logging
import time
import sys

# Utility function for handling paths in both development and PyInstaller
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Load environment variables using the resource_path
env_path = resource_path('.env')
load_dotenv(env_path)

API_KEY = os.getenv("BREVO_API_KEY")
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

if not API_KEY or not SMTP_USERNAME or not SMTP_PASSWORD:
    print("Error: Missing environment variables. Check .env file.")
    exit()

# Store verification codes
verification_codes = {}

# Function to send email using Brevo API
def send_email(to_email, subject, message):
    url = "https://api.brevo.com/v3/smtp/email"
    
    headers = {
        "accept": "application/json",
        "api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    data = {
        "sender": {"name": "Tourism Info", "email": SMTP_USERNAME},
        "to": [{"email": to_email, "name": "User"}],
        "subject": subject,
        "htmlContent": f"<p>{message}</p>"
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP Error: {http_err} - {response.text}")
        return {"error": f"HTTP error: {http_err}"}
    except Exception as err:
        print(f"Error: {err}")
        return {"error": f"An error occurred: {err}"}
    
# Database Connection with error handling
def connect_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="tourism_db"
        )
    except mysql.connector.Error as err:
        logging.error(f"Database connection failed: {err}")
        messagebox.showerror("Database Error",
                           f"Failed to connect to database.\nPlease make sure MySQL is running.")
        return None

# Session Management
SESSION_TIMEOUT = 300  # 5 minutes

def create_session(user_id):
    """Create a session file with user ID and timestamp."""
    try:
        session_path = resource_path("session.txt")
        with open(session_path, "w") as f:
            f.write(str(user_id) + "\n")
            f.write(str(time.time()))
    except Exception as e:
        logging.error(f"Error creating session: {e}")

def read_session():
    """Read the session file and return user ID and timestamp."""
    session_path = resource_path("session.txt")
    if os.path.exists(session_path):
        try:
            with open(session_path, "r") as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    return int(lines[0].strip()), float(lines[1].strip())
        except Exception as e:
            logging.error(f"Error reading session: {e}")
    return None, None

def delete_session():
    """Delete the session file."""
    session_path = resource_path("session.txt")
    if os.path.exists(session_path):
        try:
            os.remove(session_path)
        except Exception as e:
            logging.error(f"Error deleting session: {e}")

def update_last_activity(user_id):
    """Update the last_activity timestamp in the database."""
    db = connect_db()
    if db is None:
        return
        
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE user_accounts SET last_activity = NOW() WHERE id = %s", (user_id,))
        db.commit()
    except Error as e:
        logging.error(f"Error updating last activity: {e}")
    finally:
        cursor.close()
        db.close()

# Database Manager Class
class DatabaseManager:
    @staticmethod
    def get_count(table):
        try:
            db = connect_db()
            if db:
                cursor = db.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                cursor.close()
                db.close()
                return count
            return 0
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return 0
    
    @staticmethod
    def execute_query(query, params=None):
        try:
            db = connect_db()
            if db:
                cursor = db.cursor(dictionary=True)
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                result = cursor.fetchall()
                db.commit()
                cursor.close()
                db.close()
                return result
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
        return None

class CustomDatePicker:
    """Custom date picker using ttk.Combobox for day, month, and year."""
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        
        # Get current date for default values
        current_date = datetime.now()
        
        # Day
        self.day_var = tk.StringVar(value=f"{current_date.day:02d}")
        self.day_combo = ttk.Combobox(self.frame, textvariable=self.day_var, width=3)
        self.day_combo['values'] = [f"{i:02d}" for i in range(1, 32)]
        self.day_combo.grid(row=0, column=0)
        # Month
        self.month_var = tk.StringVar(value=f"{current_date.month:02d}")
        self.month_combo = ttk.Combobox(self.frame, textvariable=self.month_var, width=3)
        self.month_combo['values'] = [f"{i:02d}" for i in range(1, 13)]
        self.month_combo.grid(row=0, column=1, padx=2)
        # Year
        self.year_var = tk.StringVar(value=str(current_date.year))
        self.year_combo = ttk.Combobox(self.frame, textvariable=self.year_var, width=5)
        self.year_combo['values'] = [str(i) for i in range(current_date.year - 5, current_date.year + 11)]
        self.year_combo.grid(row=0, column=2)

    def get_date(self):
        """Return the selected date in YYYY-MM-DD format."""
        try:
            year = self.year_var.get()
            month = self.month_var.get()
            day = self.day_var.get()
            # Validate that values are not empty and form a valid date
            if year and month and day and len(year) == 4 and len(month) == 2 and len(day) == 2:
                return f"{year}-{month}-{day}"
            return None
        except Exception as e:
            messagebox.showerror("Date Error", f"Invalid date: {str(e)}")
            return None
    
    def set_date(self, date_str):
        """Set the date from a YYYY-MM-DD string"""
        if date_str and len(date_str) >= 10:
            date_parts = date_str.split('-')
            if len(date_parts) == 3:
                self.year_var.set(date_parts[0])
                self.month_var.set(date_parts[1])
                self.day_var.set(date_parts[2])
    
    def clear(self):
        """Clear all date fields"""
        self.year_var.set("")
        self.month_var.set("")
        self.day_var.set("")

# Admin Dashboard Class
class AdminDashboard:
    def __init__(self, root, user_id):
        self.root = root
        self.current_user_id = user_id
        self.root.title("Tourism Information System - Admin Dashboard")
        self.root.geometry("900x500")
        self.root.resizable(True, True)
        
        # Colors for statistics cards - using ttkbootstrap color names
        self.colors = {
            'places': 'success',  # green
            'events': 'info',     # blue
            'reviews': 'warning', # yellow/orange
            'users': 'secondary', # purple
        }
        
        # Define button colors
        self.pending_button_bg = "#6c757d"  # Gray color for pending button
        self.approve_button_bg = "#28a745"  # Green color for approve button
        self.reject_button_bg = "#dc3545"   # Red color for reject button
        
        # Apply Modern Theme
        self.style = Style()
        
        # Define custom colors
        self.custom_blue = "#0a2351"  # Your requested blue color
        
        # Create a custom style for buttons
        self.style.configure("CustomBlue.TButton", background=self.custom_blue, foreground="white")
        self.style.map("CustomBlue.TButton",
                   background=[("active", self.custom_blue), ("disabled", "gray")],
                   foreground=[("active", "white"), ("disabled", "gray")])
                    
        self.style.configure("Active.TButton", background="white", foreground=self.custom_blue)
        self.style.map("Active.TButton",
                   background=[("active", "white"), ("disabled", "gray")],
                   foreground=[("active", self.custom_blue), ("disabled", "gray")])
        
        # Create session
        create_session(self.current_user_id)
        update_last_activity(self.current_user_id)
        
        # Navigation Menu
        self.menu_frame = ttk.Frame(self.root, bootstyle="secondary")
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # Menu Items
        self.menu_items = [
            "Dashboard",
            "Manage Places",
            "Manage Events",
            "User Management",
            "Feedback",
            "Settings"
        ]
        
        # Store references to all menu buttons
        self.menu_buttons = {}
        
        # Create Navigation Buttons
        for item in self.menu_items:
            btn = ttk.Button(
                self.menu_frame,
                text=item,
                style="CustomBlue.TButton",
                command=lambda i=item: self.show_page(i),
                width=25
            )
            btn.pack(pady=10, padx=10)
            # Store reference to the button
            self.menu_buttons[item] = btn
            
        # Track current active page
        self.current_page = None
        # Main Content Frame
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Default Page
        self.show_page("Dashboard")
        
        # Check session timeout periodically
        self.check_session_timeout()

    def check_session_timeout(self):
        """Check if the session has expired and log out the user if it has."""
        user_id, session_time = read_session()
        if user_id and session_time:
            if time.time() - session_time > SESSION_TIMEOUT:
                self.logout()
                return
        # Check again after 1 minute
        self.root.after(60000, self.check_session_timeout)

    def show_page(self, page):
        """Clears the content frame and displays the selected page."""
        # Reset all buttons to default style
        for item, btn in self.menu_buttons.items():
            if item == page:
                # Set active button to white with blue text
                btn.config(style="Active.TButton")
            else:
                # Set inactive buttons to blue with white text
                btn.config(style="CustomBlue.TButton")
        
        # Update current page tracker
        self.current_page = page
        
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        ttk.Label(self.content_frame, text=page, font=("Arial", 24, "bold")).pack(pady=20)
        
        # Display page content
        if page == "Dashboard":
            self.dashboard_page()
        elif page == "Manage Places":
            self.manage_places_page()
        elif page == "Manage Events":
            self.manage_events_page()
        elif page == "User Management":
            self.user_management_page()
        elif page == "Feedback":
            self.feedback_page()
        elif page == "Settings":
            self.settings_page()

    def dashboard_page(self):
        # Statistics Container
        stats_container = ttk.Frame(self.content_frame)
        stats_container.pack(fill=tk.X, padx=20, pady=10)

        # Statistics Cards Container - using a grid for better organization
        stats_container.columnconfigure(0, weight=1)
        stats_container.columnconfigure(1, weight=1)
        stats_container.columnconfigure(2, weight=1)
        stats_container.columnconfigure(3, weight=1)

        # Fetch Dashboard Statistics
        places_count = DatabaseManager.get_count('places')
        events_count = DatabaseManager.get_count('events')
        reviews_count = DatabaseManager.get_count('reviews')
        users_count = DatabaseManager.get_count('user_accounts')

        # Create Statistic Cards in a grid layout
        self.create_stat_card(stats_container, "TOTAL PLACES", places_count, "🏢", self.colors['places'], 0, 0)
        self.create_stat_card(stats_container, "TOTAL EVENTS", events_count, "📅", self.colors['events'], 0, 1)
        self.create_stat_card(stats_container, "TOTAL REVIEWS", reviews_count, "⭐", self.colors['reviews'], 0, 2)
        self.create_stat_card(stats_container, "TOTAL USERS", users_count, "👥", self.colors['users'], 0, 3)

    def create_stat_card(self, parent, title, value, icon, color, row, col):
        # Card frame with colored background
        card = ttk.Frame(parent, bootstyle=f"{color}", padding=10)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Icon with improved visibility
        ttk.Label(
            card,
            text=icon,
            font=("Arial", 24),
            bootstyle=f"inverse-{color}",
            padding=5
        ).pack(side=tk.TOP, pady=(0, 10))
        
        # Value with larger font for emphasis
        ttk.Label(
            card,
            text=str(value),
            font=("Arial", 32, "bold"),
            bootstyle=f"inverse-{color}",
            anchor="center"
        ).pack(side=tk.TOP, pady=5)
        
        # Title with improved positioning
        ttk.Label(
            card,
            text=title,
            font=("Arial", 10, "bold"),
            bootstyle=f"inverse-{color}",
            anchor="center"
        ).pack(side=tk.TOP)

    def manage_places_page(self):
        """Create the manage places page inside the content frame"""
        places_frame = ttk.Frame(self.content_frame)
        places_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.categories = ["Beach", "Mountains", "Museum", "Camping", "Hiking", "Farm", "Waterfalls", "Golf"]
        
        # Search and filter container row
        top_controls_frame = ttk.Frame(places_frame)
        top_controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search frame (left side)
        search_frame = ttk.Frame(top_controls_frame)
        search_frame.pack(side=tk.LEFT, anchor=tk.W)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        search_btn = ttk.Button(search_frame, text="Search", bootstyle="info",
                              command=self.search_places)
        search_btn.pack(side=tk.LEFT)
        
        # Header buttons frame (right side)
        self.header_buttons_frame = ttk.Frame(top_controls_frame)
        self.header_buttons_frame.pack(side=tk.RIGHT)
        
        # Add Pending Places button (gray color)
        self.pending_button = ttk.Button(
            self.header_buttons_frame,
            text="View Place Requests",
            style="secondary.TButton",  # Using secondary style for gray color
            command=self.show_pending_places_modal
        )
        self.pending_button.pack(side=tk.LEFT, padx=5)
        
        # Add Place button (green color)
        add_btn = ttk.Button(
            self.header_buttons_frame,
            text="Add New Place",
            bootstyle="success",
            command=self.open_add_place_modal
        )
        add_btn.pack(side=tk.LEFT)
        
        # Filter container row
        filter_frame = ttk.Frame(places_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Category filter
        category_frame = ttk.Frame(filter_frame)
        category_frame.pack(side=tk.LEFT)
        ttk.Label(category_frame, text="Category:").pack(side=tk.LEFT, padx=5)
        self.category_filter_var = tk.StringVar()
        self.category_filter = ttk.Combobox(category_frame, textvariable=self.category_filter_var, width=15)
        self.category_filter['values'] = ["All"] + self.categories
        self.category_filter.current(0)  # Set default to "All"
        self.category_filter['state'] = 'readonly'  # Make it non-editable
        self.category_filter.pack(side=tk.LEFT, padx=5)
        # Bind the combobox to filter on selection
        self.category_filter.bind("<<ComboboxSelected>>", lambda event: self.filter_places_by_category())
        
        self.table_frame = ttk.Frame(places_frame)
        self.table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scroll_y = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL)
        
        self.places_table = ttk.Treeview(self.table_frame,
                                      columns=("id", "name", "location", "category", "actions"),
                                      yscrollcommand=scroll_y.set, selectmode="browse")
        
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_y.config(command=self.places_table.yview)
        
        self.places_table.heading("id", text="ID", anchor="center")
        self.places_table.heading("name", text="Name", anchor="center")
        self.places_table.heading("location", text="Location", anchor="center")
        self.places_table.heading("category", text="Category", anchor="center")
        self.places_table.heading("actions", text="Actions", anchor="center")
        self.places_table.column("id", width=50, anchor="center")
        self.places_table.column("name", width=200, anchor="center")
        self.places_table.column("location", width=200, anchor="center")
        self.places_table.column("category", width=150, anchor="center")
        self.places_table.column("actions", width=160, anchor="center")
        
        self.places_table["show"] = "headings"
        
        self.places_table.pack(fill=tk.BOTH, expand=True)
        
        self.load_places()
        
        search_entry.bind("<Return>", lambda event: self.search_places())
        self.places_table.bind("<ButtonRelease-1>", self.handle_place_table_click)
        
    def filter_places_by_category(self):
        """Filter places by selected category"""
        selected_category = self.category_filter_var.get()
        
        # If "All" is selected, just load all places
        if selected_category == "All":
            self.load_places()
            return
        
        db = connect_db()
        if db:
            cursor = db.cursor()
            try:
                cursor.execute("SELECT id, name, location, category FROM places WHERE category = %s AND date_deleted IS NULL",
                             (selected_category,))
                filtered_places = cursor.fetchall()
                
                for item in self.places_table.get_children():
                    self.places_table.delete(item)
                
                for place in filtered_places:
                    self.places_table.insert("", tk.END, values=(
                        place[0],            
                        place[1],            
                        place[2],            
                        place[3],            
                        "Edit / Delete"      
                    ))
                
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", f"Failed to filter places: {str(e)}")
            finally:
                cursor.close()
                db.close()
        
    def handle_place_table_click(self, event):
        """Handle click events on the places table"""
        region = self.places_table.identify_region(event.x, event.y)
        
        if region == "cell":
            column = self.places_table.identify_column(event.x)
            column_index = int(column[1:]) - 1
            
            selected_item = self.places_table.focus()
            if not selected_item:
                return
                
            item_values = self.places_table.item(selected_item, "values")
            place_id = int(item_values[0])
            
            if column_index == 4:  # Actions column
                popup = tk.Menu(self.root, tearoff=0)
                popup.add_command(label="Edit", command=lambda: self.open_edit_place_modal(place_id))
                popup.add_command(label="Delete", command=lambda: self.delete_place(place_id))
                
                try:
                    popup.tk_popup(event.x_root, event.y_root)
                finally:
                    popup.grab_release()

    def load_places(self):
        """Load places into the table"""
        for item in self.places_table.get_children():
            self.places_table.delete(item)
        
        db = connect_db()
        if db:
            cursor = db.cursor()
            try:
                cursor.execute("SELECT id, name, location, category FROM places WHERE date_deleted IS NULL")
                places = cursor.fetchall()
                
                for place in places:
                    self.places_table.insert("", tk.END, values=(
                        place[0],            
                        place[1],            
                        place[2],            
                        place[3],            
                        "Edit / Delete"      
                    ))
                    
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", f"Failed to fetch places: {str(e)}")
            finally:
                cursor.close()
                db.close()  

    def search_places(self):
        """Search places by name"""
        search_term = self.search_var.get().lower()
        selected_category = self.category_filter_var.get()
        
        if search_term == "" and selected_category == "All":
            self.load_places()
            return
        
        db = connect_db()
        if db:
            cursor = db.cursor()
            try:
                if selected_category == "All":
                    # Search without category filter
                    cursor.execute("SELECT id, name, location, category FROM places WHERE LOWER(name) LIKE %s AND date_deleted IS NULL",
                                 (f"%{search_term}%",))
                else:
                    # Search with category filter
                    cursor.execute("SELECT id, name, location, category FROM places WHERE LOWER(name) LIKE %s AND category = %s AND date_deleted IS NULL",
                                 (f"%{search_term}%", selected_category))
                    
                filtered_places = cursor.fetchall()
                
                for item in self.places_table.get_children():
                    self.places_table.delete(item)
                
                for place in filtered_places:
                    self.places_table.insert("", tk.END, values=(
                        place[0],            
                        place[1],            
                        place[2],            
                        place[3],            
                        "Edit / Delete"      
                    ))
                
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", f"Failed to search places: {str(e)}")
            finally:
                cursor.close()
                db.close()
        
    def open_add_place_modal(self):
        """Open modal window for adding a new place"""
        self.add_window = tk.Toplevel(self.root)
        self.add_window.title("Add New Place")
        self.add_window.geometry("600x600")
        self.add_window.configure(bg="white")
        self.add_window.resizable(False, False)
        self.add_window.transient(self.root)
        self.add_window.grab_set()
        
        title_label = ttk.Label(self.add_window, text="Add New Place", font=("Arial", 16, "bold"))
        title_label.pack(pady=15)
        
        form_frame = ttk.Frame(self.add_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Label(form_frame, text="Name:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=5)
        self.add_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.add_name_var, width=40).grid(
            row=0, column=1, sticky=tk.W, pady=5)
        
        # Description
        ttk.Label(form_frame, text="Description:", font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky=tk.W, pady=5)
        self.add_desc_text = scrolledtext.ScrolledText(form_frame, width=40, height=5)
        self.add_desc_text.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="Location:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=5)
        self.add_location_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.add_location_var, width=40).grid(
            row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="Category:", font=("Arial", 10, "bold")).grid(
            row=3, column=0, sticky=tk.W, pady=5)
        self.add_category_var = tk.StringVar()
        category_combobox = ttk.Combobox(form_frame, textvariable=self.add_category_var,
                                       values=self.categories, width=38)
        category_combobox['state'] = 'readonly'  # Make it non-editable
        category_combobox.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="Upload Images:", font=("Arial", 10, "bold")).grid(
            row=5, column=0, sticky=tk.W, pady=5)
        
        upload_frame = ttk.Frame(form_frame)
        upload_frame.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        upload_btn = ttk.Button(upload_frame, text="Upload Images", bootstyle="info",
                              command=lambda: self.upload_place_images('add'))
        upload_btn.pack()
        
        self.add_image_preview = ttk.Frame(form_frame)
        self.add_image_preview.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        self.add_image_paths = []
        self.add_image_frames = {}
        
        buttons_frame = ttk.Frame(self.add_window)
        buttons_frame.pack(fill=tk.X, pady=15, padx=20)
        
        save_btn = ttk.Button(buttons_frame, text="Save", bootstyle="success",
                            command=self.save_place)
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = ttk.Button(buttons_frame, text="Cancel", bootstyle="secondary",
                              command=self.add_window.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
   
    def upload_place_images(self, mode='add'):
        """Open file dialog to select multiple images and display them"""
        file_types = [("Image Files", "*.png *.jpg *.jpeg *.gif")]
        files = filedialog.askopenfilenames(title="Select Images", filetypes=file_types)
        
        if files:
            if mode == 'add':
                self.add_image_paths.extend(files)
                preview_frame = self.add_image_preview
                image_paths = self.add_image_paths
                image_frames = self.add_image_frames
            else:
                self.edit_image_paths.extend(files)
                preview_frame = self.edit_image_preview
                image_paths = self.edit_image_paths
                image_frames = self.edit_image_frames
            
            self.display_place_images(mode, preview_frame, image_paths, image_frames)
   
    def display_place_images(self, mode, preview_frame, image_paths, image_frames):
        """Display thumbnails of images"""
        for widget in preview_frame.winfo_children():
            widget.destroy()
        
        for i, path in enumerate(image_paths):
            if path in image_frames:
                continue
                
            try:
                img = Image.open(path)
                img.thumbnail((80, 80))
                photo_img = ImageTk.PhotoImage(img)
                
                img_frame = ttk.Frame(preview_frame)
                img_frame.pack(side=tk.LEFT, padx=5, pady=5)
                
                img_label = ttk.Label(img_frame, image=photo_img)
                img_label.image = photo_img
                img_label.pack()
                
                delete_btn = ttk.Button(img_frame, text="x", bootstyle="danger-outline",
                                      command=lambda p=path, m=mode: self.delete_place_image(p, m))
                delete_btn.place(relx=1.0, rely=0.0, anchor=tk.NE)
                
                image_frames[path] = img_frame
                
            except Exception as e:
                print(f"Error loading image {path}: {str(e)}")
   
    def delete_place_image(self, path, mode):
        """Delete an image from the preview"""
        if mode == 'add':
            if path in self.add_image_paths:
                self.add_image_paths.remove(path)
            
            if path in self.add_image_frames and self.add_image_frames[path]:
                if self.add_image_frames[path].winfo_exists():
                    self.add_image_frames[path].destroy()
                del self.add_image_frames[path]
        else:
            if path in self.edit_image_paths:
                self.edit_image_paths.remove(path)
            
            if path in self.edit_image_frames and self.edit_image_frames[path]:
                if self.edit_image_frames[path].winfo_exists():
                    self.edit_image_frames[path].destroy()
                del self.edit_image_frames[path]
   
    def save_place(self):
        """Save a new place to the database"""
        name = self.add_name_var.get()
        description = self.add_desc_text.get("1.0", tk.END).strip()
        location = self.add_location_var.get()
        category = self.add_category_var.get()
        
        if not name or not description or not location or not category:
            messagebox.showerror("Error", "All fields are required!")
            return
            
        # Handle image upload
        image_path = None
        if self.add_image_paths:
            # Create places images directory if it doesn't exist
            upload_dir = resource_path(os.path.join("uploads", "places"))
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate a unique filename
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(self.add_image_paths[0])[1]}"
            destination = os.path.join(upload_dir, filename)
            
            try:
                # Copy the image
                shutil.copy2(self.add_image_paths[0], destination)
                image_path = os.path.join("uploads", "places", filename)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload image: {str(e)}")
                return

        db = connect_db()
        if db:
            cursor = db.cursor()
            try:
                # Modified to include status='approved' since this is an admin adding the place
                sql = """INSERT INTO places (user_id, name, description, category, location, image, date_created, status)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, 'approved')"""
                cursor.execute(sql, (self.current_user_id, name, description, category, location, image_path, datetime.now()))
                db.commit()
                new_id = cursor.lastrowid
            except mysql.connector.Error as e:
                db.rollback()
                messagebox.showerror("Database Error", f"Failed to add place: {str(e)}")
                return
            finally:
                cursor.close()
                db.close()
        else:
            return
        
        self.add_window.destroy()
        self.load_places()
        messagebox.showinfo("Success", "Place added successfully!")
   
    def open_edit_place_modal(self, place_id):
        """Open modal window for editing a place"""
        db = connect_db()
        if db:
            cursor = db.cursor()
            try:
                cursor.execute("SELECT id, name, description, location, category, image FROM places WHERE id = %s AND date_deleted IS NULL", (place_id,))
                place = cursor.fetchone()
                
                if not place:
                    messagebox.showerror("Error", "Place not found!")
                    return
                
                self.edit_window = tk.Toplevel(self.root)
                self.edit_window.title("Edit Place")
                self.edit_window.geometry("600x600")
                self.edit_window.resizable(False, False)
                self.edit_window.transient(self.root)
                self.edit_window.grab_set()
                
                title_label = ttk.Label(self.edit_window, text="Edit Place", font=("Arial", 16, "bold"))
                title_label.pack(pady=15)
                
                form_frame = ttk.Frame(self.edit_window)
                form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
                
                self.edit_place_id = place_id
                
                ttk.Label(form_frame, text="Name:", font=("Arial", 10, "bold")).grid(
                    row=0, column=0, sticky=tk.W, pady=5)
                self.edit_name_var = tk.StringVar(value=place[1])
                ttk.Entry(form_frame, textvariable=self.edit_name_var, width=40).grid(
                    row=0, column=1, sticky=tk.W, pady=5)
                
                ttk.Label(form_frame, text="Description:", font=("Arial", 10, "bold")).grid(
                    row=1, column=0, sticky=tk.W, pady=5)
                self.edit_desc_text = tk.Text(form_frame, width=40, height=5)
                self.edit_desc_text.insert("1.0", place[2])
                self.edit_desc_text.grid(row=1, column=1, sticky=tk.W, pady=5)
                
                ttk.Label(form_frame, text="Location:", font=("Arial", 10, "bold")).grid(
                    row=2, column=0, sticky=tk.W, pady=5)
                self.edit_location_var = tk.StringVar(value=place[3])
                ttk.Entry(form_frame, textvariable=self.edit_location_var, width=40).grid(
                    row=2, column=1, sticky=tk.W, pady=5)
                
                ttk.Label(form_frame, text="Category:", font=("Arial", 10, "bold")).grid(
                    row=3, column=0, sticky=tk.W, pady=5)
                self.edit_category_var = tk.StringVar(value=place[4])
                category_combobox = ttk.Combobox(form_frame, textvariable=self.edit_category_var,
                                            values=self.categories, width=38)
                category_combobox['state'] = 'readonly'  # Make it non-editable
                category_combobox.grid(row=3, column=1, sticky=tk.W, pady=5)
                
                ttk.Label(form_frame, text="Images:", font=("Arial", 10, "bold")).grid(
                    row=4, column=0, sticky=tk.W, pady=5)
                
                upload_frame = ttk.Frame(form_frame)
                upload_frame.grid(row=4, column=1, sticky=tk.W, pady=5)
                
                upload_btn = ttk.Button(upload_frame, text="Upload Images", bootstyle="info",
                                      command=lambda: self.upload_place_images('edit'))
                upload_btn.pack()
                
                self.edit_image_preview = ttk.Frame(form_frame)
                self.edit_image_preview.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=10)
                
                self.edit_image_paths = []
                self.edit_image_frames = {}
                
                self.existing_images = []
                if place[5]:
                    self.existing_images = [place[5].strip()] if place[5].strip() else []
                    self.edit_image_paths = self.existing_images.copy()
                    
                    if self.existing_images:
                        self.display_place_images('edit', self.edit_image_preview, self.edit_image_paths, self.edit_image_frames)
                
                buttons_frame = ttk.Frame(self.edit_window)
                buttons_frame.pack(fill=tk.X, pady=15, padx=20)
                
                update_btn = ttk.Button(buttons_frame, text="Update", bootstyle="success",
                                      command=self.update_place)
                update_btn.pack(side=tk.RIGHT, padx=5)
                
                cancel_btn = ttk.Button(buttons_frame, text="Cancel", bootstyle="secondary",
                                      command=self.edit_window.destroy)
                cancel_btn.pack(side=tk.RIGHT, padx=5)
                
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", f"Failed to fetch place: {str(e)}")
            finally:
                cursor.close()
                db.close()
        else:
            return
   
    def update_place(self):
        """Update an existing place"""
        name = self.edit_name_var.get()
        description = self.edit_desc_text.get("1.0", tk.END).strip()
        location = self.edit_location_var.get()
        category = self.edit_category_var.get()
        
        if not name or not description or not location or not category:
            messagebox.showerror("Error", "All fields are required!")
            return
        
        # Handle image update
        image_path = self.existing_images[0] if self.existing_images else None
        if self.edit_image_paths and self.edit_image_paths[0] != image_path:
            # Create places images directory if it doesn't exist
            upload_dir = resource_path(os.path.join("uploads", "places"))
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate a unique filename
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(self.edit_image_paths[0])[1]}"
            destination = os.path.join(upload_dir, filename)
            
            try:
                # Copy the new image
                shutil.copy2(self.edit_image_paths[0], destination)
                image_path = os.path.join("uploads", "places", filename)
                
                # Delete the old image if it exists and is different
                if self.existing_images and os.path.exists(resource_path(self.existing_images[0])):
                    os.remove(resource_path(self.existing_images[0]))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update image: {str(e)}")
                return

        db = connect_db()
        if db:
            cursor = db.cursor()
            try:
                sql = """UPDATE places
                         SET name = %s, description = %s, category = %s, location = %s,
                         image = %s, date_modified = %s
                         WHERE id = %s"""
                cursor.execute(sql, (name, description, category, location,
                                   image_path, datetime.now(), self.edit_place_id))
                db.commit()
            except mysql.connector.Error as e:
                db.rollback()
                messagebox.showerror("Database Error", f"Failed to update place: {str(e)}")
                return
            finally:
                cursor.close()
                db.close()
        else:
            return
        
        self.edit_window.destroy()
        self.load_places()
        messagebox.showinfo("Success", "Place updated successfully!")
   
    def delete_place(self, place_id):
        """Soft delete a place by setting date_deleted"""
        confirm = messagebox.askyesno("Delete Place", "Are you sure you want to delete this place?")
        
        if confirm:
            db = connect_db()
            if db:
                cursor = db.cursor()
                try:
                    sql = "UPDATE places SET status = 'rejected', date_deleted = %s WHERE id = %s"
                    now = datetime.now()
                    cursor.execute(sql, (now, place_id))
                    db.commit()
                except mysql.connector.Error as e:
                    db.rollback()
                    messagebox.showerror("Database Error", f"Failed to delete place: {str(e)}")
                    return
                finally:
                    cursor.close()
                    db.close()
            else:
                return
            
            self.load_places()
            messagebox.showinfo("Success", "Place deleted successfully!")
        
    def show_pending_places_modal(self):
        """Show modal with pending place submissions"""
        # Get pending places from the database
        db = connect_db()
        if not db:
            return
            
        cursor = db.cursor(dictionary=True)
        try:
            # Query to get pending places with user information
            cursor.execute("""
                SELECT p.*, u.username, u.email
                FROM places p
                JOIN user_accounts u ON p.user_id = u.id
                WHERE p.status = 'pending' AND p.date_deleted IS NULL
            """)
            pending_places = cursor.fetchall()
            
            if not pending_places:
                messagebox.showinfo("No Pending Places", "There are no pending place submissions.")
                return
                
            # Create modal window
            self.pending_places_modal = tk.Toplevel(self.root)
            self.pending_places_modal.title("Pending Place Submissions")
            self.pending_places_modal.geometry("800x600")
            self.pending_places_modal.transient(self.root)
            self.pending_places_modal.grab_set()
            
            # Modal header
            header_frame = tk.Frame(self.pending_places_modal, bg="white", padx=20, pady=10)
            header_frame.pack(fill="x")
            
            header_label = tk.Label(header_frame, text="Pending Place Submissions",
                                 font=("Arial", 14, "bold"), bg="white")
            header_label.pack(side="left")
            
            # Create a canvas with a scrollbar
            canvas_frame = tk.Frame(self.pending_places_modal)
            canvas_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            canvas = tk.Canvas(canvas_frame)
            scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
            
            # Configure the canvas
            canvas.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            
            # Create a frame inside the canvas
            content_frame = tk.Frame(canvas)
            canvas.create_window((0, 0), window=content_frame, anchor="nw")
            
            # Display pending places
            for i, place in enumerate(pending_places):
                self.create_pending_place_card(content_frame, place, i)
            
            # Update the canvas scroll region
            content_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))
            
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch pending places: {str(e)}")
        finally:
            cursor.close()
            db.close()

    def create_pending_place_card(self, parent, place, index):
        """Create a card for a pending place submission"""
        # Place card frame
        card = tk.Frame(parent, bg="white", bd=1, relief=tk.SOLID, padx=15, pady=15)
        card.pack(fill="x", pady=10)
        
        # User info
        user_label = tk.Label(
            card,
            text=f"Submitted by: {place['username']} ({place['email']})",
            font=("Arial", 10, "bold"),
            fg="#555",
            bg="white"
        )
        user_label.pack(anchor="w", pady=(0, 10))
        
        # Place details
        details_frame = tk.Frame(card, bg="white")
        details_frame.pack(fill="x", pady=5)
        
        # Property fields for name, category, and location
        properties = [
            ("Place Name:", place['name']),
            ("Category:", place['category']),
            ("Location:", place['location']),
        ]
        
        for prop_name, prop_value in properties:
            prop_frame = tk.Frame(details_frame, bg="white")
            prop_frame.pack(anchor="w", pady=2)
            
            label = tk.Label(
                prop_frame,
                text=prop_name,
                font=("Arial", 9, "bold"),
                width=12,
                anchor="w",
                bg="white"
            )
            label.pack(side="left")
            
            value = tk.Label(
                prop_frame,
                text=prop_value,
                font=("Arial", 9),
                anchor="w",
                bg="white"
            )
            value.pack(side="left", fill="x", expand=True)
        
        # Special handling for description with scrollable text widget
        desc_frame = tk.Frame(details_frame, bg="white")
        desc_frame.pack(anchor="w", pady=2, fill="x")
        
        desc_label = tk.Label(
            desc_frame,
            text="Description:",
            font=("Arial", 9, "bold"),
            width=12,
            anchor="w",
            bg="white"
        )
        desc_label.pack(side="left", anchor="n")
        
        # Create a frame for the description text widget and scrollbar
        desc_text_frame = tk.Frame(desc_frame, bg="white")
        desc_text_frame.pack(side="left", fill="both", expand=True)
        
        # Create scrollable text widget for description
        desc_text = tk.Text(
            desc_text_frame,
            wrap=tk.WORD,
            width=60,
            height=4,  # Fixed height of 4 lines
            font=("Arial", 9),
            bd=1,
            relief=tk.SOLID
        )
        desc_text.insert("1.0", place['description'])
        desc_text.config(state=tk.DISABLED)  # Make it read-only
        
        # Add scrollbar for the description
        desc_scroll = ttk.Scrollbar(desc_text_frame, command=desc_text.yview)
        desc_text.configure(yscrollcommand=desc_scroll.set)
        
        desc_text.pack(side="left", fill="both", expand=True)
        desc_scroll.pack(side="right", fill="y")
        
        # Approval buttons in their own frame
        buttons_frame = tk.Frame(card, bg="white")
        buttons_frame.pack(fill="x", pady=(10, 0), anchor="e")
        
        approve_button = tk.Button(
            buttons_frame,
            text="✅ Approve",
            bg=self.approve_button_bg,
            fg="white",
            bd=0,
            padx=10,
            pady=3,
            cursor="hand2",
            command=lambda pid=place['id']: self.approve_place(pid)
        )
        approve_button.pack(side="right", padx=(0, 5))
        
        reject_button = tk.Button(
            buttons_frame,
            text="❌ Reject/Delete",
            bg=self.reject_button_bg,
            fg="white",
            bd=0,
            padx=10,
            pady=3,
            cursor="hand2",
            command=lambda pid=place['id']: self.reject_place(pid)
        )
        reject_button.pack(side="right", padx=5)

    def approve_place(self, place_id):
        """Approve a pending place"""
        db = connect_db()
        if not db:
            return
            
        cursor = db.cursor()
        try:
            # Update the place to mark it as approved
            cursor.execute("""
                UPDATE places
                SET status = 'approved',
                    date_modified = %s
                WHERE id = %s
            """, (datetime.now(), place_id))
            
            db.commit()
            messagebox.showinfo("Success", "Place approved successfully!")
            
            # Close the modal and refresh the places list
            if hasattr(self, 'pending_places_modal') and self.pending_places_modal.winfo_exists():
                self.pending_places_modal.destroy()
            self.load_places()
            
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to approve place: {str(e)}")
        finally:
            cursor.close()
            db.close()

    def reject_place(self, place_id):
        """Reject and soft delete a pending place"""
        confirm = messagebox.askyesno("Confirm Rejection", "Are you sure you want to reject and delete this place?")
        if not confirm:
            return
        
        db = connect_db()
        if not db:
            return
            
        cursor = db.cursor()
        try:
            # Update status to rejected (soft delete)
            cursor.execute("""
                UPDATE places
                SET status = 'rejected',
                    date_deleted = %s
                WHERE id = %s
            """, (datetime.now(), place_id))
            
            db.commit()
            messagebox.showinfo("Success", "Place rejected and deleted successfully!")
            
            # Close the modal and refresh the places list
            if hasattr(self, 'pending_places_modal') and self.pending_places_modal.winfo_exists():
                self.pending_places_modal.destroy()
            self.load_places()
            
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to reject place: {str(e)}")
        finally:
            cursor.close()
            db.close()
    
    def manage_events_page(self):
        """Create the manage events page inside the content frame"""
        events_frame = ttk.Frame(self.content_frame)
        events_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Search and filter container row
        top_controls_frame = ttk.Frame(events_frame)
        top_controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search frame (left side)
        search_frame = ttk.Frame(top_controls_frame)
        search_frame.pack(side=tk.LEFT, anchor=tk.W)
        
        ttk.Label(search_frame, text="Search").pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        search_btn = ttk.Button(search_frame, text="Search", bootstyle="info",
                              command=self.search_events)
        search_btn.pack(side=tk.LEFT)
        
        # Header buttons frame (right side)
        self.header_buttons_frame = ttk.Frame(top_controls_frame)
        self.header_buttons_frame.pack(side=tk.RIGHT)
        
        # Add Pending Events button (gray color)
        self.pending_button = ttk.Button(
            self.header_buttons_frame,
            text="View Event Requests",
            style="secondary.TButton",  # Using secondary style for gray color
            command=self.show_pending_modal
        )
        self.pending_button.pack(side=tk.LEFT, padx=5)
        
        # Add Event button (green color)
        add_btn = ttk.Button(
            self.header_buttons_frame,
            text="Add New Event",
            bootstyle="success",
            command=self.open_add_modal
        )
        add_btn.pack(side=tk.LEFT)
        
        # Filter container row
        filter_frame = ttk.Frame(events_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Date filter
        date_frame = ttk.Frame(filter_frame)
        date_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(date_frame, text="Filter by date:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_date = CustomDatePicker(date_frame)
        self.filter_date.frame.pack(side=tk.LEFT, padx=(0, 5))
        
        # Clear date button
        clear_date_btn = ttk.Button(date_frame, text="Clear Date", bootstyle="secondary",
                                  command=lambda: self.filter_date.clear())
        clear_date_btn.pack(side=tk.LEFT)
        
        # Category filter
        category_frame = ttk.Frame(filter_frame)
        category_frame.pack(side=tk.LEFT)
        
        ttk.Label(category_frame, text="Event Type:").pack(side=tk.LEFT, padx=(0, 5))
        self.category_filter_var = tk.StringVar(value="All")
        category_combo = ttk.Combobox(category_frame, textvariable=self.category_filter_var,
                                    values=["All", "Festival", "Concert", "Exhibition", "Sports", "Conference", "Workshop"],
                                    state="readonly", width=12)
        category_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Apply filters button
        apply_btn = ttk.Button(filter_frame, text="Apply Filters", bootstyle="success",
                             command=self.filter_events)
        apply_btn.pack(side=tk.LEFT)
        
        # Create table with correct column order
        self.table_frame = ttk.Frame(events_frame)
        self.table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scroll_y = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL)
        
        # Updated column order: ID, Event Name, Category, Date, Time, Location, Actions
        self.events_table = ttk.Treeview(self.table_frame, 
                                        columns=("id", "name", "category", "date", "time", "location", "actions"),
                                        yscrollcommand=scroll_y.set, selectmode="browse")
        
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_y.config(command=self.events_table.yview)
        
        # Configure headings
        self.events_table.heading("id", text="ID", anchor="center")
        self.events_table.heading("name", text="Event Name", anchor="center")
        self.events_table.heading("category", text="Event Type", anchor="center")
        self.events_table.heading("date", text="Date", anchor="center")
        self.events_table.heading("time", text="Time", anchor="center")
        self.events_table.heading("location", text="Location", anchor="center")
        self.events_table.heading("actions", text="Actions", anchor="center")

        # Configure columns - adjust widths to match screenshot
        self.events_table.column("id", width=50, anchor="center")
        self.events_table.column("name", width=200, anchor="center")
        self.events_table.column("category", width=100, anchor="center")
        self.events_table.column("date", width=100, anchor="center")
        self.events_table.column("time", width=100, anchor="center")
        self.events_table.column("location", width=150, anchor="center")
        self.events_table.column("actions", width=100, anchor="center")
        
        self.events_table["show"] = "headings"
        
        self.events_table.pack(fill=tk.BOTH, expand=True)
        
        # Load events
        self.load_events()
        
        # Bind events
        search_entry.bind("<Return>", lambda event: self.search_events())
        self.events_table.bind("<ButtonRelease-1>", self.handle_table_click)

    def handle_table_click(self, event):
        """Handle click events on the table"""
        region = self.events_table.identify_region(event.x, event.y)
        
        if region == "cell":
            column = self.events_table.identify_column(event.x)
            column_index = int(column[1:]) - 1
            
            selected_item = self.events_table.focus()
            if not selected_item:
                return
                
            item_values = self.events_table.item(selected_item, "values")
            event_id = int(item_values[0])
            
            if column_index == 6:  # Actions column
                popup = tk.Menu(self.root, tearoff=0)
                popup.add_command(label="Edit", command=lambda: self.open_edit_modal(event_id))
                popup.add_command(label="Delete", command=lambda: self.delete_event(event_id))
                
                try:
                    popup.tk_popup(event.x_root, event.y_root)
                finally:
                    popup.grab_release()

    def load_events(self):
        """Load events into the table with the correct column order"""
        # Clear existing items
        for item in self.events_table.get_children():
            self.events_table.delete(item)
        
        db = connect_db()
        if db:
            cursor = db.cursor()
            try:
                cursor.execute("""
                    SELECT id, name, category, date, time, location 
                    FROM events 
                    WHERE date_deleted IS NULL
                    ORDER BY date DESC, time ASC
                """)
                events = cursor.fetchall()
                
                for event in events:
                    # Format date and time for display
                    if event[3]:  # Check if date is not None
                        event_date = datetime.strptime(str(event[3]), '%Y-%m-%d').strftime('%Y-%m-%d')
                    else:
                        event_date = "N/A"
                    
                    if event[4]:  # Check if time is not None
                        event_time = datetime.strptime(str(event[4]), '%H:%M:%S').strftime('%I:%M %p')
                    else:
                        event_time = "N/A"
                    
                    # Insert with correct column order: ID, Event Name, Category, Date, Time, Location, Actions
                    self.events_table.insert("", tk.END, values=(
                        event[0],             # ID
                        event[1],             # Name
                        event[2],             # Category
                        event_date,           # Date
                        event_time,           # Time
                        event[5],             # Location
                        "Edit / Delete"       # Actions
                    ))
                    
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", f"Failed to fetch events: {str(e)}")
            finally:
                cursor.close()
                db.close()

    def search_events(self):
        """Search events by name"""
        search_term = self.search_var.get().lower()
        
        if search_term == "":
            self.load_events()
            return
        
        db = connect_db()
        if db:
            cursor = db.cursor()
            try:
                cursor.execute("""
                    SELECT id, name, category, date, time, location 
                    FROM events 
                    WHERE LOWER(name) LIKE %s AND date_deleted IS NULL
                    ORDER BY date DESC, time ASC
                """, (f"%{search_term}%",))
                
                events = cursor.fetchall()
                
                # Clear existing items
                for item in self.events_table.get_children():
                    self.events_table.delete(item)
                
                for event in events:
                    # Format date and time for display
                    if event[3]:  # Check if date is not None
                        event_date = datetime.strptime(str(event[3]), '%Y-%m-%d').strftime('%Y-%m-%d')
                    else:
                        event_date = "N/A"
                    
                    if event[4]:  # Check if time is not None
                        event_time = datetime.strptime(str(event[4]), '%H:%M:%S').strftime('%I:%M %p')
                    else:
                        event_time = "N/A"
                    
                    # Insert with correct column order
                    self.events_table.insert("", tk.END, values=(
                        event[0],             # ID
                        event[1],             # Name
                        event[2],             # Category
                        event_date,           # Date
                        event_time,           # Time
                        event[5],             # Location
                        "Edit / Delete"       # Actions
                    ))
                
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", f"Failed to search events: {str(e)}")
            finally:
                cursor.close()
                db.close()

    def filter_events(self):
        """Filter events by date and category"""
        selected_date = self.filter_date.get_date()
        selected_category = self.category_filter_var.get()
        
        # Build WHERE clause based on filters
        where_clauses = ["date_deleted IS NULL"]
        params = []
        
        if selected_date:
            where_clauses.append("date = %s")
            params.append(selected_date)
            
        if selected_category != "All":
            where_clauses.append("category = %s")
            params.append(selected_category)
        
        where_clause = " AND ".join(where_clauses) if where_clauses else "1"
        
        db = connect_db()
        if db:
            cursor = db.cursor()
            try:
                query = f"""
                    SELECT id, name, category, date, time, location 
                    FROM events 
                    WHERE {where_clause}
                    ORDER BY date DESC, time ASC
                """
                cursor.execute(query, tuple(params))
                
                events = cursor.fetchall()
                
                # Clear existing items
                for item in self.events_table.get_children():
                    self.events_table.delete(item)
                
                for event in events:
                    # Format date and time for display
                    if event[3]:  # Check if date is not None
                        event_date = datetime.strptime(str(event[3]), '%Y-%m-%d').strftime('%Y-%m-%d')
                    else:
                        event_date = "N/A"
                    
                    if event[4]:  # Check if time is not None
                        event_time = datetime.strptime(str(event[4]), '%H:%M:%S').strftime('%I:%M %p')
                    else:
                        event_time = "N/A"
                    
                    # Insert with correct column order
                    self.events_table.insert("", tk.END, values=(
                        event[0],             # ID
                        event[1],             # Name
                        event[2],             # Category
                        event_date,           # Date
                        event_time,           # Time
                        event[5],             # Location
                        "Edit / Delete"       # Actions
                    ))
                
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", f"Failed to filter events: {str(e)}")
            finally:
                cursor.close()
                db.close()

    def open_add_modal(self):
        """Open modal window for adding a new event"""
        self.add_window = tk.Toplevel(self.root)
        self.add_window.title("Add New Event")
        self.add_window.geometry("600x700")
        self.add_window.configure(bg="white")
        self.add_window.resizable(False, False)
        self.add_window.transient(self.root)
        self.add_window.grab_set()
        
        title_label = ttk.Label(self.add_window, text="Add New Event", font=("Arial", 16, "bold"))
        title_label.pack(pady=15)
        
        form_frame = ttk.Frame(self.add_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Event Name
        ttk.Label(form_frame, text="Event Name:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=5)
        self.add_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.add_name_var, width=40).grid(
            row=0, column=1, sticky=tk.W, pady=5)
        
        # Description
        ttk.Label(form_frame, text="Description:", font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky=tk.W, pady=5)
        self.add_desc_text = scrolledtext.ScrolledText(form_frame, width=40, height=5)
        self.add_desc_text.grid(row=1, column=1, sticky=tk.W, pady=5)

        # Event Location
        ttk.Label(form_frame, text="Location:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=5)
        self.add_location_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.add_location_var, width=40).grid(
            row=2, column=1, sticky=tk.W, pady=5)
        
        # Event Date
        ttk.Label(form_frame, text="Event Date:", font=("Arial", 10, "bold")).grid(
            row=3, column=0, sticky=tk.W, pady=5)
        self.add_date_picker = CustomDatePicker(form_frame)
        self.add_date_picker.frame.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Event Category
        ttk.Label(form_frame, text="Event Type:", font=("Arial", 10, "bold")).grid(
            row=4, column=0, sticky=tk.W, pady=5)
        self.add_category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=self.add_category_var,
                                    values=["Festival", "Concert", "Exhibition", "Sports", "Conference", "Workshop"],
                                    state="readonly", width=38)
        category_combo.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Event Time
        ttk.Label(form_frame, text="Event Time:", font=("Arial", 10, "bold")).grid(
            row=5, column=0, sticky=tk.W, pady=5)
        
        time_frame = ttk.Frame(form_frame)
        time_frame.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        self.hour_var = tk.StringVar(value="12")
        hour_combo = ttk.Combobox(time_frame, textvariable=self.hour_var, width=3)
        hour_combo['values'] = [f"{i:02d}" for i in range(1, 13)]
        hour_combo.grid(row=0, column=0)
        
        ttk.Label(time_frame, text=":").grid(row=0, column=1)
        
        self.minute_var = tk.StringVar(value="00")
        minute_combo = ttk.Combobox(time_frame, textvariable=self.minute_var, width=3)
        minute_combo['values'] = [f"{i:02d}" for i in range(0, 60, 5)]
        minute_combo.grid(row=0, column=2)
        
        self.ampm_var = tk.StringVar(value="PM")
        ampm_combo = ttk.Combobox(time_frame, textvariable=self.ampm_var, width=3)
        ampm_combo['values'] = ["AM", "PM"]
        ampm_combo.grid(row=0, column=3, padx=(5, 0))
        
        # Entry Fee - Using radio buttons
        ttk.Label(form_frame, text="Entry Fee:", font=("Arial", 10, "bold")).grid(
            row=6, column=0, sticky=tk.W, pady=5)
        
        fee_frame = ttk.Frame(form_frame)
        fee_frame.grid(row=6, column=1, sticky=tk.W, pady=5)
        
        self.add_fee_type = tk.StringVar(value="free")  # Default to free event
        
        # Free Event radio button
        free_rb = ttk.Radiobutton(
            fee_frame, 
            text="Free Event", 
            variable=self.add_fee_type, 
            value="free"
        )
        free_rb.pack(side=tk.LEFT, padx=(0, 10))
        
        # Paid Event radio button
        paid_rb = ttk.Radiobutton(
            fee_frame, 
            text="Paid Event", 
            variable=self.add_fee_type, 
            value="paid"
        )
        paid_rb.pack(side=tk.LEFT)
        
        # Image Upload
        ttk.Label(form_frame, text="Upload Images:", font=("Arial", 10, "bold")).grid(
            row=7, column=0, sticky=tk.W, pady=5)
        
        upload_frame = ttk.Frame(form_frame)
        upload_frame.grid(row=7, column=1, sticky=tk.W, pady=5)
        
        upload_btn = ttk.Button(upload_frame, text="Upload Images", bootstyle="info",
                              command=lambda: self.upload_images('add'))
        upload_btn.pack()
        
        self.add_image_preview = ttk.Frame(form_frame)
        self.add_image_preview.grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        self.add_image_paths = []
        self.add_image_frames = {}
        
        buttons_frame = ttk.Frame(self.add_window)
        buttons_frame.pack(fill=tk.X, pady=15, padx=20)
        
        save_btn = ttk.Button(buttons_frame, text="Save", bootstyle="success",
                            command=self.save_new_event)
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = ttk.Button(buttons_frame, text="Cancel", bootstyle="secondary",
                              command=self.add_window.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

    def upload_images(self, mode='add'):
        """Open file dialog to select multiple images and display them"""
        file_types = [("Image Files", "*.png *.jpg *.jpeg *.gif")]
        files = filedialog.askopenfilenames(title="Select Images", filetypes=file_types)
        
        if files:
            if mode == 'add':
                self.add_image_paths.extend(files)
                preview_frame = self.add_image_preview
                image_paths = self.add_image_paths
                image_frames = self.add_image_frames
            else:
                self.edit_image_paths.extend(files)
                preview_frame = self.edit_image_preview
                image_paths = self.edit_image_paths
                image_frames = self.edit_image_frames
            
            self.display_images(mode, preview_frame, image_paths, image_frames)

    def display_images(self, mode, preview_frame, image_paths, image_frames):
        """Display thumbnails of images"""
        for widget in preview_frame.winfo_children():
            widget.destroy()
        
        for i, path in enumerate(image_paths):
            if path in image_frames:
                continue
                
            try:
                img = Image.open(path)
                img.thumbnail((80, 80))
                photo_img = ImageTk.PhotoImage(img)
                
                img_frame = ttk.Frame(preview_frame)
                img_frame.pack(side=tk.LEFT, padx=5, pady=5)
                
                img_label = ttk.Label(img_frame, image=photo_img)
                img_label.image = photo_img
                img_label.pack()
                
                delete_btn = ttk.Button(img_frame, text="x", bootstyle="danger-outline",
                                      command=lambda p=path, m=mode: self.delete_image(p, m))
                delete_btn.place(relx=1.0, rely=0.0, anchor=tk.NE)
                
                image_frames[path] = img_frame
                
            except Exception as e:
                print(f"Error loading image {path}: {str(e)}")

    def delete_image(self, path, mode):
        """Delete an image from the preview"""
        if mode == 'add':
            if path in self.add_image_paths:
                self.add_image_paths.remove(path)
            
            if path in self.add_image_frames and self.add_image_frames[path]:
                if self.add_image_frames[path].winfo_exists():
                    self.add_image_frames[path].destroy()
                del self.add_image_frames[path]
        else:
            if path in self.edit_image_paths:
                self.edit_image_paths.remove(path)
            
            if path in self.edit_image_frames and self.edit_image_frames[path]:
                if self.edit_image_frames[path].winfo_exists():
                    self.edit_image_frames[path].destroy()
                del self.edit_image_frames[path]

    def get_event_time(self):
        """Get the formatted time from the hour, minute, and AM/PM fields"""
        hour = int(self.hour_var.get())
        minute = int(self.minute_var.get())
        ampm = self.ampm_var.get()
        
        # Convert to 24-hour format
        if ampm == "PM" and hour < 12:
            hour += 12
        elif ampm == "AM" and hour == 12:
            hour = 0
            
        return f"{hour:02d}:{minute:02d}:00"

    def save_new_event(self):
        """Save a new event to the database"""
        # Validate required fields
        event_name = self.add_name_var.get().strip()
        event_description = self.add_desc_text.get("1.0", tk.END).strip()
        event_location = self.add_location_var.get().strip()
        event_date = self.add_date_picker.get_date()
        event_time = self.get_event_time()
        event_category = self.add_category_var.get()
        is_free = self.add_fee_type.get() == "free"  # Convert to boolean
        
        if not event_name or not event_description or not event_location or not event_date or not event_category:
            messagebox.showerror("Validation Error", "All fields except images are required!")
            return
        
        # Handle image upload
        image_path = None
        if self.add_image_paths:
            # Create events images directory if it doesn't exist
            upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads", "events")
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate a unique filename
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(self.add_image_paths[0])[1]}"
            destination = os.path.join(upload_dir, filename)
            
            try:
                # Copy the image
                shutil.copy2(self.add_image_paths[0], destination)
                image_path = os.path.join("uploads", "events", filename)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload image: {str(e)}")
                return
        
        # Insert into database
        db = connect_db()
        if db:
            cursor = db.cursor()
            try:
                # Modified to include status='approved' since this is an admin adding the event
                cursor.execute("""
                    INSERT INTO events (user_id, name, description, location, date, time, image, 
                                      category, is_free, date_created, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'approved')
                """, (
                    self.current_user_id,
                    event_name,
                    event_description,
                    event_location,
                    event_date,
                    event_time,
                    image_path,
                    event_category,
                    is_free,
                    datetime.now()
                ))
                
                db.commit()
                messagebox.showinfo("Success", "Event added successfully!")
                self.add_window.destroy()
                self.load_events()
                
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", f"Failed to save event: {str(e)}")
            finally:
                cursor.close()
                db.close()

    def open_edit_modal(self, event_id):
        """Open modal window for editing an event"""
        # Get event details
        db = connect_db()
        if not db:
            return
            
        cursor = db.cursor()
        try:
            cursor.execute("""
                SELECT name, description, location, date, time, image, category, is_free
                FROM events
                WHERE id = %s AND date_deleted IS NULL
            """, (event_id,))
            
            event = cursor.fetchone()
            if not event:
                messagebox.showerror("Error", "Event not found!")
                return
                
            # Create edit window
            self.edit_window = tk.Toplevel(self.root)
            self.edit_window.title("Edit Event")
            self.edit_window.geometry("600x700")
            self.edit_window.configure(bg="white")
            self.edit_window.resizable(False, False)
            self.edit_window.transient(self.root)
            self.edit_window.grab_set()
            
            title_label = ttk.Label(self.edit_window, text="Edit Event", font=("Arial", 16, "bold"))
            title_label.pack(pady=15)
            
            form_frame = ttk.Frame(self.edit_window)
            form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Event ID (hidden)
            self.edit_id = event_id
            
            # Event Name
            ttk.Label(form_frame, text="Event Name:", font=("Arial", 10, "bold")).grid(
                row=0, column=0, sticky=tk.W, pady=5)
            self.edit_name_var = tk.StringVar(value=event[0])
            ttk.Entry(form_frame, textvariable=self.edit_name_var, width=40).grid(
                row=0, column=1, sticky=tk.W, pady=5)
            
            # Description
            ttk.Label(form_frame, text="Description:", font=("Arial", 10, "bold")).grid(
                row=1, column=0, sticky=tk.W, pady=5)
            self.edit_desc_text = scrolledtext.ScrolledText(form_frame, width=40, height=5)
            self.edit_desc_text.grid(row=1, column=1, sticky=tk.W, pady=5)
            self.edit_desc_text.insert(tk.END, event[1])
            
            # Event Location
            ttk.Label(form_frame, text="Location:", font=("Arial", 10, "bold")).grid(
                row=2, column=0, sticky=tk.W, pady=5)
            self.edit_location_var = tk.StringVar(value=event[2])
            ttk.Entry(form_frame, textvariable=self.edit_location_var, width=40).grid(
                row=2, column=1, sticky=tk.W, pady=5)
            
            # Event Date
            ttk.Label(form_frame, text="Event Date:", font=("Arial", 10, "bold")).grid(
                row=3, column=0, sticky=tk.W, pady=5)
            self.edit_date_picker = CustomDatePicker(form_frame)
            self.edit_date_picker.frame.grid(row=3, column=1, sticky=tk.W, pady=5)
            self.edit_date_picker.set_date(str(event[3]))
            
            # Event Category
            ttk.Label(form_frame, text="Category:", font=("Arial", 10, "bold")).grid(
                row=4, column=0, sticky=tk.W, pady=5)
            self.edit_category_var = tk.StringVar(value=event[6])
            category_combo = ttk.Combobox(form_frame, textvariable=self.edit_category_var,
                                        values=["Festival", "Cultural", "Food"],
                                        state="readonly", width=38)
            category_combo.grid(row=4, column=1, sticky=tk.W, pady=5)
            
            # Event Time
            ttk.Label(form_frame, text="Event Time:", font=("Arial", 10, "bold")).grid(
                row=5, column=0, sticky=tk.W, pady=5)
            
            time_frame = ttk.Frame(form_frame)
            time_frame.grid(row=5, column=1, sticky=tk.W, pady=5)
            
            # Parse time
            event_time = datetime.strptime(str(event[4]), '%H:%M:%S')
            hour_24 = event_time.hour
            hour_12 = hour_24 % 12
            if hour_12 == 0:
                hour_12 = 12
            ampm = "AM" if hour_24 < 12 else "PM"
            
            self.edit_hour_var = tk.StringVar(value=f"{hour_12:02d}")
            hour_combo = ttk.Combobox(time_frame, textvariable=self.edit_hour_var, width=3)
            hour_combo['values'] = [f"{i:02d}" for i in range(1, 13)]
            hour_combo.grid(row=0, column=0)
            
            ttk.Label(time_frame, text=":").grid(row=0, column=1)
            
            self.edit_minute_var = tk.StringVar(value=f"{event_time.minute:02d}")
            minute_combo = ttk.Combobox(time_frame, textvariable=self.edit_minute_var, width=3)
            minute_combo['values'] = [f"{i:02d}" for i in range(0, 60, 5)]
            minute_combo.grid(row=0, column=2)
            
            self.edit_ampm_var = tk.StringVar(value=ampm)
            ampm_combo = ttk.Combobox(time_frame, textvariable=self.edit_ampm_var, width=3)
            ampm_combo['values'] = ["AM", "PM"]
            ampm_combo.grid(row=0, column=3, padx=(5, 0))
            
            # Entry Fee - Using radio buttons
            ttk.Label(form_frame, text="Entry Fee:", font=("Arial", 10, "bold")).grid(
                row=6, column=0, sticky=tk.W, pady=5)
            
            fee_frame = ttk.Frame(form_frame)
            fee_frame.grid(row=6, column=1, sticky=tk.W, pady=5)
            
            # Set the fee type based on the is_free value from the database
            self.edit_fee_type = tk.StringVar(value="free" if event[7] else "paid")
            
            # Free Event radio button
            free_rb = ttk.Radiobutton(
                fee_frame, 
                text="Free Event", 
                variable=self.edit_fee_type, 
                value="free"
            )
            free_rb.pack(side=tk.LEFT, padx=(0, 10))
            
            # Paid Event radio button
            paid_rb = ttk.Radiobutton(
                fee_frame, 
                text="Paid Event", 
                variable=self.edit_fee_type, 
                value="paid"
            )
            paid_rb.pack(side=tk.LEFT)
            
            # Images
            ttk.Label(form_frame, text="Images:", font=("Arial", 10, "bold")).grid(
                row=7, column=0, sticky=tk.W, pady=5)
            
            upload_frame = ttk.Frame(form_frame)
            upload_frame.grid(row=7, column=1, sticky=tk.W, pady=5)
            
            upload_btn = ttk.Button(upload_frame, text="Upload Images", bootstyle="info",
                                  command=lambda: self.upload_images('edit'))
            upload_btn.pack()
            
            self.edit_image_preview = ttk.Frame(form_frame)
            self.edit_image_preview.grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=10)
            
            self.edit_image_paths = []
            self.edit_image_frames = {}
            
            self.existing_images = []
            if event[5]:
                image_paths = event[5].split(';') if ';' in event[5] else [event[5]]
                self.existing_images = [path.strip() for path in image_paths if path.strip()]
                self.edit_image_paths = self.existing_images.copy()
                
                if self.existing_images:
                    self.display_images('edit', self.edit_image_preview, self.edit_image_paths, self.edit_image_frames)
            
            buttons_frame = ttk.Frame(self.edit_window)
            buttons_frame.pack(fill=tk.X, pady=15, padx=20)
            
            update_btn = ttk.Button(buttons_frame, text="Update", bootstyle="success",
                                  command=self.save_edited_event)
            update_btn.pack(side=tk.RIGHT, padx=5)
            
            cancel_btn = ttk.Button(buttons_frame, text="Cancel", bootstyle="secondary",
                                  command=self.edit_window.destroy)
            cancel_btn.pack(side=tk.RIGHT, padx=5)
                
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch event: {str(e)}")
        finally:
            cursor.close()
            db.close()

    def get_edit_event_time(self):
        """Get the formatted time from the edit hour, minute, and AM/PM fields"""
        hour = int(self.edit_hour_var.get())
        minute = int(self.edit_minute_var.get())
        ampm = self.edit_ampm_var.get()
        
        # Convert to 24-hour format
        if ampm == "PM" and hour < 12:
            hour += 12
        elif ampm == "AM" and hour == 12:
            hour = 0
            
        return f"{hour:02d}:{minute:02d}:00"

    def save_edited_event(self):
        """Save the edited event to the database"""
        # Validate required fields
        event_name = self.edit_name_var.get().strip()
        event_description = self.edit_desc_text.get("1.0", tk.END).strip()
        event_location = self.edit_location_var.get().strip()
        event_date = self.edit_date_picker.get_date()
        event_time = self.get_edit_event_time()
        event_category = self.edit_category_var.get()
        is_free = self.edit_fee_type.get() == "free"  # Convert to boolean
        
        if not event_name or not event_description or not event_location or not event_date or not event_category:
            messagebox.showerror("Validation Error", "All fields except images are required!")
            return
        
        # Handle image update
        image_path = self.existing_images[0] if self.existing_images else None
        if self.edit_image_paths and self.edit_image_paths[0] != image_path:
            # Create events images directory if it doesn't exist
            upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads", "events")
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate a unique filename
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(self.edit_image_paths[0])[1]}"
            destination = os.path.join(upload_dir, filename)
            
            try:
                # Copy the new image
                shutil.copy2(self.edit_image_paths[0], destination)
                image_path = os.path.join("uploads", "events", filename)
                
                # Delete the old image if it exists and is different
                if self.existing_images and os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), self.existing_images[0])):
                    os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)), self.existing_images[0]))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update image: {str(e)}")
                return
        
        # Update database
        db = connect_db()
        if db:
            cursor = db.cursor()
            try:
                cursor.execute("""
                    UPDATE events 
                    SET name = %s, 
                        description = %s, 
                        location = %s, 
                        date = %s, 
                        time = %s, 
                        image = %s,
                        category = %s,
                        is_free = %s,
                        date_modified = %s
                    WHERE id = %s
                """, (
                    event_name,
                    event_description,
                    event_location,
                    event_date,
                    event_time,
                    image_path,
                    event_category,
                    is_free,
                    datetime.now(),
                    self.edit_id
                ))
                
                db.commit()
                messagebox.showinfo("Success", "Event updated successfully!")
                self.edit_window.destroy()
                self.load_events()
                
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", f"Failed to update event: {str(e)}")
            finally:
                cursor.close()
                db.close()
                
    def delete_event(self, event_id):
        """Soft delete an event by setting date_deleted"""
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this event?")
        if not confirm:
            return
        
        db = connect_db() 
        if db:
            cursor = db.cursor()
            try:
                now = datetime.now()
                cursor.execute("""
                    UPDATE events 
                    SET status = 'rejected', date_deleted = %s
                    WHERE id = %s
                """, (now, event_id))
        
                db.commit()
                messagebox.showinfo("Success", "Event deleted successfully!")
                self.load_events()
        
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", f"Failed to delete event: {str(e)}")
            finally:
                cursor.close()
                db.close()

    def show_pending_modal(self):
        """Show modal with pending event submissions"""
        # Get pending events from the database
        db = connect_db()
        if not db:
            return
            
        cursor = db.cursor(dictionary=True)
        try:
            # Query to get pending events with user information
            cursor.execute("""
                SELECT e.*, u.username, u.email 
                FROM events e
                JOIN user_accounts u ON e.user_id = u.id
                WHERE e.status = 'pending' AND e.date_deleted IS NULL
            """)
            pending_events = cursor.fetchall()
            
            if not pending_events:
                messagebox.showinfo("No Pending Events", "There are no pending event submissions.")
                return
                
            # Create modal window
            self.pending_modal = tk.Toplevel(self.root)
            self.pending_modal.title("Pending Event Submissions")
            self.pending_modal.geometry("800x600")
            self.pending_modal.transient(self.root)
            self.pending_modal.grab_set()
            
            # Modal header
            header_frame = tk.Frame(self.pending_modal, bg="white", padx=20, pady=10)
            header_frame.pack(fill="x")
            
            header_label = tk.Label(header_frame, text="Pending Event Submissions", font=("Arial", 14, "bold"), bg="white")
            header_label.pack(side="left")

            
            # Create a canvas with a scrollbar
            canvas_frame = tk.Frame(self.pending_modal)
            canvas_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            canvas = tk.Canvas(canvas_frame)
            scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
            
            # Configure the canvas
            canvas.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            
            # Create a frame inside the canvas
            content_frame = tk.Frame(canvas)
            canvas.create_window((0, 0), window=content_frame, anchor="nw")
            
            # Display pending events
            for i, event in enumerate(pending_events):
                self.create_pending_event_card(content_frame, event, i)
            
            # Update the canvas scroll region
            content_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))
            
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch pending events: {str(e)}")
        finally:
            cursor.close()
            db.close()
    
    def create_pending_event_card(self, parent, event, index):
        """Create a card for a pending event submission"""
        # Event card frame
        card = tk.Frame(parent, bg="white", bd=1, relief=tk.SOLID, padx=15, pady=15)
        card.pack(fill="x", pady=10)
        
        # User info
        user_label = tk.Label(
            card,
            text=f"Submitted by: {event['username']} ({event['email']})",
            font=("Arial", 10, "bold"),
            fg="#555",
            bg="white"
        )
        user_label.pack(anchor="w", pady=(0, 10))
        
        # Event details
        details_frame = tk.Frame(card, bg="white")
        details_frame.pack(fill="x", pady=5)
        
        # Format date and time for display
        event_date = datetime.strptime(str(event['date']), '%Y-%m-%d').strftime('%Y-%m-%d') if event['date'] else "N/A"
        event_time = datetime.strptime(str(event['time']), '%H:%M:%S').strftime('%I:%M %p') if event['time'] else "N/A"
        
        # Property fields - excluding description which we'll handle separately
        properties = [
            ("Event Name:", event['name']),
            ("Category:", event['category']),
            ("Date:", event_date),
            ("Time:", event_time),
            ("Location:", event['location']),
        ]
        
        for prop_name, prop_value in properties:
            prop_frame = tk.Frame(details_frame, bg="white")
            prop_frame.pack(anchor="w", pady=2)
            
            label = tk.Label(
                prop_frame,
                text=prop_name,
                font=("Arial", 9, "bold"),
                width=12,
                anchor="w",
                bg="white"
            )
            label.pack(side="left")
            
            value = tk.Label(
                prop_frame,
                text=prop_value,
                font=("Arial", 9),
                anchor="w",
                bg="white"
            )
            value.pack(side="left", fill="x", expand=True)
        
        # Special handling for description with scrollable text widget
        desc_frame = tk.Frame(details_frame, bg="white")
        desc_frame.pack(anchor="w", pady=2, fill="x")
        
        desc_label = tk.Label(
            desc_frame,
            text="Description:",
            font=("Arial", 9, "bold"),
            width=12,
            anchor="w",
            bg="white"
        )
        desc_label.pack(side="left", anchor="n")
        
        # Create a frame for the description text widget and scrollbar
        desc_text_frame = tk.Frame(desc_frame, bg="white")
        desc_text_frame.pack(side="left", fill="both", expand=True)
        
        # Create scrollable text widget for description
        desc_text = tk.Text(
            desc_text_frame,
            wrap=tk.WORD,
            width=60,
            height=4,  # Fixed height of 4 lines
            font=("Arial", 9),
            bd=1,
            relief=tk.SOLID
        )
        desc_text.insert("1.0", event['description'])
        desc_text.config(state=tk.DISABLED)  # Make it read-only
        
        # Add scrollbar for the description
        desc_scroll = ttk.Scrollbar(desc_text_frame, command=desc_text.yview)
        desc_text.configure(yscrollcommand=desc_scroll.set)
        
        desc_text.pack(side="left", fill="both", expand=True)
        desc_scroll.pack(side="right", fill="y")
        
        # Approval buttons
        buttons_frame = tk.Frame(card, bg="white")
        buttons_frame.pack(fill="x", pady=(10, 0), anchor="e")
        
        approve_button = tk.Button(
            buttons_frame,
            text="✅ Approve",
            bg=self.approve_button_bg,
            fg="white",
            bd=0,
            padx=10,
            pady=3,
            cursor="hand2",
            command=lambda eid=event['id']: self.approve_event(eid)
        )
        approve_button.pack(side="right", padx=(0, 5))
        
        reject_button = tk.Button(
            buttons_frame,
            text="❌ Reject/Delete",
            bg=self.reject_button_bg,
            fg="white",
            bd=0,
            padx=10,
            pady=3,
            cursor="hand2",
            command=lambda eid=event['id']: self.reject_event(eid)
        )
        reject_button.pack(side="right", padx=5)
    
    def approve_event(self, event_id):
        """Approve a pending event"""
        db = connect_db()
        if not db:
            return
            
        cursor = db.cursor()
        try:
            # Update the event to mark it as approved
            cursor.execute("""
                UPDATE events 
                SET status = 'approved', 
                    date_modified = %s
                WHERE id = %s
            """, (datetime.now(), event_id))
            
            db.commit()
            messagebox.showinfo("Success", "Event approved successfully!")
            
            # Close the modal and refresh the events list
            if hasattr(self, 'pending_modal') and self.pending_modal.winfo_exists():
                self.pending_modal.destroy()
            self.load_events()
            
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to approve event: {str(e)}")
        finally:
            cursor.close()
            db.close()
    
    def reject_event(self, event_id):
        """Reject and soft delete a pending event"""
        confirm = messagebox.askyesno("Confirm Rejection", "Are you sure you want to reject and delete this event?")
        if not confirm:
            return
        
        db = connect_db()
        if not db:
            return
            
        cursor = db.cursor()
        try:
            # Update status to rejected (soft delete)
            cursor.execute("""
                UPDATE events 
                SET status = 'rejected',
                    date_deleted = %s
                WHERE id = %s
            """, (datetime.now(), event_id))
            
            db.commit()
            messagebox.showinfo("Success", "Event rejected and deleted successfully!")
            
            # Close the modal and refresh the events list
            if hasattr(self, 'pending_modal') and self.pending_modal.winfo_exists():
                self.pending_modal.destroy()
            self.load_events()
            
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to reject event: {str(e)}")
        finally:
            cursor.close()
            db.close()

    def user_management_page(self):
        """Create the user management page inside the content frame"""
        users_frame = ttk.Frame(self.content_frame)
        users_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Roles options
        self.roles = ["All", "Admin", "User"]
        
        button_frame = ttk.Frame(users_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.add_user_btn = ttk.Button(button_frame, text="Add New User", bootstyle="success",
                               command=self.open_add_user_modal)
        self.add_user_btn.pack(side=tk.RIGHT)
        
        search_frame = ttk.Frame(button_frame)
        search_frame.pack(side=tk.LEFT)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        
        # Search components - moved to the left
        self.user_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.user_search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        search_btn = ttk.Button(search_frame, text="Search", bootstyle="info",
                          command=self.search_users)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Role filter components - placed after search
        ttk.Label(search_frame, text="Role:").pack(side=tk.LEFT, padx=5)
        
        self.role_filter_var = tk.StringVar(value="All")
        role_combo = ttk.Combobox(search_frame, textvariable=self.role_filter_var, 
                          values=self.roles, width=15, state="readonly")
        role_combo.pack(side=tk.LEFT, padx=5)
        
        self.table_frame = ttk.Frame(users_frame)
        self.table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Vertical Scrollbar
        scroll_y = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL)
        
        # Horizontal Scrollbar
        scroll_x = ttk.Scrollbar(self.table_frame, orient=tk.HORIZONTAL)
        
        self.users_table = ttk.Treeview(self.table_frame, 
                                 columns=("id", "username", "address", "email", "phone", "role", "status", "last_login", "actions"),
                                 yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set, selectmode="browse")
        
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_y.config(command=self.users_table.yview)
        
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        scroll_x.config(command=self.users_table.xview)
        
        self.users_table.heading("id", text="ID", anchor="center")
        self.users_table.heading("username", text="Username", anchor="center")
        self.users_table.heading("address", text="Address", anchor="center")
        self.users_table.heading("email", text="Email", anchor="center")
        self.users_table.heading("phone", text="Phone", anchor="center")
        self.users_table.heading("role", text="Role", anchor="center")
        self.users_table.heading("status", text="Status", anchor="center")
        self.users_table.heading("last_login", text="Last Login", anchor="center")
        self.users_table.heading("actions", text="Actions", anchor="center")

        self.users_table.column("id", width=50, anchor="center")
        self.users_table.column("username", width=150, anchor="center")
        self.users_table.column("address", width=200, anchor="center")
        self.users_table.column("email", width=200, anchor="center")
        self.users_table.column("phone", width=100, anchor="center")
        self.users_table.column("role", width=100, anchor="center")
        self.users_table.column("status", width=100, anchor="center")
        self.users_table.column("last_login", width=150, anchor="center")
        self.users_table.column("actions", width=150, anchor="center")
        
        self.users_table["show"] = "headings"
        
        self.users_table.pack(fill=tk.BOTH, expand=True)
        
        self.load_users()
        
        search_entry.bind("<Return>", lambda event: self.search_users())
        role_combo.bind("<<ComboboxSelected>>", lambda event: self.search_users())
        self.users_table.bind("<ButtonRelease-1>", self.handle_user_table_click)

    def handle_user_table_click(self, event):
        """Handle click events on the user table"""
        region = self.users_table.identify_region(event.x, event.y)
        
        if region == "cell":
            column = self.users_table.identify_column(event.x)
            column_index = int(column[1:]) - 1
            
            selected_item = self.users_table.focus()
            if not selected_item:
                return
                
            item_values = self.users_table.item(selected_item, "values")
            user_id = int(item_values[0])
            
            if column_index == 8:  # Actions column
                popup = tk.Menu(self.root, tearoff=0)
                popup.add_command(label="Edit", command=lambda: self.open_edit_user_modal(user_id))
                popup.add_command(label="Delete", command=lambda: self.delete_user(user_id))
                
                try:
                    popup.tk_popup(event.x_root, event.y_root)
                finally:
                    popup.grab_release()

    def load_users(self):
        """Load users into the table"""
        for item in self.users_table.get_children():
            self.users_table.delete(item)
        
        db = connect_db()
        if db:
            cursor = db.cursor()
            try:
                cursor.execute("""
                    SELECT id, username, address, email, phone, role, status, last_activity 
                    FROM user_accounts 
                    WHERE date_deleted IS NULL
                    ORDER BY id ASC
                """)
                users = cursor.fetchall()
                
                for user in users:
                    # Format the last login date if it exists
                    last_login = user[7].strftime("%Y-%m-%d %H:%M:%S") if user[7] else "-"
                    
                    self.users_table.insert("", tk.END, values=(
                        user[0],             # ID
                        user[1],             # Username
                        user[2],             # Address
                        user[3],             # Email
                        user[4],             # Phone
                        user[5].title(),     # Role (capitalize for display)
                        user[6].title(),     # Status
                        last_login,          # Last Login
                        "Edit / Delete"      # Actions
                    ))
                    
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", f"Failed to fetch users: {str(e)}")
            finally:
                cursor.close()
                db.close()

    def search_users(self):
        """Search users by username or email and filter by role"""
        search_term = self.user_search_var.get().lower()
        role_filter = self.role_filter_var.get()
        
        # Clear the current table
        for item in self.users_table.get_children():
            self.users_table.delete(item)
        
        db = connect_db()
        if db:
            cursor = db.cursor()
            try:
                query = """
                    SELECT id, username, address, email, phone, role, status, last_activity 
                    FROM user_accounts 
                    WHERE date_deleted IS NULL 
                    AND (LOWER(username) LIKE %s OR LOWER(email) LIKE %s)
                """
                
                params = (f"%{search_term}%", f"%{search_term}%")
                
                # Add role filter if not "All"
                if role_filter != "All":
                    query += " AND LOWER(role) = %s"
                    params = (f"%{search_term}%", f"%{search_term}%", role_filter.lower())
                    
                query += " ORDER BY id ASC"
                
                cursor.execute(query, params)
                users = cursor.fetchall()
                
                for user in users:
                    # Format the last login date if it exists
                    last_login = user[7].strftime("%Y-%m-%d %H:%M:%S") if user[7] else "-"
                    
                    self.users_table.insert("", tk.END, values=(
                        user[0],             # ID
                        user[1],             # Username
                        user[2],             # Address
                        user[3],             # Email
                        user[4],             # Phone
                        user[5].title(),     # Role
                        user[6].title(),     # Status
                        last_login,          # Last Login
                        "Edit / Delete"      # Actions
                    ))
                    
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", f"Failed to search users: {str(e)}")
            finally:
                cursor.close()
                db.close()

    def open_add_user_modal(self):
        """Open modal window for adding a new user"""
        self.add_user_window = tk.Toplevel(self.root)
        self.add_user_window.title("Add New User")
        self.add_user_window.geometry("700x700")  # Increased height for better spacing
        self.add_user_window.configure(bg="white")
        self.add_user_window.resizable(False, False)
        self.add_user_window.transient(self.root)
        self.add_user_window.grab_set()

        # Add title
        title_label = ttk.Label(self.add_user_window, text="Add New User", font=("Arial", 18, "bold"))
        title_label.pack(pady=(30, 20))

        # Create main content frame with padding
        main_frame = ttk.Frame(self.add_user_window, padding=(40, 10, 40, 10))
        main_frame.pack(fill="both", expand=True)

        # Create two-column layout
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(20, 0))

        # Configure grid weights
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # Left Column Fields
        # Username
        ttk.Label(left_frame, text="Username:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.add_username_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.add_username_var, width=30).grid(row=1, column=0, sticky="ew", pady=(0, 20))

        # Address
        ttk.Label(left_frame, text="Address:", font=("Arial", 11)).grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.add_address_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.add_address_var, width=30).grid(row=3, column=0, sticky="ew", pady=(0, 20))

        # Email
        ttk.Label(left_frame, text="Email:", font=("Arial", 11)).grid(row=4, column=0, sticky="w", pady=(0, 5))
        self.add_email_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.add_email_var, width=30).grid(row=5, column=0, sticky="ew", pady=(0, 20))

        # Phone
        ttk.Label(left_frame, text="Phone:", font=("Arial", 11)).grid(row=6, column=0, sticky="w", pady=(0, 5))
        self.add_phone_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.add_phone_var, width=30).grid(row=7, column=0, sticky="ew", pady=(0, 20))

        # Password
        ttk.Label(left_frame, text="Password:", font=("Arial", 11)).grid(row=8, column=0, sticky="w", pady=(0, 5))
        self.add_password_var = tk.StringVar()
        
        # Password frame for entry and button
        password_frame = ttk.Frame(left_frame)
        password_frame.grid(row=9, column=0, sticky="ew", pady=(0, 5))
        password_frame.columnconfigure(0, weight=1)
        
        self.add_password_entry = ttk.Entry(password_frame, textvariable=self.add_password_var, width=30, show="*")
        self.add_password_entry.grid(row=0, column=0, sticky="ew")
        
        self.show_password_btn = ttk.Button(password_frame, text="Hide", width=10, 
                                          command=self.toggle_password_visibility)
        self.show_password_btn.grid(row=0, column=1, padx=(10, 0))

        # Password requirements
        ttk.Label(left_frame, text="* Password must be at least 6 characters with uppercase,\n  lowercase, and numbers", 
                 font=("Arial", 8), foreground="gray").grid(row=10, column=0, sticky="w", pady=(0, 20))

        # Right Column Fields
        # Role
        ttk.Label(right_frame, text="Role:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.add_role_var = tk.StringVar(value="User")
        ttk.Combobox(right_frame, textvariable=self.add_role_var, values=["Admin", "User"], 
                    state="readonly", width=30).grid(row=1, column=0, sticky="ew", pady=(0, 20))

        # Status
        ttk.Label(right_frame, text="Status:", font=("Arial", 11)).grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.add_status_var = tk.StringVar(value="Active")
        ttk.Combobox(right_frame, textvariable=self.add_status_var, values=["Active", "Inactive"], 
                    state="readonly", width=30).grid(row=3, column=0, sticky="ew", pady=(0, 20))

        # Profile Picture
        ttk.Label(right_frame, text="Profile Picture:", font=("Arial", 11)).grid(row=4, column=0, sticky="w", pady=(0, 5))
        
        # Profile picture frame
        image_frame = ttk.Frame(right_frame)
        image_frame.grid(row=5, column=0, sticky="w", pady=(0, 20))
        
        # Choose file button
        self.choose_image_btn = ttk.Button(image_frame, text="Choose File", 
                                         command=self.choose_profile_image,
                                         style="Accent.TButton")  # Custom style for blue button
        self.choose_image_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Image preview label
        self.image_label = ttk.Label(image_frame)
        self.image_label.grid(row=0, column=1, padx=(10, 10))
        
        # Remove image button
        self.remove_image_btn = ttk.Button(image_frame, text="X", 
                                         command=self.remove_profile_image,
                                         style="Danger.TButton")  # Custom style for X button
        self.remove_image_btn.grid(row=0, column=2, padx=(0, 10))
        self.remove_image_btn.grid_remove()  # Hide initially

        # Button frame at the bottom
        button_frame = ttk.Frame(self.add_user_window)
        button_frame.pack(fill="x", pady=(30, 40), padx=40)

        # Cancel button
        cancel_btn = ttk.Button(button_frame, text="Cancel", width=15, 
                               command=self.add_user_window.destroy,
                               style="Secondary.TButton")
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))

        # Save button
        save_btn = ttk.Button(button_frame, text="Save", width=15, 
                             command=self.save_new_user,
                             style="Success.TButton")
        save_btn.pack(side=tk.RIGHT, padx=(0, 0))

        # Define custom button styles
        self.define_custom_styles()

    def define_custom_styles(self):
        """Define custom ttk styles for buttons"""
        # Create style object
        s = ttk.Style()
        
        # Blue Button (Choose File)
        s.configure("Accent.TButton", background="#4a7dff", foreground="white")
        
        # Green Button (Save)
        s.configure("Success.TButton", background="#00c853", foreground="white")
        
        # Gray Button (Cancel)
        s.configure("Secondary.TButton", background="#9e9e9e", foreground="white")
        
        # Red Button (X)
        s.configure("Danger.TButton", background="#ff5252", foreground="white")

    def choose_profile_image(self):
        """Open file dialog to choose a profile image"""
        file_types = [("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        image_path = filedialog.askopenfilename(title="Select Profile Image", filetypes=file_types)
        
        if image_path:
            try:
                # Check file size
                file_size = os.path.getsize(image_path) / (1024 * 1024)  # Convert to MB
                if file_size > 2:
                    messagebox.showerror("Error", "Image size should be less than 2MB")
                    return
                
                # Open and resize image for preview
                img = Image.open(image_path)
                img.thumbnail((100, 100))
                photo_img = ImageTk.PhotoImage(img)
                
                # Update preview
                self.image_label.config(image=photo_img)
                self.image_label.image = photo_img  # Keep a reference
                
                # Store the path
                self.profile_picture_path = image_path
                
                # Show the remove button
                self.remove_image_btn.grid()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def remove_profile_image(self):
        """Remove the selected profile image"""
        self.image_label.config(image="")
        self.image_label.image = None
        self.profile_picture_path = None
        self.remove_image_btn.grid_remove()

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.add_password_entry.cget("show") == "*":
            self.add_password_entry.config(show="")
            self.show_password_btn.config(text="Hide")
        else:
            self.add_password_entry.config(show="*")
            self.show_password_btn.config(text="Show")

    def save_new_user(self):
        """Validate and save a new user"""
        # Get values from form
        username = self.add_username_var.get().strip()
        address = self.add_address_var.get().strip()
        email = self.add_email_var.get().strip()
        phone = self.add_phone_var.get().strip()
        password = self.add_password_var.get()
        role = self.add_role_var.get()
        status = self.add_status_var.get()

        # Validate input
        if not username or not email or not password or not address or not phone:
            messagebox.showerror("Error", "All fields are required")
            return

        # Email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            messagebox.showerror("Error", "Invalid email format")
            return

        # Username validation
        if len(username) < 3:
            messagebox.showerror("Error", "Username must be at least 3 characters")
            return

        # Password strength validation
        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters")
            return
        if not re.search(r"[A-Z]", password):
            messagebox.showerror("Error", "Password must contain at least one uppercase letter")
            return
        if not re.search(r"[a-z]", password):
            messagebox.showerror("Error", "Password must contain at least one lowercase letter")
            return
        if not re.search(r"[0-9]", password):
            messagebox.showerror("Error", "Password must contain at least one number")
            return

        # Connect to database
        db = connect_db()
        if not db:
            return

        cursor = db.cursor()
        try:
            # Check if username or email already exists
            cursor.execute("SELECT id FROM user_accounts WHERE username = %s OR email = %s", 
                          (username, email))
            if cursor.fetchone():
                messagebox.showerror("Error", "Username or email already exists")
                return

            # Hash the password using bcrypt
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

            # Prepare the profile image
            profile_picture_filename = None
            if hasattr(self, 'profile_picture_path') and self.profile_picture_path:
                # Create a unique filename
                _, ext = os.path.splitext(self.profile_picture_path)
                profile_picture_filename = f"profile_{username.lower()}_{int(datetime.now().timestamp())}{ext}"

                # Create directory if it doesn't exist
                profile_images_dir = os.path.join(os.getcwd(), "profile_images")
                if not os.path.exists(profile_images_dir):
                    os.makedirs(profile_images_dir)

                # Save the image
                destination = os.path.join(profile_images_dir, profile_picture_filename)
                shutil.copy2(self.profile_picture_path, destination)

            # Insert the new user
            cursor.execute("""
                INSERT INTO user_accounts (username, address, email, phone, password_hash, role, status, profile_picture_path, date_created, last_activity) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                username, address, email, phone, hashed_password, role.lower(), status.lower(), 
                profile_picture_filename, datetime.now(), datetime.now()
            ))

            db.commit()
            messagebox.showinfo("Success", "User added successfully")

            # Close the window and refresh the user list
            self.add_user_window.destroy()
            self.load_users()

        except mysql.connector.Error as e:
            db.rollback()
            messagebox.showerror("Database Error", f"Failed to add user: {str(e)}")
        finally:
            cursor.close()
            db.close()
            
    def open_edit_user_modal(self, user_id):
        """Open modal window for editing a user"""
        db = connect_db()
        if not db:
            return
            
        cursor = db.cursor()
        try:
            cursor.execute("""
                SELECT id, username, address, email, phone, role, status, profile_picture_path 
                FROM user_accounts 
                WHERE id = %s AND date_deleted IS NULL
            """, (user_id,))
            
            user = cursor.fetchone()
            if not user:
                messagebox.showerror("Error", "User not found")
                return
                
            # Create the edit window
            self.edit_user_window = tk.Toplevel(self.root)
            self.edit_user_window.title("Edit User")
            self.edit_user_window.geometry("800x600")
            self.edit_user_window.configure(bg="white")
            self.edit_user_window.resizable(False, False)
            self.edit_user_window.transient(self.root)
            self.edit_user_window.grab_set()
            
            # Store the user ID
            self.edit_user_id = user_id
            
            # Add title
            title_frame = ttk.Frame(self.edit_user_window)
            title_frame.pack(fill=tk.X, pady=15)
            title_label = ttk.Label(title_frame, text="Edit User", font=("Arial", 18, "bold"), anchor="center")
            title_label.pack(expand=True)
            
            # Create a canvas with scrollbar for the form
            canvas = tk.Canvas(self.edit_user_window, bg="white")
            scrollbar = ttk.Scrollbar(self.edit_user_window, orient="vertical", command=canvas.yview)
            form_frame = ttk.Frame(canvas)
            
            # Configure scrolling
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True, padx=20)
            scrollbar.pack(side="right", fill="y")
            
            # Create a window inside the canvas to hold the form frame
            canvas_frame = canvas.create_window((0, 0), window=form_frame, anchor="nw")
            
            # Configure canvas scrolling region when frame size changes
            def configure_scroll_region(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
            
            form_frame.bind("<Configure>", configure_scroll_region)
            
            # Make sure the canvas window uses the full width
            def configure_canvas_window(event):
                canvas.itemconfig(canvas_frame, width=event.width)
            
            canvas.bind("<Configure>", configure_canvas_window)
            
            # Create two-column layout for the form
            left_frame = ttk.Frame(form_frame)
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            right_frame = ttk.Frame(form_frame)
            right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Left Column Fields
            # Username
            ttk.Label(left_frame, text="Username:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 5))
            self.edit_username_var = tk.StringVar(value=user[1])
            username_entry = ttk.Entry(left_frame, textvariable=self.edit_username_var, width=40)
            username_entry.pack(fill=tk.X, pady=(0, 15))
            
            # Address
            ttk.Label(left_frame, text="Address:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 5))
            self.edit_address_var = tk.StringVar(value=user[2])
            address_entry = ttk.Entry(left_frame, textvariable=self.edit_address_var, width=40)
            address_entry.pack(fill=tk.X, pady=(0, 15))
            
            # Phone
            ttk.Label(left_frame, text="Phone:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 5))
            self.edit_phone_var = tk.StringVar(value=user[4])
            phone_entry = ttk.Entry(left_frame, textvariable=self.edit_phone_var, width=40)
            phone_entry.pack(fill=tk.X, pady=(0, 15))
            
            # Email
            ttk.Label(left_frame, text="Email:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 5))
            self.edit_email_var = tk.StringVar(value=user[3])
            email_entry = ttk.Entry(left_frame, textvariable=self.edit_email_var, width=40)
            email_entry.pack(fill=tk.X, pady=(0, 5))
            
            # Send code button
            send_code_button = ttk.Button(
                left_frame, 
                text="Send code", 
                bootstyle="primary",
                command=lambda: self.send_verification_code(self.edit_email_var.get())
            )
            send_code_button.pack(anchor=tk.E, pady=(5, 15))
            
            # Match Code on Email
            ttk.Label(left_frame, text="Match Code on Email:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 5))
            self.edit_match_code_var = tk.StringVar()
            match_code_entry = ttk.Entry(left_frame, textvariable=self.edit_match_code_var, width=40)
            match_code_entry.pack(fill=tk.X, pady=(0, 15))
            
            # Password
            ttk.Label(left_frame, text="Password:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 5))
            self.edit_password_var = tk.StringVar()
            password_frame = ttk.Frame(left_frame)
            password_frame.pack(fill=tk.X, pady=(0, 5))
            
            password_entry = ttk.Entry(password_frame, textvariable=self.edit_password_var, width=40, show="*")
            password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Toggle password visibility
            self.password_visible = False
            def toggle_password_visibility():
                if self.password_visible:
                    password_entry.config(show="*")
                    hide_button.config(text="Show")
                else:
                    password_entry.config(show="")
                    hide_button.config(text="Hide")
                self.password_visible = not self.password_visible
            
            hide_button = ttk.Button(password_frame, text="Show", bootstyle="primary", command=toggle_password_visibility)
            hide_button.pack(side=tk.RIGHT, padx=(5, 0))
            
            # Password requirements
            password_req_label = ttk.Label(
                left_frame, 
                text="* Password must be at least 6 characters with uppercase,\n  lowercase, and numbers",
                font=("Arial", 8), 
                foreground="gray"
            )
            password_req_label.pack(anchor=tk.W, pady=(0, 15))
            
            # Right Column Fields
            # Role
            ttk.Label(right_frame, text="Role:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 5))
            self.edit_role_var = tk.StringVar(value=user[5].title())
            role_combo = ttk.Combobox(right_frame, textvariable=self.edit_role_var, values=["Admin", "User"], 
                       state="readonly", width=40)
            role_combo.pack(fill=tk.X, pady=(0, 15))
            
            # Status
            ttk.Label(right_frame, text="Status:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 5))
            self.edit_status_var = tk.StringVar(value=user[6].title())
            status_combo = ttk.Combobox(right_frame, textvariable=self.edit_status_var, values=["Active", "Inactive"], 
                       state="readonly", width=40)
            status_combo.pack(fill=tk.X, pady=(0, 15))
            
            # Profile Picture
            ttk.Label(right_frame, text="Profile Picture:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 5))
            
            profile_pic_frame = ttk.Frame(right_frame)
            profile_pic_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Choose file button
            self.edit_choose_image_btn = ttk.Button(profile_pic_frame, text="Choose File", 
                                             bootstyle="primary", command=self.choose_edit_profile_image)
            self.edit_choose_image_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            # Store current image path
            self.current_profile_picture = user[7]
            self.edit_profile_picture_path = None
            
            # Image preview frame
            self.edit_image_preview_frame = ttk.Frame(right_frame)
            self.edit_image_preview_frame.pack(fill=tk.X, pady=(10, 10))
            
            self.edit_profile_image_label = ttk.Label(self.edit_image_preview_frame)
            self.edit_profile_image_label.pack(side=tk.LEFT)
            
            # Load current image if exists
            if self.current_profile_picture:
                profile_images_dir = os.path.join(os.getcwd(), "profile_images")
                img_path = os.path.join(profile_images_dir, self.current_profile_picture)
                if os.path.exists(img_path):
                    try:
                        img = Image.open(img_path)
                        img.thumbnail((100, 100))
                        photo_img = ImageTk.PhotoImage(img)
                        self.edit_profile_image_label.config(image=photo_img)
                        self.edit_profile_image_label.image = photo_img  # Keep a reference
                        
                        # Show remove button
                        self.edit_remove_image_btn = ttk.Button(
                            self.edit_image_preview_frame, 
                            text="X", 
                            bootstyle="danger-outline", 
                            width=2,
                            command=self.remove_edit_profile_image
                        )
                        self.edit_remove_image_btn.pack(side=tk.LEFT, padx=(5, 0))
                    except Exception:
                        pass
            
            # Add buttons at the bottom
            button_frame = ttk.Frame(self.edit_user_window)
            button_frame.pack(fill=tk.X, pady=20, padx=20, side=tk.BOTTOM)
            
            cancel_btn = ttk.Button(
                button_frame, 
                text="Cancel", 
                bootstyle="secondary", 
                width=10,
                command=self.edit_user_window.destroy
            )
            cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
            
            save_btn = ttk.Button(
                button_frame, 
                text="Save", 
                bootstyle="success", 
                width=10,
                command=self.update_user
            )
            save_btn.pack(side=tk.RIGHT)
            
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch user: {str(e)}")
        finally:
            cursor.close()
            db.close()

    def choose_edit_profile_image(self):
        """Open file dialog to choose a profile image for editing"""
        file_types = [("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        image_path = filedialog.askopenfilename(title="Select Profile Image", filetypes=file_types)
        
        if image_path:
            try:
                # Check file size
                file_size = os.path.getsize(image_path) / (1024 * 1024)  # Convert to MB
                if file_size > 2:
                    messagebox.showerror("Error", "Image size should be less than 2MB")
                    return
                
                # Open and resize image for preview
                img = Image.open(image_path)
                img.thumbnail((100, 100))
                photo_img = ImageTk.PhotoImage(img)
                
                # Update preview
                self.edit_profile_image_label.config(image=photo_img)
                self.edit_profile_image_label.image = photo_img  # Keep a reference
                
                # Store the path
                self.edit_profile_picture_path = image_path
                
                # Show the remove button
                if not hasattr(self, 'edit_remove_image_btn') or not self.edit_remove_image_btn:
                    self.edit_remove_image_btn = ttk.Button(
                        self.edit_image_preview_frame, 
                        text="X", 
                        bootstyle="danger-outline", 
                        width=2,
                        command=self.remove_edit_profile_image
                    )
                    self.edit_remove_image_btn.pack(side=tk.LEFT, padx=(5, 0))
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def send_verification_code(self, email):
        """Send verification code to the user's email"""
        if not email:
            messagebox.showerror("Error", "Please enter an email address")
            return
            
        # Email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            messagebox.showerror("Error", "Invalid email format")
            return
        
        # Generate a random 6-digit code
        verification_code = str(random.randint(100000, 999999))
        verification_codes[email] = verification_code
        
        # Send the code via email
        subject = "Your Verification Code"
        message = f"Your verification code is: <b>{verification_code}</b>"
        
        response = send_email(email, subject, message)
        
        if "messageId" in response:
            messagebox.showinfo("Success", "Verification code sent to your email")
        else:
            error_msg = response.get("error", "Unknown error")
            messagebox.showerror("Error", f"Failed to send email: {error_msg}")

    def remove_edit_profile_image(self):
        """Remove the selected profile image"""
        self.edit_profile_image_label.config(image="")
        self.edit_profile_image_label.image = None
        self.edit_profile_picture_path = None
        if hasattr(self, 'edit_remove_image_btn') and self.edit_remove_image_btn:
            self.edit_remove_image_btn.pack_forget()

    def update_user(self):
        """Validate and update user information"""
        # Get values from form
        username = self.edit_username_var.get().strip()
        address = self.edit_address_var.get().strip()
        phone = self.edit_phone_var.get().strip()
        email = self.edit_email_var.get().strip()
        match_code = self.edit_match_code_var.get().strip()
        password = self.edit_password_var.get()
        role = self.edit_role_var.get()
        status = self.edit_status_var.get()
        
        # Validate input
        if not username or not email:
            messagebox.showerror("Error", "Username and email are required")
            return
            
        # Email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            messagebox.showerror("Error", "Invalid email format")
            return
            
        # Username validation
        if len(username) < 3:
            messagebox.showerror("Error", "Username must be at least 3 characters")
            return
            
        # Password strength validation if provided
        if password and len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return
        if password and not re.search(r"[A-Z]", password):
            messagebox.showerror("Error", "Password must contain at least one uppercase letter")
            return
        if password and not re.search(r"[a-z]", password):
            messagebox.showerror("Error", "Password must contain at least one lowercase letter")
            return
        if password and not re.search(r"[0-9]", password):
            messagebox.showerror("Error", "Password must contain at least one number")
            return
    
        # Verify the match code if a new password is provided
        if password:
            email = self.edit_email_var.get().strip()
            entered_code = match_code
            
            if not entered_code:
                messagebox.showerror("Error", "Please enter the verification code sent to your email")
                return
                
            if email not in verification_codes or verification_codes[email] != entered_code:
                messagebox.showerror("Error", "Invalid verification code")
                return
                
            # Clear the verification code after successful use
            if email in verification_codes:
                del verification_codes[email]
        
        # Connect to database
        db = connect_db()
        if not db:
            return
            
        cursor = db.cursor()
        try:
            # Check if username or email already exists for other users
            cursor.execute("""
                SELECT id FROM user_accounts 
                WHERE (username = %s OR email = %s) AND id != %s AND date_deleted IS NULL
            """, (username, email, self.edit_user_id))
            
            if cursor.fetchone():
                messagebox.showerror("Error", "Username or email already exists")
                return
                
            # Prepare the SQL query and parameters
            update_query = """
                UPDATE user_accounts SET 
                username = %s, 
                address = %s,
                phone = %s,
                email = %s, 
                role = %s, 
                status = %s
            """
            update_params = [username, address, phone, email, role.lower(), status.lower()]
            
            # Add password to update if provided
            if password:
                hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                update_query += ", password_hash = %s"
                update_params.append(hashed_password)
                
            # Process profile image if a new one is selected
            profile_picture_filename = self.current_profile_picture
            if self.edit_profile_picture_path:
                # Create a unique filename
                _, ext = os.path.splitext(self.edit_profile_picture_path)
                profile_picture_filename = f"profile_{username.lower()}_{int(datetime.now().timestamp())}{ext}"
                
                # Create directory if it doesn't exist
                profile_images_dir = os.path.join(os.getcwd(), "profile_images")
                if not os.path.exists(profile_images_dir):
                    os.makedirs(profile_images_dir)
                    
                # Save the image
                destination = os.path.join(profile_images_dir, profile_picture_filename)
                shutil.copy2(self.edit_profile_picture_path, destination)
                
                # Delete the old image if it exists
                if self.current_profile_picture:
                    old_image_path = os.path.join(profile_images_dir, self.current_profile_picture)
                    if os.path.exists(old_image_path):
                        try:
                            os.remove(old_image_path)
                        except:
                            pass  # Ignore errors if file cannot be deleted
                
                update_query += ", profile_picture_path = %s"
                update_params.append(profile_picture_filename)
                
            # Add WHERE clause and execute
            update_query += " WHERE id = %s"
            update_params.append(self.edit_user_id)
            
            cursor.execute(update_query, update_params)
            db.commit()
            
            messagebox.showinfo("Success", "User updated successfully")
            
            # Close the window and refresh the user list
            self.edit_user_window.destroy()
            self.load_users()
            
        except mysql.connector.Error as e:
            db.rollback()
            messagebox.showerror("Database Error", f"Failed to update user: {str(e)}")
        finally:
            cursor.close()
            db.close()

    def delete_user(self, user_id):
        """Soft delete a user by setting date_deleted"""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this user?"):
            db = connect_db()
            if not db:
                return
                
            cursor = db.cursor()
            try:
                # Soft delete by setting date_deleted
                cursor.execute("""
                    UPDATE user_accounts 
                    SET date_deleted = %s, status = 'inactive' 
                    WHERE id = %s
                """, (datetime.now(), user_id))
                
                db.commit()
                messagebox.showinfo("Success", "User deleted successfully")
                
                # Refresh the user list
                self.load_users()
                
            except mysql.connector.Error as e:
                db.rollback()
                messagebox.showerror("Database Error", f"Failed to delete user: {str(e)}")
            finally:
                cursor.close()
                db.close()
                           
    def feedback_page(self):
        """Create the feedback/reviews management page."""
        # Main frame
        main_frame = ttk.Frame(self.content_frame, bootstyle="light")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="User Reviews", font=("Arial", 14, "bold"))
        title_label.pack(fill=tk.X, pady=(0, 10))
        
        # Filter frame
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Filter by label
        filter_label = ttk.Label(filter_frame, text="Filter by:")
        filter_label.grid(row=0, column=0, padx=(0, 5), pady=5)
        
        # Date filter
        date_label = ttk.Label(filter_frame, text="Date:")
        date_label.grid(row=0, column=1, padx=(10, 5), pady=5)
        
        # Use CustomDatePicker for date input
        self.date_picker = CustomDatePicker(filter_frame)
        self.date_picker.frame.grid(row=0, column=2, padx=5, pady=5)
        
        # Clear date button
        clear_date_btn = ttk.Button(filter_frame, text="Clear Date", command=self.clear_date_filter, bootstyle="secondary", width=10)
        clear_date_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Rating filter
        rating_label = ttk.Label(filter_frame, text="Rating:")
        rating_label.grid(row=0, column=5, padx=(10, 5), pady=5)
        
        # Rating dropdown
        self.rating_var = tk.StringVar(value="All")
        rating_dropdown = ttk.Combobox(filter_frame, textvariable=self.rating_var, values=["All", "5", "4", "3", "2", "1"], width=5, state="readonly")
        rating_dropdown.grid(row=0, column=6, padx=5, pady=5)
        
        # Apply filters button
        apply_button = ttk.Button(filter_frame, text="Apply Filters", command=self.apply_filters, bootstyle="success")
        apply_button.grid(row=0, column=7, padx=(10, 0), pady=5)
        
        # Feedback container with scrollbar
        feedback_container_frame = ttk.Frame(main_frame)
        feedback_container_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(feedback_container_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas for scrolling
        self.canvas = tk.Canvas(feedback_container_frame, yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbar
        scrollbar.config(command=self.canvas.yview)
        
        # Frame inside canvas for feedback items
        self.feedback_container = ttk.Frame(self.canvas)
        self.feedback_container_window = self.canvas.create_window((0, 0), window=self.feedback_container, anchor="nw", width=self.canvas.winfo_width())
        
        # Configure canvas scrolling
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.feedback_container.bind("<Configure>", self.on_frame_configure)
        
        # Bind mouse wheel to scroll
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
        # Load initial feedback
        self.load_feedback()

    def on_canvas_configure(self, event):
        """Update the width of the frame to fit the canvas."""
        self.canvas.itemconfig(self.feedback_container_window, width=event.width)

    def on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mousewheel(self, event):
        """Scroll the canvas with the mousewheel."""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def clear_date_filter(self):
        """Clear the date picker selections."""
        self.date_picker.clear()

    def load_feedback(self, date_filter=None, rating_filter="All"):
        """Load feedback from the database with optional filters."""
        # Clear existing feedback
        for widget in self.feedback_container.winfo_children():
            widget.destroy()
            
        # Build query based on filters
        query = """
        SELECT r.id, ua.username, p.name as place_name, r.rating, r.comment, r.date_created,
               (SELECT COUNT(*) FROM review_replies WHERE review_id = r.id) as reply_count
        FROM reviews r
        JOIN user_accounts ua ON r.user_id = ua.id
        JOIN places p ON r.place_id = p.id
        WHERE r.date_deleted IS NULL
        """
        
        params = []
        
        # Date filter
        if date_filter and date_filter.strip():
            try:
                # Parse date
                date_obj = datetime.strptime(date_filter, "%Y-%m-%d")
                query += " AND DATE(r.date_created) = %s"
                params.append(date_obj.strftime("%Y-%m-%d"))
            except ValueError:
                messagebox.showwarning("Invalid Date", "Please enter a valid date in YYYY-MM-DD format.")
                return
        
        # Rating filter
        if rating_filter and rating_filter != "All":
            query += " AND r.rating = %s"
            params.append(int(rating_filter))
        
        # Order by date
        query += " ORDER BY r.date_created DESC"
        
        # Execute query
        result = DatabaseManager.execute_query(query, params if params else None)
        
        if result:
            # Display feedback from database
            for feedback in result:
                self.create_feedback_card(
                    feedback['id'], 
                    feedback['username'], 
                    feedback['place_name'], 
                    feedback['rating'], 
                    feedback['comment'], 
                    feedback['date_created'],
                    feedback['reply_count']
                )
        else:
            # Show a message if no reviews match the filters
            no_data_label = ttk.Label(self.feedback_container, text="No reviews match the selected filters", font=("Arial", 12))
            no_data_label.pack(pady=20)
        
    def create_feedback_card(self, id, username, place_name, rating, comment, date, reply_count):
        """Create a card for a single feedback/review item."""
        # Create the main card frame with a thin border
        card_frame = ttk.Frame(self.feedback_container, style="TFrame")
        card_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create a frame with border for the card content
        content_frame = ttk.Frame(card_frame, style="TFrame")
        content_frame.pack(fill=tk.X)
        content_frame.configure(relief="solid", borderwidth=1)
        
        # Username header - bold font
        username_label = ttk.Label(content_frame, text=username, font=("Arial", 11, "bold"))
        username_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))
        
        # Create place and rating line
        place_frame = ttk.Frame(content_frame)
        place_frame.grid(row=1, column=0, sticky="w", padx=10, pady=(5, 0))
        
        # Place label
        place_label = ttk.Label(place_frame, text=f"Place: {place_name}", font=("Arial", 10))
        place_label.pack(side=tk.LEFT)
        
        # Star rating - using colored stars
        rating_frame = ttk.Frame(content_frame)
        rating_frame.grid(row=2, column=0, sticky="w", padx=10, pady=(2, 0))
        
        # Display gold stars based on rating
        for i in range(5):
            star_color = "#FFD700" if i < rating else "#D3D3D3"  # Gold or Light Gray
            star_label = ttk.Label(rating_frame, text="★", font=("Arial", 12), foreground=star_color)
            star_label.pack(side=tk.LEFT, padx=0)
        
        # Date info
        date_str = date.strftime("%Y-%m-%d %H:%M") if isinstance(date, datetime) else str(date)
        date_label = ttk.Label(content_frame, text=f"Reviewed on: {date_str}", font=("Arial", 9))
        date_label.grid(row=3, column=0, sticky="w", padx=10, pady=(5, 0))
        
        # Separator between header and comment
        separator = ttk.Separator(content_frame, orient="horizontal")
        separator.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        
        # Comment text
        comment_label = ttk.Label(content_frame, text=comment, wraplength=700, justify=tk.LEFT)
        comment_label.grid(row=5, column=0, sticky="w", padx=10, pady=(0, 10))
        
        # "See Replies" button with blue underline styling
        see_replies_frame = ttk.Frame(content_frame)
        see_replies_frame.grid(row=6, column=0, sticky="w", padx=10, pady=(0, 5))
        
        # Create a label that looks like a hyperlink
        self.see_replies_label = ttk.Label(
            see_replies_frame, 
            text=f"See Replies ({reply_count})", 
            font=("Arial", 9, "underline"), 
            foreground="blue",
            cursor="hand2"
        )
        self.see_replies_label.pack(side=tk.LEFT)
        self.see_replies_label.bind("<Button-1>", lambda e, review_id=id: self.show_replies(review_id))
        
        # Button frame at the bottom
        button_frame = ttk.Frame(content_frame)
        button_frame.grid(row=7, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        # Reply button - purple like in the image
        reply_btn = ttk.Button(
            button_frame, 
            text="Reply", 
            command=lambda id=id: self.reply_to_feedback(id),
            style="purple.TButton",
            width=8
        )
        reply_btn.pack(side=tk.LEFT)
        
        # Delete button - red, aligned to the right
        delete_btn = ttk.Button(
            button_frame, 
            text="Delete", 
            command=lambda id=id: self.delete_feedback(id), 
            style="danger.TButton",
            width=8
        )
        delete_btn.pack(side=tk.RIGHT)

    def show_replies(self, review_id):
        """Show all replies for a specific review."""
        # Fetch replies from the database
        query = """
        SELECT rr.id, rr.review_id, ua.username, rr.reply_text, rr.date_created, rr.date_modified
        FROM review_replies rr
        JOIN user_accounts ua ON rr.admin_id = ua.id
        WHERE rr.review_id = %s AND rr.date_deleted IS NULL
        ORDER BY rr.date_created DESC
        """
        
        replies = DatabaseManager.execute_query(query, (review_id,))
        
        # Create a popup window to display replies
        popup = tk.Toplevel(self.root)
        popup.title(f"Replies for Review #{review_id}")
        popup.geometry("600x400")
        
        # Title
        title_frame = ttk.Frame(popup)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(title_frame, text=f"Replies for Review #{review_id}", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        # Container for replies
        container = ttk.Frame(popup)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas for scrolling
        canvas = tk.Canvas(container, yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbar
        scrollbar.config(command=canvas.yview)
        
        # Frame inside canvas for replies
        replies_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=replies_frame, anchor="nw", width=580)
        
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        replies_frame.bind("<Configure>", on_frame_configure)
        
        # Display each reply
        if replies:
            for reply in replies:
                self.create_reply_card(replies_frame, reply)
        else:
            ttk.Label(replies_frame, text="No replies yet", font=("Arial", 10)).pack(pady=20)
        
        # Add a button to add a new reply
        add_reply_btn = ttk.Button(
            popup, 
            text="Add Reply", 
            command=lambda: self.reply_to_feedback(review_id, popup),
            style="success.TButton"
        )
        add_reply_btn.pack(pady=10)

    def create_reply_card(self, parent, reply):
        """Create a card for a single reply with edit/delete options."""
        # Main frame for the reply
        reply_frame = ttk.Frame(parent, style="TFrame")
        reply_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Content frame with border
        content_frame = ttk.Frame(reply_frame, style="TFrame")
        content_frame.pack(fill=tk.X)
        content_frame.configure(relief="solid", borderwidth=1)
        
        # Admin username and date
        header_frame = ttk.Frame(content_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        ttk.Label(header_frame, text=f"Admin: {reply['username']}", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        # Date information
        date_str = reply['date_created'].strftime("%Y-%m-%d %H:%M") if isinstance(reply['date_created'], datetime) else str(reply['date_created'])
        if reply['date_modified']:
            modified_str = reply['date_modified'].strftime("%Y-%m-%d %H:%M") if isinstance(reply['date_modified'], datetime) else str(reply['date_modified'])
            date_label = ttk.Label(header_frame, text=f"Posted: {date_str} (Edited: {modified_str})", font=("Arial", 8))
        else:
            date_label = ttk.Label(header_frame, text=f"Posted: {date_str}", font=("Arial", 8))
        date_label.pack(side=tk.RIGHT)
        
        # Reply text
        reply_text = ttk.Label(content_frame, text=reply['reply_text'], wraplength=550, justify=tk.LEFT)
        reply_text.pack(fill=tk.X, padx=10, pady=5)
        
        # Edit/Delete buttons (only shown for current admin)
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        edit_btn = ttk.Button(
            button_frame,
            text="Edit",
            command=lambda: self.edit_reply(reply['id'], reply['reply_text']),
            style="info.TButton",
            width=8
        )
        edit_btn.pack(side=tk.LEFT)
        
        delete_btn = ttk.Button(
            button_frame,
            text="Delete",
            command=lambda: self.delete_reply(reply['id']),
            style="danger.TButton",
            width=8
        )
        delete_btn.pack(side=tk.RIGHT)

    def reply_to_feedback(self, review_id, parent_window=None):
        """Open a dialog to reply to feedback."""
        dialog = tk.Toplevel(self.root if parent_window is None else parent_window)
        dialog.title(f"Reply to Review #{review_id}")
        dialog.geometry("500x300")
        
        # Text box for reply
        ttk.Label(dialog, text="Your Reply:", font=("Arial", 10)).pack(pady=(10, 5))
        reply_text = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, width=60, height=10)
        reply_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Button frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        # Submit button
        submit_btn = ttk.Button(
            button_frame,
            text="Submit",
            command=lambda: self.submit_reply(review_id, reply_text.get("1.0", tk.END).strip(), dialog),
            style="success.TButton"
        )
        submit_btn.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            style="secondary.TButton"
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)

    def submit_reply(self, review_id, reply_text, dialog):
        """Submit a reply to the database."""
        if not reply_text:
            messagebox.showwarning("Input Error", "Please enter a reply.")
            return
            
        try:
            db = connect_db()
            cursor = db.cursor()
            
            # Insert the reply
            cursor.execute(
                "INSERT INTO review_replies (review_id, admin_id, reply_text) VALUES (%s, %s, %s)",
                (review_id, self.current_user_id, reply_text)
            )
            
            db.commit()
            messagebox.showinfo("Success", "Reply submitted successfully!")
            dialog.destroy()
            
            # Refresh the replies view if it's open
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Toplevel) and "Replies for Review" in widget.title():
                    widget.destroy()
                    self.show_replies(review_id)
                    break
                    
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error submitting reply: {err}")
        finally:
            cursor.close()
            db.close()

    def edit_reply(self, reply_id, current_text):
        """Edit an existing reply."""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Reply #{reply_id}")
        dialog.geometry("500x300")
        
        # Text box with current reply
        ttk.Label(dialog, text="Edit Reply:", font=("Arial", 10)).pack(pady=(10, 5))
        reply_text = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, width=60, height=10)
        reply_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        reply_text.insert("1.0", current_text)
        
        # Button frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        # Update button
        update_btn = ttk.Button(
            button_frame,
            text="Update",
            command=lambda: self.update_reply(reply_id, reply_text.get("1.0", tk.END).strip(), dialog),
            style="success.TButton"
        )
        update_btn.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            style="secondary.TButton"
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)

    def update_reply(self, reply_id, reply_text, dialog):
        """Update an existing reply in the database."""
        if not reply_text:
            messagebox.showwarning("Input Error", "Please enter a reply.")
            return
            
        try:
            db = connect_db()
            cursor = db.cursor()
            
            # Update the reply
            cursor.execute(
                "UPDATE review_replies SET reply_text = %s, date_modified = NOW() WHERE id = %s",
                (reply_text, reply_id)
            )
            
            db.commit()
            messagebox.showinfo("Success", "Reply updated successfully!")
            dialog.destroy()
            
            # Refresh the replies view if it's open
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Toplevel) and "Replies for Review" in widget.title():
                    # Get the review_id from the window title
                    title = widget.title()
                    review_id = int(title.split("#")[-1])
                    widget.destroy()
                    self.show_replies(review_id)
                    break
                    
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error updating reply: {err}")
        finally:
            cursor.close()
            db.close()

    def delete_reply(self, reply_id):
        """Delete a reply (soft delete)."""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this reply?"):
            try:
                db = connect_db()
                cursor = db.cursor()
                
                # Soft delete the reply
                cursor.execute(
                    "UPDATE review_replies SET date_deleted = NOW() WHERE id = %s",
                    (reply_id,)
                )
                
                db.commit()
                messagebox.showinfo("Success", "Reply deleted successfully!")
                
                # Refresh the replies view if it's open
                for widget in self.root.winfo_children():
                    if isinstance(widget, tk.Toplevel) and "Replies for Review" in widget.title():
                        # Get the review_id from the window title
                        title = widget.title()
                        review_id = int(title.split("#")[-1])
                        widget.destroy()
                        self.show_replies(review_id)
                        break
                        
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error deleting reply: {err}")
            finally:
                cursor.close()
                db.close()

    def delete_feedback(self, review_id):
        """Delete a review (soft delete)."""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this review?"):
            try:
                db = connect_db()
                cursor = db.cursor()
                
                # Soft delete the review
                cursor.execute(
                    "UPDATE reviews SET date_deleted = NOW() WHERE id = %s",
                    (review_id,)
                )
                
                db.commit()
                messagebox.showinfo("Success", "Review deleted successfully!")
                self.load_feedback()
                
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error deleting review: {err}")
            finally:
                cursor.close()
                db.close()

    def apply_filters(self):
        """Apply the selected filters to the feedback list."""
        date = self.date_picker.get_date()
        rating = self.rating_var.get()
        self.load_feedback(date, rating)

    def settings_page(self):
        """Displays the user account settings page."""
        # Create scrollable container
        container = ttk.Frame(self.content_frame)
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # Configure mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Bind the scrollable_frame size to canvas
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        # Create a window in the canvas for the scrollable frame
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack the elements
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Get user data for the currently logged-in user
        db = connect_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT username, email, phone, profile_picture_path, address, status FROM user_accounts WHERE id = %s",
                (self.current_user_id,)
            )
            user_data = cursor.fetchone()
            if not user_data:
                ttk.Label(scrollable_frame, text="User data not found!", font=("Arial", 12)).pack(pady=10)
                return
            
            username, email, phone, profile_pic, address, status = user_data
        except mysql.connector.Error as err:
            ttk.Label(scrollable_frame, text=f"Error fetching user data: {err}", font=("Arial", 12)).pack(pady=10)
            return
        finally:
            cursor.close()
            db.close()

        # Profile Section with Preview
        profile_section = ttk.Frame(scrollable_frame)
        profile_section.pack(pady=10, fill="x", padx=20)

        # User info with mini preview
        profile_header = ttk.Frame(profile_section)
        profile_header.pack(fill="x")

        # Mini profile preview with border
        preview_frame = ttk.Frame(profile_header, style="primary.TFrame", padding=3)
        preview_frame.pack(side=tk.LEFT, padx=10)

        # Profile preview
        self.profile_preview = ttk.Label(preview_frame, text="No Image", style="light.TLabel", width=5)
        self.profile_preview.pack()

        # Welcome text next to preview
        welcome_frame = ttk.Frame(profile_header)
        welcome_frame.pack(side=tk.LEFT, fill="x", expand=True)

        ttk.Label(welcome_frame, text="Welcome to your account", font=("Arial", 12, "bold")).pack(anchor="w")
        ttk.Label(welcome_frame, text="Manage your profile and account settings").pack(anchor="w")

        # Main profile picture with border
        profile_frame = ttk.Frame(profile_section, style="primary.TFrame", padding=5)
        profile_frame.pack(pady=15)

        # Profile picture
        self.profile_picture = ttk.Label(profile_frame, text="No Image", style="light.TLabel", width=20)
        self.profile_picture.pack()

        # Load profile picture if available
        if profile_pic and os.path.exists(profile_pic):
            try:
                # Load main profile image
                image = Image.open(profile_pic)
                image.thumbnail((150, 150), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.profile_picture.config(image=photo)
                self.profile_picture.image = photo  # Keep a reference to prevent garbage collection
                
                # Load preview image
                preview_image = Image.open(profile_pic)
                preview_image.thumbnail((50, 50), Image.Resampling.LANCZOS)
                preview_photo = ImageTk.PhotoImage(preview_image)
                self.profile_preview.config(image=preview_photo)
                self.profile_preview.image = preview_photo
            except Exception as e:
                logging.error(f"Error loading profile image: {e}")

        # Upload button for profile picture
        upload_btn = ttk.Button(
            profile_section, 
            text="Upload New Picture", 
            style="success.TButton",
            command=lambda: self.upload_profile_picture()
        )
        upload_btn.pack(pady=5)

        # User Details Frame
        details_frame = ttk.Frame(scrollable_frame, style="light.TFrame", padding=15)
        details_frame.pack(pady=10, fill="x", padx=20)

        self.name_label = ttk.Label(details_frame, text=f"Username: {username or 'Not set'}", anchor="w", font=("Arial", 10))
        self.name_label.pack(anchor="w", pady=2)

        self.email_label = ttk.Label(details_frame, text=f"Email: {email or 'Not set'}", anchor="w", font=("Arial", 10))
        self.email_label.pack(anchor="w", pady=2)

        self.phone_label = ttk.Label(details_frame, text=f"Phone: {phone or 'Not set'}", anchor="w", font=("Arial", 10))
        self.phone_label.pack(anchor="w", pady=2)

        self.address_label = ttk.Label(details_frame, text=f"Address: {address or 'Not set'}", anchor="w", font=("Arial", 10))
        self.address_label.pack(anchor="w", pady=2)

        self.status_label = ttk.Label(details_frame, text=f"Account Status: {status.capitalize()}", anchor="w", font=("Arial", 10))
        self.status_label.pack(anchor="w", pady=2)

        # Edit Links Frame
        edit_links_frame = ttk.Frame(scrollable_frame)
        edit_links_frame.pack(pady=10, padx=20, fill="x")

        # Title for edit section
        ttk.Label(edit_links_frame, text="Edit Your Profile", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)

        # Create edit buttons
        edit_buttons = [
            ("Change Username", "username", "👤"),
            ("Change Email", "email", "📧"),
            ("Change Phone", "phone", "📱"),
            ("Change Address", "address", "🏠"),
            ("Change Password", "password", "🔒"),
            ("Toggle Account Status", "status", "🔄")
        ]

        for idx, (text, field, icon) in enumerate(edit_buttons):
            btn_frame = ttk.Frame(edit_links_frame)
            btn_frame.pack(fill="x", pady=3)
            
            # Button with icon
            btn = ttk.Button(
                btn_frame, 
                text=f"{icon} {text}", 
                style="info.Link.TButton",
                command=lambda f=field: self.handle_edit_action(f)
            )
            btn.pack(side=tk.LEFT, anchor="w")
            
            # Add separator except for the last item
            if idx < len(edit_buttons) - 1:
                ttk.Separator(edit_links_frame, orient="horizontal").pack(fill="x", pady=3)

        # Add a separator after the last edit button
        ttk.Separator(edit_links_frame, orient="horizontal").pack(fill="x", pady=3)

        # Logout button
        logout_btn = ttk.Button(
            edit_links_frame,
            text="🚪 Logout",
            style="info.Link.TButton",
            command=self.logout
        )
        logout_btn.pack(anchor="w", pady=5)

        # Add a separator after the logout button
        ttk.Separator(edit_links_frame, orient="horizontal").pack(fill="x", pady=3)

        # Password Change Frame (initially hidden)
        self.password_change_frame = ttk.Frame(scrollable_frame, style="light.TFrame", padding=15)

        # Password Change Title
        ttk.Label(self.password_change_frame, text="Change Password", font=("Arial", 12, "bold")).pack(pady=5)

        # Current Password
        ttk.Label(self.password_change_frame, text="Current Password:", anchor="w").pack(fill=tk.X)
        current_password_frame = ttk.Frame(self.password_change_frame)
        current_password_frame.pack(pady=5, fill=tk.X)
        self.current_password = ttk.Entry(current_password_frame, show="*", width=25)
        self.current_password.pack(side=tk.LEFT)
        self.current_show_btn = ttk.Button(
            current_password_frame, 
            text="Show", 
            command=lambda: self.toggle_password(self.current_password, self.current_show_btn)
        )
        self.current_show_btn.pack(side=tk.LEFT, padx=5)

        # New Password
        ttk.Label(self.password_change_frame, text="New Password:", anchor="w").pack(fill=tk.X)
        new_password_frame = ttk.Frame(self.password_change_frame)
        new_password_frame.pack(pady=5, fill=tk.X)
        self.new_password = ttk.Entry(new_password_frame, show="*", width=25)
        self.new_password.pack(side=tk.LEFT)
        self.new_show_btn = ttk.Button(
            new_password_frame, 
            text="Show", 
            command=lambda: self.toggle_password(self.new_password, self.new_show_btn)
        )
        self.new_show_btn.pack(side=tk.LEFT, padx=5)

        # Password requirements label
        ttk.Label(
            self.password_change_frame, 
            text="Password must be at least 8 characters with uppercase, lowercase, and numbers",
            font=("Arial", 8),
            wraplength=300
        ).pack(pady=2)

        # Confirm Password
        ttk.Label(self.password_change_frame, text="Confirm Password:", anchor="w").pack(fill=tk.X)
        confirm_password_frame = ttk.Frame(self.password_change_frame)
        confirm_password_frame.pack(pady=5, fill=tk.X)
        self.confirm_password = ttk.Entry(confirm_password_frame, show="*", width=25)
        self.confirm_password.pack(side=tk.LEFT)
        self.confirm_show_btn = ttk.Button(
            confirm_password_frame,
            text="Show",
            command=lambda: self.toggle_password(self.confirm_password, self.confirm_show_btn)
        )
        self.confirm_show_btn.pack(side=tk.LEFT, padx=5)

        # Button frame
        password_buttons_frame = ttk.Frame(self.password_change_frame)
        password_buttons_frame.pack(pady=10)

        # Update and Cancel buttons
        ttk.Button(
            password_buttons_frame,
            text="Update Password",
            style="success.TButton",
            command=self.change_password
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            password_buttons_frame, 
            text="Cancel", 
            style="danger.TButton",
            command=lambda: self.password_change_frame.pack_forget()
        ).pack(side=tk.LEFT, padx=5)

    def toggle_password(self, entry_widget, button):
        """Toggle password visibility in entry widgets."""
        if entry_widget['show'] == '*':
            entry_widget.config(show='')
            button.config(text='Hide')
        else:
            entry_widget.config(show='*')
            button.config(text='Show')

    def upload_profile_picture(self):
        """Handle profile picture upload."""
        file_types = [("Image files", "*.jpg *.jpeg *.png *.gif")]
        file_path = filedialog.askopenfilename(title="Select Profile Picture", filetypes=file_types)
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Create directory if it doesn't exist
            save_dir = "profile_pictures"
            os.makedirs(save_dir, exist_ok=True)
            
            # Generate a unique filename
            filename = f"user_{self.current_user_id}_{int(time.time())}{os.path.splitext(file_path)[1]}"
            save_path = os.path.join(save_dir, filename)
            
            # Process and save the image
            image = Image.open(file_path)
            image.thumbnail((300, 300), Image.Resampling.LANCZOS)
            image.save(save_path)
            
            # Update database
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("UPDATE user_accounts SET profile_picture_path = %s WHERE id = %s", (save_path, self.current_user_id))
            db.commit()
            logging.info(f"✅ Profile picture updated: {save_path}")
                
            # Update UI
            self.refresh_profile_picture(save_path)
            messagebox.showinfo("Success", "Profile picture updated successfully!")
        except Exception as e:
            logging.error(f"Error uploading profile picture: {e}")
            messagebox.showerror("Error", f"Failed to upload profile picture: {e}")
        finally:
            if db:
                cursor.close()
                db.close()

    def refresh_profile_picture(self, image_path):
        """Refresh profile picture in UI."""
        try:
            # Update main profile image
            image = Image.open(image_path)
            image.thumbnail((150, 150), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.profile_picture.config(image=photo)
            self.profile_picture.image = photo  # Keep a reference
            
            # Update preview image
            preview_image = Image.open(image_path)
            preview_image.thumbnail((50, 50), Image.Resampling.LANCZOS)
            preview_photo = ImageTk.PhotoImage(preview_image)
            self.profile_preview.config(image=preview_photo)
            self.profile_preview.image = preview_photo
        except Exception as e:
            logging.error(f"Error refreshing profile image: {e}")

    def handle_edit_action(self, field):
        """Handle different edit actions based on the field."""
        if field == "password":
            # Show password change frame
            self.password_change_frame.pack(pady=10, fill="x", padx=20)
        elif field == "status":
            self.toggle_account_status()
        else:
            # For other fields, show a dialog
            db = connect_db()
            cursor = db.cursor()
            try:
                cursor.execute(f"SELECT {field} FROM user_accounts WHERE id = %s", (self.current_user_id,))
                result = cursor.fetchone()
                current_value = result[0] if result else None
                
                # Show dialog with current value
                prompt_text = f"Enter new {field.capitalize()}:"
                new_value = simpledialog.askstring(f"Change {field.capitalize()}", prompt_text, initialvalue=current_value or "")
                
                if new_value is not None:  # User didn't cancel
                    self.update_user_field(field, new_value)
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Failed to fetch current {field}: {err}")
            finally:
                cursor.close()
                db.close()

    def update_user_field(self, field, value):
        """Update user field in database."""
        db = connect_db()
        cursor = db.cursor()
        try:
            # Validation for specific fields
            if field == "email" and not self.validate_email(value):
                messagebox.showerror("Invalid Input", "Please enter a valid email address.")
                return False
            elif field == "phone" and not self.validate_phone(value):
                messagebox.showerror("Invalid Input", "Please enter a valid phone number.")
                return False
            
            cursor.execute(f"UPDATE user_accounts SET {field} = %s WHERE id = %s", (value, self.current_user_id))
            db.commit()
            logging.info(f"✅ User {field} updated for user ID {self.current_user_id}")
            
            # Update UI
            if field == "username":
                self.name_label.config(text=f"Username: {value}")
            elif field == "email":
                self.email_label.config(text=f"Email: {value}")
            elif field == "phone":
                self.phone_label.config(text=f"Phone: {value}")
            elif field == "address":
                self.address_label.config(text=f"Address: {value}")
            
            messagebox.showinfo("Success", f"{field.capitalize()} updated successfully!")
            return True
        except mysql.connector.Error as err:
            logging.error(f"❌ Database Error: {err}")
            messagebox.showerror("Database Error", f"Failed to update {field}: {err}")
            return False
        finally:
            cursor.close()
            db.close()

    def toggle_account_status(self):
        """Toggle user account status between active and inactive."""
        db = connect_db()
        cursor = db.cursor()
        try:
            # Get current status
            cursor.execute("SELECT status FROM user_accounts WHERE id = %s", (self.current_user_id,))
            current_status = cursor.fetchone()[0]
            
            # Toggle status
            new_status = "inactive" if current_status.lower() == "active" else "active"
            
            # Update database
            cursor.execute("UPDATE user_accounts SET status = %s WHERE id = %s", (new_status, self.current_user_id))
            db.commit()
            
            # Update UI
            self.status_label.config(text=f"Account Status: {new_status.capitalize()}")
            
            messagebox.showinfo("Status Changed", f"Your account is now {new_status}.")
            logging.info(f"✅ User status changed to {new_status} for user ID {self.current_user_id}")
        except Exception as e:
            logging.error(f"Error toggling account status: {e}")
            messagebox.showerror("Error", f"Failed to update account status: {e}")
        finally:
            cursor.close()
            db.close()

    def change_password(self):
        """Handle password change."""
        current_pwd = self.current_password.get()
        new_pwd = self.new_password.get()
        confirm_pwd = self.confirm_password.get()
        
        # Validation
        if not current_pwd or not new_pwd or not confirm_pwd:
            messagebox.showerror("Error", "All password fields are required!")
            return
        
        if new_pwd != confirm_pwd:
            messagebox.showerror("Error", "New password and confirmation do not match!")
            return
        
        if not self.validate_password(new_pwd):
            messagebox.showerror("Error", "Password must be at least 8 characters with uppercase, lowercase, and numbers!")
            return
        
        db = connect_db()
        cursor = db.cursor()
        try:
            # Get current password hash from DB
            cursor.execute("SELECT password_hash FROM user_accounts WHERE id = %s", (self.current_user_id,))
            result = cursor.fetchone()
            
            if not result:
                messagebox.showerror("Error", "User not found!")
                return
            
            stored_hash = result[0]
            
            # Check if current password is correct
            if not bcrypt.checkpw(current_pwd.encode('utf-8'), stored_hash.encode('utf-8')):
                messagebox.showerror("Error", "Current password is incorrect!")
                return
            
            # Hash new password
            hashed_pwd = bcrypt.hashpw(new_pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Update database
            cursor.execute("UPDATE user_accounts SET password_hash = %s WHERE id = %s", (hashed_pwd, self.current_user_id))
            db.commit()
            
            logging.info(f"✅ Password updated for user ID {self.current_user_id}")
            messagebox.showinfo("Success", "Password changed successfully!")
            
            # Clear password fields and hide frame
            self.current_password.delete(0, tk.END)
            self.new_password.delete(0, tk.END)
            self.confirm_password.delete(0, tk.END)
            self.password_change_frame.pack_forget()
            
        except Exception as e:
            logging.error(f"Error changing password: {e}")
            messagebox.showerror("Error", f"Failed to change password: {e}")
        finally:
            cursor.close()
            db.close()

    def validate_email(self, email):
        """Validate email format."""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

    def validate_phone(self, phone):
        """Validate phone number format."""
        # Allow different formats but ensure it contains enough digits
        digits = re.sub(r'\D', '', phone)  # Remove non-digits
        return len(digits) >= 10

    def validate_password(self, password):
        """Validate password strength."""
        # At least 8 chars, 1 uppercase, 1 lowercase, 1 number
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        return True

    def logout(self):
        """Handle user logout."""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            logging.info(f"User ID {self.current_user_id} logged out")
            self.root.destroy()
            # Here you would typically redirect to login screen
            # For demonstration, just show a message
            messagebox.showinfo("Logged Out", "You have been logged out successfully.")
            # In a real app, you would launch the login window here

# Run Admin Dashboard
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python admindashboard.py <user_id>")
        sys.exit(1)
    user_id = int(sys.argv[1])
    root = tk.Tk()
    app = AdminDashboard(root, user_id)
    root.mainloop()
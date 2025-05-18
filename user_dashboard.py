import tkinter as tk
from tkinter import Toplevel, messagebox, ttk, Text, filedialog, scrolledtext, simpledialog
from tkinter import font
from ttkbootstrap import Style
from ttkbootstrap.constants import *
import mysql.connector
from mysql.connector import Error
from PIL import Image, ImageTk
import os
import cv2
from ffpyplayer.player import MediaPlayer
import logging
import webbrowser
import re
import bcrypt
import time
import sys
from datetime import datetime, date

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection (XAMPP MySQL)
def connect_to_database():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="tourism_db"
        )
        cursor = db.cursor()
        logging.info("✅ Connected to MySQL successfully.")
        return db, cursor
    except mysql.connector.Error as err:
        logging.error(f"❌ Database Error: {err}")
        return None, None

db, cursor = connect_to_database()

# Session timeout in seconds (5 minutes)
SESSION_TIMEOUT = 300

class UserDashboard:
    def __init__(self, root, user_id):
        self.root = root
        self.current_user_id = user_id
        self.root.title("Tourism Information System - User Dashboard")
        self.root.geometry("900x500")
        self.root.resizable(True, True)

        # Apply Modern Theme
        self.style = Style()
        
        # Define custom colors
        self.custom_blue = "#0a2351"  # Your requested blue color
        self.dark_blue = "#1a3361"    # The color that wasn't displaying properly
        self.medium_blue = "#2a4371"  # Slightly lighter blue for cards

        # Define custom colors
        self.custom_blue = "#0a2351"  # Dark blue color for sidebar
        self.dark_blue = "#1a3361"    # Darker blue for right sidebar
        self.medium_blue = "#2a4371"  # Medium blue for cards
        self.light_blue = "#64b5f6"   # Light blue for links

        # Create custom styles for all widgets
        self.style.configure("DarkBlue.TFrame", background=self.custom_blue)
        self.style.configure("DarkBlue.TLabel", background=self.dark_blue, foreground="white")
        
        # Style for sidebar buttons - blue background with white text
        self.style.configure("CustomBlue.TButton", background=self.custom_blue, foreground="white")
        self.style.map("CustomBlue.TButton",
                   background=[("active", self.custom_blue), ("disabled", "gray")],
                   foreground=[("active", "white"), ("disabled", "gray")])
                   
        # Style for active button - white background with blue text
        self.style.configure("Active.TButton", background="white", foreground=self.custom_blue)
        self.style.map("Active.TButton",
                   background=[("active", "white"), ("disabled", "gray")],
                   foreground=[("active", self.custom_blue), ("disabled", "gray")])
        
        # Create custom styles for all widgets
        self.style.configure("CustomBlue.TButton", background=self.custom_blue, foreground="white")
        self.style.map("CustomBlue.TButton",
                   background=[("active", self.custom_blue), ("disabled", "gray")],
                   foreground=[("active", "white"), ("disabled", "gray")])
                   
        self.style.configure("Active.TButton", background="white", foreground=self.custom_blue)
        self.style.map("Active.TButton",
                   background=[("active", "white"), ("disabled", "gray")],
                   foreground=[("active", self.custom_blue), ("disabled", "gray")])

        # Configure styles for dark blue elements
        self.style.configure("DarkBlue.TFrame", background=self.dark_blue)
        self.style.configure("DarkBlue.TLabel", background=self.dark_blue, foreground="white")
        self.style.configure("MediumBlue.TFrame", background=self.medium_blue)
        self.style.configure("MediumBlue.TLabel", background=self.medium_blue, foreground="white")
        self.style.configure("LightBlue.TLabel", background=self.dark_blue, foreground="#64b5f6")
        self.style.configure("ReadMore.TButton", background="#1e88e5", foreground="white")

        # Configure styles for right sidebar elements
        self.style.configure("RightSidebar.TFrame", background=self.dark_blue)
        self.style.configure("RightSidebar.TLabel", background=self.dark_blue, foreground="white")
        self.style.configure("MediumBlue.TFrame", background=self.medium_blue)
        self.style.configure("MediumBlue.TLabel", background=self.medium_blue, foreground="white")
        self.style.configure("LightBlue.TLabel", background=self.dark_blue, foreground=self.light_blue)
        self.style.configure("ReadMore.TButton", background="#1e88e5", foreground="white")

        # Configure dark theme styles
        self.style.configure("dark.TFrame", background="#2c2c2c")
        self.style.configure("dark.TLabel", background="#2c2c2c", foreground="white")
        self.style.configure("dark.TRadiobutton", background="#2c2c2c", foreground="white")
        
        # Configure entry styles
        self.style.configure("dark.TEntry", 
                            fieldbackground="#333333", 
                            foreground="white",
                            bordercolor="#555555",
                            darkcolor="#555555",
                            lightcolor="#555555")
        
        # Configure combobox styles
        self.style.map('TCombobox', 
                      fieldbackground=[('readonly', '#333333')],
                      background=[('readonly', '#333333')],
                      foreground=[('readonly', 'white')])
        
        # Initialize session
        self.create_session()
        self.update_last_activity()

        # Fetch user-specific data
        self.user_data = self.fetch_user_data()
        if not self.user_data:
            messagebox.showerror("Error", "Failed to fetch user data. Please try again.")
            self.root.destroy()
            return

        # Navigation Menu
        self.menu_frame = ttk.Frame(self.root, bootstyle="secondary")
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Menu Items
        self.menu_items = [
            "Home",
            "Explore Places",
            "Saved Places",
            "Reviews",
            "Events",
            "Propose Event & Place",
            "Account"
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
        self.show_page("Home")
        
        # Cleanup on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Check session timeout periodically
        self.check_session_timeout()

    def fetch_user_data(self):
        """Fetch user-specific data from the database."""
        if db and cursor:
            try:
                cursor.execute(
                    "SELECT username, email, phone, profile_picture_path, address, status, role FROM user_accounts WHERE id = %s",
                    (self.current_user_id,)
                )
                user_data = cursor.fetchone()
                if user_data:
                    return {
                        "username": user_data[0],
                        "email": user_data[1],
                        "phone": user_data[2],
                        "profile_picture_path": user_data[3],
                        "address": user_data[4],
                        "status": user_data[5],
                        "role": user_data[6]
                    }
                else:
                    return None
            except Error as e:
                logging.error(f"Error fetching user data: {e}")
                return None
        else:
            return None

    def create_session(self):
        """Create a session file with user ID and timestamp."""
        with open("session.txt", "w") as f:
            f.write(str(self.current_user_id) + "\n")
            f.write(str(time.time()))

    def update_last_activity(self):
        """Update the last_activity timestamp in the database."""
        if db and cursor:
            try:
                cursor.execute("UPDATE user_accounts SET last_activity = NOW() WHERE id = %s", (self.current_user_id,))
                db.commit()
            except Error as e:
                logging.error(f"Error updating last activity: {e}")

    def check_session_timeout(self):
        """Check if the session has expired and log out the user if it has."""
        if os.path.exists("session.txt"):
            with open("session.txt", "r") as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    session_time = float(lines[1].strip())
                    if time.time() - session_time > SESSION_TIMEOUT:
                        self.logout()
                        return

        # Check again after 1 minute
        self.root.after(60000, self.check_session_timeout)
    
    def logout(self):
        """Log out the user and return to login screen."""
        # Update database status
        if db and cursor:
            try:
                cursor.execute("UPDATE user_accounts SET is_online = 0, last_activity = NULL WHERE id = %s", 
                              (self.current_user_id,))
                db.commit()
            except Error as e:
                logging.error(f"Error updating logout status: {e}")
        
        # Remove session file
        if os.path.exists("session.txt"):
            try:
                os.remove("session.txt")
            except Exception as e:
                logging.error(f"Error removing session file: {e}")
        
        # Close the current window
        self.root.destroy()
        
        # Restart login window
        try:
            # Get the path to the current Python executable
            python_executable = sys.executable
            
            # Get the path to the login script (assuming it's in the same directory)
            login_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "login.py")
            
            # Check if the login script exists
            if os.path.exists(login_script):
                # Start a new process for the login window
                os.system(f'"{python_executable}" "{login_script}"')
            else:
                messagebox.showerror("Error", "Login script not found. Please contact support.")
        except Exception as e:
            logging.error(f"Error restarting login window: {e}")
            messagebox.showerror("Error", f"Could not restart login window: {str(e)}")

    def on_close(self):
        """Clean up resources when the window is closed."""
        if db:
            db.close()
            logging.info("✅ Database connection closed.")
        self.root.destroy()
        
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
        if page == "Home":
            self.home_page()
        elif page == "Explore Places":
            self.explore_places_page()
        elif page == "Saved Places":
            self.saved_places_page()
        elif page == "Reviews":
            self.reviews_page()
        elif page == "Events":
            self.events_page()
        elif page == "Propose Event & Place":
            self.propose_event_page()
        elif page == "Account":
            self.account_page()

    def home_page(self):
        # Create custom fonts
        self.title_font = font.Font(family="Segoe UI", size=24, weight="bold")
        self.subtitle_font = font.Font(family="Segoe UI", size=12)
        self.section_title_font = font.Font(family="Segoe UI", size=16, weight="bold")
        self.regular_font = font.Font(family="Segoe UI", size=10)
        self.feature_title_font = font.Font(family="Segoe UI", size=12, weight="bold")

        # Main container - using ttk.Frame with proper styling
        self.main_frame = ttk.Frame(self.content_frame, padding=(30, 30, 30, 30))
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create container frame with dark blue background
        self.container = ttk.Frame(self.main_frame, style="DarkBlue.TFrame", padding=(30, 30, 30, 30))
        self.container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        self.header_frame = ttk.Frame(self.container, style="DarkBlue.TFrame")
        self.header_frame.pack(fill=tk.X, pady=(0, 20))

        # Title with dark blue background
        self.title_label = ttk.Label(
            self.header_frame, 
            text="Tourism Information System", 
            style="DarkBlue.TLabel",
            font=self.title_font
        )
        self.title_label.pack()

        # Subtitle with dark blue background
        self.subtitle_label = ttk.Label(
            self.header_frame, 
            text="Discover the Wonders of SOCCSKSARGEN", 
            style="DarkBlue.TLabel",
            font=self.subtitle_font
        )
        self.subtitle_label.pack(pady=(5, 15))

        # Short description with dark blue background
        self.desc_label = ttk.Label(
            self.container, 
            text="A comprehensive system to explore and manage tourism details in the SOCCSKSARGEN region.\nDiscover breathtaking destinations and plan your perfect adventure.", 
            style="DarkBlue.TLabel",
            font=self.regular_font,
            justify=tk.CENTER
        )
        self.desc_label.pack(fill=tk.X, pady=10)

        # Read More button
        self.button_frame = ttk.Frame(self.container, style="DarkBlue.TFrame")
        self.button_frame.pack(pady=15)
        
        self.read_more_btn = ttk.Button(
            self.button_frame, 
            text="Read More", 
            style="ReadMore.TButton",
            padding=(20, 8),
            command=self.toggle_description
        )
        self.read_more_btn.pack()

        # Create canvas with dark blue background
        self.canvas = tk.Canvas(self.container, bg=self.dark_blue, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        self.scrollbar = ttk.Scrollbar(self.container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Extended description frame (initially hidden) with dark blue background
        self.extended_frame = ttk.Frame(self.canvas, style="DarkBlue.TFrame")
        self.canvas.create_window((0, 0), window=self.extended_frame, anchor='nw', width=700)
        
        # Description content (initially hidden)
        self.extended_frame.visible = False
        
        # Bind mouse wheel to scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Create the detailed content (initially hidden)
        self.create_detailed_content()
        
        # Update the canvas scroll region
        self.extended_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        
        # Hide the detailed description initially
        self.canvas.pack_forget()
        self.scrollbar.pack_forget()

    def create_detailed_content(self):
        # About section
        self.section_frame1 = ttk.Frame(self.extended_frame, style="DarkBlue.TFrame", padding=(10, 10, 10, 10))
        self.section_frame1.pack(fill=tk.X, pady=10)

        self.section_title1 = ttk.Label(
            self.section_frame1, 
            text="About SOCCSKSARGEN Tourism", 
            style="LightBlue.TLabel",
            font=self.section_title_font
        )
        self.section_title1.pack(anchor=tk.W)

        self.about_text = ttk.Label(
            self.section_frame1, 
            text="The Tourism Information System for SOCCSKSARGEN is dedicated to showcasing the rich cultural heritage and natural beauty\nof South Cotabato, Cotabato, Sultan Kudarat, Sarangani, and General Santos City. Our platform provides a comprehensive\nguide to help tourists and locals alike explore the hidden gems of this magnificent region.",
            style="DarkBlue.TLabel",
            font=self.regular_font,
            justify=tk.LEFT
        )
        self.about_text.pack(fill=tk.X, pady=10)

        # Explore SOCCSKSARGEN section
        self.section_frame2 = ttk.Frame(self.extended_frame, style="DarkBlue.TFrame", padding=(10, 10, 10, 10))
        self.section_frame2.pack(fill=tk.X, pady=10)

        self.section_title2 = ttk.Label(
            self.section_frame2, 
            text="Explore SOCCSKSARGEN", 
            style="LightBlue.TLabel",
            font=self.section_title_font
        )
        self.section_title2.pack(anchor=tk.W)

        # Feature grid
        self.feature_grid = ttk.Frame(self.section_frame2, style="DarkBlue.TFrame")
        self.feature_grid.pack(fill=tk.X, pady=15)
        
        # Feature cards
        features = [
            {"icon": "🏖️", "title": "Beaches", "desc": "Pristine shorelines with crystal clear waters"},
            {"icon": "🏔️", "title": "Mountains", "desc": "Majestic peaks and breathtaking views"},
            {"icon": "🏛️", "title": "Museums", "desc": "Cultural heritage and historical artifacts"},
            {"icon": "⛺", "title": "Camping", "desc": "Serene camping sites amidst nature"},
            {"icon": "🥾", "title": "Hiking", "desc": "Adventure trails for all experience levels"},
            {"icon": "🚜", "title": "Farms", "desc": "Agricultural tourism and local produce"},
            {"icon": "💦", "title": "Waterfalls", "desc": "Stunning cascades hidden in lush forests"},
            {"icon": "⛳", "title": "Golf", "desc": "World-class courses with scenic views"},
            {"icon": "📅", "title": "Events", "desc": "Local festivals and cultural celebrations"}
        ]
        
        # Create a 3x3 grid for features
        row, col = 0, 0
        for feature in features:
            card = self.create_feature_card(self.feature_grid, feature["icon"], feature["title"], feature["desc"])
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            col += 1
            if col > 2:  # 3 columns
                col = 0
                row += 1
        
        # Configure grid columns to be equal width
        for i in range(3):
            self.feature_grid.columnconfigure(i, weight=1)
        
        # Purpose section
        self.section_frame3 = ttk.Frame(self.extended_frame, style="DarkBlue.TFrame", padding=(10, 10, 10, 10))
        self.section_frame3.pack(fill=tk.X, pady=10)

        self.section_title3 = ttk.Label(
            self.section_frame3, 
            text="Purpose of Our Tourism Information System", 
            style="LightBlue.TLabel",
            font=self.section_title_font
        )
        self.section_title3.pack(anchor=tk.W)
        
        self.purpose_label = ttk.Label(
            self.section_frame3, 
            text="Our system aims to promote sustainable tourism in the SOCCSKSARGEN region by:",
            style="DarkBlue.TLabel",
            font=self.regular_font,
            justify=tk.LEFT
        )
        self.purpose_label.pack(anchor=tk.W, pady=(10, 5))
        
        # Purpose bullets
        purposes = [
            "• Providing accurate and up-to-date information about tourist destinations",
            "• Supporting local businesses and communities through tourism",
            "• Preserving the cultural heritage and natural resources of the region",
            "• Offering personalized travel itineraries based on user preferences",
            "• Facilitating convenient booking of accommodations and tours",
            "• Showcasing upcoming events and festivals in the region"
        ]
        
        for purpose in purposes:
            purpose_item = ttk.Label(
                self.section_frame3, 
                text=purpose, 
                style="DarkBlue.TLabel",
                font=self.regular_font,
                justify=tk.LEFT
            )
            purpose_item.pack(anchor=tk.W, padx=15)

    def create_feature_card(self, parent, icon, title, desc):
        # Create card frame with medium blue background
        card = ttk.Frame(parent, style="MediumBlue.TFrame", padding=(10, 10, 10, 10))
        
        # Icon - using regular Label for emoji support
        icon_label = tk.Label(card, text=icon, font=font.Font(size=24), bg=self.medium_blue, fg="white")
        icon_label.pack(pady=(5, 10))
        
        # Title with medium blue background
        title_label = ttk.Label(
            card, 
            text=title, 
            style="MediumBlue.TLabel",
            font=self.feature_title_font
        )
        title_label.pack()
        
        # Description with medium blue background
        desc_label = ttk.Label(
            card, 
            text=desc, 
            style="MediumBlue.TLabel",
            font=self.regular_font,
            wraplength=150
        )
        desc_label.pack(pady=(5, 0))
        
        # Instead of directly changing bg/fg on hover, we'll change styles
        card.bind("<Enter>", lambda e, c=card: self.on_card_hover(c, True))
        card.bind("<Leave>", lambda e, c=card: self.on_card_hover(c, False))
        
        return card
    
    def on_card_hover(self, card, is_hover):
        # This is more complex with ttk - would require dynamic style creation
        # For simplicity, we'll keep the original color for now
        # A more advanced approach would be to create hover-specific styles
        pass
    
    def toggle_description(self):
        if not self.extended_frame.visible:
            # Show extended description
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.read_more_btn.configure(text="Read Less")
            self.extended_frame.visible = True
        else:
            # Hide extended description
            self.canvas.pack_forget()
            self.scrollbar.pack_forget()
            self.read_more_btn.configure(text="Read More")
            self.extended_frame.visible = False
            
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def explore_places_page(self):
        """Displays the Explore Places page with working search functionality."""
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Title
        ttk.Label(self.content_frame, text="Explore Places", font=("Arial", 24, "bold")).pack(pady=20)

        # Search Bar Frame
        search_frame = ttk.Frame(self.content_frame)
        search_frame.pack(pady=10)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20, font=("Arial", 12))
        self.search_entry.pack(pady=5, side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda event: self.search_places_explore())

        # Search Button
        search_button = ttk.Button(search_frame, text="Search", command=self.search_places_explore, bootstyle="primary")
        search_button.pack(side=tk.LEFT, padx=5)

        # Category Filter
        category_frame = ttk.Frame(search_frame)
        category_frame.pack(side=tk.LEFT, padx=10)

        ttk.Label(category_frame, text="Category:").pack(side=tk.LEFT, padx=5)

        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(category_frame, textvariable=self.category_var, 
                                            values=["All", "Beach", "Mountains", "Museum", "Camping", 
                                                    "Hiking", "Farm", "Waterfalls", "Golf"],
                                            state="readonly", width=15)
        self.category_dropdown.current(0)
        self.category_dropdown.pack(side=tk.LEFT, padx=5)

        filter_button = ttk.Button(category_frame, text="Filter", command=self.filter_places, bootstyle="primary")
        filter_button.pack(side=tk.LEFT, padx=5)

        # Scrollable Frame Setup
        self.canvas = tk.Canvas(self.content_frame)
        self.scroll_frame = ttk.Frame(self.canvas)
        self.scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        # Bind scrolling
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

        # Load initial places
        self.load_places()

    def _on_mousewheel(self, event):
        """Enables scrolling with the mouse wheel."""
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def load_places(self):
        """Loads all APPROVED places from the database into the UI."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if db is None:
            messagebox.showerror("Database Error", "No database connection available.")
            return

        try:
            # Only select places with status 'approved'
            cursor.execute("SELECT id, name, category, description, image, location FROM places WHERE status = 'approved'")
            places = cursor.fetchall()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error fetching places: {err}")
            return

        if not places:
            ttk.Label(self.scroll_frame, text="No approved places found.", font=("Arial", 14)).pack(pady=10)
            return

        for place in places:
            self.create_place_card(place)

    def search_places_explore(self):
        """Searches APPROVED places in Explore Places page based on user input."""
        query = self.search_var.get().strip()
        
        # Clear previous results
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not query:
            self.load_places()
            return

        if db is None:
            messagebox.showerror("Database Error", "No database connection available.")
            return

        try:
            # Search by name, location or category in APPROVED places only
            cursor.execute("""
                SELECT id, name, category, description, image, location 
                FROM places 
                WHERE status = 'approved' AND (name LIKE %s OR location LIKE %s OR category LIKE %s)
                """, (f"%{query}%", f"%{query}%", f"%{query}%"))
            places = cursor.fetchall()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error searching places: {err}")
            return

        if not places:
            ttk.Label(self.scroll_frame, text="No results found.", font=("Arial", 14)).pack(pady=10)
            return

        for place in places:
            self.create_place_card(place)

    def filter_places(self):
        """Filters APPROVED places based on selected category."""
        category = self.category_var.get()
        
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if db is None:
            messagebox.showerror("Database Error", "No database connection available.")
            return

        query = "SELECT id, name, category, description, image, location FROM places WHERE status = 'approved'"
        params = []

        if category != "All":
            query += " AND category = %s"
            params.append(category)

        try:
            cursor.execute(query, params)
            places = cursor.fetchall()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error filtering places: {err}")
            return

        if not places:
            ttk.Label(self.scroll_frame, text="No places found in this category.", font=("Arial", 14)).pack(pady=10)
            return

        for place in places:
            self.create_place_card(place)

    def create_place_card(self, place, saved=False):
        """Creates a UI card for each place in the database."""
        place_frame = ttk.Frame(self.scroll_frame, relief="ridge", borderwidth=2)
        place_frame.pack(fill=tk.X, pady=5, padx=5)

        # Load Image
        img_path = place[4]
        if os.path.exists(img_path):
            img = Image.open(img_path)
            img = img.resize((500, 250), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
            img_label = ttk.Label(place_frame, image=img)
            img_label.image = img
            img_label.pack(side=tk.LEFT, padx=10)

        # Place Details
        details_frame = ttk.Frame(place_frame)
        details_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(details_frame, text=f"📍 {place[1]}", font=("Arial", 16, "bold")).pack(anchor="w")
        ttk.Label(details_frame, text=f"Category: {place[2]}", font=("Arial", 12, "italic")).pack(anchor="w")
        ttk.Label(details_frame, text=place[3], font=("Arial", 12), wraplength=400).pack(anchor="w", pady=5)

        # Location
        ttk.Label(details_frame, text=f"🗺️ {place[5]}", font=("Arial", 12)).pack(anchor="w", pady=5)

        # Buttons
        button_frame = ttk.Frame(place_frame)
        button_frame.pack(side=tk.RIGHT, padx=10)

        map_button = ttk.Button(button_frame, text="🗺️ Map", command=lambda p=place: self.open_google_maps(p), bootstyle="info")
        map_button.pack(side=tk.LEFT, padx=5)

        if saved:
            save_button = ttk.Button(button_frame, text="❌ Unsave", command=lambda p=place: self.toggle_save_place(p), bootstyle="danger")
        else:
            save_button = ttk.Button(button_frame, text="💾 Save", command=lambda p=place: self.toggle_save_place(p), bootstyle="success")
        save_button.pack(side=tk.LEFT, padx=5)

    def open_google_maps(self, place):
        """Opens Google Maps for the selected place."""
        location = place[1]
        webbrowser.open(f"https://www.google.com/maps/search/?api=1&query={location}")

    def toggle_save_place(self, place):
        """Toggles save/unsave state and refreshes the saved places page."""
        try:
            cursor.execute("SELECT * FROM saved_places WHERE user_id = %s AND place_id = %s", (self.current_user_id, place[0]))
            saved = cursor.fetchone()

            if saved:
                self.unsave_place(place)
            else:
                self.save_place(place)

            self.saved_places_page()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error toggling save state: {err}")

    def save_place(self, place):
        """Saves a place to the saved_places table."""
        try:
            cursor.execute("INSERT INTO saved_places (user_id, place_id) VALUES (%s, %s)", (self.current_user_id, place[0]))
            db.commit()
            messagebox.showinfo("Saved", f"{place[1]} has been added to your saved places.")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error saving place: {err}")

    def unsave_place(self, place):
        """Removes a place from the saved_places table."""
        try:
            cursor.execute("DELETE FROM saved_places WHERE user_id = %s AND place_id = %s", (self.current_user_id, place[0]))
            db.commit()
            messagebox.showinfo("Removed", f"{place[1]} has been removed from your saved places.")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error unsaving place: {err}")

    def saved_places_page(self):
        """Displays the Saved Places page properly."""
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Title
        ttk.Label(self.content_frame, text="Saved Places", font=("Arial", 24, "bold")).pack(pady=20)
        
        # Scrollable Frame Setup
        self.canvas = tk.Canvas(self.content_frame)
        self.scroll_frame = ttk.Frame(self.canvas)
        self.scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        # Bind scrolling
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

        # Fetch saved places
        try:
            cursor.execute("""
                SELECT p.id, p.name, p.category, p.description, p.image, p.location
                FROM saved_places s
                JOIN places p ON s.place_id = p.id
                WHERE s.user_id = %s
                """, (self.current_user_id,))
            saved_places = cursor.fetchall()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error fetching saved places: {err}")
            return

        if not saved_places:
            ttk.Label(self.scroll_frame, text="No saved places yet.", font=("Arial", 14)).pack(pady=10)
            return

        for place in saved_places:
            self.create_place_card(place, saved=True)

    def reviews_page(self):
        """Displays the reviews page with search, category filter, and review submission functionality."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Configure the content frame to center the content
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.columnconfigure(1, weight=1)

        # Create a main container frame to hold everything
        main_container = ttk.Frame(self.content_frame)
        main_container.grid(row=0, column=0, columnspan=2, sticky="n")
        
        # Title with styling to match the screenshot
        title_label = ttk.Label(main_container, text="Review a Place", font=("Arial", 24, "bold"))
        title_label.pack(pady=(20, 30))
        
        # Search and Filter Section - use a Frame for better layout control
        search_frame = ttk.Frame(main_container)
        search_frame.pack(padx=20, pady=10, fill="x")
        
        # Create a frame for search controls to match the layout
        search_controls = ttk.Frame(search_frame)
        search_controls.pack(pady=5)
        
        # Search Input with styling
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_controls, textvariable=self.search_var, width=30, font=("Arial", 11))
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Search Button styled to match the blue button in screenshot
        search_button = ttk.Button(search_controls, text="Search", bootstyle="primary", command=self.search_places)
        search_button.pack(side=tk.LEFT, padx=5)
        
        # Category Filter with dropdown in the right position
        category_frame = ttk.Frame(search_controls)
        category_frame.pack(side=tk.LEFT, padx=20)
        
        self.categories = ["Beach", "Mountains", "Museum", "Camping", "Hiking", "Farm", "Waterfalls", "Golf"]
        self.category_var = tk.StringVar()
        category_dropdown = ttk.Combobox(category_frame, textvariable=self.category_var, values=self.categories, state="readonly", width=15)
        category_dropdown.pack(side=tk.LEFT, padx=5)
        category_dropdown.bind("<<ComboboxSelected>>", self.filter_by_category)
        
        # Filter Button styled to match
        filter_button = ttk.Button(category_frame, text="Filter", bootstyle="primary", command=self.filter_by_category_button)
        filter_button.pack(side=tk.LEFT, padx=5)
        
        # Results Frame (for displaying search results)
        self.results_frame = ttk.Frame(main_container, width=550)
        self.results_frame.pack(padx=20, pady=10, fill="x")
        
        # Add scrollbar to results frame - adjust height to match screenshot
        self.results_canvas = tk.Canvas(self.results_frame, height=150, width=550)
        scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.results_canvas.yview)
        self.scrollable_results = ttk.Frame(self.results_canvas)
        
        self.scrollable_results.bind(
            "<Configure>",
            lambda e: self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all"))
        )
        self.results_canvas.create_window((0, 0), window=self.scrollable_results, anchor=tk.NW)
        self.results_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.results_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind mouse scroll wheel to the canvas
        self.results_canvas.bind_all("<MouseWheel>", self.on_mousewheel_results)
        
        # Create a separator between search results and review form
        ttk.Separator(main_container, orient='horizontal').pack(fill="x", padx=20, pady=10)
        
        # Rating Section with improved styling to match the screenshot
        rating_label = ttk.Label(main_container, text="Rating:", font=("Arial", 14))
        rating_label.pack(pady=5)
        
        # Star Rating Frame
        self.star_frame = ttk.Frame(main_container)
        self.star_frame.pack(pady=5)
        
        self.stars = []
        self.rating = 0
        for i in range(5):
            # Use gold stars to match the screenshot
            star = ttk.Label(self.star_frame, text="★", font=("Arial", 24), foreground="#bbb")
            star.bind("<Button-1>", lambda e, idx=i: self.set_rating(idx + 1))
            star.pack(side=tk.LEFT, padx=5)
            self.stars.append(star)
        
        self.rating_label = ttk.Label(main_container, text="Select a rating", font=("Arial", 12))
        self.rating_label.pack(pady=5)
        
        # Review Text Box styled to match the screenshot
        review_label = ttk.Label(main_container, text="Your Review:", font=("Arial", 14))
        review_label.pack(pady=5)
        
        self.comment_box = tk.Text(main_container, height=5, width=60, font=("Arial", 12))
        self.comment_box.pack(pady=5)
        
        # Submit Button styled to match the blue button in the screenshot
        self.submit_button = ttk.Button(main_container, text="Submit", bootstyle="primary", command=self.submit_review)
        self.submit_button.pack(pady=10)
        
        # See All Reviews Link
        see_reviews_link = ttk.Label(
            main_container,
            text="See All Reviews",
            foreground="blue",
            cursor="hand2",
            font=("Arial", 12, "underline")
        )
        see_reviews_link.pack(pady=10)
        see_reviews_link.bind("<Button-1>", lambda e: self.show_all_reviews_popup())
        
        # Initialize with default data
        self.selected_place_id = None
        self.load_initial_places()

    def on_mousewheel_results(self, event):
        """Handle mouse wheel scrolling for the results canvas."""
        if event.delta > 0:
            self.results_canvas.yview_scroll(-1, "units")
        else:
            self.results_canvas.yview_scroll(1, "units")

    def load_initial_places(self):
        """Load initial set of places to display with images."""
        try:
            cursor.execute("SELECT id, name, description, category, location, image FROM places LIMIT 5")
            places = cursor.fetchall()
            self.display_places(places)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading places: {err}")

    def search_places(self):
        """Search places based on the search term with images."""
        search_term = self.search_var.get().strip()
        if not search_term:
            self.load_initial_places()
            return
            
        try:
            cursor.execute("SELECT id, name, description, category, location, image FROM places WHERE name LIKE %s", (f"%{search_term}%",))
            places = cursor.fetchall()
            self.display_places(places)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error searching places: {err}")

    def filter_by_category(self, event=None):
        """Filter places by selected category with images (triggered by combobox selection)."""
        selected_category = self.category_var.get()
        if not selected_category:
            self.load_initial_places()
            return
            
        try:
            cursor.execute("SELECT id, name, description, category, location, image FROM places WHERE category = %s", (selected_category,))
            places = cursor.fetchall()
            self.display_places(places)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error filtering places: {err}")

    def filter_by_category_button(self):
        """Filter places by selected category with images (triggered by filter button)."""
        selected_category = self.category_var.get()
        if not selected_category:
            messagebox.showwarning("No Category Selected", "Please select a category first.")
            return
            
        try:
            cursor.execute("SELECT id, name, description, category, location, image FROM places WHERE category = %s", (selected_category,))
            places = cursor.fetchall()
            self.display_places(places)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error filtering places: {err}")

    def display_places(self, places):
        """Display places in the results frame to match the layout in the screenshot."""
        # Clear previous results
        for widget in self.scrollable_results.winfo_children():
            widget.destroy()
            
        if not places:
            no_results = ttk.Label(self.scrollable_results, text="No places found", font=("Arial", 12, "italic"))
            no_results.pack(pady=10)
            return
            
        for place in places:
            place_id, name, description, category, location = place[:5]  # First 5 columns
            image_data = place[5] if len(place) > 5 else None  # Image data if available
            
            # Create frame for each place result
            place_frame = ttk.Frame(self.scrollable_results)
            place_frame.pack(fill=tk.X, pady=5, padx=5)
            
            # Try to display image
            img_frame = ttk.Frame(place_frame, width=80)
            img_frame.pack(side=tk.LEFT, padx=(0, 10))
            
            if image_data:
                try:
                    from PIL import Image, ImageTk
                    import io
                    
                    # Check if image_data is a file path or binary data
                    if isinstance(image_data, str) and os.path.exists(image_data):
                        image = Image.open(image_data)
                    else:
                        image = Image.open(io.BytesIO(image_data))
                    
                    image = image.resize((80, 60))
                    photo = ImageTk.PhotoImage(image)
                    
                    img_label = ttk.Label(img_frame, image=photo)
                    img_label.image = photo  # Keep a reference
                    img_label.pack(side=tk.LEFT)
                except Exception as e:
                    logging.error(f"Error loading image: {e}")
                    # Fallback placeholder
                    img_label = ttk.Label(img_frame, text=f"{name[:1]}'s\n{category}")
                    img_label.pack(side=tk.LEFT)
            else:
                # No image available - create a text placeholder
                img_label = ttk.Label(img_frame, text=f"{name[:1]}'s\n{category}")
                img_label.pack(side=tk.LEFT)
            
            # Content frame for text information
            content_frame = ttk.Frame(place_frame)
            content_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Place name with styling to match screenshot
            name_label = ttk.Label(
                content_frame, 
                text=name, 
                font=("Arial", 12, "bold"), 
                foreground="blue",
                cursor="hand2"
            )
            name_label.pack(anchor=tk.W)
            name_label.bind("<Button-1>", lambda e, pid=place_id, pname=name: self.select_place(pid, pname))
            
            # Category label
            category_label = ttk.Label(content_frame, text=f"Category: {category}")
            category_label.pack(anchor=tk.W)
            
            # Description text (shortened)
            desc_text = description[:100] + "..." if description and len(description) > 100 else description
            desc_label = ttk.Label(content_frame, text=desc_text, wraplength=400)
            desc_label.pack(anchor=tk.W)
            
            # Location text
            location_label = ttk.Label(content_frame, text=f"Location: {location}")
            location_label.pack(anchor=tk.W)
            
            # "Click here to review this place" link with styling to match screenshot
            review_link = ttk.Label(
                content_frame,
                text="✓ Click here to review this place",
                foreground="#007bff",
                cursor="hand2",
                font=("Arial", 10, "underline")
            )
            review_link.pack(anchor=tk.E, padx=5, pady=5)
            review_link.bind("<Button-1>", lambda e, pid=place_id, pname=name: self.select_place_for_review(pid, pname))
            
            # Add separator between places
            ttk.Separator(self.scrollable_results, orient='horizontal').pack(fill=tk.X, padx=5, pady=5)

    def load_image_from_db(self, place_id, size=(80, 60)):
        """Load an image for a place from the database."""
        try:
            cursor.execute("SELECT image FROM places WHERE id = %s", (place_id,))
            image_data = cursor.fetchone()
            
            if image_data and image_data[0]:
                # Convert binary data to image
                from PIL import Image, ImageTk
                import io
                
                # Check if the image is a path or binary data
                if isinstance(image_data[0], str) and os.path.exists(image_data[0]):
                    # It's a file path
                    image = Image.open(image_data[0])
                else:
                    # It's binary data
                    image = Image.open(io.BytesIO(image_data[0]))
                    
                image = image.resize(size)
                photo = ImageTk.PhotoImage(image)
                return photo
            return None
        except Exception as e:
            logging.error(f"Error loading image: {e}")
            return None
        
    def select_place(self, place_id, place_name):
        """Set the selected place for viewing details."""
        self.selected_place_id = place_id
        messagebox.showinfo("Place Selected", f"You've selected {place_name}")
        
        # Update the UI to show which place is selected
        self.search_var.set(place_name)
        
    def select_place_for_review(self, place_id, place_name):
        """Set the selected place for review and scroll to review section."""
        self.selected_place_id = place_id
        
        # Clear any existing review
        self.comment_box.delete("1.0", tk.END)
        self.rating = 0
        self.set_rating(0)
        
        # Scroll to the review section
        self.content_frame.update_idletasks()
        self.rating_label.update_idletasks()
        
        # Calculate position of rating section to scroll to
        y_position = self.rating_label.winfo_y()
        
        # Use update to ensure the widget has been drawn
        self.content_frame.update()
        
        # Set focus to the comment box
        self.comment_box.focus_set()
        
        # Show visual indicator that review section is ready
        self.rating_label.config(text=f"Rate {place_name}")
        
        # Flash the rating stars to draw attention
        def flash_stars(count=0):
            if count < 3:  # Flash 3 times
                for star in self.stars:
                    star.config(foreground="#ffcc00")
                self.content_frame.after(200, lambda: reset_stars(count))
            else:
                self.rating_label.config(text=f"Select a rating for {place_name}")
                
        def reset_stars(count):
            for star in self.stars:
                star.config(foreground="#bbb")
            self.content_frame.after(200, lambda: flash_stars(count + 1))
        
        flash_stars()

    def set_rating(self, rating):
        """Sets the star rating based on user selection with gold stars to match the screenshot."""
        self.rating = rating
        # Set stars to gold color when selected (matches the screenshot)
        for i in range(5):
            self.stars[i].config(foreground="#FFD700" if i < rating else "#bbb")
        
        # Update the rating label with the selected place name if available
        if self.selected_place_id is not None:
            try:
                cursor.execute("SELECT name FROM places WHERE id = %s", (self.selected_place_id,))
                place_name = cursor.fetchone()[0]
                self.rating_label.config(text=f"Rating for {place_name}: {rating}")
            except:
                self.rating_label.config(text=f"Rating: {rating}")
        else:
            self.rating_label.config(text=f"Rating: {rating}")

    def submit_review(self):
        """Submits a new review to the database."""
        if not self.selected_place_id:
            messagebox.showwarning("Input Error", "Please select a place from the search results first.")
            return
            
        comment = self.comment_box.get("1.0", tk.END).strip()
        if not comment or self.rating == 0:
            messagebox.showwarning("Input Error", "Please enter a comment and select a rating.")
            return
        
        if messagebox.askyesno("Confirm Submission", "Are you sure you want to submit this review?"):
            try:
                cursor.execute("INSERT INTO reviews (user_id, place_id, rating, comment) VALUES (%s, %s, %s, %s)",
                              (self.current_user_id, self.selected_place_id, self.rating, comment))
                db.commit()
                messagebox.showinfo("Success", "Review submitted successfully!")
                self.comment_box.delete("1.0", tk.END)
                self.rating = 0
                self.set_rating(0)
                self.selected_place_id = None
                self.search_var.set("")
                self.rating_label.config(text="Select a rating")
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error submitting review: {err}")

    def fetch_all_reviews(self):
        """Fetches all reviews from the database with user and place information."""
        try:
            cursor.execute("""
                SELECT 
                    r.id,
                    r.user_id,
                    u.username, 
                    p.name AS place_name, 
                    r.rating, 
                    r.comment,
                    r.date_created,
                    rr.reply_text AS admin_reply,
                    a.username AS admin_username
                FROM reviews r
                JOIN user_accounts u ON r.user_id = u.id
                JOIN places p ON r.place_id = p.id
                LEFT JOIN review_replies rr ON r.id = rr.review_id
                LEFT JOIN user_accounts a ON rr.admin_id = a.id
                ORDER BY r.date_created DESC
            """)
            return cursor.fetchall()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error fetching reviews: {err}")
            return []

    def show_all_reviews_popup(self):
        """Displays all reviews in a popup window with edit/delete options for user's own reviews."""
        if hasattr(self, 'all_reviews_popup') and self.all_reviews_popup.winfo_exists():
            self.all_reviews_popup.lift()
            return
        
        self.all_reviews_popup = Toplevel(self.root)
        self.all_reviews_popup.title("All Reviews")
        self.all_reviews_popup.geometry("800x600")
        
        # Center the popup window
        window_width = 800
        window_height = 600
        screen_width = self.all_reviews_popup.winfo_screenwidth()
        screen_height = self.all_reviews_popup.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.all_reviews_popup.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Title
        title_label = ttk.Label(self.all_reviews_popup, text="All Reviews", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Create a Canvas and Scrollbar for scrolling
        self.reviews_canvas = tk.Canvas(self.all_reviews_popup, borderwidth=0, highlightthickness=0)
        self.reviews_scrollbar = ttk.Scrollbar(self.all_reviews_popup, orient="vertical", command=self.reviews_canvas.yview)
        self.reviews_canvas.configure(yscrollcommand=self.reviews_scrollbar.set)
        
        # Pack the scrollbar and canvas
        self.reviews_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.reviews_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame inside canvas for content
        self.scrollable_reviews_frame = ttk.Frame(self.reviews_canvas)
        self.reviews_canvas.create_window((0, 0), window=self.scrollable_reviews_frame, anchor="nw")
        
        # Configure the canvas to use the scrollbar
        self.scrollable_reviews_frame.bind(
            "<Configure>",
            lambda e: self.reviews_canvas.configure(scrollregion=self.reviews_canvas.bbox("all"))
        )
        
        # Bind mouse wheel to scroll properly
        def _on_mousewheel(event):
            self.reviews_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.reviews_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Bind the close event
        self.all_reviews_popup.protocol("WM_DELETE_WINDOW", self.close_all_reviews_popup)
        
        self.load_all_reviews()

    def on_mousewheel_reviews(self, event):
        """Handle mouse wheel scrolling for the reviews canvas."""
        if event.delta > 0:
            self.reviews_canvas.yview_scroll(-1, "units")
        else:
            self.reviews_canvas.yview_scroll(1, "units")

    def close_all_reviews_popup(self):
        """Closes the all reviews popup window and re-establishes the mouse wheel binding."""
        if hasattr(self, 'all_reviews_popup') and self.all_reviews_popup.winfo_exists():
            self.all_reviews_popup.destroy()
        # Re-establish the mouse wheel binding for the results canvas
        self.results_canvas.bind_all("<MouseWheel>", self.on_mousewheel_results)

    def load_all_reviews(self):
        """Loads all reviews into the scrollable frame with edit/delete options for user's own reviews."""
        reviews = self.fetch_all_reviews()
        
        # Clear any existing reviews
        for widget in self.scrollable_reviews_frame.winfo_children():
            widget.destroy()
        
        if not reviews:
            no_reviews_label = tk.Label(self.scrollable_reviews_frame, text="No reviews found", bg="white")
            no_reviews_label.pack(pady=20)
            return
        
        for review in reviews:
            (review_id, user_id, username, place_name, rating, comment, 
             date_created, admin_reply, admin_username) = review
            
            # Format the date
            formatted_date = date_created.strftime("%B %d, %Y at %I:%M %p")
            
            # Create a frame for each review
            review_frame = tk.Frame(self.scrollable_reviews_frame, bg="white", bd=1, relief="solid")
            review_frame.pack(fill="x", pady=5, padx=5)
            
            # User and place information
            user_place_label = tk.Label(
                review_frame, 
                text=f"{username} reviewed {place_name} on {formatted_date}", 
                font=("Arial", 12), 
                bg="white"
            )
            user_place_label.pack(anchor="w", padx=5, pady=5)
            
            # Star rating display
            rating_frame = tk.Frame(review_frame, bg="white")
            rating_frame.pack(anchor="w", padx=5, pady=5)
            for i in range(5):
                star = tk.Label(
                    rating_frame, 
                    text="★" if i < rating else "☆", 
                    font=("Arial", 12), 
                    fg="gold" if i < rating else "#bbb", 
                    bg="white"
                )
                star.pack(side=tk.LEFT)
            
            # Review comment
            comment_label = tk.Label(
                review_frame, 
                text=f"📝 {comment}", 
                font=("Arial", 12), 
                bg="white", 
                wraplength=700,
                justify="left"
            )
            comment_label.pack(anchor="w", padx=5, pady=5)
            
            # Admin reply if available
            if admin_reply:
                reply_label = tk.Label(
                    review_frame, 
                    text=f"🔹 {admin_username} (Admin): {admin_reply}", 
                    font=("Arial", 12, "italic"), 
                    fg="blue", 
                    bg="white",
                    wraplength=700,
                    justify="left"
                )
                reply_label.pack(anchor="w", padx=5, pady=5)
            
            # Only show edit/delete buttons for the current user's reviews
            if user_id == self.current_user_id:
                buttons_frame = tk.Frame(review_frame, bg="white")
                buttons_frame.pack(anchor="e", padx=5, pady=5)
                
                edit_button = tk.Button(
                    buttons_frame, 
                    text="Edit", 
                    fg="#007bff", 
                    bg="white", 
                    bd=0, 
                    cursor="hand2", 
                    command=lambda rid=review_id: self.edit_review(rid)
                )
                edit_button.pack(side=tk.LEFT, padx=5)
                
                delete_button = tk.Button(
                    buttons_frame, 
                    text="Delete", 
                    fg="#dc3545", 
                    bg="white", 
                    bd=0, 
                    cursor="hand2", 
                    command=lambda rid=review_id: self.delete_review(rid)
                )
                delete_button.pack(side=tk.LEFT, padx=5)

    def edit_review(self, review_id):
        """Handles the editing of a review after verifying ownership."""
        try:
            # First verify that the review belongs to the current user
            cursor.execute("SELECT user_id FROM reviews WHERE id = %s", (review_id,))
            result = cursor.fetchone()
            
            if not result:
                messagebox.showerror("Error", "Review not found.")
                return
                
            review_user_id = result[0]
            
            if review_user_id != self.current_user_id:
                messagebox.showerror("Permission Denied", "You can only edit your own reviews.")
                return
                
            # If ownership is verified, proceed with editing
            cursor.execute("SELECT place_id, comment, rating FROM reviews WHERE id = %s", (review_id,))
            review = cursor.fetchone()
            
            if review:
                place_id, comment, rating = review
                cursor.execute("SELECT name FROM places WHERE id = %s", (place_id,))
                place_name = cursor.fetchone()[0]
                
                # Update UI
                self.selected_place_id = place_id
                self.search_var.set(place_name)
                self.comment_box.delete("1.0", tk.END)
                self.comment_box.insert("1.0", comment)
                self.set_rating(rating)
                self.comment_box.focus_set()
                
                # Change button function
                self.submit_button.config(text="Save Changes", command=lambda: self.update_review(review_id))
                
                # Close the popup
                self.close_all_reviews_popup()
                
                # Scroll to the review section
                self.content_frame.update_idletasks()
                self.rating_label.update_idletasks()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error retrieving review details: {err}")

    def update_review(self, review_id):
        """Updates the existing review in the database after verifying ownership."""
        # Verify ownership again before updating
        try:
            cursor.execute("SELECT user_id FROM reviews WHERE id = %s", (review_id,))
            result = cursor.fetchone()
            
            if not result or result[0] != self.current_user_id:
                messagebox.showerror("Permission Denied", "You can only update your own reviews.")
                return
                
            comment = self.comment_box.get("1.0", tk.END).strip()
            if not comment or self.rating == 0:
                messagebox.showwarning("Input Error", "Please enter a comment and select a rating.")
                return
            
            if messagebox.askyesno("Confirm Update", "Are you sure you want to update this review?"):
                cursor.execute("""
                    UPDATE reviews 
                    SET comment = %s, rating = %s, date_modified = NOW() 
                    WHERE id = %s
                """, (comment, self.rating, review_id))
                db.commit()
                messagebox.showinfo("Success", "Review updated successfully!")
                self.comment_box.delete("1.0", tk.END)
                self.rating = 0
                self.set_rating(0)
                self.submit_button.config(text="Submit", command=self.submit_review)
                self.selected_place_id = None
                self.search_var.set("")
                self.rating_label.config(text="Select a rating")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error updating review: {err}")

    def delete_review(self, review_id):
        """Deletes a review from the database after verifying ownership."""
        # Verify ownership before deleting
        try:
            cursor.execute("SELECT user_id FROM reviews WHERE id = %s", (review_id,))
            result = cursor.fetchone()
            
            if not result or result[0] != self.current_user_id:
                messagebox.showerror("Permission Denied", "You can only delete your own reviews.")
                return
                
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this review?"):
                cursor.execute("DELETE FROM reviews WHERE id = %s", (review_id,))
                db.commit()
                messagebox.showinfo("Success", "Review deleted successfully!")
                self.load_all_reviews()  # Refresh the reviews list
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error deleting review: {err}")

    def events_page(self):
        """Display events from the database in a grid format with filters."""

        
        # Main content container - holding both the event display and right sidebar
        main_container = ttk.Frame(self.content_frame)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left content area for events
        left_content = ttk.Frame(main_container)
        left_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 10), pady=10)
        
        # Search Bar
        search_frame = ttk.Frame(left_content)
        search_frame.pack(fill=tk.X, pady=10)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        search_button = ttk.Button(search_frame, text="Search", style="CustomBlue.TButton", 
                                  command=self.search_events)
        search_button.pack(side=tk.LEFT)
        
        # Add binding for Enter key
        search_entry.bind("<Return>", lambda e: self.search_events())
        
        # Category Filters
        category_frame = ttk.Frame(left_content)
        category_frame.pack(fill=tk.X, pady=10)

        self.current_category = "all"  # Track current category filter

        # Style for the category links
        link_font = font.Font(family="Arial", size=10, underline=False)
        active_link_font = font.Font(family="Arial", size=10, underline=True)

        # Create a frame for the links with proper spacing
        links_frame = ttk.Frame(category_frame)
        links_frame.pack(fill=tk.X)

        # Store references to all category labels
        self.category_labels = {}

        # Create the category links
        categories = [("All Events", "all"), ("Festival", "festival"), ("Concert", "concert"),
                    ("Exhibition", "exhibition"), ("Sports", "sports"), 
                    ("Conference", "conference"), ("Workshop", "workshop")]

        for i, (text, category) in enumerate(categories):
            # Create a label styled as a link
            link = ttk.Label(
                links_frame, 
                text=text,
                foreground="#0066cc",
                cursor="hand2"
            )
            
            # Set initial font (underlined for "All Events", regular for others)
            if category == "all":
                link.configure(font=active_link_font)  # Active by default
            else:
                link.configure(font=link_font)
                
            # Position the link in the frame with appropriate spacing
            link.grid(row=0, column=i, padx=15)
            
            # Bind click event
            link.bind("<Button-1>", lambda e, cat=category: self.category_link_click(cat))
            
            # Bind hover events for underline effect
            link.bind("<Enter>", lambda e, lbl=link: lbl.configure(font=active_link_font) 
                                           if lbl.cget("font") != active_link_font else None)
            link.bind("<Leave>", lambda e, lbl=link, cat=category: lbl.configure(font=link_font) 
                                           if cat != self.current_category else None)
            
            # Store reference to the label
            self.category_labels[category] = link
        
        # Main container for both grid and detail views with scrollbar
        self.main_event_container = ttk.Frame(left_content)
        self.main_event_container.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas and scrollbar for the main content
        self.main_canvas = tk.Canvas(self.main_event_container, borderwidth=0, highlightthickness=0)
        self.main_scrollbar = ttk.Scrollbar(self.main_event_container, orient="vertical", command=self.main_canvas.yview)
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        
        # Pack the scrollbar and canvas
        self.main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame inside canvas for content
        self.main_content_frame = ttk.Frame(self.main_canvas)
        self.main_canvas_window = self.main_canvas.create_window((0, 0), window=self.main_content_frame, anchor="nw")
        
        # Bind the canvas to configure events
        self.main_content_frame.bind("<Configure>", self.on_main_content_configure)
        self.main_canvas.bind("<Configure>", self.on_main_canvas_configure)
        
        # Make the canvas scrollable with the mouse wheel
        self.main_canvas.bind("<Enter>", self.bind_mousewheel)
        self.main_canvas.bind("<Leave>", self.unbind_mousewheel)
        
        # No results message (hidden initially)
        self.no_results_frame = ttk.Frame(self.main_content_frame)
        no_results_label = ttk.Label(self.no_results_frame, 
                                    text="No events found matching your search criteria.\nTry adjusting your search terms or filters.",
                                    font=("Arial", 12))
        no_results_label.pack(pady=20)
        
        # Event grid view (inside main_content_frame)
        self.event_grid = ttk.Frame(self.main_content_frame)
        
        # Event detail view (inside main_content_frame)
        self.event_detail_frame = ttk.Frame(self.main_content_frame)
        
        # Image display in detail view
        self.detail_image_label = ttk.Label(self.event_detail_frame)
        self.detail_image_label.pack(pady=10)
        
        # Navigation buttons
        nav_frame = ttk.Frame(self.event_detail_frame)
        nav_frame.pack(pady=10)
        
        prev_btn = ttk.Button(nav_frame, text="◀ Prev", style="CustomBlue.TButton",
                             command=self.show_prev_event)
        prev_btn.pack(side=tk.LEFT, padx=5)
        
        next_btn = ttk.Button(nav_frame, text="Next ▶", style="CustomBlue.TButton",
                             command=self.show_next_event)
        next_btn.pack(side=tk.LEFT, padx=5)
        
        # Event details
        self.event_info_frame = ttk.Frame(self.event_detail_frame, relief="solid", borderwidth=1)
        self.event_info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.detail_name_label = ttk.Label(self.event_info_frame, text="", font=("Arial", 16, "bold"))
        self.detail_name_label.pack(anchor="w", padx=10, pady=5)
        
        self.detail_location_label = ttk.Label(self.event_info_frame, text="", font=("Arial", 12))
        self.detail_location_label.pack(anchor="w", padx=10, pady=2)
        
        self.detail_date_label = ttk.Label(self.event_info_frame, text="", font=("Arial", 12))
        self.detail_date_label.pack(anchor="w", padx=10, pady=2)
        
        self.detail_time_label = ttk.Label(self.event_info_frame, text="", font=("Arial", 12))
        self.detail_time_label.pack(anchor="w", padx=10, pady=2)
        
        self.detail_fee_label = ttk.Label(self.event_info_frame, text="", font=("Arial", 12))
        self.detail_fee_label.pack(anchor="w", padx=10, pady=2)
        
        self.detail_description_label = ttk.Label(self.event_info_frame, text="", font=("Arial", 12), 
                                                 wraplength=600, justify="left")
        self.detail_description_label.pack(anchor="w", padx=10, pady=5)
        
        # Back to grid button
        back_btn = ttk.Button(self.event_detail_frame, text="Back to Events", style="CustomBlue.TButton",
                             command=self.show_event_grid)
        back_btn.pack(pady=10)
        
        # Right sidebar with filters and popular events (with scrolling)
        self.right_sidebar = ttk.Frame(main_container, width=250, style="RightSidebar.TFrame")
        self.right_sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        self.right_sidebar.pack_propagate(False)  # Prevent the frame from shrinking
        
        # Add content to right sidebar
        self.create_right_sidebar()
        
        # Fetch events from database
        self.fetch_events()
        
        # Display the event grid by default
        self.show_event_grid()
        
        # Update the canvas scroll region
        self.main_content_frame.update_idletasks()
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def category_link_click(self, category):
        """Handle category link clicks."""
        # Reset all labels to non-active state
        for cat, lbl in self.category_labels.items():
            lbl.configure(font=font.Font(family="Arial", size=10, underline=False))
        
        # Set clicked label to active state
        self.category_labels[category].configure(font=font.Font(family="Arial", size=10, underline=True))
        
        # Filter events by the selected category
        self.filter_by_category(category)

    def on_main_content_configure(self, event):
        """Handle main content frame configuration changes."""
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def on_main_canvas_configure(self, event):
        """Handle main canvas configuration changes."""
        self.main_canvas.itemconfig(self.main_canvas_window, width=event.width)

    def bind_mousewheel(self, event):
        """Bind mousewheel to canvas when mouse enters."""
        self.main_canvas.bind_all("<MouseWheel>", self.on_main_mousewheel)

    def unbind_mousewheel(self, event):
        """Unbind mousewheel from canvas when mouse leaves."""
        self.main_canvas.unbind_all("<MouseWheel>")

    def on_main_mousewheel(self, event):
        """Handle mouse wheel scrolling for the main content area."""
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def create_right_sidebar(self):
        """Create content for the right sidebar with scrolling."""
        # Clear existing widgets
        for widget in self.right_sidebar.winfo_children():
            widget.destroy()
            
        # Create a canvas with scrollbar for the sidebar content
        self.sidebar_canvas = tk.Canvas(self.right_sidebar, bg=self.dark_blue, highlightthickness=0)
        sidebar_scrollbar = ttk.Scrollbar(self.right_sidebar, orient="vertical", command=self.sidebar_canvas.yview)
        self.sidebar_canvas.configure(yscrollcommand=sidebar_scrollbar.set)
        
        sidebar_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sidebar_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame inside canvas for sidebar content
        self.sidebar_content = ttk.Frame(self.sidebar_canvas, style="RightSidebar.TFrame")
        self.sidebar_window = self.sidebar_canvas.create_window((0, 0), window=self.sidebar_content, anchor="nw", width=230)
        
        # Header label
        ttk.Label(self.sidebar_content, text="Advanced Filters", font=("Arial", 14, "bold"), 
                 style="RightSidebar.TLabel").pack(anchor="w", padx=10, pady=10)
        
        # Event Type filter
        ttk.Label(self.sidebar_content, text="Event Type:", style="RightSidebar.TLabel").pack(anchor="w", padx=10, pady=(5, 0))
        self.event_type_var = tk.StringVar(value="All")
        event_type_combo = ttk.Combobox(self.sidebar_content, textvariable=self.event_type_var,
                                      values=["All", "Festival", "Concert", "Exhibition", "Sports", "Conference", "Workshop"],
                                      state="readonly", width=15)
        event_type_combo.pack(fill=tk.X, padx=10, pady=5)
        
        # Location filter
        ttk.Label(self.sidebar_content, text="Location:", style="RightSidebar.TLabel").pack(anchor="w", padx=10, pady=(5, 0))
        self.location_var = tk.StringVar(value="All")
        location_combo = ttk.Combobox(self.sidebar_content, textvariable=self.location_var,
                                    values=["All", "General Santos City", "South Cotabato", "Koronadal City", 
                                           "Sarangani Province", "Cotabato Province", "Sultan Kudarat"],
                                    state="readonly", width=15)
        location_combo.pack(fill=tk.X, padx=10, pady=5)
        
        # Entry Fee filter
        ttk.Label(self.sidebar_content, text="Entry Fee:", style="RightSidebar.TLabel").pack(anchor="w", padx=10, pady=(5, 0))
        self.fee_var = tk.StringVar(value="All")
        fee_combo = ttk.Combobox(self.sidebar_content, textvariable=self.fee_var,
                               values=["All", "Free", "Paid"],
                               state="readonly", width=15)
        fee_combo.pack(fill=tk.X, padx=10, pady=5)
        
        # Date filter section
        ttk.Label(self.sidebar_content, text="Filter by Date", font=("Arial", 14, "bold"), 
                 style="RightSidebar.TLabel").pack(anchor="w", padx=10, pady=(20, 10))
        
        # Month filter
        ttk.Label(self.sidebar_content, text="Month:", style="RightSidebar.TLabel").pack(anchor="w", padx=10, pady=(5, 0))
        self.month_var = tk.StringVar(value="All")
        month_combo = ttk.Combobox(self.sidebar_content, textvariable=self.month_var, 
                                  values=["All", "January", "February", "March", "April", "May", "June", 
                                          "July", "August", "September", "October", "November", "December"],
                                  state="readonly", width=15)
        month_combo.pack(fill=tk.X, padx=10, pady=5)
        
        # Year filter
        ttk.Label(self.sidebar_content, text="Year:", style="RightSidebar.TLabel").pack(anchor="w", padx=10, pady=(5, 0))
        self.year_var = tk.StringVar(value="All")
        current_year = datetime.now().year
        year_combo = ttk.Combobox(self.sidebar_content, textvariable=self.year_var, 
                                  values=["All", str(current_year), str(current_year+1)],
                                  state="readonly", width=15)
        year_combo.pack(fill=tk.X, padx=10, pady=5)
        
        # Add Apply and Clear buttons
        buttons_frame = ttk.Frame(self.sidebar_content, style="RightSidebar.TFrame")
        buttons_frame.pack(fill=tk.X, padx=10, pady=15)
        
        # Apply Filter button
        apply_btn = ttk.Button(
            buttons_frame, 
            text="Apply Filter", 
            style="CustomBlue.TButton",
            command=self.apply_all_filters
        )
        apply_btn.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        # Clear Filter button
        clear_btn = ttk.Button(
            buttons_frame, 
            text="Clear Filter", 
            style="CustomBlue.TButton",
            command=self.clear_all_filters
        )
        clear_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # Popular Events section
        ttk.Label(self.sidebar_content, text="Popular Events", font=("Arial", 14, "bold"), 
                 style="RightSidebar.TLabel").pack(anchor="w", padx=10, pady=(20, 10))
        
        self.popular_events_frame = ttk.Frame(self.sidebar_content, style="RightSidebar.TFrame")
        self.popular_events_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Update the canvas scroll region when the sidebar content size changes
        self.sidebar_content.bind("<Configure>", lambda e: self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all")))
        self.sidebar_canvas.bind("<Configure>", lambda e: self.sidebar_canvas.itemconfig(self.sidebar_window, width=e.width))
        
        # Make the sidebar canvas scrollable with the mouse wheel
        self.sidebar_canvas.bind("<Enter>", lambda e: self.sidebar_canvas.bind_all("<MouseWheel>", self.on_sidebar_mousewheel))
        self.sidebar_canvas.bind("<Leave>", lambda e: self.sidebar_canvas.unbind_all("<MouseWheel>"))

    def on_sidebar_mousewheel(self, event):
        """Handle mouse wheel scrolling for the sidebar."""
        self.sidebar_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def fetch_events(self):
        """Fetch events from the database."""
        if not db or not cursor:
            messagebox.showerror("Database Error", "Failed to connect to the database.")
            return

        try:
            # Query to get all events that haven't been soft deleted
            query = """
            SELECT id, name, description, category, location, date, time, image, is_free
            FROM events
            WHERE status = 'approved' AND date_deleted IS NULL
            ORDER BY date ASC
            """
            cursor.execute(query)
            result = cursor.fetchall()
            
            # Convert tuple results to dictionaries for easier access
            self.events = []
            for row in result:
                self.events.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'category': row[3],
                    'location': row[4],
                    'date': row[5],
                    'time': row[6],
                    'image': row[7],
                    'is_free': bool(row[8]) if row[8] is not None else True
                })
                
            self.filtered_events = self.events.copy()  # Initial filtered events is all events
            
            # Update the event grid
            self.update_event_grid()
            
            # Add popular events to sidebar
            self.update_popular_events()
            
        except Error as e:
            logging.error(f"Error fetching events: {e}")
            messagebox.showerror("Database Error", f"Failed to fetch events: {e}")

    def create_event_card(self, event, index):
        """Create an event card widget."""
        # Card frame with white background and border
        card = ttk.Frame(self.event_grid, relief="solid", borderwidth=1)
        
        # Image
        img_frame = ttk.Frame(card)
        img_frame.pack(fill=tk.X)
        
        # Default image path
        DEFAULT_IMAGE = "assets/no_image.jpg"
        
        # Try to load the image
        try:
            img_path = event['image'] if event['image'] else DEFAULT_IMAGE
            if os.path.exists(img_path):
                img = Image.open(img_path)
                img = img.resize((250, 180), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                img_label = ttk.Label(img_frame)
                img_label.image = photo  # Keep a reference to prevent garbage collection
                img_label.configure(image=photo)
                img_label.pack(fill=tk.X)
            else:
                ttk.Label(img_frame, text="Image not available", font=("Arial", 10, "italic")).pack(fill=tk.X, pady=80)
        except Exception as e:
            logging.error(f"Error loading image for event {event['id']}: {e}")
            ttk.Label(img_frame, text="Image not available", font=("Arial", 10, "italic")).pack(fill=tk.X, pady=80)
        
        # Event info
        info_frame = ttk.Frame(card, padding=10)
        info_frame.pack(fill=tk.X)
        
        ttk.Label(info_frame, text=event['name'], font=("Arial", 12, "bold")).pack(anchor="w")
        ttk.Label(info_frame, text=event['location'], foreground="#666").pack(anchor="w")
        
        # Format date
        if event['date']:
            try:
                date_obj = event['date']
                date_str = date_obj.strftime("%B %d, %Y")
            except:
                date_str = str(event['date'])
            ttk.Label(info_frame, text=date_str, foreground="#f44336").pack(anchor="w")
        
        # Category badge
        if event.get('category'):
            category_frame = ttk.Frame(info_frame)
            category_frame.pack(anchor="w", pady=2)
            
            # Create custom style for category label
            category_style = f"Category{index}.TLabel"
            self.style.configure(category_style, background="#1e88e5", foreground="white")
            
            category_label = ttk.Label(category_frame, text=event['category'].title(), 
                                      style=category_style)
            category_label.pack(pady=2, padx=5)
        
        # Fee label with green background for free events
        fee_frame = ttk.Frame(info_frame)
        fee_frame.pack(anchor="w", pady=2)
        
        # Create custom style for fee label
        fee_style = f"Fee{index}.TLabel"
        fee_color = "#4caf50" if event.get('is_free', True) else "#f44336"
        self.style.configure(fee_style, background=fee_color, foreground="white")
        
        fee_text = "Free" if event.get('is_free', True) else "Paid"
        fee_label = ttk.Label(fee_frame, text=fee_text, style=fee_style)
        fee_label.pack(pady=2, padx=5)
        
        # View details button
        view_btn = ttk.Button(
            info_frame, 
            text="View Details", 
            style="CustomBlue.TButton",
            command=lambda idx=index: self.view_event_details(idx)
        )
        view_btn.pack(fill=tk.X, pady=5)
        
        return card

    def update_event_grid(self):
        """Update the event grid with current filtered events."""
        # Clear existing widgets
        for widget in self.event_grid.winfo_children():
            widget.destroy()
        
        # Hide no results message if it's showing
        self.no_results_frame.pack_forget()
        
        # Show event grid if we have events
        if len(self.filtered_events) > 0:
            # Create 3 columns
            cols = 3
            for i, event in enumerate(self.filtered_events):
                row = i // cols
                col = i % cols
                
                card = self.create_event_card(event, i)
                card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                
                # Configure row and column weights for even spacing
                self.event_grid.grid_rowconfigure(row, weight=1)
                self.event_grid.grid_columnconfigure(col, weight=1)
        else:
            # Show "no results" message if we have no events
            self.no_results_frame.pack(fill=tk.BOTH, expand=True)
            
        # Update the canvas scroll region
        self.main_content_frame.update_idletasks()
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def search_events(self):
        """Search events based on search query."""
        query = self.search_var.get().lower().strip()
        
        if query:
            self.filtered_events = [
                event for event in self.events 
                if query in event['name'].lower() 
                or query in event['description'].lower() 
                or query in event['location'].lower()
            ]
        else:
            # If search query is empty, apply category filter only
            self.filter_by_category(self.current_category)
            return
            
        # Apply category filter to search results if category isn't "all"
        if self.current_category != "all":
            self.filtered_events = [
                event for event in self.filtered_events 
                if event['category'].lower() == self.current_category
            ]
            
        # Update grid with filtered results
        self.update_event_grid()
        
    def filter_by_category(self, category):
        """Filter events by category."""
        self.current_category = category
        
        if category == "all":
            self.filtered_events = self.events.copy()
        else:
            self.filtered_events = [
                event for event in self.events 
                if event['category'] and event['category'].lower() == category
            ]
            
        # Also apply search query if there is any
        query = self.search_var.get().lower().strip()
        if query:
            self.filtered_events = [
                event for event in self.filtered_events 
                if query in event['name'].lower() 
                or query in event['description'].lower() 
                or query in event['location'].lower()
            ]
            
        # Update grid with filtered results
        self.update_event_grid()
        
    def apply_all_filters(self):
        """Apply all filters from the sidebar."""
        # Start with all events
        self.filtered_events = self.events.copy()
        
        # Apply event type filter
        event_type = self.event_type_var.get()
        if event_type != "All":
            self.filtered_events = [
                event for event in self.filtered_events
                if event['category'] and event['category'].lower() == event_type.lower()
            ]
            
        # Apply location filter
        location = self.location_var.get()
        if location != "All":
            self.filtered_events = [
                event for event in self.filtered_events
                if event['location'] and location in event['location']
            ]
            
        # Apply fee filter
        fee_filter = self.fee_var.get()
        if fee_filter != "All":
            is_free = (fee_filter == "Free")
            self.filtered_events = [
                event for event in self.filtered_events
                if event.get('is_free', True) == is_free
            ]
            
        # Apply month filter
        month = self.month_var.get()
        if month != "All":
            # Get month number (1-12) from month name
            month_names = ["January", "February", "March", "April", "May", "June", 
                          "July", "August", "September", "October", "November", "December"]
            month_num = month_names.index(month) + 1
            
            self.filtered_events = [
                event for event in self.filtered_events
                if event['date'] and event['date'].month == month_num
            ]
            
        # Apply year filter
        year = self.year_var.get()
        if year != "All":
            year_num = int(year)
            self.filtered_events = [
                event for event in self.filtered_events
                if event['date'] and event['date'].year == year_num
            ]
            
        # Update grid with filtered results
        self.update_event_grid()
        
    def clear_all_filters(self):
        """Clear all filters and reset to default."""
        self.event_type_var.set("All")
        self.location_var.set("All")
        self.fee_var.set("All")
        self.month_var.set("All")
        self.year_var.set("All")
        self.search_var.set("")
        self.current_category = "all"
        
        # Reset all category links to default state
        for cat, lbl in self.category_labels.items():
            lbl.configure(font=font.Font(family="Arial", size=10, underline=(cat == "all")))
        
        # Reset to all events
        self.filtered_events = self.events.copy()
        self.update_event_grid()
        
    def update_popular_events(self):
        """Update the popular events section in the sidebar."""
        # Clear existing popular events
        for widget in self.popular_events_frame.winfo_children():
            widget.destroy()
            
        # Get top 3 events (for demo purposes, we'll just use the first 3)
        top_events = self.events[:3] if len(self.events) >= 3 else self.events
        
        for event in top_events:
            # Create a mini event card
            card = ttk.Frame(self.popular_events_frame, style="MediumBlue.TFrame", padding=5)
            card.pack(fill=tk.X, pady=5)
            
            # Event name (clickable)
            name_btn = ttk.Label(card, text=event['name'], font=("Arial", 10, "bold"), 
                               style="LightBlue.TLabel", cursor="hand2")
            name_btn.pack(anchor="w")
            name_btn.bind("<Button-1>", lambda e, idx=self.events.index(event): self.view_event_details(idx))
            
            # Event date
            if event['date']:
                try:
                    date_obj = event['date']
                    date_str = date_obj.strftime("%b %d, %Y")
                except:
                    date_str = str(event['date'])
                date_label = ttk.Label(card, text=date_str, style="RightSidebar.TLabel")
                date_label.pack(anchor="w")
    
    def view_event_details(self, index):
        """Show detailed view of an event."""
        # Hide the grid view and no results frame
        self.event_grid.pack_forget()
        self.no_results_frame.pack_forget()
        
        # Store current event index for navigation
        self.current_event_index = index
        
        # Show the detail view
        self.event_detail_frame.pack(fill=tk.BOTH, expand=True)
        
        # Get the current event
        event = self.filtered_events[index]
        
        # Display event image
        DEFAULT_IMAGE = "assets/no_image.jpg"
        try:
            img_path = event['image'] if event['image'] else DEFAULT_IMAGE
            if os.path.exists(img_path):
                img = Image.open(img_path)
                img = img.resize((600, 350), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                self.detail_image_label.image = photo  # Keep a reference
                self.detail_image_label.configure(image=photo)
            else:
                # Clear image if not available
                self.detail_image_label.image = None
                self.detail_image_label.configure(image="")
        except Exception as e:
            logging.error(f"Error loading image for event details: {e}")
            self.detail_image_label.image = None
            self.detail_image_label.configure(image="")
            
        # Update event details
        self.detail_name_label.configure(text=event['name'])
        self.detail_location_label.configure(text=f"📍 {event['location']}")
        
        # Format date
        if event['date']:
            try:
                date_obj = event['date']
                date_str = date_obj.strftime("%B %d, %Y")
            except:
                date_str = str(event['date'])
            self.detail_date_label.configure(text=f"📅 Date: {date_str}")
        else:
            self.detail_date_label.configure(text="📅 Date: Not specified")
            
        # Format time
        self.detail_time_label.configure(text=f"🕒 Time: {event['time'] if event['time'] else 'Not specified'}")
        
        # Fee info
        fee_text = "Free Entry" if event.get('is_free', True) else "Paid Entry"
        self.detail_fee_label.configure(text=f"💲 {fee_text}")
        
        # Description
        self.detail_description_label.configure(text=event['description'])
        
        # Update scroll region
        self.main_content_frame.update_idletasks()
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        
    def show_event_grid(self):
        """Show the event grid view."""
        # Hide the detail view
        self.event_detail_frame.pack_forget()
        
        # Show the grid view
        self.event_grid.pack(fill=tk.BOTH, expand=True)
        
        # Update scroll region
        self.main_content_frame.update_idletasks()
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
            
    def show_prev_event(self):
        """Show the previous event in the list."""
        if self.current_event_index > 0:
            self.view_event_details(self.current_event_index - 1)
            
    def show_next_event(self):
        """Show the next event in the list."""
        if self.current_event_index < len(self.filtered_events) - 1:
            self.view_event_details(self.current_event_index + 1)

    def propose_event_page(self):
        """Display the page for sharing events and places."""
        # Clear existing content first
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Make content frame use grid for proper layout
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.columnconfigure(1, weight=1)
        
        # --- LEFT CARD - EVENT SUBMISSION ---
        event_card = ttk.Frame(self.content_frame, style="dark.TFrame")
        event_card.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        
        # Event title with bright blue color (#3498db)
        event_title = ttk.Label(
            event_card, 
            text="Submit an Event",
            font=("Arial", 16, "bold"),
            foreground="#3498db",
            style="dark.TLabel"
        )
        event_title.pack(anchor=tk.W, padx=20, pady=(20, 15))
        
        # Event Name field
        ttk.Label(event_card, text="Event Name:", style="dark.TLabel").pack(anchor=tk.W, padx=20, pady=(5, 0))
        event_name_entry = ttk.Entry(event_card, style="dark.TEntry")
        event_name_entry.pack(fill=tk.X, padx=20, pady=(5, 10))
        
        # Location field
        ttk.Label(event_card, text="Location:", style="dark.TLabel").pack(anchor=tk.W, padx=20, pady=(5, 0))
        event_location_entry = ttk.Entry(event_card, style="dark.TEntry")
        event_location_entry.pack(fill=tk.X, padx=20, pady=(5, 10))
        
        # Description field
        ttk.Label(event_card, text="Description:", style="dark.TLabel").pack(anchor=tk.W, padx=20, pady=(5, 0))
        event_description_text = scrolledtext.ScrolledText(event_card, height=4)
        event_description_text.pack(fill=tk.X, padx=20, pady=(5, 10))
        event_description_text.config(background="#333", foreground="white")
        
        # Create a container for the date and time sections to be side by side
        datetime_container = ttk.Frame(event_card, style="dark.TFrame")
        datetime_container.pack(fill=tk.X, padx=20, pady=0)
        
        # Left side - Event Date section
        date_section = ttk.Frame(datetime_container, style="dark.TFrame")
        date_section.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(date_section, text="Event Date:", style="dark.TLabel").pack(anchor=tk.W, pady=(5, 0))
        
        date_frame = ttk.Frame(date_section, style="dark.TFrame")
        date_frame.pack(fill=tk.X, pady=(5, 10))
        
        day_combo = ttk.Combobox(date_frame, width=5, values=[str(i).zfill(2) for i in range(1, 32)])
        day_combo.set("23")
        day_combo.pack(side=tk.LEFT, padx=(0, 5))
        
        month_combo = ttk.Combobox(date_frame, width=5, values=[str(i).zfill(2) for i in range(1, 13)])
        month_combo.set("04")
        month_combo.pack(side=tk.LEFT, padx=5)
        
        year_combo = ttk.Combobox(date_frame, width=8, values=[str(i) for i in range(2023, 2031)])
        year_combo.set("2025")
        year_combo.pack(side=tk.LEFT, padx=5)
        
        # Right side - Event Time section
        time_section = ttk.Frame(datetime_container, style="dark.TFrame")
        time_section.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        ttk.Label(time_section, text="Event Time:", style="dark.TLabel").pack(anchor=tk.W, pady=(5, 0))
        
        time_frame = ttk.Frame(time_section, style="dark.TFrame")
        time_frame.pack(fill=tk.X, pady=(5, 10))
        
        hour_combo = ttk.Combobox(time_frame, width=5, values=[str(i).zfill(2) for i in range(1, 13)])
        hour_combo.set("12")
        hour_combo.pack(side=tk.LEFT, padx=(0, 5))
        
        minute_combo = ttk.Combobox(time_frame, width=5, values=[str(i).zfill(2) for i in range(0, 60, 5)])
        minute_combo.set("00")
        minute_combo.pack(side=tk.LEFT, padx=5)
        
        ampm_combo = ttk.Combobox(time_frame, width=5, values=["AM", "PM"], state="readonly")
        ampm_combo.set("PM")
        ampm_combo.pack(side=tk.LEFT, padx=5)
        
        # Create another container for category and entry fee
        category_fee_container = ttk.Frame(event_card, style="dark.TFrame")
        category_fee_container.pack(fill=tk.X, padx=20, pady=0)
        
        # Left side - Category dropdown
        category_section = ttk.Frame(category_fee_container, style="dark.TFrame")
        category_section.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(category_section, text="Event Type:", style="dark.TLabel").pack(anchor=tk.W, pady=(5, 0))
        event_category_combo = ttk.Combobox(
            category_section,
            values=["Festival", "Concert", "Exhibition", "Sports", "Conference", "Workshop"],
            state="readonly"
        )
        event_category_combo.pack(fill=tk.X, pady=(5, 10), padx=(0, 10))
        
        # Right side - Entry Fee section
        fee_section = ttk.Frame(category_fee_container, style="dark.TFrame")
        fee_section.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        ttk.Label(fee_section, text="Entry Fee:", style="dark.TLabel").pack(anchor=tk.W, pady=(5, 0))
        
        fee_frame = ttk.Frame(fee_section, style="dark.TFrame")
        fee_frame.pack(fill=tk.X, pady=(5, 10))
        
        fee_var = tk.StringVar(value="free")
        free_radio = ttk.Radiobutton(fee_frame, text="Free Event", variable=fee_var, value="free", style="dark.TRadiobutton")
        free_radio.pack(side=tk.LEFT, padx=(0, 15))
        
        paid_radio = ttk.Radiobutton(fee_frame, text="Paid Event", variable=fee_var, value="paid", style="dark.TRadiobutton")
        paid_radio.pack(side=tk.LEFT)
        
        # Upload Image section
        ttk.Label(event_card, text="Upload Image:", style="dark.TLabel").pack(anchor=tk.W, padx=20, pady=(5, 0))
        
        file_frame = ttk.Frame(event_card, style="dark.TFrame")
        file_frame.pack(fill=tk.X, padx=20, pady=(5, 10))
        
        # Style the Choose File button with purple color to match screenshot
        file_button = ttk.Button(file_frame, text="Choose File", style="info.TButton")
        file_button.pack(side=tk.LEFT)
        
        file_label = ttk.Label(file_frame, text="No file chosen", style="dark.TLabel")
        file_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Submit button - position at bottom right of the card
        btn_frame = ttk.Frame(event_card, style="dark.TFrame")
        btn_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        submit_button = ttk.Button(
            btn_frame, 
            text="Submit Event",
            style="success.TButton"
        )
        submit_button.pack(side=tk.RIGHT)
        
        # --- RIGHT CARD - PLACE SUBMISSION ---
        place_card = ttk.Frame(self.content_frame, style="dark.TFrame")
        place_card.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        
        # Place title with matching blue color
        place_title = ttk.Label(
            place_card, 
            text="Submit a Place",
            font=("Arial", 16, "bold"),
            foreground="#3498db",
            style="dark.TLabel"
        )
        place_title.pack(anchor=tk.W, padx=20, pady=(20, 15))
        
        # Place Name field
        ttk.Label(place_card, text="Place Name:", style="dark.TLabel").pack(anchor=tk.W, padx=20, pady=(5, 0))
        place_name_entry = ttk.Entry(place_card, style="dark.TEntry")
        place_name_entry.pack(fill=tk.X, padx=20, pady=(5, 10))
        
        # Location field
        ttk.Label(place_card, text="Location:", style="dark.TLabel").pack(anchor=tk.W, padx=20, pady=(5, 0))
        place_location_entry = ttk.Entry(place_card, style="dark.TEntry")
        place_location_entry.pack(fill=tk.X, padx=20, pady=(5, 10))
        
        # Description field
        ttk.Label(place_card, text="Description:", style="dark.TLabel").pack(anchor=tk.W, padx=20, pady=(5, 0))
        description_text = scrolledtext.ScrolledText(place_card, height=5)
        description_text.pack(fill=tk.X, padx=20, pady=(5, 10))
        description_text.config(background="#333", foreground="white")
        
        # Category dropdown
        ttk.Label(place_card, text="Category:", style="dark.TLabel").pack(anchor=tk.W, padx=20, pady=(5, 0))
        category_combo = ttk.Combobox(
            place_card, 
            values=["Beach", "Mountains", "Museum", "Camping", "Hiking", "Farm", "Waterfalls","Golf"],
            state="readonly"
        )
        category_combo.pack(fill=tk.X, padx=20, pady=(5, 10))
        
        # Upload Image section
        ttk.Label(place_card, text="Upload Image:", style="dark.TLabel").pack(anchor=tk.W, padx=20, pady=(5, 0))
        
        place_file_frame = ttk.Frame(place_card, style="dark.TFrame")
        place_file_frame.pack(fill=tk.X, padx=20, pady=(5, 10))
        
        place_file_button = ttk.Button(place_file_frame, text="Choose File", style="info.TButton")
        place_file_button.pack(side=tk.LEFT)
        
        place_file_label = ttk.Label(place_file_frame, text="No file chosen", style="dark.TLabel")
        place_file_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Submit button - position at bottom right
        place_btn_frame = ttk.Frame(place_card, style="dark.TFrame")
        place_btn_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        place_submit_button = ttk.Button(
            place_btn_frame, 
            text="Submit Place",
            style="success.TButton"
        )
        place_submit_button.pack(side=tk.RIGHT)
        
        # Add functionality to buttons
        event_file_path = [None]
        place_file_path = [None]
        
        def event_file_browse():
            path = self.browse_file(file_label)
            event_file_path[0] = path
        
        def place_file_browse():
            path = self.browse_file(place_file_label)
            place_file_path[0] = path
        
        file_button.config(command=event_file_browse)
        place_file_button.config(command=place_file_browse)
        
        submit_button.config(command=lambda: self.submit_event_form(
            event_name_entry, 
            event_location_entry, 
            event_description_text, 
            day_combo, 
            month_combo, 
            year_combo,
            hour_combo,
            minute_combo,
            ampm_combo,
            fee_var,
            event_category_combo,
            event_file_path[0]
        ))
        
        place_submit_button.config(command=lambda: self.submit_place_form(
            place_name_entry, 
            place_location_entry, 
            description_text, 
            category_combo,
            place_file_path[0]
        ))

    def browse_file(self, label_widget):
        """Browse for a file and update the label."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")]
        )
        if file_path:
            # Extract just the filename from the path
            filename = os.path.basename(file_path)
            label_widget.config(text=filename)
            return file_path
        return None

    def submit_event_form(self, name_entry, location_entry, description_text, 
                         day_combo, month_combo, year_combo, hour_combo, 
                         minute_combo, ampm_combo, fee_var, category_combo, file_path=None):
        """Process the event submission."""
        # Get form data
        name = name_entry.get()
        location = location_entry.get()
        description = description_text.get("1.0", tk.END).strip()
        
        # Date and time formatting
        day = day_combo.get()
        month = month_combo.get()
        year = year_combo.get()
        date_str = f"{month}/{day}/{year}"
        
        hour = hour_combo.get()
        minute = minute_combo.get()
        ampm = ampm_combo.get()
        time_str = f"{hour}:{minute} {ampm}"
        
        # Entry fee and category
        is_free = True if fee_var.get() == "free" else False
        category = category_combo.get()
        
        # Simple validation
        if not name or not location or not description or not category:
            messagebox.showerror("Error", "Please fill in all required fields.")
            return
        
        # Save to database 
        if db and cursor:
            try:
                # Get current user ID
                user_id = self.current_user_id
                
                # Insert into database with 'pending' status
                sql = """
                INSERT INTO events (
                    user_id, name, description, location, 
                    date, time, category, is_free, image, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
                """
                
                # Format date for MySQL
                mysql_date = f"{year}-{month}-{day}"
                
                # Convert time to 24-hour format for MySQL
                if ampm == "PM" and hour != "12":
                    hour_24 = str(int(hour) + 12)
                elif ampm == "AM" and hour == "12":
                    hour_24 = "00"
                else:
                    hour_24 = hour
                
                mysql_time = f"{hour_24}:{minute}:00"
                
                cursor.execute(sql, (
                    user_id, name, description, location, 
                    mysql_date, mysql_time, category, is_free, 
                    file_path if file_path else ""
                ))
                
                db.commit()
                
                # Show confirmation message
                messagebox.showinfo("Success", 
                    f"Event '{name}' has been submitted for approval.\n\n"
                    f"Date: {date_str}\nTime: {time_str}\nLocation: {location}\n"
                    f"Category: {category}\nEntry Fee: {'Free' if is_free else 'Paid'}"
                )
                
                # Clear form fields
                name_entry.delete(0, tk.END)
                location_entry.delete(0, tk.END)
                description_text.delete("1.0", tk.END)
                category_combo.set("")
                
            except Error as e:
                db.rollback()
                messagebox.showerror("Database Error", f"Could not save event: {e}")
        else:
            # If no database connection, just show a success message
            messagebox.showinfo("Success", 
                f"Event '{name}' has been submitted for approval.\n\n"
                f"Date: {date_str}\nTime: {time_str}\nLocation: {location}\n"
                f"Category: {category}\nEntry Fee: {'Free' if is_free else 'Paid'}"
            )
            
            # Clear form fields anyway
            name_entry.delete(0, tk.END)
            location_entry.delete(0, tk.END)
            description_text.delete("1.0", tk.END)
            category_combo.set("")

    def submit_place_form(self, name_entry, location_entry, description_text, category_combo, file_path=None):
        """Process the place submission."""
        # Get form data
        name = name_entry.get()
        location = location_entry.get()
        description = description_text.get("1.0", tk.END).strip()
        category = category_combo.get()
        
        # Simple validation
        if not name or not location or not description or not category:
            messagebox.showerror("Error", "Please fill in all required fields.")
            return
        
        # Save to database
        if db and cursor:
            try:
                # First get the current user ID
                user_id = self.current_user_id
                
                # Save the place to the database
                sql = """
                INSERT INTO places (
                    user_id, name, description, location, 
                    category, image, status
                ) VALUES (%s, %s, %s, %s, %s, %s, 'pending')
                """
                
                # Execute the query with parameters
                cursor.execute(sql, (
                    user_id, name, description, location, 
                    category, file_path if file_path else ""
                ))
                
                # Commit the transaction
                db.commit()
                
                messagebox.showinfo("Success", 
                    f"Place '{name}' has been submitted for approval.\n\n"
                    f"Location: {location}\nCategory: {category}"
                )
                
                # Clear form fields
                name_entry.delete(0, tk.END)
                location_entry.delete(0, tk.END)
                description_text.delete("1.0", tk.END)
                category_combo.set("")
                
            except Error as e:
                db.rollback()
                messagebox.showerror("Database Error", f"Could not save place: {e}")
        else:
            # If no database connection, just show a success message
            messagebox.showinfo("Success", 
                f"Place '{name}' has been submitted for approval.\n\n"
                f"Location: {location}\nCategory: {category}"
            )
            
            # Clear form fields anyway
            name_entry.delete(0, tk.END)
            location_entry.delete(0, tk.END)
            description_text.delete("1.0", tk.END)
            category_combo.set("")
            
    def account_page(self):
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

        # Get user data
        if db and cursor:
            try:
                cursor.execute("SELECT username, email, phone, profile_picture_path, address, status FROM user_accounts WHERE id = %s", (self.current_user_id,))
                user_data = cursor.fetchone()
                if not user_data:
                    ttk.Label(scrollable_frame, text="User data not found!", font=("Arial", 12)).pack(pady=10)
                    return
                
                username, email, phone, profile_pic, address, status = user_data
            except mysql.connector.Error as err:
                ttk.Label(scrollable_frame, text=f"Error fetching user data: {err}", font=("Arial", 12)).pack(pady=10)
                return
        else:
            ttk.Label(scrollable_frame, text="Database connection failed!", font=("Arial", 12)).pack(pady=10)
            return

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
            if db and cursor:
                cursor.execute("UPDATE user_accounts SET profile_picture_path = %s WHERE id = %s", (save_path, self.current_user_id))
                db.commit()
                logging.info(f"✅ Profile picture updated: {save_path}")
                
                # Update UI
                self.refresh_profile_picture(save_path)
                messagebox.showinfo("Success", "Profile picture updated successfully!")
            else:
                messagebox.showerror("Error", "Database connection failed!")
        except Exception as e:
            logging.error(f"Error uploading profile picture: {e}")
            messagebox.showerror("Error", f"Failed to upload profile picture: {e}")

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
            current_value = None
            if db and cursor:
                cursor.execute(f"SELECT {field} FROM user_accounts WHERE id = %s", (self.current_user_id,))
                result = cursor.fetchone()
                if result:
                    current_value = result[0]
            
            # Show dialog with current value
            prompt_text = f"Enter new {field.capitalize()}:"
            new_value = simpledialog.askstring(f"Change {field.capitalize()}", prompt_text, initialvalue=current_value or "")
            
            if new_value is not None:  # User didn't cancel
                self.update_user_field(field, new_value)

    def update_user_field(self, field, value):
        """Update user field in database."""
        if not db or not cursor:
            messagebox.showerror("Error", "Database connection failed!")
            return False
        
        # Validation for specific fields
        if field == "email" and not self.validate_email(value):
            messagebox.showerror("Invalid Input", "Please enter a valid email address.")
            return False
        elif field == "phone" and not self.validate_phone(value):
            messagebox.showerror("Invalid Input", "Please enter a valid phone number.")
            return False
        
        try:
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

    def toggle_account_status(self):
        """Toggle user account status between active and inactive."""
        if not db or not cursor:
            messagebox.showerror("Error", "Database connection failed!")
            return
        
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
        
        if not db or not cursor:
            messagebox.showerror("Error", "Database connection failed!")
            return
        
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

# Main Program
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python userdashboard.py <user_id>")
        sys.exit(1)

    user_id = int(sys.argv[1])
    root = tk.Tk()
    dashboard = UserDashboard(root, user_id)
    root.mainloop()
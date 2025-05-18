import tkinter as tk
from tkinter import messagebox
import mysql.connector
import bcrypt
import os
import sys
import re

class Registration(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Create Account")
        self.geometry("400x550")
        self.configure(bg="#000000")
        self.resizable(False, False)
        
        # Widget variables
        self.entry_username = None
        self.entry_email = None
        self.entry_phone = None
        self.entry_address = None
        self.entry_password = None
        self.btn_toggle_password = None
        
        self.create_widgets()
        self.center_window()
        
    def create_widgets(self):
        # Main frame - using black background
        main_frame = tk.Frame(self, bg="#000000")
        main_frame.place(relx=0.5, rely=0.5, anchor="center", width=350, height=500)
        
        # Title
        tk.Label(main_frame, text="Create Account", font=("Arial", 16, "bold"), bg="#000000", fg="#FF9900").pack(pady=(10, 20))
        
        # Form frame
        form_frame = tk.Frame(main_frame, bg="#000000")
        form_frame.pack(fill="both", expand=True, padx=10)
        
        # Username
        tk.Label(form_frame, text="Username", font=("Arial", 10), bg="#000000", fg="white", anchor="w").pack(fill="x", pady=(0, 5))
        self.entry_username = tk.Entry(form_frame, font=("Arial", 10), relief="flat", bg="white")
        self.entry_username.pack(fill="x", pady=(0, 10), ipady=5)
        
        # Email
        tk.Label(form_frame, text="Email", font=("Arial", 10), bg="#000000", fg="white", anchor="w").pack(fill="x", pady=(0, 5))
        self.entry_email = tk.Entry(form_frame, font=("Arial", 10), relief="flat", bg="white")
        self.entry_email.pack(fill="x", pady=(0, 10), ipady=5)
        
        # Phone
        tk.Label(form_frame, text="Phone", font=("Arial", 10), bg="#000000", fg="white", anchor="w").pack(fill="x", pady=(0, 5))
        self.entry_phone = tk.Entry(form_frame, font=("Arial", 10), relief="flat", bg="white")
        self.entry_phone.pack(fill="x", pady=(0, 10), ipady=5)
        
        # Address
        tk.Label(form_frame, text="Address", font=("Arial", 10), bg="#000000", fg="white", anchor="w").pack(fill="x", pady=(0, 5))
        self.entry_address = tk.Entry(form_frame, font=("Arial", 10), relief="flat", bg="white")
        self.entry_address.pack(fill="x", pady=(0, 10), ipady=5)
        
        # Password with toggle
        tk.Label(form_frame, text="Password", font=("Arial", 10), bg="#000000", fg="white", anchor="w").pack(fill="x", pady=(0, 5))
        
        # Password field container
        password_frame = tk.Frame(form_frame, bg="white")  # White background to match entry field
        password_frame.pack(fill="x", pady=(0, 5))
        
        # Password entry
        self.entry_password = tk.Entry(password_frame, font=("Arial", 10), relief="flat", bg="white", show="*", bd=0)
        self.entry_password.pack(side="left", fill="x", expand=True, ipady=5)
        
        # Toggle password button - now inside the white entry field
        self.btn_toggle_password = tk.Button(password_frame, text="👁", font=("Arial", 10), bg="white", fg="gray", relief="flat",
                                           command=self.toggle_password_visibility, cursor="hand2", width=2,
                                           bd=0, highlightthickness=0, activebackground="white")
        self.btn_toggle_password.pack(side="right", padx=(0, 5))
        
        # Password requirements hint
        password_hint = tk.Label(form_frame, 
                                text="Password must be at least 8 characters with uppercase, lowercase, and numbers",
                                font=("Arial", 8), bg="#000000", fg="#cccccc", anchor="w", wraplength=330)
        password_hint.pack(fill="x", pady=(0, 10))
        
        # Register button - orange with white text
        btn_register = tk.Button(form_frame, text="Register", font=("Arial", 10, "bold"), bg="#FF9900", fg="white",
                                relief="flat", command=self.register, cursor="hand2", activebackground="#e68a00")
        btn_register.pack(fill="x", pady=(20, 10), ipady=5)
        
        # Back to Login button - black with orange text and border
        btn_back = tk.Button(form_frame, text="Back to Login", font=("Arial", 10), bg="#000000", fg="#FF9900",
                            relief="flat", command=self.back_to_login, cursor="hand2",
                            bd=1, highlightthickness=1, highlightbackground="#FF9900", activebackground="#222222")
        btn_back.pack(fill="x", pady=5, ipady=5)
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def connect_db(self):
        """Establish database connection"""
        try:
            db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="tourism_db"
            )
            return db
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not connect to database: {err}")
            sys.exit(1)
    
    def validate_password(self, password):
        """Check if password meets security requirements"""
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'[0-9]', password):
            return False
        return True
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.entry_password.cget("show") == "*":
            self.entry_password.config(show="")
            self.btn_toggle_password.config(text="👁")
        else:
            self.entry_password.config(show="*")
            self.btn_toggle_password.config(text="👁")
    
    def register(self):
        """Register new user"""
        # Get form data
        username = self.entry_username.get().strip()
        email = self.entry_email.get().strip()
        phone = self.entry_phone.get().strip()
        address = self.entry_address.get().strip()
        password = self.entry_password.get().strip()
        
        # Basic validation
        if not (username and email and password):
            messagebox.showerror("Registration Error", "Username, email, and password are required!")
            return
        
        # Password validation
        if not self.validate_password(password):
            messagebox.showerror("Registration Error", 
                               "Password must be at least 8 characters with uppercase, lowercase, and numbers!")
            return
        
        # Connect to database
        db = self.connect_db()
        cursor = db.cursor()
        
        # Check if username or email already exists
        cursor.execute("SELECT * FROM user_accounts WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            messagebox.showerror("Registration Error", "Username or email already exists!")
            db.close()
            return
        
        # Hash the password
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        try:
            # Insert new user into database
            cursor.execute(
                "INSERT INTO user_accounts (username, email, phone, password_hash, role, address) VALUES (%s, %s, %s, %s, %s, %s)",
                (username, email, phone, password_hash, "user", address)
            )
            db.commit()
            messagebox.showinfo("Registration Successful", 
                              "Your account has been created successfully! You can now login.")
            
            # Close the registration window and reopen login
            self.destroy()
            os.system(f"{sys.executable} login.py")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error creating account: {err}")
        finally:
            db.close()
    
    def back_to_login(self):
        """Return to login window"""
        self.destroy()
        os.system(f"{sys.executable} login.py")

if __name__ == "__main__":
    app = Registration()
    app.mainloop()
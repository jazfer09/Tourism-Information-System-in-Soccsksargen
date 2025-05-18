import tkinter as tk
from tkinter import messagebox
import mysql.connector
import requests
import random
import bcrypt
from dotenv import load_dotenv
import os
import sys

class Forgot(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Forgot Password")
        self.geometry("400x530")
        self.configure(bg="#000000")
        self.resizable(False, False)
        
        # Load environment variables with PyInstaller compatibility
        try:
            if getattr(sys, 'frozen', False):
                # Running as compiled EXE
                env_path = os.path.join(sys._MEIPASS, '.env')
            else:
                # Running as script
                env_path = '.env'
            
            load_dotenv(env_path)
            
            self.API_KEY = os.getenv("BREVO_API_KEY")
            self.SMTP_USERNAME = os.getenv("SMTP_USERNAME")
            self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
            
            if not all([self.API_KEY, self.SMTP_USERNAME, self.SMTP_PASSWORD]):
                raise ValueError("Missing one or more required environment variables")
                
        except Exception as e:
            messagebox.showerror("Configuration Error", 
                               f"Failed to load configuration: {str(e)}\n"
                               f"Please ensure .env file exists with required variables.")
            self.destroy()
            return
        
        # SMTP Configuration
        self.SMTP_SERVER = "smtp-relay.brevo.com"
        self.SMTP_PORT = 587
        
        # Store verification codes
        self.verification_codes = {}
        
        # Database Connection
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="tourism_db"
            )
            self.cursor = self.db.cursor()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to connect: {err}")
            self.destroy()
            return
        
        # Widgets
        self.entry_email = None
        self.entry_code = None
        self.entry_new_password = None
        self.btn_toggle_password = None
        
        # Style constants
        self.ENTRY_WIDTH = 37
        self.ENTRY_FONT = ("Arial", 10)
        self.INPUT_PADDING = 5
        self.ORANGE_COLOR = "#FF9900"
        self.BUTTON_WIDTH = 15
        self.BUTTON_FONT = ("Arial", 10, "bold")
        self.LABEL_FONT = ("Arial", 12)
        self.TITLE_FONT = ("Arial", 18, "bold")
        self.SECTION_PADDING = 15
        
        self.create_widgets()
        self.center_window()
        
    def create_widgets(self):
        # Create a main container frame with some padding
        container = tk.Frame(self, bg="#000000", padx=25, pady=20)
        container.pack(expand=True, fill="both")
        
        # Title with larger font and more padding
        title_label = tk.Label(
            container, 
            text="Reset Your Password", 
            font=self.TITLE_FONT, 
            bg="#000000", 
            fg=self.ORANGE_COLOR
        )
        title_label.pack(pady=self.SECTION_PADDING)
        
        # Email section with frame for organization
        email_frame = tk.Frame(container, bg="#000000")
        email_frame.pack(fill="x", pady=10)
        
        email_label = tk.Label(
            email_frame, 
            text="Email Address", 
            bg="#000000", 
            fg="white", 
            font=self.LABEL_FONT,
            anchor="w"
        )
        email_label.pack(fill="x")
        
        self.entry_email = tk.Entry(email_frame, width=self.ENTRY_WIDTH, font=self.ENTRY_FONT)
        self.entry_email.pack(ipady=self.INPUT_PADDING, pady=5, fill="x")
        
        # Send code button in its own frame
        send_code_frame = tk.Frame(container, bg="#000000")
        send_code_frame.pack(fill="x", pady=5)
        
        send_code_button = tk.Button(
            send_code_frame, 
            text="Send Code", 
            command=self.send_verification_code, 
            bg=self.ORANGE_COLOR, 
            fg="white", 
            font=self.BUTTON_FONT,
            width=self.BUTTON_WIDTH,
            cursor="hand2"
        )
        send_code_button.pack(side="left")
        
        # Verification code section
        code_frame = tk.Frame(container, bg="#000000")
        code_frame.pack(fill="x", pady=self.SECTION_PADDING)
        
        code_label = tk.Label(
            code_frame, 
            text="Verification Code", 
            bg="#000000", 
            fg="white", 
            font=self.LABEL_FONT,
            anchor="w"
        )
        code_label.pack(fill="x")
        
        self.entry_code = tk.Entry(code_frame, width=self.ENTRY_WIDTH, font=self.ENTRY_FONT)
        self.entry_code.pack(ipady=self.INPUT_PADDING, pady=5, fill="x")
        
        # New password section
        password_frame = tk.Frame(container, bg="#000000")
        password_frame.pack(fill="x", pady=self.SECTION_PADDING)
        
        password_label = tk.Label(
            password_frame, 
            text="New Password", 
            bg="#000000", 
            fg="white", 
            font=self.LABEL_FONT,
            anchor="w"
        )
        password_label.pack(fill="x")
        
        # Password input with toggle visibility button
        password_input_frame = tk.Frame(password_frame, bg="#000000")
        password_input_frame.pack(fill="x", pady=5)
        
        self.entry_new_password = tk.Entry(
            password_input_frame, 
            show="*", 
            font=self.ENTRY_FONT,
            width=self.ENTRY_WIDTH
        )
        self.entry_new_password.pack(side=tk.LEFT, ipady=self.INPUT_PADDING, fill="x", expand=True)
        
        self.btn_toggle_password = tk.Button(
            password_input_frame, 
            text="🔒", 
            command=self.toggle_password, 
            bg="#000000", 
            fg=self.ORANGE_COLOR, 
            bd=0, 
            font=("Arial", 10),
            width=3,
            cursor="hand2"
        )
        self.btn_toggle_password.pack(side=tk.RIGHT)
        
        # Reset button frame
        reset_frame = tk.Frame(container, bg="#000000")
        reset_frame.pack(fill="x", pady=self.SECTION_PADDING)
        
        reset_button = tk.Button(
            reset_frame, 
            text="Reset Password", 
            command=self.verify_code, 
            bg=self.ORANGE_COLOR, 
            fg="white", 
            font=self.BUTTON_FONT,
            width=self.BUTTON_WIDTH,
            cursor="hand2"
        )
        reset_button.pack(side="left")
        
        # Back to login link
        back_frame = tk.Frame(container, bg="#000000")
        back_frame.pack(fill="x", pady=10)
        
        back_link = tk.Label(
            back_frame,
            text="Back to Login",
            fg=self.ORANGE_COLOR,
            bg="#000000",
            font=("Arial", 10, "underline"),
            cursor="hand2"
        )
        back_link.pack(side="left")
        back_link.bind("<Button-1>", lambda e: self.go_to_login())
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def send_email(self, to_email, subject, message):
        """Send email using Brevo API"""
        url = "https://api.brevo.com/v3/smtp/email"
        
        headers = {
            "accept": "application/json",
            "api-key": self.API_KEY,
            "Content-Type": "application/json"
        }
        
        data = {
            "sender": {"name": "Tourism Info", "email": self.SMTP_USERNAME},
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
    
    def send_verification_code(self):
        """Send verification code to user's email"""
        email = self.entry_email.get().strip()

        if not email:
            messagebox.showerror("Error", "Please enter your email address.")
            return

        try:
            self.cursor.execute("SELECT `email` FROM `user_accounts` WHERE `email` = %s", (email,))
            user = self.cursor.fetchone()
            if not user:
                messagebox.showerror("Error", "Email not found in our records.")
                return

            verification_code = str(random.randint(100000, 999999))
            self.verification_codes[email] = verification_code

            subject = "Your Password Reset Code"
            message = f"Your verification code is: <b>{verification_code}</b>"

            response = self.send_email(email, subject, message)
            
            if "messageId" in response:
                messagebox.showinfo("Success", "Verification code sent to your email.")
            else:
                messagebox.showerror("Error", "Failed to send email. Check API key and settings.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error checking email: {err}")
    
    def verify_code(self):
        """Verify code and reset password"""
        email = self.entry_email.get().strip()
        entered_code = self.entry_code.get().strip()
        new_password = self.entry_new_password.get().strip()

        if not email or not entered_code or not new_password:
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            if email in self.verification_codes and self.verification_codes[email] == entered_code:
                hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                self.cursor.execute("UPDATE `user_accounts` SET `password_hash` = %s WHERE `email` = %s", 
                                  (hashed_password, email))
                self.db.commit()
                messagebox.showinfo("Success", "Password has been reset successfully!")
                self.go_to_login()
            else:
                messagebox.showerror("Error", "Invalid verification code!")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to update password: {err}")
        except Exception as err:
            messagebox.showerror("Error", f"An error occurred: {err}")
    
    def toggle_password(self):
        """Toggle password visibility"""
        if self.entry_new_password.cget('show') == '*':
            self.entry_new_password.config(show='')
            self.btn_toggle_password.config(text='👁️')
        else:
            self.entry_new_password.config(show='*')
            self.btn_toggle_password.config(text='🔒')
    
    def go_to_login(self):
        """Return to login window"""
        if hasattr(self, 'db') and self.db.is_connected():
            self.cursor.close()
            self.db.close()
        self.destroy()
        from login import LoginApp
        login_app = LoginApp()
        login_app.mainloop()
    
    def __del__(self):
        """Clean up resources when object is destroyed"""
        if hasattr(self, 'db') and self.db.is_connected():
            self.cursor.close()
            self.db.close()

if __name__ == "__main__":
    app = Forgot()
    app.mainloop()
import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
import bcrypt
from datetime import datetime

class LoginApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login")
        self.configure(bg="#2c3e50")
        
        # Database connection
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
        
        # UI variables
        self.entry_username = None
        self.entry_password = None
        self.combo_role = None
        self.btn_toggle_password = None
        self.btn_login = None
        
        self.create_widgets()
        self.setup_bindings()
        
    def create_widgets(self):
        # Calculate center position
        window_width = 400
        window_height = 450
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        style = ttk.Style()
        style.configure("TCombobox", padding=5, relief="flat", background="white")

        frame = tk.Frame(self, bg="black", bd=5, relief="ridge")
        frame.place(relx=0.5, rely=0.5, anchor="center", width=350, height=380)

        tk.Label(frame, text="Login", font=("Arial", 18, "bold"), bg="black", fg="cyan").pack(pady=10)

        # Username Entry
        self.entry_username = tk.Entry(frame, font=("Arial", 12), relief="flat", bg="#ecf0f1", fg="gray")
        self.entry_username.pack(pady=10, padx=20, fill="x")
        self.entry_username.insert(0, "Username")
        self.entry_username.bind("<FocusIn>", lambda event: self.clear_placeholder(event, self.entry_username, "Username"))
        self.entry_username.bind("<FocusOut>", lambda event: self.add_placeholder(self.entry_username, "Username"))

        # Password Entry with toggle button
        password_frame = tk.Frame(frame, bg="#ecf0f1")
        password_frame.pack(pady=10, padx=20, fill="x")
        
        self.entry_password = tk.Entry(password_frame, font=("Arial", 12), relief="flat", bg="#ecf0f1", fg="gray")
        self.entry_password.pack(side="left", fill="x", expand=True)
        self.entry_password.insert(0, "Password")
        self.entry_password.bind("<FocusIn>", lambda event: self.clear_placeholder(event, self.entry_password, "Password"))
        self.entry_password.bind("<FocusOut>", lambda event: self.add_placeholder(self.entry_password, "Password"))
        
        # Toggle password button
        self.btn_toggle_password = tk.Button(password_frame, text="👁", font=("Arial", 10), bg="white", fg="gray", 
                                          relief="flat", command=self.toggle_password_visibility, cursor="hand2", width=2,
                                          bd=0, highlightthickness=0, activebackground="white")
        self.btn_toggle_password.pack(side="right", padx=(0, 5))

        # Role Dropdown
        self.combo_role = ttk.Combobox(frame, values=["Admin", "User"], state="readonly", font=("Arial", 12))
        self.combo_role.pack(pady=10, padx=20, fill="x")
        self.combo_role.set("User")  # Default to User role

        # Login Button
        self.btn_login = tk.Button(frame, text="Login", font=("Arial", 12, "bold"), bg="#27ae60", fg="white", 
                                 relief="flat", command=self.login)
        self.btn_login.pack(pady=10, padx=20, fill="x")

        # Register Button
        btn_register = tk.Button(frame, text="Register", font=("Arial", 12, "bold"), bg="#f39c12", fg="white", 
                                relief="flat", command=self.open_register)
        btn_register.pack(pady=5, padx=20, fill="x")

        # Forgot Password Label (Clickable)
        lbl_forgot = tk.Label(frame, text="Forgot Password?", font=("Arial", 12), fg="cyan", bg="black", cursor="hand2")
        lbl_forgot.pack(pady=5)
        lbl_forgot.bind("<Button-1>", self.open_forgot_password)
        lbl_forgot.bind("<Enter>", lambda e: lbl_forgot.config(font=("Arial", 12, "underline")))
        lbl_forgot.bind("<Leave>", lambda e: lbl_forgot.config(font=("Arial", 12)))

    def setup_bindings(self):
        # Key bindings for arrow navigation and Enter to login
        self.bind('<Down>', self.on_arrow_key)
        self.bind('<Up>', self.on_arrow_key)
        self.bind('<Return>', self.login)  # Enter key to login
        self.entry_username.bind('<Return>', lambda e: self.entry_password.focus())
        self.entry_password.bind('<Return>', lambda e: self.combo_role.focus())
        self.combo_role.bind('<Return>', lambda e: self.btn_login.focus())
        self.btn_login.bind('<Return>', self.login)  # Enter key on login button

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def login(self, event=None):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        selected_role = self.combo_role.get().strip().lower()

        try:
            # Fetch user data from the database
            self.cursor.execute("SELECT id, password_hash, role FROM user_accounts WHERE username = %s", (username,))
            result = self.cursor.fetchone()

            if result:
                user_id, stored_hash, db_role = result
                db_role = db_role.strip().lower()

                # Check if password is correct and role matches
                if bcrypt.checkpw(password.encode(), stored_hash.encode()) and db_role == selected_role:
                    # Update last_activity and is_online
                    self.cursor.execute("UPDATE user_accounts SET last_activity = %s, is_online = 1 WHERE id = %s", 
                                      (datetime.now(), user_id))
                    self.db.commit()

                    messagebox.showinfo("Login Successful", f"Welcome, {username} ({db_role.capitalize()})!")
                    self.destroy()

                    # Redirect to the appropriate dashboard
                    if db_role == "admin":
                        from admin_dashboard import AdminDashboard
                        admin_window = AdminDashboard(tk.Tk(), user_id)
                        admin_window.mainloop()
                    else:
                        from user_dashboard import UserDashboard
                        user_window = UserDashboard(tk.Tk(), user_id)
                        user_window.mainloop()
                elif not bcrypt.checkpw(password.encode(), stored_hash.encode()):
                    messagebox.showerror("Login Failed", "Incorrect password!")
                else:
                    messagebox.showerror("Login Failed", f"You don't have {selected_role} privileges!")
            else:
                messagebox.showerror("Login Failed", "User not found!")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error during login: {err}")

    def open_register(self):
        self.destroy()
        from registration import Registration
        register_window = Registration()
        register_window.mainloop()

    def open_forgot_password(self, event=None):
        self.destroy()
        from forgot import Forgot
        forgot_window = Forgot()
        forgot_window.mainloop()

    def toggle_password_visibility(self):
        if self.entry_password.cget('show') == '':
            self.entry_password.config(show='*')
            self.btn_toggle_password.config(text='👁')
        else:
            self.entry_password.config(show='')
            self.btn_toggle_password.config(text='👁')

    def clear_placeholder(self, event, entry, default_text):
        if entry.get() == default_text:
            entry.delete(0, tk.END)
            entry.config(fg="black", show="*" if entry == self.entry_password else "")

    def add_placeholder(self, entry, default_text):
        if entry.get() == "":
            entry.insert(0, default_text)
            entry.config(fg="gray", show="" if entry == self.entry_password else "")

    def on_arrow_key(self, event):
        if event.keysym == 'Down':
            if event.widget == self.entry_username:
                self.entry_password.focus()
            elif event.widget == self.entry_password:
                self.combo_role.focus()
            elif event.widget == self.combo_role:
                self.btn_login.focus()
        elif event.keysym == 'Up':
            if event.widget == self.entry_password:
                self.entry_username.focus()
            elif event.widget == self.combo_role:
                self.entry_password.focus()
            elif event.widget == self.btn_login:
                self.combo_role.focus()

    def on_close(self):
        if hasattr(self, 'db') and self.db.is_connected():
            self.cursor.close()
            self.db.close()
        self.destroy()

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()
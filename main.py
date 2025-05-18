import tkinter as tk
from newsplashscreen import SplashScreen
from login import LoginApp

def main():
    # Create a hidden root window (for splash screen)
    splash_root = tk.Tk()
    splash_root.withdraw()  

    # Show splash screen (pass parent if required)
    splash = SplashScreen(splash_root)  # or SplashScreen(parent=splash_root)

    # After 5 seconds, destroy splash and show login
    splash.after(6000, lambda: open_login(splash_root))
    
    splash_root.mainloop()

def open_login(splash_root):
    # Destroy splash and its root
    splash_root.destroy()  

    # Create LoginApp (as a standalone window)
    login_app = LoginApp()  # No parent if it's tk.Tk()
    login_app.mainloop()

if __name__ == "__main__":
    main()
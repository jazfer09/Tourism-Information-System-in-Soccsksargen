import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import math
import sys
import time

class SplashScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.withdraw()  # Hide until fully initialized
        
        # Window setup
        self.title("Tourism Information System")
        width_of_window = 900
        height_of_window = 650
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_coordinate = (screen_width // 2) - (width_of_window // 2)
        y_coordinate = (screen_height // 2) - (height_of_window // 2)
        self.geometry(f"{width_of_window}x{height_of_window}+{x_coordinate}+{y_coordinate}")
        self.configure(bg='#0a2351')
        self.overrideredirect(True)  # Hide title bar
        self.resizable(False, False)
        
        # Make sure window stays on top
        self.attributes('-topmost', True)
        self.after_idle(self.attributes, '-topmost', False)
        
        # Canvas setup
        self.canvas = tk.Canvas(self, width=width_of_window, height=height_of_window, 
                              bg='#0a2351', highlightthickness=0)
        self.canvas.pack()
        
        # Create background with gradient effect
        self.create_gradient_background(width_of_window, height_of_window)
        
        # Create decorative elements
        self.create_decorative_elements(width_of_window, height_of_window)
        
        # Create main content frame
        self.create_content_frame(width_of_window, height_of_window)
        
        # Text elements
        self.title_string = "Tourism Information System"
        self.subtitle_string = "SOCCSKSARGEN"
        self.title_index = 0
        self.subtitle_index = 0
        
        self.title_text = self.canvas.create_text(width_of_window / 2, 150, text="",
                                                fill="#0a2351", font=('Montserrat', 28, 'bold'))
        self.subtitle_text = self.canvas.create_text(width_of_window / 2, 190, text="", 
                                                   fill="#29b6f6", font=('Montserrat', 18))
        
        # Loading bar
        self.progress = 0
        self.create_loading_bar(width_of_window, height_of_window)
        
        # Credits
        self.create_credits(width_of_window, height_of_window)
        
        # Load logo
        self.logo_img = self.load_image('stratford logo.png', (200, 200))
        self.logo = self.canvas.create_image(width_of_window / 2, 300, image=self.logo_img)
        
        # Animation control variables
        self.animation_running = True
        
        # Start animations
        self.start_animations()
        
        # Show the window after initialization
        self.deiconify()

    def create_gradient_background(self, width, height):
        """Create the gradient background effect"""
        for i in range(height):
            r = int(10 + (20 - 10) * i / height)
            g = int(35 + (74 - 35) * i / height)
            b = int(81 + (150 - 81) * i / height)
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.create_line(0, i, width, i, fill=color)

    def create_decorative_elements(self, width, height):
        """Create the decorative sine wave elements"""
        # Top curved line
        for x in range(0, width, 2):
            y = 50 + 25 * math.sin(x / 100)
            self.canvas.create_oval(x, y, x+3, y+3, fill='#29b6f6', outline='')
        
        # Bottom curved line
        for x in range(0, width, 2):
            y = height - 100 + 25 * math.sin(x / 100 + 2)
            self.canvas.create_oval(x, y, x+3, y+3, fill='#29b6f6', outline='')

    def create_content_frame(self, width, height):
        """Create the main content frame with rounded corners"""
        # Rounded rectangle frame
        self.rounded_rectangle(100, 100, width-100, height-100, 
                             radius=30, fill='#ffffff', outline='')
        
        # Inner rectangle to cover the rounded corners
        self.canvas.create_rectangle(105, 105, width-105, height-105,
                                   fill='#ffffff', outline='')

    def rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        """Draw a rectangle with rounded corners"""
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def create_loading_bar(self, width, height):
        """Create the loading bar elements"""
        self.bar_border = self.canvas.create_rectangle(
            200, height - 170, 700, height - 140, 
            fill="", outline="#29b6f6", width=2
        )
        self.loading_bar = self.canvas.create_rectangle(
            202, height - 168, 202, height - 142, 
            fill="#29b6f6", outline=""
        )
        self.loading_text = self.canvas.create_text(
            width / 2, height - 120, 
            text="Loading 0%", fill="#0a2351", 
            font=('Montserrat', 12)
        )

    def create_credits(self, width, height):
        """Create the credit text elements"""
        self.developer_credit = self.canvas.create_text(
            width / 2, height - 60,
            text="Developed by Jazfer John Emnace",
            fill="#0a2351", font=('Montserrat', 14, 'bold')
        )
        self.copyright_credit = self.canvas.create_text(
            width / 2, height - 35,
            text="© 2025 SOCCSKSARGEN Tourism",
            fill="#0a2351", font=('Montserrat', 12)
        )

    def load_image(self, path, size):
        """Load an image with fallback if not found"""
        try:
            # Handle paths for both development and PyInstaller bundle
            if getattr(sys, 'frozen', False):
                # Running in a bundle (PyInstaller)
                base_path = sys._MEIPASS
            else:
                # Running in normal Python environment
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            full_path = os.path.join(base_path, path)
            
            # Try to load the image
            img = Image.open(full_path)
            img = img.resize(size)
            return ImageTk.PhotoImage(img)
            
        except Exception as e:
            print(f"Warning: {path} not found or error loading image: {e}")
            # Create fallback logo with text
            fallback_img = Image.new('RGB', size, color='#0a2351')
            draw = ImageDraw.Draw(fallback_img)
            
            try:
                # Try to use Montserrat if available
                font_path = os.path.join(base_path, 'Montserrat-Regular.ttf')
                font = ImageFont.truetype(font_path, 18)
            except:
                # Fallback to default font
                font = ImageFont.load_default()
            
            text = "SOCCSKSARGEN\nTOURISM"
            draw.text((size[0]/2, size[1]/2), text, fill="white", 
                     font=font, anchor="mm")
            
            return ImageTk.PhotoImage(fallback_img)

    def start_animations(self):
        """Start all the animations"""
        self.after(500, self.animate_title)
        self.after(1000, self.update_loading)
        self.after(2000, self.animate_credits)
        self.after(3000, self.pulse_logo)

    def animate_title(self):
        """Animate the title text typing effect"""
        if self.title_index <= len(self.title_string) and self.animation_running:
            self.canvas.itemconfig(self.title_text, 
                                 text=self.title_string[:self.title_index])
            self.title_index += 1
            self.after(80, self.animate_title)
        elif self.animation_running:
            self.animate_subtitle()

    def animate_subtitle(self):
        """Animate the subtitle text typing effect"""
        if self.subtitle_index <= len(self.subtitle_string) and self.animation_running:
            self.canvas.itemconfig(self.subtitle_text, 
                                 text=self.subtitle_string[:self.subtitle_index])
            self.subtitle_index += 1
            self.after(80, self.animate_subtitle)

    def update_loading(self):
        """Update the loading bar progress"""
        if self.progress < 100 and self.animation_running:
            self.progress += 1
            bar_width = 496 * (self.progress / 100)
            
            # Update loading bar width
            self.canvas.coords(
                self.loading_bar, 
                202, self.winfo_height() - 168, 
                202 + bar_width, self.winfo_height() - 142
            )
            
            # Update percentage text
            self.canvas.itemconfig(
                self.loading_text, 
                text=f"Loading {self.progress}%"
            )
            
            # Add pulsing effect every 10%
            if self.progress % 10 == 0:
                self.canvas.itemconfig(self.bar_border, outline="#4fc3f7")
                self.after(50, lambda: self.canvas.itemconfig(
                    self.bar_border, outline="#29b6f6"
                ))
            
            # Variable speed for more natural feel
            delay = 30 if self.progress > 80 else (20 if self.progress > 50 else 40)
            self.after(delay, self.update_loading)
        elif self.animation_running:
            self.canvas.itemconfig(
                self.loading_text, 
                text="Launching Application..."
            )
            self.after(500, self.fade_out)

    def animate_credits(self):
        """Animate the credits with fade effect"""
        if not self.animation_running:
            return
            
        # Fade out
        for alpha in range(10, -1, -1):
            if not self.animation_running:
                return
                
            color = f"#{int(10*alpha):02x}{int(35*alpha):02x}{int(81*alpha):02x}"
            self.canvas.itemconfig(self.developer_credit, fill=color)
            self.canvas.itemconfig(self.copyright_credit, fill=color)
            self.update()
            self.after(30)
        
        # Fade in
        for alpha in range(0, 11):
            if not self.animation_running:
                return
                
            color = f"#{int(10*alpha):02x}{int(35*alpha):02x}{int(81*alpha):02x}"
            self.canvas.itemconfig(self.developer_credit, fill=color)
            self.canvas.itemconfig(self.copyright_credit, fill=color)
            self.update()
            self.after(30)
        
        if self.progress < 100 and self.animation_running:
            self.after(3000, self.animate_credits)

    def pulse_logo(self):
        """Create a pulsing animation effect on the logo"""
        if not self.animation_running:
            return
            
        for scale in [1.0, 1.05, 1.1, 1.05, 1.0, 0.95, 0.9, 0.95, 1.0]:
            if not self.animation_running:
                return
                
            self.canvas.scale(
                self.logo, 
                self.winfo_width() / 2, 
                300, 
                scale, 
                scale
            )
            self.update()
            self.after(100)
            
        if self.progress < 90 and self.animation_running:
            self.after(3000, self.pulse_logo)

    def fade_out(self, alpha=1.0):
        """Fade out the splash screen"""
        if alpha > 0 and self.animation_running:
            self.attributes('-alpha', alpha)
            self.after(20, self.fade_out, alpha - 0.025)
        elif self.animation_running:
            self.close_splash()

    def close_splash(self):
        """Clean up and close the splash screen"""
        self.animation_running = False
        self.destroy()
        self.parent.deiconify()  # Show the parent window

    def force_close(self):
        """Force close the splash screen immediately"""
        self.animation_running = False
        self.destroy()
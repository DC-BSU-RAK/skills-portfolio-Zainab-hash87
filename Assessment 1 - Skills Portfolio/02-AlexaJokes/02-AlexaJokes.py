import tkinter as tk
from tkinter import messagebox
import random
import os
import threading
import pygame  # For sound effects

# --- Voice Setup ---
try:
    import pyttsx3
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)
except:
    engine = None

# ==============================================================================
#  CUSTOM IMAGE BUTTON CLASS
# ==============================================================================
class ImageButton(tk.Canvas):
    """
    Creates a button that blends into the design or uses a custom shape/color
    to match the background image positions.
    """
    def __init__(self, parent, text, bg_color, command, width=260, height=55):
        super().__init__(parent, width=width, height=height, bg="#FDF6E3", highlightthickness=0)
        self.command = command
        self.default_color = bg_color
        self.hover_color = self.lighten_color(bg_color)
        self.text_str = text
        
        # We set the background of the canvas to match the beige of your image
        # Adjust "bg" in super().__init__ if your image background isn't exactly #FDF6E3
        
        # Draw Pill Shape
        self.rect = self.create_rounded_rect(5, 5, width-5, height-5, 25, fill=bg_color, outline="black", width=3)
        self.text_id = self.create_text(width/2, height/2, text=text, font=("Comic Sans MS", 14, "bold"), fill="white")
        
        # Bind Events
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = (x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1)
        return self.create_polygon(points, **kwargs, smooth=True)

    def on_click(self, e):
        if self.command: self.command()

    def on_enter(self, e):
        self.itemconfig(self.rect, fill=self.hover_color)

    def on_leave(self, e):
        self.itemconfig(self.rect, fill=self.default_color)

    def lighten_color(self, color):
        if color == "#FF0099": return "#FF66B2" # Pink
        if color == "#FFEB3B": return "#FFF59D" # Yellow
        if color == "#00E5FF": return "#84FFFF" # Cyan
        return color

# ==============================================================================
#  MAIN APPLICATION
# ==============================================================================
class JokeApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # --- Window Config ---
        self.title("Alexa Joke Assistant")
        self.geometry("450x800") # Adjusted for your tall image
        self.resizable(False, False)

        # --- Load Background Image ---
        # We use a Canvas to hold the image and overlay text/buttons
        self.canvas = tk.Canvas(self, width=450, height=800, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        try:
            self.bg_image = tk.PhotoImage(file="background.png")
            self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        except:
            self.canvas.config(bg="pink") # Fallback if image fails
            self.canvas.create_text(225, 400, text="Image Not Found", font=("Arial", 20))

        # --- Setup Audio ---
        pygame.mixer.init()

        # --- Data ---
        self.jokes_list = []
        self.load_jokes()

        # --- UI Elements (Overlay on Canvas) ---
        self.setup_ui_overlays()
        
        # --- Start Interaction ---
        self.speak_threaded("Hi, I am Alexa. Ready to laugh?")

    def setup_ui_overlays(self):
        """Places text and buttons on top of the background image."""
        
        # 1. Setup Text Area (Inside the White Box of your image)
        # Adjust coordinates (x, y) to fit inside the white box of your specific image
        self.setup_text = self.canvas.create_text(225, 300, text="Click 'Tell me a joke'!", 
                                                  width=320, font=("Arial", 16, "bold"), 
                                                  fill="#333", justify="center")
        
        # 2. Punchline Text (Inside the same box, below setup)
        self.punch_text = self.canvas.create_text(225, 400, text="", 
                                                  width=320, font=("Comic Sans MS", 18, "bold"), 
                                                  fill="#FF0099", justify="center")

        # 3. Buttons (Placed over the pink bars in your image)
        # Note: Since your image has pink bars drawn, we can either:
        # A) Place our custom buttons ON TOP of them (easiest for interaction)
        # B) Use transparent rectangles if you just want the image's buttons (harder to click)
        # We will use Custom RoundedButtons that match the style to ensure they are clickable.

        # Button 1: Tell Joke (Pink) - Matches bottom area
        self.btn_tell = ImageButton(self, "Alexa, tell me a joke", "#FF0099", self.tell_joke)
        # Use .place() to position it exactly over the first pink bar in your image
        self.btn_tell_window = self.canvas.create_window(225, 520, window=self.btn_tell) 

        # Button 2: Show Punchline (Yellow) - Initially Hidden
        self.btn_punch = ImageButton(self, "Show Punchline", "#FFEB3B", self.show_punchline)
        # This will replace the first button when needed
        
        # Button 3: Next Joke (Cyan) - Initially Hidden
        self.btn_next = ImageButton(self, "Next Joke", "#00E5FF", self.tell_joke)

        # Quit Button (Small black button at bottom)
        self.btn_quit = tk.Button(self, text="Quit", bg="black", fg="white", 
                                  font=("Arial", 10, "bold"), command=self.quit, relief="flat")
        self.canvas.create_window(225, 750, window=self.btn_quit)

    # ---------------- Logic & Interaction ----------------
    def load_jokes(self):
        try:
            with open("randomJokes.txt", "r", encoding="utf-8") as f:
                self.jokes_list = [l.strip() for l in f if "?" in l]
        except: self.jokes_list = []

    def play_sound(self, file):
        """Plays sound effect safely."""
        try:
            if os.path.exists(file):
                pygame.mixer.Sound(file).play()
        except: pass

    def speak_threaded(self, text):
        """Non-blocking voice."""
        def run():
            if engine:
                engine.say(text)
                engine.runAndWait()
        threading.Thread(target=run, daemon=True).start()

    def tell_joke(self):
        if not self.jokes_list: return
        
        joke = random.choice(self.jokes_list)
        parts = joke.split("?")
        self.current_setup = parts[0] + "?"
        self.current_punchline = parts[1] if len(parts) > 1 else ""

        # Update Text
        self.canvas.itemconfig(self.setup_text, text=self.current_setup)
        self.canvas.itemconfig(self.punch_text, text="")

        # Swap Buttons: Remove Tell/Next -> Show Punchline
        self.canvas.delete(self.btn_tell_window) # Remove current button window
        # Create window for punchline button at same position (520 is approx y for first bar)
        self.btn_tell_window = self.canvas.create_window(225, 520, window=self.btn_punch)
        
        # Fix text color for yellow button visibility
        self.canvas.itemconfig(self.btn_punch.text_id, fill="black")

        self.speak_threaded(self.current_setup)

    def show_punchline(self):
        # Show Text
        self.canvas.itemconfig(self.punch_text, text=self.current_punchline)
        
        # Play Sounds
        self.play_sound("drum.wav")
        self.after(1000, lambda: self.play_sound("laughter.mp3"))

        # Swap Buttons: Remove Punchline -> Show Next
        self.canvas.delete(self.btn_tell_window)
        self.btn_tell_window = self.canvas.create_window(225, 520, window=self.btn_next)
        
        self.speak_threaded(self.current_punchline)

if __name__ == "__main__":
    app = JokeApp()
    app.mainloop()
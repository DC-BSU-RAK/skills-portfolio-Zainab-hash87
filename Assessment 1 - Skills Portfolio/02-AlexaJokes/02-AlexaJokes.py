import tkinter as tk
from tkinter import messagebox
import random
import os
import threading  # To make voice work smoothly without freezing app

# --- Voice Setup ---
try:
    import pyttsx3
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
except:
    engine = None

# ==============================================================================
#  CUSTOM ROUNDED BUTTON CLASS (For that "Mobile App" Look)
# ==============================================================================
class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, color, command, width=300, height=60):
        super().__init__(parent, width=width, height=height, bg="#FDF6E3", highlightthickness=0)
        self.command = command
        self.default_color = color
        self.hover_color = self.lighten_color(color)
        self.text = text
        
        # Draw rounded rectangle
        self.rect = self.create_rounded_rect(5, 5, width-5, height-5, 25, fill=color, outline="black", width=3)
        self.text_id = self.create_text(width/2, height/2, text=text, font=("Comic Sans MS", 14, "bold"), fill="white")
        
        # Bind events for interactivity
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = (x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1)
        return self.create_polygon(points, **kwargs, smooth=True)

    def on_click(self, e):
        if self.command: self.command()

    def on_enter(self, e):
        self.itemconfig(self.rect, fill=self.hover_color) # Interactive Hover

    def on_leave(self, e):
        self.itemconfig(self.rect, fill=self.default_color)

    def lighten_color(self, color):
        # Simple logic to return a lighter hex for hover effect
        if color == "#FF0099": return "#FF66B2" # Pink -> Light Pink
        if color == "#FFEB3B": return "#FFF59D" # Yellow -> Light Yellow
        if color == "#00E5FF": return "#84FFFF" # Cyan -> Light Cyan
        return color

# ==============================================================================
#  MAIN APP
# ==============================================================================
class JokeApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # --- Window Config ---
        self.title("Alexa Joke Assistant")
        self.geometry("450x750")
        self.resizable(False, False)
        self.configure(bg="#FDF6E3") # Beige Background

        # --- Draw Background Grid (Designing via Code) ---
        self.canvas = tk.Canvas(self, width=450, height=750, bg="#FDF6E3", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.draw_grid()

        # --- Data ---
        self.jokes_list = []
        self.load_jokes()

        # --- UI Elements ---
        self.create_header()
        self.create_joke_area()
        self.create_buttons()

    def draw_grid(self):
        """Draws the graph paper lines like in the video."""
        w, h = 450, 750
        for i in range(0, w, 40):
            self.canvas.create_line(i, 0, i, h, fill="#E0D6C2", width=1)
        for j in range(0, h, 40):
            self.canvas.create_line(0, j, w, j, fill="#E0D6C2", width=1)

    def create_header(self):
        """Draws JOKE TIME header manually on canvas."""
        # JOKE (White Box)
        self.canvas.create_rectangle(40, 40, 180, 100, fill="white", outline="black", width=3)
        self.canvas.create_text(110, 70, text="JOKE", font=("Comic Sans MS", 30, "bold"), fill="#FF0099")

        # Question Mark Icon
        self.canvas.create_oval(195, 50, 245, 100, fill="#FFEB3B", outline="black", width=3)
        self.canvas.create_text(220, 75, text="?", font=("Arial", 30, "bold"), fill="black")

        # TIME (Pink Box)
        self.canvas.create_rectangle(260, 40, 400, 100, fill="#FF0099", outline="black", width=3)
        self.canvas.create_text(330, 70, text="TIME", font=("Comic Sans MS", 30, "bold"), fill="white")

    def create_joke_area(self):
        """The white rounded card for text."""
        # Card Background (Rounded Rectangle on Canvas)
        x1, y1, x2, y2 = 30, 140, 420, 450
        r = 20
        points = (x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1)
        self.canvas.create_polygon(points, smooth=True, fill="#FFF0F5", outline="black", width=3)

        # Setup Text
        self.setup_text = self.canvas.create_text(225, 220, text="Ready for fun?", width=350, 
                                                  font=("Arial", 18, "bold"), fill="#333")
        
        # Punchline Text (Hidden)
        self.punch_text = self.canvas.create_text(225, 350, text="", width=350, 
                                                  font=("Comic Sans MS", 20, "bold"), fill="#FF0099")

    def create_buttons(self):
        """Places the custom rounded buttons."""
        # We use place() to put our custom widgets on top of the canvas
        
        # Button 1: Tell Joke
        self.btn_tell = RoundedButton(self, "Alexa, tell me a joke", "#FF0099", self.tell_joke)
        self.btn_tell.place(x=75, y=500)

        # Button 2: Show Punchline (Hidden)
        self.btn_punch = RoundedButton(self, "Show Punchline", "#FFEB3B", self.show_punchline)
        
        # Button 3: Next Joke (Hidden)
        self.btn_next = RoundedButton(self, "Next Joke", "#00E5FF", self.tell_joke)

        # Quit Button
        self.btn_quit = tk.Button(self, text="Quit", bg="black", fg="white", font=("Arial", 10, "bold"), 
                                  command=self.quit, relief="flat")
        self.btn_quit.place(x=200, y=700)

    # ---------------- Logic ----------------
    def load_jokes(self):
        try:
            with open(os.path.join(os.path.dirname(__file__), "randomJokes.txt"), "r", encoding="utf-8") as f:
                self.jokes_list = [l.strip() for l in f if "?" in l]
        except: self.jokes_list = []

    def speak_threaded(self, text):
        """Runs voice in a separate thread to prevent freezing."""
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

        # Update Canvas Text
        self.canvas.itemconfig(self.setup_text, text=self.current_setup)
        self.canvas.itemconfig(self.punch_text, text="")

        # Swap Buttons
        self.btn_tell.place_forget()
        self.btn_next.place_forget()
        self.btn_punch.place(x=75, y=500)
        
        # Fix: Change text color of Punchline button to black for visibility
        self.canvas.itemconfig(self.btn_punch.text_id, fill="black")

        self.speak_threaded(self.current_setup)

    def show_punchline(self):
        self.canvas.itemconfig(self.punch_text, text=self.current_punchline)
        
        self.btn_punch.place_forget()
        self.btn_next.place(x=75, y=500)
        
        self.speak_threaded(self.current_punchline)

if __name__ == "__main__":
    app = JokeApp()
    app.mainloop()
import tkinter as tk
from tkinter import messagebox
import random
import pyttsx3
import pygame
import threading
import time
import os  # For Smart Paths (Fixes Missing File Error)

# --- CUSTOM ROUNDED BUTTON CLASS (Pink Pill Shape) ---
class RoundedButton(tk.Canvas):
    def __init__(self, parent, width, height, corner_radius, padding, color, text, command, text_color="black"):
        tk.Canvas.__init__(self, parent, borderwidth=0, relief="flat", highlightthickness=0, bg="#f0e4d0")
        self.command = command
        self.color = color
        self.width = width
        self.height = height
        self.padding = padding
        self.text = text
        self.corner_radius = corner_radius

        # Resize canvas to fit shadow offset
        self.configure(width=width + padding, height=height + padding)
        
        # Initial Draw
        self.draw_button()

        # Bind mouse events for click effect
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def draw_button(self, offset_x=0, offset_y=0):
        self.delete("all") # Clear previous drawings
        
        # Draw Shadow (Black) - Fixed position
        self.create_polygon(
            self.round_rect(self.padding, self.padding, self.width, self.height, self.corner_radius),
            fill="black", outline="black"
        )
        
        # Draw Main Button (Color) - Moves on click
        self.id = self.create_polygon(
            self.round_rect(offset_x, offset_y, self.width, self.height, self.corner_radius),
            fill=self.color, outline="black", width=2
        )
        
        # Draw Text - Moves with button
        self.text_id = self.create_text(
            self.width/2 + offset_x, 
            self.height/2 + offset_y, 
            text=self.text, 
            fill="white", 
            font=("Comic Sans MS", 12, "bold")
        )

    def round_rect(self, x, y, w, h, r):
        return (x+r, y, x+w-r, y, x+w, y+r, x+w, y+h-r, x+w-r, y+h, x+r, y+h, x, y+h-r, x, y+r)

    def _on_press(self, event):
        # Move visual down to simulate press
        self.draw_button(offset_x=self.padding, offset_y=self.padding)

    def _on_release(self, event):
        # Move visual back up
        self.draw_button(offset_x=0, offset_y=0)
        if self.command:
            self.command()
            
    def change_color(self, new_color):
        self.color = new_color
        self.draw_button()

# --- MAIN APPLICATION CLASS ---
class PopArtJokeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Joke Time")
        self.root.geometry("400x650")
        self.root.resizable(False, False)

        # --- 1. SMART PATH SETUP (The Critical Fix) ---
        # Finds the exact folder where this script is located
        self.base_path = os.path.dirname(os.path.abspath(__file__))

        # --- 2. THEME COLORS ---
        self.bg_color = "#f0e4d0"      # Graph paper beige
        self.btn_color = "#ff4bb5"     # Pop-art Pink
        self.display_bg = "#fffbf0"    # Off-white for text box
        self.grid_color = "#dcd3c2"    # Light lines

        # --- 3. INITIALIZE ENGINES ---
        pygame.mixer.init()
        self.engine = pyttsx3.init()
        try:
            # Try to set a female voice if available
            voices = self.engine.getProperty('voices')
            self.engine.setProperty('voice', voices[1].id) 
        except:
            pass
        self.engine.setProperty('rate', 150)

        # --- 4. BUILD UI (Before loading data to prevent crash) ---
        self.create_background_grid()
        self.setup_ui()

        # --- 5. LOAD RESOURCES ---
        self.check_files() # Print status to terminal
        self.jokes_list = []
        self.current_joke = None
        self.load_jokes()
        
        # Startup Greeting
        threading.Thread(target=self.speak, args=("Welcome to Joke Time!",)).start()

    def get_resource_path(self, filename):
        """Joins the script's folder path with the filename"""
        return os.path.join(self.base_path, filename)

    def check_files(self):
        """Debugs file locations in the terminal"""
        files = ["drum.wav", "laugh.mp3", "laugh-icon.png", "randomJokes.txt"]
        print("\n--- CHECKING FILES ---")
        for f in files:
            full_path = self.get_resource_path(f)
            if os.path.exists(full_path):
                print(f"✅ Found: {f}")
            else:
                print(f"❌ MISSING: {f} (Expected at: {full_path})")
        print("----------------------\n")

        # Set Window Icon
        icon_path = self.get_resource_path("laugh-icon.png")
        if os.path.exists(icon_path):
            try:
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(False, icon)
            except Exception as e:
                print(f"Icon Error: {e}")

    def create_background_grid(self):
        """Draws the graph paper background"""
        self.canvas = tk.Canvas(self.root, width=400, height=650, bg=self.bg_color, highlightthickness=0)
        self.canvas.place(x=0, y=0)
        
        # Draw Grid Lines
        for i in range(0, 400, 30):
            self.canvas.create_line(i, 0, i, 650, fill=self.grid_color)
        for i in range(0, 650, 30):
            self.canvas.create_line(0, i, 400, i, fill=self.grid_color)

    def setup_ui(self):
        # -- TITLE (Shadow Effect) --
        self.canvas.create_text(203, 63, text="JOKE TIME", font=("Impact", 36), fill="black") # Shadow
        self.canvas.create_text(200, 60, text="JOKE TIME", font=("Impact", 36), fill=self.btn_color) # Pink Text

        # -- DISPLAY BOX (Rounded Rectangle) --
        x1, y1, x2, y2 = 40, 130, 360, 330
        radius = 20
        
        # Shadow Box (Black)
        self.round_rectangle(self.canvas, x1+5, y1+5, x2+5, y2+5, radius, fill="black")
        # Main Box (White)
        self.round_rectangle(self.canvas, x1, y1, x2, y2, radius, fill=self.display_bg, outline="black", width=2)

        # Labels inside the box
        self.lbl_setup = tk.Label(self.root, text="Ready to laugh?", font=("Comic Sans MS", 13, "bold"), 
                                  bg=self.display_bg, fg="black", wraplength=280, justify="center")
        self.lbl_setup.place(x=50, y=150, width=300)

        self.lbl_punchline = tk.Label(self.root, text="", font=("Comic Sans MS", 12, "italic"), 
                                      bg=self.display_bg, fg=self.btn_color, wraplength=280, justify="center")
        self.lbl_punchline.place(x=50, y=240, width=300)

        # -- CUSTOM BUTTONS --
        btn_x = 100
        
        self.btn_joke = RoundedButton(self.root, 200, 50, 25, 5, self.btn_color, 
                                      "TELL ME A JOKE", self.tell_joke)
        self.btn_joke.place(x=btn_x, y=360)

        self.btn_punch = RoundedButton(self.root, 200, 50, 25, 5, "#bfbfbf", 
                                       "SHOW PUNCHLINE", self.reveal_punchline)
        self.btn_punch.place(x=btn_x, y=440)

        self.btn_quit = RoundedButton(self.root, 200, 50, 25, 5, self.btn_color, 
                                      "QUIT", self.root.destroy)
        self.btn_quit.place(x=btn_x, y=520)

    # Helper function to draw rounded shapes on canvas
    def round_rectangle(self, canvas, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1,
                  x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2,
                  x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2,
                  x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    def load_jokes(self):
        file_path = self.get_resource_path("randomJokes.txt")
        try:
            with open(file_path, "r") as file:
                lines = file.readlines()
                for line in lines:
                    parts = line.strip().split('?')
                    if len(parts) == 2:
                        self.jokes_list.append(parts)
        except FileNotFoundError:
            self.lbl_setup.config(text="Error: randomJokes.txt missing!\nCheck terminal.")

    def tell_joke(self):
        if not self.jokes_list: return
        
        # Reset UI
        self.lbl_punchline.config(text="")
        self.btn_punch.change_color(self.btn_color) # Enable pink color
        
        # Pick Joke
        self.current_joke = random.choice(self.jokes_list)
        setup_text = self.current_joke[0] + "?"
        
        # Animate & Speak
        self.typewriter_effect(self.lbl_setup, setup_text)
        threading.Thread(target=self.speak, args=(setup_text,)).start()

    def reveal_punchline(self):
        if not self.current_joke: return
        
        # Play Drum
        self.play_sound("drum.wav")
        
        # Show Text
        punch_text = self.current_joke[1]
        self.typewriter_effect(self.lbl_punchline, punch_text)
        
        # Disable button visually (Grey out)
        self.btn_punch.change_color("#bfbfbf")

        # Sequence: Speak -> Laugh
        def audio_sequence():
            self.speak(punch_text)
            time.sleep(0.5)
            self.play_sound("laugh.mp3")
        threading.Thread(target=audio_sequence).start()

    def typewriter_effect(self, widget, text, index=0):
        if index < len(text):
            widget.config(text=text[:index+1])
            self.root.after(30, self.typewriter_effect, widget, text, index+1)
        else:
            widget.config(text=text)

    def speak(self, text):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except: pass

    def play_sound(self, filename):
        file_path = self.get_resource_path(filename)
        if os.path.exists(file_path):
            try:
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
            except Exception as e:
                print(f"Audio Error: {e}")
        else:
            print(f"Audio File Not Found: {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PopArtJokeApp(root)
    root.mainloop()
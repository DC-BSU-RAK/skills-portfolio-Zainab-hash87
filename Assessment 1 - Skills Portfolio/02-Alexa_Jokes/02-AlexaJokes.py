"""
PROGRAMMING SKILLS PORTFOLIO - EXERCISE 2: ALEXA JOKE APP
Student Name: Zainab Afzal
University: Bath Spa University

REFERENCES & ACKNOWLEDGEMENTS:
1. CLASS RESOURCES:
   - GUI Canvas structure & Image handling adapted from Module Lecture Notes.
   - File handling (reading jokes) conforms to class exercises.
   
2. EXTERNAL & AI SUPPORT:
   - Libraries: 'pyttsx3' (TTS) and 'pygame' (Audio) integrated for advanced functionality.
   - Logic: 'threading' for UI responsiveness and 'Typewriter Effect' were 
     refined with the assistance of Generative AI (Google Gemini).
"""


import tkinter as tk                 # Main GUI framework for window management
from tkinter import messagebox       # Displays alert dialogs if needed
import random                        # Handles random selection of jokes/coordinates
import pyttsx3                       # Offline Text-to-Speech conversion engine
import pygame                        # Library used for low-latency audio playback
import threading                     # Manages background threads to prevent UI freezing
import time                          # Provides timing delays for audio synchronization
import os                            # Manages cross-platform file paths and assets
from PIL import Image, ImageTk       # Pillow library for advanced image rendering

class PopArtJokeApp:
    def __init__(self, root):
        """Initializes the main application, UI components, and audio engines."""
        self.root = root
        self.root.title("GiggleByte: Alexa's Joke Box")
        self.root.geometry("400x650") 
        self.root.resizable(False, False)

        # Fix working directory to ensure assets load correctly
        self.base_path = os.path.dirname(os.path.abspath(__file__))

        # --- Audio System Initialization ---
        print("--- AUDIO STATUS ---")
        try:
            pygame.mixer.init()
            print("[OK] Pygame Ready")
        except Exception as e:
            print(f"[ERROR] Pygame Error: {e}")

        # Load Sound Effects
        self.click_fx = None
        click_path = self.get_resource_path("click.mp3")
        if os.path.exists(click_path):
            try:
                self.click_fx = pygame.mixer.Sound(click_path)
                self.click_fx.set_volume(0.4) 
            except: pass

        # --- Text-to-Speech Engine Setup ---
        self.engine = pyttsx3.init()
        try:
            # Attempt to set voice profile to female (Index 1)
            voices = self.engine.getProperty('voices')
            self.engine.setProperty('voice', voices[1].id) 
        except: pass
        self.engine.setProperty('rate', 145) # Set speaking rate

        # --- Application State ---
        self.check_files()
        self.jokes_list = []
        self.current_joke = None
        self.emojis = [] 
        self.btns = {} 
        
        self.prepare_emoji_image()
        self.load_jokes()
        
        # --- UI Construction ---
        self.setup_background() 
        self.setup_text_labels()
        self.setup_buttons() 
        
        # Run intro speech on a separate thread to ensure smooth startup
        threading.Thread(target=self.speak, args=("Hello am Alexa! Are you Ready for some jokes?",)).start()

    def get_resource_path(self, filename):
        """Constructs absolute path to a resource file."""
        return os.path.join(self.base_path, filename)

    def prepare_emoji_image(self):
        """Pre-loads and resizes the emoji image for animation efficiency."""
        icon_path = self.get_resource_path("laugh-icon.png")
        if os.path.exists(icon_path):
            try:
                pil_img = Image.open(icon_path).resize((35, 35), Image.Resampling.LANCZOS)
                self.particle_img = ImageTk.PhotoImage(pil_img)
            except: self.particle_img = None
        else: self.particle_img = None

    def check_files(self):
        """Debug utility: Verifies presence of required asset files."""
        files = ["drum.mp3", "laugh.wav", "bg.png", "randomJokes.txt", "laugh-icon.png", "click.mp3"]
        for f in files:
            path = self.get_resource_path(f)
            # Professional log output
            print(f"{'[FOUND]' if os.path.exists(path) else '[MISSING]'} {f}")
        
        icon = self.get_resource_path("laugh-icon.png")
        if os.path.exists(icon):
            try: self.root.iconphoto(False, tk.PhotoImage(file=icon))
            except: pass

    def setup_background(self):
        """Configures the main Canvas and Background image."""
        self.canvas = tk.Canvas(self.root, width=400, height=650, highlightthickness=0, bg="#f0e4d0")
        self.canvas.pack(fill="both", expand=True)

        img_path = self.get_resource_path("bg.png")
        if os.path.exists(img_path):
            pil_image = Image.open(img_path).resize((400, 650), Image.Resampling.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(pil_image)
            self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw", tags="bg")

    def setup_text_labels(self):
        """Creates text objects for displaying Setup and Punchline."""
        self.text_setup_id = self.canvas.create_text(
            200, 190, text="Ready to laugh?", font=("Comic Sans MS", 15, "bold"), 
            fill="black", width=280, justify="center", anchor="center"
        )
        self.text_punch_id = self.canvas.create_text(
            200, 280, text="", font=("Comic Sans MS", 14, "bold italic"), 
            fill="#ff4bb5", width=280, justify="center", anchor="center"
        )

    def setup_buttons(self):
        """Initializes interactive buttons on the canvas."""
        self.create_canvas_button(100, 400, 200, 55, "#ff4bb5", "TELL ME A JOKE", "joke", self.tell_joke)
        self.create_canvas_button(100, 480, 200, 55, "#bfbfbf", "PUNCHLINE !", "punch", self.reveal_punchline)
        self.create_canvas_button(280, 580, 80, 40, "#ff4bb5", "QUIT", "quit", self.root.destroy, font_size=10)
        self.btns['punch']['state'] = 'disabled'

    def create_canvas_button(self, x, y, w, h, color, text, tag, command, font_size=14):
        """Draws a vector-style button with shadow and binds event handlers."""
        radius = 25
        
        # Draw Shadow & Body
        self.canvas.create_polygon(self.round_rect(x+4, y+4, w, h, radius), fill="black", tags=f"shadow_{tag}")
        poly_id = self.canvas.create_polygon(self.round_rect(x, y, w, h, radius), fill=color, outline="black", width=2, tags=f"poly_{tag}")
        
        # Draw Text
        txt_id = self.canvas.create_text(x + w/2, y + h/2, text=text, fill="white", font=("Impact", font_size), tags=f"text_{tag}")

        self.btns[tag] = {
            'x': x, 'y': y, 'w': w, 'h': h, 'r': radius,
            'color': color, 'text': text, 'command': command,
            'state': 'normal' if color != "#bfbfbf" else 'disabled',
            'pulsing': False, 'pulse_step': 0, 'font_size': font_size,
            'poly_id': poly_id, 'txt_id': txt_id, 'hover_color': "#ff85d5"
        }

        # Bind Interaction Events
        for item in [poly_id, txt_id]:
            self.canvas.tag_bind(item, "<Enter>", lambda e, t=tag: self.on_hover(t, True))
            self.canvas.tag_bind(item, "<Leave>", lambda e, t=tag: self.on_hover(t, False))
            self.canvas.tag_bind(item, "<Button-1>", lambda e, t=tag: self.on_press(t))
            self.canvas.tag_bind(item, "<ButtonRelease-1>", lambda e, t=tag: self.on_release(t))

    def round_rect(self, x, y, w, h, r):
        """Calculates coordinates for rounded rectangles."""
        return (x+r, y, x+w-r, y, x+w, y+r, x+w, y+h-r, x+w-r, y+h, x+r, y+h, x, y+h-r, x, y+r)

    # --- Interaction Handlers ---
    def on_hover(self, tag, entering):
        """Updates button visual state on mouse hover."""
        btn = self.btns[tag]
        if btn['state'] == 'disabled': return
        self.canvas.itemconfig(btn['poly_id'], fill=btn['hover_color'] if entering else btn['color'])

    def on_press(self, tag):
        """Simulates button press depth and plays sound."""
        if self.click_fx: 
            try: self.click_fx.play()
            except: pass
        self.canvas.move(f"poly_{tag}", 2, 2)
        self.canvas.move(f"text_{tag}", 2, 2)

    def on_release(self, tag):
        """Triggers the button command on release."""
        self.canvas.move(f"poly_{tag}", -2, -2)
        self.canvas.move(f"text_{tag}", -2, -2)
        btn = self.btns[tag]
        if btn['state'] != 'disabled' and btn['command']: btn['command']()

    def update_btn_state(self, tag, state, new_text=None):
        """Programmatically updates button enabled/disabled state."""
        btn = self.btns[tag]
        btn['state'] = state
        new_color = "#bfbfbf" if state == 'disabled' else "#ff4bb5"
        if state == 'disabled': self.stop_heartbeat(tag)
        btn['color'] = new_color
        self.canvas.itemconfig(btn['poly_id'], fill=new_color)
        if new_text: self.canvas.itemconfig(btn['txt_id'], text=new_text)

    # --- Animation System ---
    def start_heartbeat(self, tag):
        """Starts the pulsing animation for a specific button."""
        if not self.btns[tag]['pulsing']:
            self.btns[tag]['pulsing'] = True
            self._pulse_frame(tag)

    def stop_heartbeat(self, tag):
        """Stops the pulsing animation."""
        self.btns[tag]['pulsing'] = False
        self.update_visual_scale(tag, 0)

    def _pulse_frame(self, tag):
        """Recursive loop for the pulse effect."""
        if not self.btns[tag]['pulsing']: return
        scale = 2 if self.btns[tag]['pulse_step'] == 0 else 0
        self.update_visual_scale(tag, scale)
        self.btns[tag]['pulse_step'] = 1 - self.btns[tag]['pulse_step']
        self.root.after(600 if scale else 400, lambda: self._pulse_frame(tag))

    def update_visual_scale(self, tag, scale):
        """Redraws button elements to simulate scaling."""
        btn = self.btns[tag]
        new_pts = self.round_rect(btn['x']-scale, btn['y']-scale, btn['w']+scale*2, btn['h']+scale*2, btn['r'])
        self.canvas.coords(btn['poly_id'], *new_pts)
        self.canvas.itemconfig(btn['txt_id'], font=("Impact", btn['font_size'] + scale))

    # --- Core Application Logic ---
    def load_jokes(self):
        """Reads and parses jokes from the text file."""
        try:
            with open(self.get_resource_path("randomJokes.txt"), "r") as file:
                self.jokes_list = [line.strip().split('?') for line in file.readlines() if '?' in line]
        except: self.canvas.itemconfig(self.text_setup_id, text="Error: Jokes missing!")

    def tell_joke(self):
        """Initiates the joke sequence with delayed animation."""
        if not self.jokes_list or self.btns['joke']['state'] == 'disabled': return
        
        self.stop_heartbeat("joke")
        self.canvas.itemconfig(self.text_punch_id, text="") 
        self.update_btn_state("punch", "normal")
        self.update_btn_state("joke", "disabled", "NEXT JOKE")
        
        self.current_joke = random.choice(self.jokes_list)
        setup_text = self.current_joke[0] + "?"
        self.typewriter_effect(self.text_setup_id, setup_text)
        
        # Sequence: Speak -> Wait (Delay) -> Start Animation
        def setup_sequence():
            self.speak(setup_text)
            time.sleep(1.7) # Delay to allow user to read/listen before distracting animation
            self.root.after(0, lambda: self.start_heartbeat("punch"))

        threading.Thread(target=setup_sequence).start()

    def reveal_punchline(self):
        """Delivers the punchline with synchronized audio."""
        if not self.current_joke or self.btns['punch']['state'] == 'disabled': return
        
        punch_text = self.current_joke[1]
        self.update_btn_state("punch", "disabled")
        
        def audio_sequence():
            self.root.after(0, lambda: self.typewriter_effect(self.text_punch_id, punch_text))
            self.speak(punch_text) 
            self.play_sound("drum.mp3")
            time.sleep(1.7)
            self.play_sound("laugh.wav")
            self.root.after(0, self.trigger_laugh_animation)
            self.root.after(0, lambda: self.update_btn_state("joke", "normal"))
            self.root.after(0, lambda: self.start_heartbeat("joke"))
            
        threading.Thread(target=audio_sequence).start()

    # --- Visual Effects ---
    def trigger_laugh_animation(self):
        """Spawns rising emoji particles."""
        for _ in range(27): 
            x, y = random.randint(20, 380), 650 + random.randint(0, 100)
            # Use text emoji as fallback if image fails
            emoji_id = self.canvas.create_image(x, y, image=self.particle_img) if self.particle_img else self.canvas.create_text(x, y, text="😂", font=("Arial", 30))
            self.animate_emoji(emoji_id, random.randint(3, 7))

    def animate_emoji(self, item_id, speed):
        """Recursive loop to move particles upwards."""
        try:
            self.canvas.move(item_id, 0, -speed)
            if self.canvas.coords(item_id)[1] > -50:
                self.root.after(30, lambda: self.animate_emoji(item_id, speed))
            else: self.canvas.delete(item_id)
        except: pass

    def typewriter_effect(self, item_id, text, index=0):
        """Displays text character-by-character."""
        if index < len(text):
            self.canvas.itemconfig(item_id, text=text[:index+1])
            self.root.after(30, lambda: self.typewriter_effect(item_id, text, index+1))
        else: self.canvas.itemconfig(item_id, text=text)

    def speak(self, text):
        """Wraps TTS engine calls."""
        try: self.engine.say(text); self.engine.runAndWait()
        except: pass

    def play_sound(self, filename):
        """Wraps Pygame audio playback."""
        path = self.get_resource_path(filename)
        if os.path.exists(path):
            try: pygame.mixer.music.load(path); pygame.mixer.music.play()
            except: pass

if __name__ == "__main__":
    root = tk.Tk()
    app = PopArtJokeApp(root)
    root.mainloop()
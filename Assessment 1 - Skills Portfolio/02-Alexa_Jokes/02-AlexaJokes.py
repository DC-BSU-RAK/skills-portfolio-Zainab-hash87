import tkinter as tk
from tkinter import messagebox
import random
import pyttsx3
import pygame
import threading
import time
import os
from PIL import Image, ImageTk 

class PopArtJokeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Joke Time")
        self.root.geometry("400x650") 
        self.root.resizable(False, False)

        self.base_path = os.path.dirname(os.path.abspath(__file__))

        # --- AUDIO SETUP ---
        print("--- AUDIO STATUS ---")
        try:
            pygame.mixer.init()
            print("✅ Pygame Mixer Initialized")
        except Exception as e:
            print(f"❌ Pygame Error: {e}")

        # Load Click Sound
        self.click_fx = None
        click_path = self.get_resource_path("click.mp3")
        if os.path.exists(click_path):
            try:
                self.click_fx = pygame.mixer.Sound(click_path)
                self.click_fx.set_volume(0.4) 
            except: pass

        self.engine = pyttsx3.init()
        try:
            voices = self.engine.getProperty('voices')
            self.engine.setProperty('voice', voices[1].id) 
        except: pass
        self.engine.setProperty('rate', 145)

        # --- DATA & STATE ---
        self.check_files()
        self.jokes_list = []
        self.current_joke = None
        self.emojis = [] 
        self.btns = {} # Dictionary to store button IDs for color changing
        self.prepare_emoji_image()
        self.load_jokes()
        
        # --- UI BUILD ---
        self.setup_background() # Draws BG and Buttons directly
        self.setup_text_labels()
        
        # Intro
        threading.Thread(target=self.speak, args=("Hello! Ready to laugh?",)).start()

    def get_resource_path(self, filename):
        return os.path.join(self.base_path, filename)

    def prepare_emoji_image(self):
        icon_path = self.get_resource_path("laugh-icon.png")
        if os.path.exists(icon_path):
            try:
                pil_img = Image.open(icon_path)
                pil_img = pil_img.resize((35, 35), Image.Resampling.LANCZOS)
                self.particle_img = ImageTk.PhotoImage(pil_img)
            except: self.particle_img = None
        else: self.particle_img = None

    def check_files(self):
        files = ["drum.mp3", "laugh.wav", "bg.png", "randomJokes.txt", "laugh-icon.png", "click.mp3"]
        print("\n--- CHECKING FILES ---")
        for f in files:
            path = self.get_resource_path(f)
            print(f"{'✅' if os.path.exists(path) else '❌'} {f}")
        print("----------------------\n")
        
        # Icon
        icon_path = self.get_resource_path("laugh-icon.png")
        if os.path.exists(icon_path):
            try: self.root.iconphoto(False, tk.PhotoImage(file=icon_path))
            except: pass

    def setup_background(self):
        # Single Canvas for EVERYTHING
        self.canvas = tk.Canvas(self.root, width=400, height=650, highlightthickness=0, bg="#f0e4d0")
        self.canvas.pack(fill="both", expand=True)

        # Draw BG Image
        img_path = self.get_resource_path("bg.png")
        if os.path.exists(img_path):
            pil_image = Image.open(img_path)
            pil_image = pil_image.resize((400, 650), Image.Resampling.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(pil_image)
            self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw", tags="bg")
        else:
            self.canvas.create_text(200, 300, text="bg.png MISSING", font=("Arial", 20))

        # Draw Buttons directly on this canvas (Transparent Look)
        self.create_canvas_button(100, 400, 200, 55, "#ff4bb5", "TELL ME A JOKE", "joke", self.tell_joke)
        self.create_canvas_button(100, 480, 200, 55, "#bfbfbf", "SHOW PUNCHLINE", "punch", self.reveal_punchline)
        self.create_canvas_button(280, 580, 80, 40, "#ff4bb5", "QUIT", "quit", self.root.destroy, font_size=10)

    def setup_text_labels(self):
        # Draw Text on top of BG
        self.text_setup_id = self.canvas.create_text(
            200, 190, text="Ready to laugh?", font=("Comic Sans MS", 15, "bold"), 
            fill="black", width=280, justify="center", anchor="center"
        )
        self.text_punch_id = self.canvas.create_text(
            200, 280, text="", font=("Comic Sans MS", 14, "bold italic"), 
            fill="#ff4bb5", width=280, justify="center", anchor="center"
        )

    # --- THE MAGIC BUTTON FUNCTION ---
    def create_canvas_button(self, x, y, w, h, color, text, tag_name, command, font_size=14):
        radius = 25
        padding = 4
        
        # 1. Shadow Polygon
        shadow_pts = self.round_rect(x+padding, y+padding, w, h, radius)
        self.canvas.create_polygon(shadow_pts, fill="black", tags=tag_name)
        
        # 2. Main Button Polygon
        main_pts = self.round_rect(x, y, w, h, radius)
        btn_id = self.canvas.create_polygon(main_pts, fill=color, outline="black", width=2, tags=(tag_name, "btn_shape"))
        
        # 3. Text
        txt_id = self.canvas.create_text(x + w/2, y + h/2, text=text, fill="white", 
                                         font=("Impact", font_size), tags=(tag_name, "btn_text"))

        # Store data for state management
        self.btns[tag_name] = {
            "id": btn_id, "txt_id": txt_id, "color": color, 
            "command": command, "state": "normal" if color != "#bfbfbf" else "disabled",
            "base_x": x, "base_y": y, "w": w, "h": h, "pts": main_pts
        }

        # Bindings
        self.canvas.tag_bind(tag_name, "<Enter>", lambda e: self.on_hover(tag_name, True))
        self.canvas.tag_bind(tag_name, "<Leave>", lambda e: self.on_hover(tag_name, False))
        self.canvas.tag_bind(tag_name, "<Button-1>", lambda e: self.on_click(tag_name))
        self.canvas.tag_bind(tag_name, "<ButtonRelease-1>", lambda e: self.on_release(tag_name))

    def round_rect(self, x, y, w, h, r):
        return (x+r, y, x+w-r, y, x+w, y+r, x+w, y+h-r, x+w-r, y+h, x+r, y+h, x, y+h-r, x, y+r)

    # --- EVENT HANDLERS ---
    def on_hover(self, tag, entering):
        btn = self.btns[tag]
        if btn["state"] == "disabled": return
        color = "#ff85d5" if entering else btn["color"]
        self.canvas.itemconfig(btn["id"], fill=color)

    def on_click(self, tag):
        btn = self.btns[tag]
        # Play sound
        if self.click_fx: 
            try: self.click_fx.play()
            except: pass
            
        # Move Visuals Down
        self.canvas.move(tag, 4, 4) # Moves shadow too, but it looks okay as a "press"
        # Actually we only want to move top layer. 
        # Since tag selects all (shadow+btn), let's refine move:
        # Only move the specific items manually? No, moving group is fine for press effect.

    def on_release(self, tag):
        # Move Visuals Back Up
        self.canvas.move(tag, -4, -4)
        
        btn = self.btns[tag]
        if btn["state"] != "disabled" and btn["command"]:
            btn["command"]()

    def set_btn_state(self, tag, state):
        btn = self.btns[tag]
        btn["state"] = state
        if state == "disabled":
            new_color = "#bfbfbf"
        else:
            new_color = "#ff4bb5" # Default Pink
            
        btn["color"] = new_color
        self.canvas.itemconfig(btn["id"], fill=new_color)

    def set_btn_text(self, tag, text):
        self.canvas.itemconfig(self.btns[tag]["txt_id"], text=text)

    # --- LOGIC ---
    def load_jokes(self):
        try:
            with open(self.get_resource_path("randomJokes.txt"), "r") as file:
                self.jokes_list = [line.strip().split('?') for line in file.readlines() if '?' in line]
        except:
            self.canvas.itemconfig(self.text_setup_id, text="Error: Jokes missing!")

    def tell_joke(self):
        if not self.jokes_list: return
        if self.btns['joke']['state'] == 'disabled': return # Safety check

        self.canvas.itemconfig(self.text_punch_id, text="") 
        
        # Update Button States using new Helper
        self.set_btn_state("punch", "normal")
        self.set_btn_text("joke", "NEXT JOKE")
        self.set_btn_state("joke", "disabled") # Prevent double click
        
        self.current_joke = random.choice(self.jokes_list)
        setup_text = self.current_joke[0] + "?"
        
        self.typewriter_effect(self.text_setup_id, setup_text)
        threading.Thread(target=self.speak, args=(setup_text,)).start()

    def reveal_punchline(self):
        if not self.current_joke: return
        if self.btns['punch']['state'] == 'disabled': return

        punch_text = self.current_joke[1]
        
        self.set_btn_state("punch", "disabled")
        self.set_btn_state("joke", "normal")

        def audio_sequence():
            self.root.after(0, lambda: self.typewriter_effect(self.text_punch_id, punch_text))
            self.speak(punch_text) 
            
            self.play_sound("drum.mp3")
            time.sleep(2.0) 
            
            self.play_sound("laugh.wav")
            self.root.after(0, self.trigger_laugh_animation)

        threading.Thread(target=audio_sequence).start()

    # --- ANIMATION & UTILS ---
    def trigger_laugh_animation(self):
        for _ in range(15): 
            x = random.randint(20, 380)
            y = 650 + random.randint(0, 100)
            speed = random.randint(3, 7)
            
            if self.particle_img:
                emoji_id = self.canvas.create_image(x, y, image=self.particle_img)
            else:
                emoji_id = self.canvas.create_text(x, y, text="😂", font=("Arial", 30))
            self.animate_emoji(emoji_id, speed)

    def animate_emoji(self, item_id, speed):
        try:
            self.canvas.move(item_id, 0, -speed)
            if self.canvas.coords(item_id)[1] > -50:
                self.root.after(30, lambda: self.animate_emoji(item_id, speed))
            else:
                self.canvas.delete(item_id)
        except: pass

    def typewriter_effect(self, item_id, text, index=0):
        if index < len(text):
            self.canvas.itemconfig(item_id, text=text[:index+1])
            self.root.after(30, lambda: self.typewriter_effect(item_id, text, index+1))
        else:
            self.canvas.itemconfig(item_id, text=text)

    def speak(self, text):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except: pass

    def play_sound(self, filename):
        path = self.get_resource_path(filename)
        if os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
            except: pass

if __name__ == "__main__":
    root = tk.Tk()
    app = PopArtJokeApp(root)
    root.mainloop()
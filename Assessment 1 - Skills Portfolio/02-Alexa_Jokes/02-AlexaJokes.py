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
        self.btns = {} # Stores button data for animations
        
        self.prepare_emoji_image()
        self.load_jokes()
        
        # --- UI BUILD ---
        self.setup_background() 
        self.setup_text_labels()
        self.setup_buttons() 
        
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
        
        icon_path = self.get_resource_path("laugh-icon.png")
        if os.path.exists(icon_path):
            try: self.root.iconphoto(False, tk.PhotoImage(file=icon_path))
            except: pass

    def setup_background(self):
        # Single Canvas for EVERYTHING (Transparent effect)
        self.canvas = tk.Canvas(self.root, width=400, height=650, highlightthickness=0, bg="#f0e4d0")
        self.canvas.pack(fill="both", expand=True)

        img_path = self.get_resource_path("bg.png")
        if os.path.exists(img_path):
            pil_image = Image.open(img_path)
            pil_image = pil_image.resize((400, 650), Image.Resampling.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(pil_image)
            self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw", tags="bg")
        else:
            self.canvas.create_text(200, 300, text="bg.png MISSING", font=("Arial", 20))

    def setup_text_labels(self):
        self.text_setup_id = self.canvas.create_text(
            200, 190, text="Ready to laugh?", font=("Comic Sans MS", 15, "bold"), 
            fill="black", width=280, justify="center", anchor="center"
        )
        self.text_punch_id = self.canvas.create_text(
            200, 280, text="", font=("Comic Sans MS", 14, "bold italic"), 
            fill="#ff4bb5", width=280, justify="center", anchor="center"
        )

    def setup_buttons(self):
        # Create persistent buttons
        self.create_canvas_button(100, 400, 200, 55, "#ff4bb5", "TELL ME A JOKE", "joke", self.tell_joke)
        self.create_canvas_button(100, 480, 200, 55, "#bfbfbf", "SHOW PUNCHLINE", "punch", self.reveal_punchline)
        # QUIT Button (Small size restored: width 80)
        self.create_canvas_button(280, 580, 80, 40, "#ff4bb5", "QUIT", "quit", self.root.destroy, font_size=10)
        
        # Set Logic State
        self.btns['punch']['state'] = 'disabled'

    # --- ROBUST CANVAS BUTTON LOGIC ---
    def create_canvas_button(self, x, y, w, h, color, text, tag, command, font_size=14):
        radius = 25
        
        # Draw Shadow (Fixed)
        shadow_pts = self.round_rect(x+4, y+4, w, h, radius)
        self.canvas.create_polygon(shadow_pts, fill="black", outline="black", tags=f"shadow_{tag}")
        
        # Draw Main Body (Dynamic)
        main_pts = self.round_rect(x, y, w, h, radius)
        poly_id = self.canvas.create_polygon(main_pts, fill=color, outline="black", width=2, tags=f"poly_{tag}")
        
        # Draw Text
        txt_id = self.canvas.create_text(
            x + w/2, y + h/2, 
            text=text, fill="white", 
            font=("Impact", font_size), 
            tags=f"text_{tag}"
        )

        # Store Button Data
        self.btns[tag] = {
            'x': x, 'y': y, 'w': w, 'h': h, 'r': radius,
            'color': color, 'text': text, 'command': command,
            'state': 'normal' if color != "#bfbfbf" else 'disabled',
            'pulsing': False, 'pulse_step': 0, 'font_size': font_size,
            'poly_id': poly_id, 'txt_id': txt_id, 'hover_color': "#ff85d5"
        }

        # Bind Events to the POLYGON and TEXT (Not the shadow)
        for item in [poly_id, txt_id]:
            self.canvas.tag_bind(item, "<Enter>", lambda e, t=tag: self.on_hover(t, True))
            self.canvas.tag_bind(item, "<Leave>", lambda e, t=tag: self.on_hover(t, False))
            self.canvas.tag_bind(item, "<Button-1>", lambda e, t=tag: self.on_press(t))
            self.canvas.tag_bind(item, "<ButtonRelease-1>", lambda e, t=tag: self.on_release(t))

    def round_rect(self, x, y, w, h, r):
        return (x+r, y, x+w-r, y, x+w, y+r, x+w, y+h-r, x+w-r, y+h, x+r, y+h, x, y+h-r, x, y+r)

    # --- INTERACTION HANDLERS ---
    def on_hover(self, tag, entering):
        btn = self.btns[tag]
        if btn['state'] == 'disabled': return
        
        target_color = btn['hover_color'] if entering else btn['color']
        self.canvas.itemconfig(btn['poly_id'], fill=target_color)

    def on_press(self, tag):
        # Play Click
        if self.click_fx: 
            try: self.click_fx.play()
            except: pass
            
        # Visual Press (Move down 2px)
        self.canvas.move(f"poly_{tag}", 2, 2)
        self.canvas.move(f"text_{tag}", 2, 2)

    def on_release(self, tag):
        # Visual Release (Move up 2px)
        self.canvas.move(f"poly_{tag}", -2, -2)
        self.canvas.move(f"text_{tag}", -2, -2)
        
        btn = self.btns[tag]
        if btn['state'] != 'disabled' and btn['command']:
            btn['command']()

    # --- STATE MANAGEMENT (Without Deleting) ---
    def update_btn_state(self, tag, state, new_text=None):
        btn = self.btns[tag]
        btn['state'] = state
        
        # Color Update
        if state == 'disabled':
            new_color = "#bfbfbf"
            self.stop_heartbeat(tag)
        else:
            new_color = "#ff4bb5" # Default Pink
        
        btn['color'] = new_color
        self.canvas.itemconfig(btn['poly_id'], fill=new_color)
        
        # Text Update
        if new_text:
            btn['text'] = new_text
            self.canvas.itemconfig(btn['txt_id'], text=new_text)

    # --- ANIMATION ---
    def start_heartbeat(self, tag):
        if not self.btns[tag]['pulsing']:
            self.btns[tag]['pulsing'] = True
            self._pulse_frame(tag)

    def stop_heartbeat(self, tag):
        self.btns[tag]['pulsing'] = False
        # Reset scale visually
        self.update_visual_scale(tag, 0)

    def _pulse_frame(self, tag):
        if not self.btns[tag]['pulsing']: return
        
        if self.btns[tag]['pulse_step'] == 0:
            self.update_visual_scale(tag, 2) # Expand
            self.btns[tag]['pulse_step'] = 1
            delay = 600
        else:
            self.update_visual_scale(tag, 0) # Contract
            self.btns[tag]['pulse_step'] = 0
            delay = 400
            
        self.root.after(delay, lambda: self._pulse_frame(tag))

    def update_visual_scale(self, tag, scale):
        # Updates coordinates to simulate resizing without deleting
        btn = self.btns[tag]
        x, y, w, h, r = btn['x'], btn['y'], btn['w'], btn['h'], btn['r']
        
        # New coords
        new_pts = self.round_rect(x - scale, y - scale, w + (scale*2), h + (scale*2), r)
        self.canvas.coords(btn['poly_id'], *new_pts)
        
        # Update text font size for effect
        self.canvas.itemconfig(btn['txt_id'], font=("Impact", btn['font_size'] + int(scale)))

    # --- LOGIC ---
    def load_jokes(self):
        try:
            with open(self.get_resource_path("randomJokes.txt"), "r") as file:
                self.jokes_list = [line.strip().split('?') for line in file.readlines() if '?' in line]
        except:
            self.canvas.itemconfig(self.text_setup_id, text="Error: Jokes missing!")

    def tell_joke(self):
        if not self.jokes_list: return
        if self.btns['joke']['state'] == 'disabled': return

        self.stop_heartbeat("joke")
        self.canvas.itemconfig(self.text_punch_id, text="") 
        
        self.update_btn_state("punch", "normal")
        self.update_btn_state("joke", "disabled", "NEXT JOKE")
        
        self.current_joke = random.choice(self.jokes_list)
        setup_text = self.current_joke[0] + "?"
        
        self.typewriter_effect(self.text_setup_id, setup_text)
        
        def speech_sequence():
            self.speak(setup_text)
            self.root.after(0, lambda: self.start_heartbeat("punch"))
            
        threading.Thread(target=speech_sequence).start()

    def reveal_punchline(self):
        if not self.current_joke: return
        if self.btns['punch']['state'] == 'disabled': return

        punch_text = self.current_joke[1]
        self.update_btn_state("punch", "disabled")
        
        def audio_sequence():
            self.root.after(0, lambda: self.typewriter_effect(self.text_punch_id, punch_text))
            self.speak(punch_text) 
            
            self.play_sound("drum.mp3")
            time.sleep(1.7) # Fixed Timing: 1.7 seconds
            
            self.play_sound("laugh.wav")
            self.root.after(0, self.trigger_laugh_animation)
            
            self.root.after(0, lambda: self.update_btn_state("joke", "normal"))
            self.root.after(0, lambda: self.start_heartbeat("joke"))

        threading.Thread(target=audio_sequence).start()

    # --- EMOJI ANIMATION ---
    def trigger_laugh_animation(self):
        for _ in range(27): 
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
            try: pygame.mixer.music.load(path); pygame.mixer.music.play()
            except: pass

if __name__ == "__main__":
    root = tk.Tk()
    app = PopArtJokeApp(root)
    root.mainloop()
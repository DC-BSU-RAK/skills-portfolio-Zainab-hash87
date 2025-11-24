import tkinter as tk
from tkinter import messagebox
import random
from PIL import Image, ImageTk, ImageSequence
import pygame
import os

class JokeTellerApp:
    """
    A professional GUI Application for telling jokes.
    Features:
    - Animated GIF background
    - Sound effects (Drum roll & Laughter)
    - Random joke selection from a database
    """
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        
        # --- constants ---
        self.JOKE_FILE = "randomJokes.txt"
        self.BG_FILE = "laugh.gif"  # Your GIF file
        self.SOUND_DRUM = "joke-drum.wav"
        self.SOUND_LAUGH = "laughing.wav"
        
        # --- Initialize Systems ---
        self.init_audio()
        self.jokes = self.load_jokes()
        
        # --- UI Setup ---
        self.setup_background()  # Load GIF background first
        self.create_widgets()    # Then create widgets on top
        
    def setup_window(self):
        """Configures the main window settings and centers it on screen."""
        self.root.title("Alexa Comedy Show")
        
        # App dimensions
        width = 700
        height = 500
        
        # Logic to center the window on your monitor
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_cordinate = int((screen_width/2) - (width/2))
        y_cordinate = int((screen_height/2) - (height/2))
        
        self.root.geometry(f"{width}x{height}+{x_cordinate}+{y_cordinate}")
        self.root.resizable(False, False)

    def init_audio(self):
        """Initialize the Pygame mixer for sound effects."""
        try:
            pygame.mixer.init()
            self.drum_sound = pygame.mixer.Sound(self.SOUND_DRUM) if os.path.exists(self.SOUND_DRUM) else None
            self.laugh_sound = pygame.mixer.Sound(self.SOUND_LAUGH) if os.path.exists(self.SOUND_LAUGH) else None
        except Exception as e:
            print(f"Audio System Error: {e}")
            self.drum_sound = None
            self.laugh_sound = None

    def load_jokes(self):
        """Reads jokes from the text file."""
        if not os.path.exists(self.JOKE_FILE):
            # Fallback jokes if file is missing
            return [
                "Why did the chicken cross the road?To get to the other side.",
                "What happens if you boil a clown?You get a laughing stock.",
                "Why did the car get a flat tire?Because there was a fork in the road!",
                "How did the hipster burn his mouth?He ate his pizza before it was cool.",
                "Why does the golfer wear two pants?Because he's afraid he might get a Hole-in-one."
            ]
        
        with open(self.JOKE_FILE, "r", encoding="utf-8") as f:
            # List comprehension to clean up lines
            return [line.strip() for line in f if line.strip()]

    def setup_background(self):
        """
        Loads an animated GIF and handles the animation loop.
        """
        if os.path.exists(self.BG_FILE):
            try:
                # Open the GIF
                self.gif_image = Image.open(self.BG_FILE)
                
                # Create a list of frames, resized to fit the window
                self.frames = []
                for frame in ImageSequence.Iterator(self.gif_image):
                    frame = frame.resize((700, 500), Image.Resampling.LANCZOS)
                    self.frames.append(ImageTk.PhotoImage(frame))
                
                # Create background label
                self.bg_label = tk.Label(self.root)
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                
                # Start animation
                self.animate(0)
                print("GIF background loaded successfully!")
                
            except Exception as e:
                print(f"Background Error: {e}")
                self.root.configure(bg="#2C3E50")  # Fallback color
        else:
            print(f"GIF file not found: {self.BG_FILE}")
            self.root.configure(bg="#2C3E50")  # Fallback color

    def animate(self, frame_index):
        """Recursive function to update the background frame."""
        if hasattr(self, 'frames') and self.frames:
            current_frame = self.frames[frame_index]
            self.bg_label.configure(image=current_frame)
            
            # Loop to next frame
            next_index = (frame_index + 1) % len(self.frames)
            
            # Speed of animation (milliseconds)
            self.root.after(100, self.animate, next_index)

    def create_widgets(self):
        """Creates the professional GUI elements on top of GIF background."""
        
        # Styles
        TITLE_FONT = ("Arial", 24, "bold")
        BUTTON_FONT = ("Arial", 12, "bold")
        JOKE_FONT = ("Arial", 13)
        PUNCHLINE_FONT = ("Arial", 12, "italic")
        
        # Main Container with semi-transparent effect
        main_frame = tk.Frame(self.root, bg="white", bd=3, relief="ridge")
        main_frame.place(relx=0.5, rely=0.5, anchor="center", width=650, height=400)

        # Header Section
        header_frame = tk.Frame(main_frame, bg="#1ABC9C", height=80)
        header_frame.pack(fill="x", padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🎭 ALEXA COMEDY SHOW 🎤", 
                 font=TITLE_FONT, bg="#1ABC9C", fg="white").pack(expand=True)

        # Joke Display Area
        joke_frame = tk.Frame(main_frame, bg="#ECF0F1", relief="sunken", bd=2)
        joke_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Setup Label
        self.setup_label = tk.Label(joke_frame, 
                                   text="Click 'Tell Joke' to start the fun! 😄", 
                                   font=JOKE_FONT, 
                                   bg="#ECF0F1", 
                                   fg="#2C3E50", 
                                   wraplength=550,
                                   justify="center",
                                   pady=20)
        self.setup_label.pack(pady=15)

        # Punchline Label
        self.punchline_label = tk.Label(joke_frame, 
                                       text="", 
                                       font=PUNCHLINE_FONT, 
                                       bg="#ECF0F1", 
                                       fg="#E74C3C", 
                                       wraplength=550,
                                       justify="center",
                                       pady=15)
        self.punchline_label.pack(pady=10)

        # Button Container
        btn_frame = tk.Frame(main_frame, bg="#34495E")
        btn_frame.pack(side="bottom", pady=20)

        # Button Styles
        button_style = {
            'font': BUTTON_FONT,
            'width': 12,
            'height': 1,
            'relief': "raised",
            'bd': 3,
            'cursor': "hand2"
        }

        # Tell Joke Button
        self.btn_joke = tk.Button(btn_frame, 
                                 text="🎯 TELL JOKE", 
                                 bg="#3498DB", 
                                 fg="white",
                                 command=self.tell_joke,
                                 **button_style)
        self.btn_joke.grid(row=0, column=0, padx=8)

        # Show Punchline Button
        self.btn_punchline = tk.Button(btn_frame, 
                                      text="🤣 SHOW ANSWER", 
                                      bg="#F39C12", 
                                      fg="white",
                                      state="disabled",
                                      command=self.show_punchline,
                                      **button_style)
        self.btn_punchline.grid(row=0, column=1, padx=8)

        # Next Joke Button
        self.btn_next = tk.Button(btn_frame, 
                                 text="🔄 NEXT JOKE", 
                                 bg="#27AE60", 
                                 fg="white",
                                 state="disabled",
                                 command=self.next_joke,
                                 **button_style)
        self.btn_next.grid(row=0, column=2, padx=8)

        # Quit Button
        self.btn_quit = tk.Button(btn_frame, 
                                 text="🚪 EXIT", 
                                 bg="#E74C3C", 
                                 fg="white",
                                 command=self.root.quit,
                                 **button_style)
        self.btn_quit.grid(row=0, column=3, padx=8)

        # Status Bar
        status_frame = tk.Frame(main_frame, bg="#2C3E50", height=25)
        status_frame.pack(side="bottom", fill="x")
        status_frame.pack_propagate(False)
        
        joke_count = len(self.jokes)
        status_text = f"📊 Jokes Available: {joke_count} | 🔊 Sound: {'ON' if self.drum_sound or self.laugh_sound else 'OFF'}"
        tk.Label(status_frame, text=status_text, 
                font=("Arial", 8), 
                bg="#2C3E50", fg="white").pack(pady=3)

    def tell_joke(self):
        """Logic to pick a joke and show the setup."""
        if not self.jokes:
            self.setup_label.config(text="❌ No jokes available!")
            return
            
        joke_text = random.choice(self.jokes)
        
        # Reset labels
        self.punchline_label.config(text="")
        
        # Parse Setup vs Punchline
        if "?" in joke_text:
            parts = joke_text.split("?")
            self.current_setup = parts[0] + "?"
            self.current_punchline = parts[1].strip()
        else:
            self.current_setup = joke_text
            self.current_punchline = "No punchline available"

        # Update UI
        self.setup_label.config(text=self.current_setup)
        self.btn_punchline.config(state="normal", bg="#E67E22")
        self.btn_next.config(state="normal", bg="#27AE60")
        self.btn_joke.config(state="disabled", bg="#7FB3D5")
        
        # Play Drum Sound
        if self.drum_sound:
            try:
                self.drum_sound.play()
            except:
                pass

    def show_punchline(self):
        """Logic to show the punchline and play laugh."""
        self.punchline_label.config(text=self.current_punchline)
        self.btn_punchline.config(state="disabled", bg="#F39C12")
        
        # Play Laugh Sound
        if self.laugh_sound:
            try:
                self.laugh_sound.play()
            except:
                pass

    def next_joke(self):
        """Reset for next joke"""
        self.setup_label.config(text="Ready for the next joke! Click 'Tell Joke'")
        self.punchline_label.config(text="")
        self.btn_punchline.config(state="disabled", bg="#F39C12")
        self.btn_next.config(state="disabled", bg="#7FB3D5")
        self.btn_joke.config(state="normal", bg="#3498DB")

if __name__ == "__main__":
    # Create main window
    root = tk.Tk()
    
    # Initialize App
    app = JokeTellerApp(root)
    
    # Run Main Loop
    root.mainloop()
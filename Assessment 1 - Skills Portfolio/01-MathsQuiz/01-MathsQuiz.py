"""
PROGRAMMING SKILLS PORTFOLIO - EXERCISE 1: MATH QUIZ
-----------------------------------------------

REFERENCES & ACKNOWLEDGEMENTS:
1. CLASS RESOURCES:
   - GUI structure & JSON handling adapted from Module Lecture Notes.
   
2. EXTERNAL & AI SUPPORT:
   - Pygame Library: Integrated for background music and sound effects.
   - Pillow Library: Used for image rendering on Canvas.
   - Animations: Logic for 'Confetti' and 'Slide Transitions' refined with 
     assistance from Generative AI (Google Gemini).
"""

import tkinter as tk      # Standard GUI library for windows and widgets
from tkinter import messagebox  # For displaying alert pop-ups
from PIL import Image, ImageTk  # Pillow library for handling .png/.jpg assets
import pygame             # Used for background music and sound effects (SFX)
import time               # Required for time-based logic (though .after() is preferred in GUI)
import random             # Generates random numbers for math problems
import json               # Handles reading/writing leaderboard data
import os                 # Used for dynamic file path handling

# --- ENVIRONMENT SETUP ---
# Ensures the script looks for assets (images/audio) in the same folder as the .py file
script_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_directory)

# --- MAIN CONTROLLER ---
class MathQuizApp(tk.Tk):
    """
    The main application class inheriting from tk.Tk.
    It acts as the 'Controller' managing shared data and page navigation.
    """
    def __init__(self):
        super().__init__()
        self.title("Brain Brawl: Arithmetic Quiz")
        self.geometry("1200x680")
        self.resizable(False, False) # Locks window size to prevent layout distortion
        
        # Set window icon if available
        try:
            self.iconphoto(False, tk.PhotoImage(file="root-icon.png"))
        except: pass

        # Initialize Audio Mixer
        pygame.mixer.init()
        self.clock_channel = None # Dedicated channel for ticking sound

        # Global Game State Variables
        self.user_name = "Player"
        self.difficulty = 1
        self.score = 0
        self.attempts_left = 2
        self.current_question_num = 0
        
        # Stats Tracking for Final Results
        self.total_correct = 0 
        self.total_wrong = 0

        # Main container frame that holds all page layouts
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        self.frames = {} # Dictionary to store all page objects
        
        # Initialize all pages and stack them
        for F in (WelcomePage, InstructionPage, NamePage, DifficultyPage, QuizPage, ResultPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.place(x=0, y=0, width=1200, height=700)

        # Start at Welcome Page
        self.show_frame("WelcomePage", instant=True)
        self.play_bg_music()

    def show_frame(self, page_name, instant=False):
        """Raises a frame to the top. Optional 'instant' flag skips animation."""
        frame = self.frames[page_name]
        frame.tkraise()
        if instant:
            frame.place(x=0, y=0, width=1200, height=700)
        else:
            # Prepare frame off-screen (right side) for sliding effect
            frame.place(x=1200, y=0, width=1200, height=700) 
            self.slide_animation(frame, 1200)

    def slide_animation(self, frame, current_x):
        """Recursive function to animate frame sliding from right to left."""
        if current_x > 0:
            new_x = current_x - 45 # Speed of slide
            frame.place(x=new_x, y=0)
            self.after(10, lambda: self.slide_animation(frame, new_x))
        else:
            frame.place(x=0, y=0) # Lock in place

    def play_bg_music(self):
        """Loops the background music indefinitely."""
        try:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load("welcome.mp3")
                pygame.mixer.music.play(-1) # -1 means loop forever
                pygame.mixer.music.set_volume(0.4)
        except: pass

    def play_sfx(self, file):
        """Plays a one-shot sound effect."""
        try:
            sfx = pygame.mixer.Sound(file)
            sfx.set_volume(1.0)
            sfx.play()
        except: pass

    def stop_all_sounds(self):
        """Stops all audio (used when game ends)."""
        pygame.mixer.music.stop()
        pygame.mixer.stop()

# --- BASE PAGE CLASS ---
class BasePage(tk.Frame):
    """
    Parent class for all pages. 
    Reduces code repetition by setting up the Canvas and common button effects.
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        # Canvas allows for placing images and text at specific x,y coordinates
        self.canvas = tk.Canvas(self, width=1200, height=700)
        self.canvas.pack(fill="both", expand=True)
        
    def add_button_effects(self, btn):
        """Adds hover (highlight) and click (sound) effects to buttons."""
        original_color = btn['bg']
        highlight_color = "#7d4e4e"
        
        def on_enter(e):
            if btn['bg'] != "#FFD700": btn['background'] = highlight_color
        def on_leave(e):
            if btn['bg'] != "#FFD700": btn['background'] = original_color
        def on_click(e):
            self.controller.play_sfx("button_press.mp3")
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<Button-1>", on_click, add="+")

# --- INDIVIDUAL PAGES ---

class WelcomePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        # Load Background Image
        try:
            self.bg_img = ImageTk.PhotoImage(Image.open("01-welcome.png").resize((1200, 700)))
            self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")
        except: self.canvas.config(bg="#452929") # Fallback color

        # Start Button
        self.start_btn = tk.Button(self, text="Let's Begin →", font=("Comic Sans MS", 24, "bold"), 
                                   bg="#452929", fg="white", cursor="hand2", 
                                   command=lambda: controller.show_frame("InstructionPage"))
        self.add_button_effects(self.start_btn)
        
        # Place button off-screen initially for animation
        self.btn_window = self.canvas.create_window(600, 720, window=self.start_btn)
        self.animate_button_entry(720)

    def animate_button_entry(self, y_pos):
        """Animates the start button rising from the bottom."""
        if y_pos > 580:
            y_pos -= 5
            self.canvas.coords(self.btn_window, 600, y_pos)
            self.after(10, lambda: self.animate_button_entry(y_pos))

class InstructionPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        try:
            self.bg_img = ImageTk.PhotoImage(Image.open("02-instruction.png").resize((1200, 700)))
            self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")
        except: self.canvas.config(bg="black")

        # Static text instructions using Canvas text for transparency support
        font_inst = ("Comic Sans MS", 18, "bold")
        self.canvas.create_text(342, 355, text="•10 questions per round\n•10 points-1st try correct\n•5 points-2nd try correct", font=font_inst, fill="white", justify="center")
        self.canvas.create_text(608, 512, text=" • Easy-1 digit numbers\n• Moderate-2 digits\n• Advanced-4 digits", font=font_inst, fill="white", justify="center")
        self.canvas.create_text(890, 360, text="• Choose difficulty level\n• Solve math problems\n• Type your answer", font=font_inst, fill="white", justify="center")

        next_btn = tk.Button(self, text="Next →", font=("Comic Sans MS", 22, "bold"), bg="#452929", fg="white", 
                             cursor="hand2", command=lambda: controller.show_frame("NamePage"))
        self.canvas.create_window(1015, 597, window=next_btn)
        self.add_button_effects(next_btn)

class NamePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        try:
            self.bg_img = ImageTk.PhotoImage(Image.open("03-name.png").resize((1200, 700)))
            self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")
        except: self.canvas.config(bg="black")

        self.name_entry = tk.Entry(self, font=("Arial", 24), width=20, justify="center")
        self.canvas.create_window(600, 350, window=self.name_entry)

        # Navigation Buttons
        back_btn = tk.Button(self, text="← Back", font=("Comic Sans MS", 18, "bold"), bg="#5a2c2c", fg="white", 
                             cursor="hand2", command=lambda: controller.show_frame("InstructionPage"))
        next_btn = tk.Button(self, text="Next →", font=("Comic Sans MS", 18, "bold"), bg="#3b5a2c", fg="white", 
                             cursor="hand2", command=self.save_name_and_next)
        
        self.canvas.create_window(450, 450, window=back_btn)
        self.canvas.create_window(750, 450, window=next_btn)
        self.add_button_effects(back_btn)
        self.add_button_effects(next_btn)

    def save_name_and_next(self):
        """Validates input to ensure name is not empty."""
        typed = self.name_entry.get().strip()
        if typed == "":
            messagebox.showwarning("Name Required", "Please enter your name!")
            return
        self.controller.user_name = typed
        self.controller.show_frame("DifficultyPage")

class DifficultyPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        try:
            self.bg_img = ImageTk.PhotoImage(Image.open("04-Difficulty.png").resize((1200, 700)))
            self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")
        except: self.canvas.config(bg="black")

        # Buttons for selecting level
        btn_font = ("Comic Sans MS", 22, "bold")
        btn_easy = tk.Button(self, text="Easy (1 digit)", font=btn_font, bg="#452929", fg="white", width=15, 
                             cursor="hand2", command=lambda: self.start_game(1))
        btn_mod = tk.Button(self, text="Moderate (2 digits)", font=btn_font, bg="#452929", fg="white", width=15, 
                            cursor="hand2", command=lambda: self.start_game(2))
        btn_adv = tk.Button(self, text="Advanced (4 digits)", font=btn_font, bg="#452929", fg="white", width=15, 
                            cursor="hand2", command=lambda: self.start_game(3))
        
        self.canvas.create_window(360, 320, window=btn_easy)
        self.canvas.create_window(510, 420, window=btn_mod)
        self.canvas.create_window(690, 510, window=btn_adv)
        
        back_btn = tk.Button(self, text="← Back", font=("Comic Sans MS", 16, "bold"), bg="#5a2c2c", fg="white", 
                             width=10, cursor="hand2", command=lambda: controller.show_frame("NamePage"))
        self.canvas.create_window(180, 612, window=back_btn)
        for b in [btn_easy, btn_mod, btn_adv, back_btn]: self.add_button_effects(b)

    def start_game(self, level):
        """Resets all scoring variables and starts the Quiz."""
        self.controller.difficulty = level
        self.controller.score = 0
        self.controller.current_question_num = 0
        self.controller.total_correct = 0
        self.controller.total_wrong = 0
        # Trigger the setup for the first question
        self.controller.frames["QuizPage"].start_new_game()
        self.controller.show_frame("QuizPage")

class QuizPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        try:
            self.bg_img = ImageTk.PhotoImage(Image.open("05-quiz.png").resize((1200, 700)))
            self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")
        except: self.canvas.config(bg="#4d8c57")

        self.timer_running = False
        self.timer_seconds = 12
        self.correct_answer = 0

        # Create text placeholders (IDs used for updates later)
        self.id_heading = self.canvas.create_text(590, 129, text="Question 1 / 10", font=("Comic Sans MS", 24, "bold"), fill="#452929")
        self.id_score = self.canvas.create_text(200, 110, text="Score: 0", font=("Comic Sans MS", 22, "bold"), fill="white")
        self.id_timer = self.canvas.create_text(990, 112, text="Time: 12s", font=("Comic Sans MS", 22, "bold"), fill="white")
        self.id_main_q = self.canvas.create_text(600, 320, text="Ready?", font=("Comic Sans MS", 50, "bold"), fill="white")
        self.id_hint = self.canvas.create_text(569, 260, text="", font=("Arial", 16, "italic"), fill="#FFD700")
        self.id_feedback = self.canvas.create_text(593, 500, text="", font=("Arial", 18, "bold"), fill="white")

        self.entry_answer = tk.Entry(self, font=("Arial", 30), width=12, justify="center")
        self.entry_answer.place(x=425, y=400, width=300, height=60)

        # Game control buttons
        btn_hint = tk.Button(self, text=" Hint", font=("Arial", 12, "bold"), bg="#FFD700", fg="black", cursor="hand2", command=self.show_hint)
        btn_submit = tk.Button(self, text="Submit", font=("Comic Sans MS", 20, "bold"), width=10, bg="#3b5a2c", fg="white", cursor="hand2", command=self.check_answer)
        btn_back = tk.Button(self, text="← Back", font=("Comic Sans MS", 16, "bold"), bg="#5a2c2c", fg="white", width=8, cursor="hand2", command=self.go_back)

        self.canvas.create_window(790, 430, window=btn_hint)
        self.canvas.create_window(580, 576, window=btn_submit)
        self.canvas.create_window(180, 595, window=btn_back) 
        
        self.add_button_effects(btn_hint)
        self.add_button_effects(btn_submit)
        self.add_button_effects(btn_back)
        # Allow pressing 'Enter' key to submit
        self.entry_answer.bind('<Return>', lambda event: self.check_answer())

    def start_new_game(self):
        """Reset question counter and start."""
        self.controller.current_question_num = 0
        self.next_question()

    def go_back(self):
        """Abort game and return to menu."""
        self.timer_running = False
        self.stop_clock_sound()
        self.controller.show_frame("DifficultyPage")

    def stop_clock_sound(self):
        """Helper to silence the ticking clock."""
        if self.controller.clock_channel and self.controller.clock_channel.get_busy():
            self.controller.clock_channel.stop()

    def next_question(self):
        """Generates logic for the next question based on difficulty."""
        self.stop_clock_sound()
        if self.controller.current_question_num < 10:
            self.controller.current_question_num += 1
            self.controller.attempts_left = 2
            self.timer_seconds = 12
            self.timer_running = True

            # Difficulty Logic
            dif = self.controller.difficulty
            if dif == 1: num1, num2 = random.randint(1, 9), random.randint(1, 9)
            elif dif == 2: num1, num2 = random.randint(10, 99), random.randint(10, 99)
            else: num1, num2 = random.randint(1000, 9999), random.randint(1000, 9999)

            op = random.choice(["+", "-"])
            if op == "+":
                self.correct_answer = num1 + num2
                q_text = f"{num1} + {num2} = ?"
            else:
                # Ensure subtraction doesn't result in negatives for simplicity
                if num1 < num2: num1, num2 = num2, num1 
                self.correct_answer = num1 - num2
                q_text = f"{num1} - {num2} = ?"

            # Update UI elements
            self.canvas.itemconfigure(self.id_heading, text=f"Question {self.controller.current_question_num} / 10")
            self.canvas.itemconfigure(self.id_main_q, text=q_text)
            self.canvas.itemconfigure(self.id_score, text=f"Score: {self.controller.score}")
            self.canvas.itemconfigure(self.id_hint, text="")
            self.canvas.itemconfigure(self.id_feedback, text="")
            
            self.entry_answer.delete(0, tk.END)
            self.entry_answer.config(bg="white")
            self.entry_answer.focus()
            self.countdown_timer()
        else:
            # Game Over Sequence
            self.timer_running = False
            self.stop_clock_sound()
            self.controller.stop_all_sounds()
            self.controller.play_sfx("gameover.mp3")
            self.after(1000, self.go_to_results)

    def countdown_timer(self):
        """Recursive timer function decrementing every 1 second."""
        if self.timer_running:
            if self.timer_seconds > 0:
                # Turn text red and play sound if 5 seconds remaining
                fg_color = "#D62E2E" if self.timer_seconds <= 5 else "white"
                if self.timer_seconds == 5:
                    try:
                        clock_sound = pygame.mixer.Sound("clock.wav")
                        self.controller.clock_channel = clock_sound.play()
                    except: pass
                self.canvas.itemconfigure(self.id_timer, text=f"Time: {self.timer_seconds}s", fill=fg_color)
                self.timer_seconds -= 1
                self.after(1000, self.countdown_timer)
            else:
                # Time Expired Logic
                self.timer_running = False
                self.stop_clock_sound()
                self.controller.total_wrong += 1
                self.canvas.itemconfigure(self.id_timer, text="Time's Up!", fill="red")
                self.controller.play_sfx("wrong.mp3")
                self.canvas.itemconfigure(self.id_feedback, text="Time Up! Moving on...", fill="orange")
                self.after(2000, self.next_question)

    def check_answer(self):
        """Validates user input and updates score."""
        user_input = self.entry_answer.get()
        if not user_input.strip(): return
        try:
            user_ans = int(user_input)
        except ValueError:
            self.canvas.itemconfigure(self.id_feedback, text="Numbers only please!", fill="yellow")
            return

        if user_ans == self.correct_answer:
            self.timer_running = False
            self.stop_clock_sound()
            self.controller.play_sfx("correct.mp3")
            self.flash_board("lightgreen")
            self.controller.total_correct += 1
            
            # Scoring: 10 pts for 1st try, 5 pts for 2nd try
            points = 10 if self.controller.attempts_left == 2 else 5
            self.controller.score += points
            self.canvas.itemconfigure(self.id_feedback, text=f"Awesome! +{points} Points", fill="#00FF00")
            self.canvas.itemconfigure(self.id_score, text=f"Score: {self.controller.score}")
            self.after(1500, self.next_question)
        else:
            self.controller.attempts_left -= 1
            self.controller.play_sfx("wrong.mp3")
            self.shake_entry()
            
            if self.controller.attempts_left > 0:
                self.canvas.itemconfigure(self.id_feedback, text="Wrong! Try Again (+5 pts left)", fill="#D62E2E")
                self.entry_answer.delete(0, tk.END)
            else:
                self.timer_running = False
                self.stop_clock_sound()
                self.controller.total_wrong += 1
                self.canvas.itemconfigure(self.id_feedback, text=f"Wrong! Answer was {self.correct_answer}", fill="#D62E2E")
                self.after(2000, self.next_question)

    def show_hint(self):
        """Displays simple parity hint."""
        if self.correct_answer % 2 == 0: hint_msg = "Hint: Answer is EVEN"
        else: hint_msg = "Hint: Answer is ODD"
        self.canvas.itemconfigure(self.id_hint, text=hint_msg, fill="#FFD700")

    def shake_entry(self):
        """Visual feedback: Shakes the input box left/right on wrong answer."""
        original_x = 425
        offsets = [-10, 10, -8, 8, -5, 5, 0]
        delay = 50
        for offset in offsets:
            self.entry_answer.after(delay, lambda o=offset: self.entry_answer.place(x=original_x + o))
            delay += 50
        self.entry_answer.config(bg="#ffcccc")
        self.entry_answer.after(500, lambda: self.entry_answer.config(bg="white"))

    def flash_board(self, color):
        """Visual feedback: Flashes the screen briefly on correct answer."""
        try:
            flash = self.canvas.create_rectangle(0,0,1200,700, fill=color, stipple="gray50")
            self.update()
            time.sleep(0.2)
            self.canvas.delete(flash)
        except: pass

    def go_to_results(self):
        """Transitions to the final scoreboard."""
        self.controller.frames["ResultPage"].show_results()
        self.controller.show_frame("ResultPage")

class ResultPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.confetti_particles = []
        
        try:
            self.bg_img = ImageTk.PhotoImage(Image.open("06-results.png").resize((1200, 700)))
            self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")
        except: self.canvas.config(bg="#1a3a2a")

        # Layout for the results box
        frame_width, frame_height = 560, 400 
        frame_x = (1210 - frame_width) // 2
        frame_y = (740 - frame_height) // 2 + 20
        center_x = frame_x + frame_width // 2

        self.canvas.create_rectangle(frame_x, frame_y, frame_x+frame_width, frame_y+frame_height, 
                                     fill="#2d5a3d", outline="#F3EFD8", width=3)

        self.id_rank = self.canvas.create_text(center_x, frame_y + 50, text="", font=("Comic Sans MS", 28, "bold"), fill="#F3E08A")
        self.id_final_score = self.canvas.create_text(center_x, frame_y + 110, text="", font=("Comic Sans MS", 24, "bold"), fill="white")
        self.id_grade = self.canvas.create_text(center_x, frame_y + 160, text="", font=("Comic Sans MS", 22, "bold"), fill="#F8E88B")
        
        # Correct/Wrong Stats display
        self.id_stats = self.canvas.create_text(center_x, frame_y + 210, text="", font=("Comic Sans MS", 18, "bold"), fill="white")
        
        # Leaderboard display
        self.id_leaderboard = self.canvas.create_text(center_x, frame_y + 320, text="", font=("Arial", 14, "bold"), fill="white", justify="center")

        # Control Buttons
        btn_play = tk.Button(self, text="Play Again ↻", font=("Comic Sans MS", 16, "bold"), bg="#3b5a2c", fg="white", 
                             width=11, cursor="hand2", command=lambda: controller.show_frame("DifficultyPage"))
        btn_exit = tk.Button(self, text="Exit ✕", font=("Comic Sans MS", 16, "bold"), bg="#8b0000", fg="white", 
                             width=9, cursor="hand2", command=controller.quit)
        
        self.canvas.create_window(402, 565, window=btn_play)
        self.canvas.create_window(820, 565, window=btn_exit)
        self.add_button_effects(btn_play)
        self.add_button_effects(btn_exit)

    def show_results(self):
        """Calculates final grade, saves score, and triggers celebrations."""
        score = self.controller.score
        correct = self.controller.total_correct
        wrong = self.controller.total_wrong
        
        # Grading Logic
        if score >= 90:
            grade, color, msg = "A+ (Math Wizard)", "#FFD700", f"Outstanding, {self.controller.user_name}!"
            self.controller.play_sfx("yay.mp3")
            self.start_confetti()
        elif score >= 70:
            grade, color, msg = "B (Math Pro)", "#00FF00", f"Excellent Work, {self.controller.user_name}!"
            self.controller.play_sfx("yay.mp3")
            self.start_confetti()
        elif score >= 50:
            grade, color, msg = "C (Good Try)", "#FFA500", f"Keep Going, {self.controller.user_name}!"
            self.controller.play_sfx("sad.mp3")
        else:
            grade, color, msg = "D (Keep Practicing)", "#FF4444", f"Don't Give Up, {self.controller.user_name}!"
            self.controller.play_sfx("sad.mp3")

        self.canvas.itemconfigure(self.id_rank, text=msg)
        self.canvas.itemconfigure(self.id_grade, text=f"Grade: {grade}", fill=color)
        self.canvas.itemconfigure(self.id_stats, text=f"✅ Correct: {correct}   |   ❌ Wrong: {wrong}")
        
        self.update_leaderboard_file()
        self.animate_score_count(0, score)
        self.after(3000, lambda: pygame.mixer.music.play(-1))

    def animate_score_count(self, current, target):
        """Visually counts up the score from 0 to target."""
        if current <= target:
            self.canvas.itemconfigure(self.id_final_score, text=f"Your Score: {current} / 100")
            self.after(20, lambda: self.animate_score_count(current + 1, target))

    def update_leaderboard_file(self):
        """Reads JSON file, appends current score, sorts, and saves top 3."""
        file = "leaderboard.json"
        data = []
        if os.path.exists(file):
            try:
                with open(file, "r") as f: data = json.load(f)
            except: pass
            
        data.append({"name": self.controller.user_name, "score": self.controller.score})
        # Sort by score descending and keep top 3
        data = sorted(data, key=lambda x: x["score"], reverse=True)[:3]
        
        try:
            with open(file, "w") as f: json.dump(data, f, indent=4)
        except: pass
        
        # Format text for display
        text = "TOP 3 SCORERS\n\n"
        for i, p in enumerate(data):
            text += f"{['1st','2nd','3rd'][i] if i<3 else ''} {p['name']} : {p['score']} pts\n"
        self.canvas.itemconfigure(self.id_leaderboard, text=text)

    def start_confetti(self):
        """Initializes particles for celebration effect."""
        colors = ['#FFD700', '#FF0000', '#00FF00', '#00FFFF', '#FF00FF']
        self.confetti_particles.clear()
        for _ in range(80):
            x, y = random.randint(0, 1200), random.randint(-700, 0)
            size = random.randint(6, 18)
            item = self.canvas.create_oval(x, y, x+size, y+size, fill=random.choice(colors), outline="")
            self.confetti_particles.append({"id": item, "speed": random.randint(4, 10), "sway": random.choice([-1, 1])})
        self.animate_confetti_loop()

    def animate_confetti_loop(self):
        """Recursively moves confetti particles down the screen."""
        if not self.winfo_ismapped(): return
        for p in self.confetti_particles:
            self.canvas.move(p["id"], p["sway"], p["speed"])
            # Reset particle to top if it falls off screen
            if self.canvas.coords(p["id"])[1] > 700:
                self.canvas.move(p["id"], 0, -800)
        self.after(25, self.animate_confetti_loop)

# --- ENTRY POINT ---
if __name__ == "__main__":
    app = MathQuizApp()
    app.mainloop()
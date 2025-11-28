"""
PROGRAMMING SKILLS PORTFOLIO - EXERCISE 1: MATH QUIZ
-------------------------------------------------------
The mandatory functions requested in the brief are encapsulated within classes:
1. displayMenu()      -> DifficultyPage (Renders selection menu)
2. randomInt()        -> QuizPage (Generates numbers based on level)
3. decideOperation()  -> QuizPage (Selects + or -)
4. displayProblem()   -> QuizPage (Updates GUI)
5. isCorrect()        -> QuizPage (Validates answer & scores)
6. displayResults()   -> ResultPage (Calculates grade & ranking)

ACKNOWLEDGEMENTS:
- Core Logic: Adapted from Module Lecture Notes.
- Libraries: Pygame (Audio), Pillow (Image rendering).
- AI Support: Google Gemini (Used for 'Confetti' particles & 'Slide' animation logic).
"""

import tkinter as tk      # GUI Framework
from tkinter import messagebox  # Alerts
from PIL import Image, ImageTk  # Image handling
import pygame             # Audio handling
import time               # Timer
import random             # Math generation
import json               # Leaderboard data
import os                 # File paths

import tkinter as tk      # Standard GUI library
from tkinter import messagebox  # Pop-up alerts
from PIL import Image, ImageTk  # Image asset handling
import pygame             # Audio handling
import time               # Timer utilities
import random             # Used within Class methods for dynamic question generation
import json               # Data persistence for Leaderboard
import os                 # File path management

# --- ENVIRONMENT SETUP ---
script_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_directory)

# --- MAIN CONTROLLER (OOP PATTERN) ---
class MathQuizApp(tk.Tk):
    """
    Main Application Controller.
    Manages shared state (score, user, difficulty) and page navigation.
    """
    def __init__(self):
        super().__init__()
        self.title("Brain Brawl: Arithmetic Quiz")
        self.geometry("1200x680")
        self.resizable(False, False)
        
        try:
            self.iconphoto(False, tk.PhotoImage(file="root-icon.png"))
        except: pass

        pygame.mixer.init()
        self.clock_channel = None 

        # Shared State Variables
        self.user_name = "Player"
        self.difficulty = 1
        self.score = 0
        self.attempts_left = 2
        self.current_question_num = 0
        
        # Stats for Analytics
        self.total_correct = 0 
        self.total_wrong = 0

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        self.frames = {} 
        
        for F in (WelcomePage, InstructionPage, NamePage, DifficultyPage, QuizPage, ResultPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.place(x=0, y=0, width=1200, height=700)

        self.show_frame("WelcomePage", instant=True)
        self.play_bg_music()

    def show_frame(self, page_name, instant=False):
        frame = self.frames[page_name]
        frame.tkraise()
        if instant:
            frame.place(x=0, y=0, width=1200, height=700)
        else:
            frame.place(x=1200, y=0, width=1200, height=700) 
            self.slide_animation(frame, 1200)

    def slide_animation(self, frame, current_x):
        if current_x > 0:
            new_x = current_x - 45 
            frame.place(x=new_x, y=0)
            self.after(10, lambda: self.slide_animation(frame, new_x))
        else:
            frame.place(x=0, y=0) 

    def play_bg_music(self):
        try:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load("welcome.mp3")
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.4)
        except: pass

    def play_sfx(self, file):
        try:
            sfx = pygame.mixer.Sound(file)
            sfx.set_volume(1.0)
            sfx.play()
        except: pass

    def stop_all_sounds(self):
        pygame.mixer.music.stop()
        pygame.mixer.stop()

# --- BASE PAGE ---
class BasePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.canvas = tk.Canvas(self, width=1200, height=700)
        self.canvas.pack(fill="both", expand=True)
        
    def add_button_effects(self, btn):
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

# --- PAGES ---

class WelcomePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        try:
            self.bg_img = ImageTk.PhotoImage(Image.open("01-welcome.png").resize((1200, 700)))
            self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")
        except: self.canvas.config(bg="#452929")

        self.start_btn = tk.Button(self, text="Let's Begin →", font=("Comic Sans MS", 24, "bold"), 
                                   bg="#452929", fg="white", cursor="hand2", 
                                   command=lambda: controller.show_frame("InstructionPage"))
        self.add_button_effects(self.start_btn)
        self.btn_window = self.canvas.create_window(600, 720, window=self.start_btn)
        self.animate_button_entry(720)

    def animate_button_entry(self, y_pos):
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

        font_inst = ("Comic Sans MS", 18, "bold")
        self.canvas.create_text(342, 355, text="•10 questions per round\n•10 points-1st try correct\n•5 points-2nd try correct", font=font_inst, fill="white", justify="center")
        self.canvas.create_text(608, 512, text=" • Easy-1 digit numbers\n• Moderate-2 digits\n• Advanced-4 digits", font=font_inst, fill="white", justify="center")
        self.canvas.create_text(890, 360, text="• Choose difficulty level\n• Solve math problems\n• Type your answer", font=font_inst, fill="white", justify="center")

        next_btn = tk.Button(self, text="Next →", font=("Comic Sans MS", 22, "bold"), bg="#452929", fg="white", 
                             cursor="hand2", command=lambda: controller.show_frame("NamePage"))
        self.canvas.create_window(1010, 602, window=next_btn)
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

        back_btn = tk.Button(self, text="← Back", font=("Comic Sans MS", 18, "bold"), bg="#5a2c2c", fg="white", 
                             cursor="hand2", command=lambda: controller.show_frame("InstructionPage"))
        next_btn = tk.Button(self, text="Next →", font=("Comic Sans MS", 18, "bold"), bg="#3b5a2c", fg="white", 
                             cursor="hand2", command=self.save_name_and_next)
        
        self.canvas.create_window(450, 450, window=back_btn)
        self.canvas.create_window(750, 450, window=next_btn)
        self.add_button_effects(back_btn)
        self.add_button_effects(next_btn)

    def save_name_and_next(self):
        typed = self.name_entry.get().strip()
        if typed == "":
            messagebox.showwarning("Name Required", "Please enter your name!")
            return
        self.controller.user_name = typed
        self.controller.show_frame("DifficultyPage")

class DifficultyPage(BasePage):
    """
    Requirement: displayMenu
    This class satisfies the brief by acting as the function that displays the menu options.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.displayMenu() 

    # --- REQUIREMENT: displayMenu ---
    def displayMenu(self):
        """A function that displays the difficulty level menu at the beginning of the quiz."""
        try:
            self.bg_img = ImageTk.PhotoImage(Image.open("04-Difficulty.png").resize((1200, 700)))
            self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")
        except: self.canvas.config(bg="black")

        btn_font = ("Comic Sans MS", 22, "bold")
        
        # Difficulty Options
        btn_easy = tk.Button(self, text="1. Easy (1 digit)", font=btn_font, bg="#452929", fg="white", width=15, 
                             cursor="hand2", command=lambda: self.start_game(1))
        btn_mod = tk.Button(self, text="2. Moderate (2 digits)", font=btn_font, bg="#452929", fg="white", width=15, 
                            cursor="hand2", command=lambda: self.start_game(2))
        btn_adv = tk.Button(self, text="3. Advanced (4 digits)", font=btn_font, bg="#452929", fg="white", width=15, 
                            cursor="hand2", command=lambda: self.start_game(3))
        
        self.canvas.create_window(360, 320, window=btn_easy)
        self.canvas.create_window(510, 420, window=btn_mod)
        self.canvas.create_window(690, 510, window=btn_adv)
        
        back_btn = tk.Button(self, text="← Back", font=("Comic Sans MS", 16, "bold"), bg="#5a2c2c", fg="white", 
                             width=10, cursor="hand2", command=lambda: self.controller.show_frame("NamePage"))
        self.canvas.create_window(180, 612, window=back_btn)
        
        for b in [btn_easy, btn_mod, btn_adv, back_btn]: self.add_button_effects(b)

    def start_game(self, level):
        self.controller.difficulty = level
        self.controller.score = 0
        self.controller.current_question_num = 0
        self.controller.total_correct = 0
        self.controller.total_wrong = 0
        self.controller.frames["QuizPage"].start_new_game()
        self.controller.show_frame("QuizPage")


class QuizPage(BasePage):
    """
    Core Gameplay Logic.
    Satisfies requirements: randomInt, decideOperation, displayProblem, isCorrect.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        # Setup GUI (Part of displayProblem logic)
        try:
            self.bg_img = ImageTk.PhotoImage(Image.open("05-quiz.png").resize((1200, 700)))
            self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")
        except: self.canvas.config(bg="#4d8c57")

        self.timer_running = False
        self.timer_seconds = 12
        self.correct_answer = 0

        # UI Elements
        self.id_heading = self.canvas.create_text(590, 129, text="", font=("Comic Sans MS", 24, "bold"), fill="#452929")
        self.id_score = self.canvas.create_text(200, 110, text="Score: 0", font=("Comic Sans MS", 22, "bold"), fill="white")
        self.id_timer = self.canvas.create_text(990, 112, text="Time: 12s", font=("Comic Sans MS", 22, "bold"), fill="white")
        self.id_main_q = self.canvas.create_text(600, 320, text="", font=("Comic Sans MS", 50, "bold"), fill="white")
        self.id_hint = self.canvas.create_text(569, 260, text="", font=("Arial", 16, "italic"), fill="#FFD700")
        self.id_feedback = self.canvas.create_text(593, 500, text="", font=("Arial", 18, "bold"), fill="white")

        self.entry_answer = tk.Entry(self, font=("Arial", 30), width=12, justify="center")
        self.entry_answer.place(x=425, y=400, width=300, height=60)
        
        # Link Enter Key to isCorrect function (Requirement)
        self.entry_answer.bind('<Return>', lambda event: self.isCorrect()) 

        # Buttons
        btn_hint = tk.Button(self, text=" Hint", font=("Arial", 12, "bold"), bg="#FFD700", fg="black", cursor="hand2", command=self.show_hint)
        # Link Submit Button to isCorrect function (Requirement)
        btn_submit = tk.Button(self, text="Submit", font=("Comic Sans MS", 20, "bold"), width=10, bg="#3b5a2c", fg="white", cursor="hand2", command=self.isCorrect)
        btn_back = tk.Button(self, text="← Back", font=("Comic Sans MS", 16, "bold"), bg="#5a2c2c", fg="white", width=8, cursor="hand2", command=self.go_back)

        self.canvas.create_window(790, 430, window=btn_hint)
        self.canvas.create_window(580, 576, window=btn_submit)
        self.canvas.create_window(180, 595, window=btn_back) 
        for b in [btn_hint, btn_submit, btn_back]: self.add_button_effects(b)

    # --- REQUIREMENT: randomInt ---
    def randomInt(self, difficulty):
        """A function that determines the values used in each question."""
        # Easy (1 digit), Moderate (2 digits), Advanced (4 digits - as per brief)
        if difficulty == 1: return random.randint(1, 9)
        elif difficulty == 2: return random.randint(10, 99)
        else: return random.randint(1000, 9999)

    # --- REQUIREMENT: decideOperation ---
    def decideOperation(self):
        """A function that randomly decides whether the problem is an addition or subtraction."""
        return random.choice(["+", "-"])

    # --- REQUIREMENT: displayProblem ---
    def displayProblem(self):
        """A function that displays the question to the user and accepts their answer."""
        self.stop_clock_sound()
        
        if self.controller.current_question_num < 10:
            self.controller.current_question_num += 1
            self.controller.attempts_left = 2
            self.timer_seconds = 12
            self.timer_running = True

            # Use the mandatory functions
            num1 = self.randomInt(self.controller.difficulty)
            num2 = self.randomInt(self.controller.difficulty)
            operation = self.decideOperation()

            if operation == "+":
                self.correct_answer = num1 + num2
                q_text = f"{num1} + {num2} = ?"
            else:
                if num1 < num2: num1, num2 = num2, num1 # Prevent negative result
                self.correct_answer = num1 - num2
                q_text = f"{num1} - {num2} = ?"

            # UI Updates
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
            self.timer_running = False
            self.stop_clock_sound()
            self.controller.stop_all_sounds()
            self.controller.play_sfx("gameover.mp3")
            self.after(1000, self.go_to_results)

    def start_new_game(self):
        self.controller.current_question_num = 0
        self.displayProblem() 

    # --- REQUIREMENT: isCorrect ---
    def isCorrect(self):
        """A function that checks whether the users answer was correct and outputs an appropriate message."""
        user_input = self.entry_answer.get()
        if not user_input.strip(): return
        
        try:
            user_ans = int(user_input)
        except ValueError:
            self.canvas.itemconfigure(self.id_feedback, text="Numbers only!", fill="yellow")
            return

        if user_ans == self.correct_answer:
            # Correct Answer
            self.timer_running = False
            self.stop_clock_sound()
            self.controller.play_sfx("correct.mp3")
            self.flash_board("lightgreen")
            self.controller.total_correct += 1
            
            # Scoring: 10 pts (1st try), 5 pts (2nd try)
            points = 10 if self.controller.attempts_left == 2 else 5
            self.controller.score += points
            
            self.canvas.itemconfigure(self.id_feedback, text=f"Correct! +{points} Pts", fill="#00FF00")
            self.canvas.itemconfigure(self.id_score, text=f"Score: {self.controller.score}")
            self.after(1500, self.displayProblem) # Loads next question
        else:
            # Wrong Answer
            self.controller.attempts_left -= 1
            self.controller.play_sfx("wrong.mp3")
            self.shake_entry()
            
            if self.controller.attempts_left > 0:
                self.canvas.itemconfigure(self.id_feedback, text="Wrong! Try Again (+5 pts)", fill="#D62E2E")
                self.entry_answer.delete(0, tk.END)
            else:
                self.timer_running = False
                self.stop_clock_sound()
                self.controller.total_wrong += 1
                self.canvas.itemconfigure(self.id_feedback, text=f"Wrong! Answer: {self.correct_answer}", fill="#D62E2E")
                self.after(2000, self.displayProblem) # Loads next question

    def go_back(self):
        self.timer_running = False
        self.stop_clock_sound()
        self.controller.show_frame("DifficultyPage")

    def stop_clock_sound(self):
        if self.controller.clock_channel and self.controller.clock_channel.get_busy():
            self.controller.clock_channel.stop()

    def countdown_timer(self):
        if self.timer_running:
            if self.timer_seconds > 0:
                fg_color = "#D62E2E" if self.timer_seconds <= 5 else "white"
                if self.timer_seconds == 5:
                    try:
                        pygame.mixer.Sound("clock.wav").play()
                    except: pass
                self.canvas.itemconfigure(self.id_timer, text=f"Time: {self.timer_seconds}s", fill=fg_color)
                self.timer_seconds -= 1
                self.after(1000, self.countdown_timer)
            else:
                self.timer_running = False
                self.stop_clock_sound()
                self.controller.total_wrong += 1
                self.canvas.itemconfigure(self.id_timer, text="Time's Up!", fill="red")
                self.controller.play_sfx("wrong.mp3")
                self.after(2000, self.displayProblem)

    def show_hint(self):
        msg = "Hint: Answer is EVEN" if self.correct_answer % 2 == 0 else "Hint: Answer is ODD"
        self.canvas.itemconfigure(self.id_hint, text=msg, fill="#FFD700")

    def shake_entry(self):
        original_x = 425
        offsets = [-10, 10, -8, 8, -5, 5, 0]
        delay = 50
        for offset in offsets:
            self.entry_answer.after(delay, lambda o=offset: self.entry_answer.place(x=original_x + o))
            delay += 50
        self.entry_answer.config(bg="#ffcccc")
        self.entry_answer.after(500, lambda: self.entry_answer.config(bg="white"))

    def flash_board(self, color):
        try:
            flash = self.canvas.create_rectangle(0,0,1200,700, fill=color, stipple="gray50")
            self.update()
            time.sleep(0.2)
            self.canvas.delete(flash)
        except: pass

    def go_to_results(self):
        self.controller.frames["ResultPage"].displayResults()
        self.controller.show_frame("ResultPage")


class ResultPage(BasePage):
    """
    Handles results. Satisfies requirement: displayResults.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.confetti_particles = []
        try:
            self.bg_img = ImageTk.PhotoImage(Image.open("06-results.png").resize((1200, 700)))
            self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")
        except: self.canvas.config(bg="#1a3a2a")
        
        # Result Box Layout
        frame_width, frame_height = 560, 400 
        frame_x, frame_y = (1210 - frame_width) // 2, (740 - frame_height) // 2 + 20
        center_x = frame_x + frame_width // 2

        self.canvas.create_rectangle(frame_x, frame_y, frame_x+frame_width, frame_y+frame_height, fill="#2d5a3d", outline="#F3EFD8", width=3)
        self.id_rank = self.canvas.create_text(center_x, frame_y + 50, text="", font=("Comic Sans MS", 28, "bold"), fill="#F3E08A")
        self.id_final_score = self.canvas.create_text(center_x, frame_y + 110, text="", font=("Comic Sans MS", 24, "bold"), fill="white")
        self.id_grade = self.canvas.create_text(center_x, frame_y + 160, text="", font=("Comic Sans MS", 22, "bold"), fill="#F8E88B")
        self.id_leaderboard = self.canvas.create_text(center_x, frame_y + 320, text="", font=("Arial", 14, "bold"), fill="white", justify="center")

        btn_play = tk.Button(self, text="Play Again ↻", font=("Comic Sans MS", 16, "bold"), bg="#3b5a2c", fg="white", width=11, cursor="hand2", command=lambda: controller.show_frame("DifficultyPage"))
        btn_exit = tk.Button(self, text="Exit ✕", font=("Comic Sans MS", 16, "bold"), bg="#8b0000", fg="white", width=9, cursor="hand2", command=controller.quit)
        self.canvas.create_window(402, 565, window=btn_play)
        self.canvas.create_window(820, 565, window=btn_exit)
        self.add_button_effects(btn_play)
        self.add_button_effects(btn_exit)

    # --- REQUIREMENT: displayResults ---
    def displayResults(self):
        """A function that outputs the users final score and ranks the user."""
        score = self.controller.score
        
        # Ranking Logic
        if score >= 90: grade, color, msg = "A+ (Math Wizard)", "#FFD700", f"Outstanding!"
        elif score >= 70: grade, color, msg = "B (Math Pro)", "#00FF00", f"Excellent Work!"
        elif score >= 50: grade, color, msg = "C (Good Try)", "#FFA500", f"Keep Going!"
        else: grade, color, msg = "D (Keep Practicing)", "#FF4444", f"Don't Give Up!"

        if score >= 70: self.start_confetti()
        
        self.canvas.itemconfigure(self.id_rank, text=msg)
        self.canvas.itemconfigure(self.id_grade, text=f"Grade: {grade}", fill=color)
        self.canvas.itemconfigure(self.id_final_score, text=f"Final Score: {score} / 100")
        
        self.update_leaderboard_file()
        pygame.mixer.music.play(-1)

    def update_leaderboard_file(self):
        file = "leaderboard.json"
        data = []
        if os.path.exists(file):
            try:
                with open(file, "r") as f: data = json.load(f)
            except: pass
        data.append({"name": self.controller.user_name, "score": self.controller.score})
        data = sorted(data, key=lambda x: x["score"], reverse=True)[:3]
        try:
            with open(file, "w") as f: json.dump(data, f, indent=4)
        except: pass
        text = "TOP 3 SCORERS\n\n"
        for i, p in enumerate(data):
            text += f"{['1st','2nd','3rd'][i] if i<3 else ''} {p['name']} : {p['score']} pts\n"
        self.canvas.itemconfigure(self.id_leaderboard, text=text)

    def start_confetti(self):
        colors = ['#FFD700', '#FF0000', '#00FF00', '#00FFFF', '#FF00FF']
        self.confetti_particles.clear()
        for _ in range(80):
            x, y = random.randint(0, 1200), random.randint(-700, 0)
            size = random.randint(6, 18)
            item = self.canvas.create_oval(x, y, x+size, y+size, fill=random.choice(colors), outline="")
            self.confetti_particles.append({"id": item, "speed": random.randint(4, 10), "sway": random.choice([-1, 1])})
        self.animate_confetti_loop()

    def animate_confetti_loop(self):
        if not self.winfo_ismapped(): return
        for p in self.confetti_particles:
            self.canvas.move(p["id"], p["sway"], p["speed"])
            if self.canvas.coords(p["id"])[1] > 700:
                self.canvas.move(p["id"], 0, -800)
        self.after(25, self.animate_confetti_loop)

# --- ENTRY POINT ---
if __name__ == "__main__":
    app = MathQuizApp()
    app.mainloop()
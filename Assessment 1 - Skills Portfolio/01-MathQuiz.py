import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pygame
import time
import random  # Zaroori hai math questions ke liye

pygame.mixer.init()

# ---------------- GLOBAL VARIABLES (QUIZ STATE) -------------------
selected_difficulty = None
# Quiz Logic Variables
current_question = 0
score = 0
attempts_left = 2
correct_answer = 0
timer_seconds = 12
timer_running = False
user_name = "" # To store name from Page 3

# ---------------- SOUND FUNCTIONS -------------------
def play_sound(file):
    try:
        sound = pygame.mixer.Sound(file)
        sound.play()
    except:
        pass

# ---------------- BUTTON EFFECT HELPER -------------------
def add_button_effects(btn):
    original_color = btn['bg']
    highlight_color = "#7d4e4e"
    def on_enter(e):
        if btn['bg'] != "#FFD700": btn['background'] = highlight_color
    def on_leave(e):
        if btn['bg'] != "#FFD700": btn['background'] = original_color
    def on_click(e):
        play_sound("button_press.mp3")
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    btn.bind("<Button-1>", on_click, add="+")

# ---------------- FADE IN EFFECT -------------------
def fade_in(widget, delay=7):
    try:
        widget.attributes("-alpha", 0.0)
        for i in range(0, 100, 5):
            widget.attributes("-alpha", i / 100)
            widget.update()
            time.sleep(delay / 1000)
        widget.attributes("-alpha", 1.0)
    except: pass

# ==============================================================================
#  PAGE 5 LOGIC FUNCTIONS (REQUIRED FOR ASSIGNMENT)
# ==============================================================================

# --- Requirement: randomInt function ---
def randomInt(difficulty):
    """Returns a random number based on difficulty level."""
    if difficulty == 1:   # Easy: 1 digit (1-9)
        return random.randint(1, 9)
    elif difficulty == 2: # Moderate: 2 digits (10-99)
        return random.randint(10, 99)
    else:                 # Advanced: 4 digits (1000-9999)
        return random.randint(1000, 9999)

# --- Requirement: decideOperation function ---
def decideOperation():
    """Randomly decides addition or subtraction."""
    return random.choice(["+", "-"])

# --- Core Quiz Logic ---
def start_quiz(level):
    global selected_difficulty, current_question, score
    selected_difficulty = level
    # Reset variables for new game
    current_question = 0
    score = 0
    show_frame(page5)
    next_question() # Start first question

def next_question():
    global current_question, attempts_left, correct_answer, timer_seconds, timer_running
    
    if current_question < 10:
        current_question += 1
        attempts_left = 2
        timer_seconds = 12
        timer_running = True
        
        # Generate Numbers & Operation
        num1 = randomInt(selected_difficulty)
        num2 = randomInt(selected_difficulty)
        op = decideOperation()
        
        # Calculate correct answer and create question string
        if op == "+":
            correct_answer = num1 + num2
            q_text = f"{num1} + {num2} = ?"
        else:
            # Ensure bigger number first for subtraction to avoid negatives (optional but cleaner)
            if num1 < num2: num1, num2 = num2, num1 
            correct_answer = num1 - num2
            q_text = f"{num1} - {num2} = ?"
            
        # Update GUI elements on Page 5
        lbl_q_heading.config(text=f"Question {current_question} / 10")
        lbl_main_q.config(text=q_text)
        entry_answer.delete(0, tk.END) # Clear entry box
        entry_answer.config(bg="white") # Reset color if it was red
        entry_answer.focus() # Automatically select entry box
        
        update_score_label()
        countdown_timer() # Start timer loop
        
    else:
        # Quiz Finished! (Page 6 placeholder)
        timer_running = False
        messagebox.showinfo("Quiz Finished!", f"Game Over, {user_name}!\nYour Final Score is: {score}/100")
        # Here you would redirect to a Final Result Page (Page 6)

def countdown_timer():
    """Handles the 12-second timer loop."""
    global timer_seconds, timer_running
    if timer_running:
        if timer_seconds > 0:
            # Update label color based on time left (Warning Effect)
            fg_color = "#ff4444" if timer_seconds <= 5 else "white"
            lbl_timer.config(text=f"Time: {timer_seconds}s", fg=fg_color)
            timer_seconds -= 1
            # Schedule next call in 1 second (1000ms)
            root.after(1000, countdown_timer)
        else:
            # Time's Up!
            timer_running = False
            lbl_timer.config(text="Time's Up!", fg="red")
            play_sound("wrong.mp3") # Assuming you have this sound
            messagebox.showwarning("Time's Up", "Oops! Time ran out. Moving to next question.")
            next_question()

# --- Requirement: isCorrect logic (Integrated here) ---
def check_answer():
    global score, attempts_left, timer_running
    user_input = entry_answer.get()
    
    if not user_input.isdigit() and not (user_input.startswith('-') and user_input[1:].isdigit()):
        messagebox.showwarning("Invalid Input", "Please enter a valid number.")
        return

    user_ans = int(user_input)
    
    if user_ans == correct_answer:
        # --- CORRECT ANSWER ---
        timer_running = False # Stop timer
        play_sound("correct.mp3") # Assuming you have this
        flash_board("lightgreen") # Flash animation
        
        # Scoring logic based on attempts
        points = 10 if attempts_left == 2 else 5
        score += points
        messagebox.showinfo("Correct!", f"Well done! You got {points} points.")
        next_question()
    else:
        # --- WRONG ANSWER ---
        attempts_left -= 1
        play_sound("wrong.mp3") # Assuming you have this
        shake_entry() # Shake animation
        
        if attempts_left > 0:
            # 2nd Chance given
            messagebox.showerror("Wrong!", "Incorrect answer. Try again! (Last chance for 5 points)")
            entry_answer.delete(0, tk.END)
        else:
            # No chances left
            timer_running = False
            messagebox.showerror("Wrong!", f"Sorry, no attempts left.\nThe correct answer was: {correct_answer}")
            next_question()

def update_score_label():
    lbl_score.config(text=f"Score: {score}")

# --- ANIMATIONS ---
def shake_entry():
    """Shakes the entry box left and right."""
    original_x = 450 # Original X position of entry box
    offsets = [-10, 10, -8, 8, -5, 5, 0] # Movement pattern
    delay = 50
    for offset in offsets:
        # Schedule movements with increasing delays
        entry_answer.after(delay, lambda o=offset: entry_answer.place(x=original_x + o))
        delay += 50
    # Briefly turn red
    entry_answer.config(bg="#ffcccc")
    entry_answer.after(500, lambda: entry_answer.config(bg="white"))

def flash_board(color):
    """Flashes the canvas background briefly."""
    canvas5.config(bg=color)
    # The image covers the bg, so we use a temporary rectangle cover
    flash = canvas5.create_rectangle(0,0,1200,700, fill=color, stipple="gray50")
    root.update()
    time.sleep(0.2)
    canvas5.delete(flash)

# ==============================================================================
#  MAIN APP SETUP
# ==============================================================================
root = tk.Tk()
root.title("Maths Quiz")
root.geometry("1200x700")
root.attributes("-alpha", 1.0)
root.resizable(False, False)
try: root.iconphoto(False, tk.PhotoImage(file="icon.png"))
except: pass

def show_frame(frame): frame.tkraise()

# ---------------- PAGE 1 -------------------
page1 = tk.Frame(root); page1.place(relwidth=1, relheight=1)
try:
    bg1 = ImageTk.PhotoImage(Image.open("01-welcome.png").resize((1200, 700)))
    canvas1 = tk.Canvas(page1); canvas1.pack(fill="both", expand=True)
    canvas1.create_image(0, 0, image=bg1, anchor="nw")
    start_btn = tk.Button(page1, text="Let's Begin", font=("Comic Sans MS", 24, "bold"), bg="#452929", fg="white", cursor="hand2", command=lambda: show_frame(page2))
    canvas1.create_window(600, 580, window=start_btn); add_button_effects(start_btn)
except: pass

# ---------------- PAGE 2 -------------------
page2 = tk.Frame(root); page2.place(relwidth=1, relheight=1)
try:
    bg2 = ImageTk.PhotoImage(Image.open("02-instruction.png").resize((1200, 700)))
    canvas2 = tk.Canvas(page2); canvas2.pack(fill="both", expand=True)
    canvas2.create_image(0, 0, image=bg2, anchor="nw")
    font_inst = ("Comic Sans MS", 18, "bold")
    canvas2.create_text(301, 365, text="•10 questions per round\n•10 points-1st try correct\n•5 points-2nd try correct", font=font_inst, fill="white", justify="center")
    canvas2.create_text(580, 512, text="•Easy-1 digit numbers\n• Moderate-2 digits\n• Advanced-4 digits", font=font_inst, fill="white", justify="center")
    canvas2.create_text(885, 368, text="• Choose difficulty level\n• Solve math problems\n• Type your answer", font=font_inst, fill="white", justify="center")
    next_btn_p2 = tk.Button(page2, text="Next", font=("Comic Sans MS", 22, "bold"), bg="#452929", fg="white", cursor="hand2", command=lambda: show_frame(page3))
    canvas2.create_window(1080, 620, window=next_btn_p2); add_button_effects(next_btn_p2)
except: pass

# ---------------- PAGE 3 -------------------
page3 = tk.Frame(root); page3.place(relwidth=1, relheight=1)
def save_name_and_next():
    global user_name
    user_name = name_entry.get()
    if user_name.strip() == "": user_name = "Player" # Default name
    show_frame(page4)

try:
    bg3 = ImageTk.PhotoImage(Image.open("03-name.png").resize((1200, 700)))
    canvas3 = tk.Canvas(page3); canvas3.pack(fill="both", expand=True)
    canvas3.create_image(0, 0, image=bg3, anchor="nw")
    name_entry = tk.Entry(page3, font=("Arial", 24), width=20, justify="center")
    canvas3.create_window(600, 350, window=name_entry)
    back_btn_p3 = tk.Button(page3, text="Back to Instructions", font=("Comic Sans MS", 18, "bold"), bg="#5a2c2c", fg="white", cursor="hand2", command=lambda: show_frame(page2))
    next_btn_p3 = tk.Button(page3, text="Next", font=("Comic Sans MS", 18, "bold"), bg="#3b5a2c", fg="white", cursor="hand2", command=save_name_and_next)
    add_button_effects(back_btn_p3); add_button_effects(next_btn_p3)
    canvas3.create_window(450, 450, window=back_btn_p3); canvas3.create_window(750, 450, window=next_btn_p3)
except: pass

# ---------------- PAGE 4 -------------------
page4 = tk.Frame(root); page4.place(relwidth=1, relheight=1)
try:
    bg4 = ImageTk.PhotoImage(Image.open("04-Difficulty.png").resize((1200, 700)))
    canvas4 = tk.Canvas(page4); canvas4.pack(fill="both", expand=True)
    canvas4.create_image(0, 0, image=bg4, anchor="nw")
    btn_font = ("Comic Sans MS", 22, "bold"); btn_bg = "#452929"; btn_fg = "white"
    
    btn_easy = tk.Button(page4, text="Easy- 1 digit", font=btn_font, bg=btn_bg, fg=btn_fg, width=15, cursor="hand2", command=lambda: start_quiz(1))
    canvas4.create_window(360, 320, window=btn_easy); add_button_effects(btn_easy)
    
    btn_mod = tk.Button(page4, text="Moderate- 2 digits", font=btn_font, bg=btn_bg, fg=btn_fg, width=15, cursor="hand2", command=lambda: start_quiz(2))
    canvas4.create_window(510, 420, window=btn_mod); add_button_effects(btn_mod)
    
    btn_adv = tk.Button(page4, text="Advanced- 4 digits", font=btn_font, bg=btn_bg, fg=btn_fg, width=15, cursor="hand2", command=lambda: start_quiz(3))
    canvas4.create_window(690, 510, window=btn_adv); add_button_effects(btn_adv)

    btn_back_p4 = tk.Button(page4, text="Back", font=("Comic Sans MS", 16, "bold"), bg="#5a2c2c", fg="white", width=10, cursor="hand2", command=lambda: show_frame(page3))
    canvas4.create_window(150, 620, window=btn_back_p4); add_button_effects(btn_back_p4)
except: pass

# ==============================================================================
#  PAGE 5 – THE MAIN QUIZ PAGE (UPDATED WITH NEW IMAGE & LOGIC)
# ==============================================================================
page5 = tk.Frame(root)
page5.place(relwidth=1, relheight=1)

try:
    # Ensure your cleaned image is named "05-quiz.png"
    bg5 = Image.open("05-quiz.png").resize((1200, 700))
    bg5 = ImageTk.PhotoImage(bg5)
    
    canvas5 = tk.Canvas(page5)
    canvas5.pack(fill="both", expand=True)
    canvas5.create_image(0, 0, image=bg5, anchor="nw")
    
    # --- LABELS ---
    # Question Heading (Top White Stroke area)
    lbl_q_heading = tk.Label(page5, text="Question 1 / 10", font=("Comic Sans MS", 24, "bold"), bg="#FFFFFF", fg="#452929")
    # Adjust placement to fit nicely on the white paint stroke
    canvas5.create_window(600, 160, window=lbl_q_heading)
    
    # Score Label (Top Left near Smiley)
    lbl_score = tk.Label(page5, text="Score: 0", font=("Comic Sans MS", 20, "bold"), bg="#4d8c57", fg="white")
    canvas5.create_window(150, 150, window=lbl_score)
    
    # Timer Label (Top Right near Heart)
    lbl_timer = tk.Label(page5, text="Time: 12s", font=("Comic Sans MS", 20, "bold"), bg="#4d8c57", fg="white")
    canvas5.create_window(1050, 150, window=lbl_timer)
    
    # MAIN QUESTION LABEL (Center of Board)
    lbl_main_q = tk.Label(page5, text="Ready?", font=("Comic Sans MS", 48, "bold"), bg="#4d8c57", fg="white")
    canvas5.create_window(600, 350, window=lbl_main_q)
    
    # --- ENTRY & BUTTONS ---
    # Answer Entry Box (Below Question)
    entry_answer = tk.Entry(page5, font=("Arial", 30), width=15, justify="center")
    # Using .place() here to make shake animation easier
    entry_answer.place(x=450, y=450, width=300, height=60)

    # Submit Button
    btn_submit = tk.Button(page5, text="Submit Answer", font=("Comic Sans MS", 20, "bold"), bg="#3b5a2c", fg="white", cursor="hand2", command=check_answer)
    canvas5.create_window(600, 550, window=btn_submit)
    add_button_effects(btn_submit)
    
    # Bind 'Enter' key to submit as well
    root.bind('<Return>', lambda event: check_answer())

except Exception as e:
    print(f"Page 5 Error: {e}")
    tk.Label(page5, text=f"Error loading Page 5: {e}", font=("Arial", 20), fg="red").pack(pady=200)

# ---------------- START APP -------------------
page1.tkraise()
play_sound("welcome.mp3")
fade_in(root)
root.mainloop()
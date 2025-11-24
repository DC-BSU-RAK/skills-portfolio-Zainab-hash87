import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pygame
import time
import random

# Initialize Pygame Mixer
pygame.mixer.init()

# ---------------- GLOBAL VARIABLES -------------------
selected_difficulty = None
current_question = 0
score = 0
attempts_left = 2
correct_answer = 0
timer_seconds = 12
timer_running = False
user_name = ""

# ---------------- SOUND SYSTEM -------------------
def play_bg_music():
    try:
        pygame.mixer.music.load("welcome.mp3")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.5)
    except:
        pass

def play_sfx(file):
    try:
        sfx = pygame.mixer.Sound(file)
        sfx.set_volume(1.0)
        sfx.play()
    except:
        pass

# ---------------- BUTTON EFFECT HELPER -------------------
def add_button_effects(btn):
    original_color = btn['bg']
    highlight_color = "#7d4e4e"

    def on_enter(e):
        if btn['bg'] != "#FFD700":
            btn['background'] = highlight_color

    def on_leave(e):
        if btn['bg'] != "#FFD700":
            btn['background'] = original_color

    def on_click(e):
        play_sfx("button_press.mp3")

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    btn.bind("<Button-1>", on_click, add="+")

# ---------------- FADE IN -------------------
def fade_in(widget, delay=7):
    try:
        widget.attributes("-alpha", 0.0)
        for i in range(0, 100, 5):
            widget.attributes("-alpha", i / 100)
            widget.update()
            time.sleep(delay / 1000)
        widget.attributes("-alpha", 1.0)
    except:
        pass

# ==============================================================================
#  GAME LOGIC
# ==============================================================================

def randomInt(difficulty):
    if difficulty == 1:
        return random.randint(1, 9)
    elif difficulty == 2:
        return random.randint(10, 99)
    else:
        return random.randint(1000, 9999)

def decideOperation():
    return random.choice(["+", "-"])

def start_quiz(level):
    global selected_difficulty, current_question, score
    selected_difficulty = level
    current_question = 0
    score = 0
    show_frame(page5)
    next_question()

def next_question():
    global current_question, attempts_left, correct_answer, timer_seconds, timer_running

    if current_question < 10:
        current_question += 1
        attempts_left = 2
        timer_seconds = 12
        timer_running = True

        num1 = randomInt(selected_difficulty)
        num2 = randomInt(selected_difficulty)
        op = decideOperation()

        if op == "+":
            correct_answer = num1 + num2
            q_text = f"{num1} + {num2} = ?"
        else:
            if num1 < num2:
                num1, num2 = num2, num1
            correct_answer = num1 - num2
            q_text = f"{num1} - {num2} = ?"

        # Update UI
        lbl_q_heading.config(text=f"Question {current_question} / 10")
        lbl_main_q.config(text=q_text)

        # Reset inputs & Feedback
        entry_answer.delete(0, tk.END)
        entry_answer.config(bg="white")
        entry_answer.focus()
        lbl_hint_text.config(text="")  # Hide hint
        lbl_feedback.config(text="", bg="#4d8c57")  # Clear Feedback

        update_score_label()
        countdown_timer()

    else:
        timer_running = False
        messagebox.showinfo("Quiz Finished!", f"Game Over, {user_name}!\nYour Final Score is: {score}/100")

def countdown_timer():
    global timer_seconds, timer_running
    if timer_running:
        if timer_seconds > 0:
            fg_color = "#ff4444" if timer_seconds <= 5 else "white"
            lbl_timer.config(text=f"Time: {timer_seconds}s", fg=fg_color)
            timer_seconds -= 1
            root.after(1000, countdown_timer)
        else:
            timer_running = False
            lbl_timer.config(text="Time's Up!", fg="red")
            play_sfx("wrong.mp3")
            lbl_feedback.config(text="Time Up! Moving on...", fg="orange", bg="white")
            root.after(2000, next_question)

def show_hint():
    if correct_answer % 2 == 0:
        hint_msg = "Hint: Answer is EVEN"
    else:
        hint_msg = "Hint: Answer is ODD"
    lbl_hint_text.config(text=hint_msg, fg="#FFD700")

def check_answer():
    global score, attempts_left, timer_running
    user_input = entry_answer.get()

    if not user_input.strip():
        return

    try:
        user_ans = int(user_input)
    except ValueError:
        lbl_feedback.config(text="Numbers only please!", fg="yellow")
        return

    if user_ans == correct_answer:
        # --- CORRECT ---
        timer_running = False
        play_sfx("correct.mp3")
        flash_board("lightgreen")

        points = 10 if attempts_left == 2 else 5
        score += points

        # Show Feedback
        lbl_feedback.config(text=f"Awesome! +{points} Points", fg="#00FF00", font=("Arial", 18, "bold"))
        update_score_label()

        root.after(1500, next_question)

    else:
        # --- WRONG ---
        attempts_left -= 1
        play_sfx("wrong.mp3")
        shake_entry()

        if attempts_left > 0:
            lbl_feedback.config(text="Wrong! Try Again (+5 pts left)", fg="#FF4444", font=("Arial", 18, "bold"))
            entry_answer.delete(0, tk.END)
        else:
            timer_running = False
            lbl_feedback.config(text=f"Wrong! Answer was {correct_answer}", fg="white", bg="red")
            root.after(2000, next_question)

def update_score_label():
    lbl_score.config(text=f"Score: {score}")

def shake_entry():
    original_x = 450
    offsets = [-10, 10, -8, 8, -5, 5, 0]
    delay = 50
    for offset in offsets:
        entry_answer.after(delay, lambda o=offset: entry_answer.place(x=original_x + o))
        delay += 50
    entry_answer.config(bg="#ffcccc")
    entry_answer.after(500, lambda: entry_answer.config(bg="white"))

def flash_board(color):
    try:
        flash = canvas5.create_rectangle(0, 0, 1200, 700, fill=color, stipple="gray50")
        root.update()
        time.sleep(0.2)
        canvas5.delete(flash)
    except:
        pass

# ==============================================================================
#  MAIN WINDOW SETUP
# ==============================================================================
root = tk.Tk()
root.title("Maths Quiz")
root.geometry("1200x700")
root.resizable(False, False)
try:
    root.iconphoto(False, tk.PhotoImage(file="icon.png"))
except:
    pass

def show_frame(frame):
    frame.tkraise()

# --- PAGE 1 ---
page1 = tk.Frame(root)
page1.place(relwidth=1, relheight=1)
try:
    bg1 = ImageTk.PhotoImage(Image.open("01-welcome.png").resize((1200, 700)))
    canvas1 = tk.Canvas(page1)
    canvas1.pack(fill="both", expand=True)
    canvas1.create_image(0, 0, image=bg1, anchor="nw")
    start_btn = tk.Button(page1, text="Let's Begin", font=("Comic Sans MS", 24, "bold"), bg="#452929", fg="white", cursor="hand2", command=lambda: show_frame(page2))
    canvas1.create_window(600, 580, window=start_btn)
    add_button_effects(start_btn)
except:
    pass

# --- PAGE 2 ---
page2 = tk.Frame(root)
page2.place(relwidth=1, relheight=1)
try:
    bg2 = ImageTk.PhotoImage(Image.open("02-instruction.png").resize((1200, 700)))
    canvas2 = tk.Canvas(page2)
    canvas2.pack(fill="both", expand=True)
    canvas2.create_image(0, 0, image=bg2, anchor="nw")
    font_inst = ("Comic Sans MS", 18, "bold")
    canvas2.create_text(301, 365, text="•10 questions per round\n•10 points-1st try correct\n•5 points-2nd try correct", font=font_inst, fill="white", justify="center")
    canvas2.create_text(580, 512, text="•Easy-1 digit numbers\n• Moderate-2 digits\n• Advanced-4 digits", font=font_inst, fill="white", justify="center")
    canvas2.create_text(885, 368, text="• Choose difficulty level\n• Solve math problems\n• Type your answer", font=font_inst, fill="white", justify="center")
    next_btn_p2 = tk.Button(page2, text="Next", font=("Comic Sans MS", 22, "bold"), bg="#452929", fg="white", cursor="hand2", command=lambda: show_frame(page3))
    canvas2.create_window(1080, 620, window=next_btn_p2)
    add_button_effects(next_btn_p2)
except:
    pass

# --- PAGE 3 ---
page3 = tk.Frame(root)
page3.place(relwidth=1, relheight=1)
def save_name_and_next():
    global user_name
    user_name = name_entry.get()
    if user_name.strip() == "":
        user_name = "Player"
    show_frame(page4)
try:
    bg3 = ImageTk.PhotoImage(Image.open("03-name.png").resize((1200, 700)))
    canvas3 = tk.Canvas(page3)
    canvas3.pack(fill="both", expand=True)
    canvas3.create_image(0, 0, image=bg3, anchor="nw")
    name_entry = tk.Entry(page3, font=("Arial", 24), width=20, justify="center")
    canvas3.create_window(600, 350, window=name_entry)
    back_btn_p3 = tk.Button(page3, text="Back to Instructions", font=("Comic Sans MS", 18, "bold"), bg="#5a2c2c", fg="white", cursor="hand2", command=lambda: show_frame(page2))
    next_btn_p3 = tk.Button(page3, text="Next", font=("Comic Sans MS", 18, "bold"), bg="#3b5a2c", fg="white", cursor="hand2", command=save_name_and_next)
    add_button_effects(back_btn_p3)
    add_button_effects(next_btn_p3)
    canvas3.create_window(450, 450, window=back_btn_p3)
    canvas3.create_window(750, 450, window=next_btn_p3)
except:
    pass

# --- PAGE 4 ---
page4 = tk.Frame(root)
page4.place(relwidth=1, relheight=1)
try:
    bg4 = ImageTk.PhotoImage(Image.open("04-Difficulty.png").resize((1200, 700)))
    canvas4 = tk.Canvas(page4)
    canvas4.pack(fill="both", expand=True)
    canvas4.create_image(0, 0, image=bg4, anchor="nw")
    btn_font = ("Comic Sans MS", 22, "bold")
    btn_bg = "#452929"
    btn_fg = "white"
    btn_easy = tk.Button(page4, text="Easy- 1 digit", font=btn_font, bg=btn_bg, fg=btn_fg, width=15, cursor="hand2", command=lambda: start_quiz(1))
    canvas4.create_window(360, 320, window=btn_easy)
    add_button_effects(btn_easy)
    btn_mod = tk.Button(page4, text="Moderate- 2 digits", font=btn_font, bg=btn_bg, fg=btn_fg, width=15, cursor="hand2", command=lambda: start_quiz(2))
    canvas4.create_window(510, 420, window=btn_mod)
    add_button_effects(btn_mod)
    btn_adv = tk.Button(page4, text="Advanced- 4 digits", font=btn_font, bg=btn_bg, fg=btn_fg, width=15, cursor="hand2", command=lambda: start_quiz(3))
    canvas4.create_window(690, 510, window=btn_adv)
    add_button_effects(btn_adv)
    btn_back_p4 = tk.Button(page4, text="Back", font=("Comic Sans MS", 16, "bold"), bg="#5a2c2c", fg="white", width=10, cursor="hand2", command=lambda: show_frame(page3))
    canvas4.create_window(180, 615, window=btn_back_p4)
    add_button_effects(btn_back_p4)
except:
    pass

# ==============================================================================
#  PAGE 5 – QUIZ PAGE (FIXED & SAFE)
# ==============================================================================
page5 = tk.Frame(root)
page5.place(relwidth=1, relheight=1)

# Step 1: Create Canvas (Always happens)
canvas5 = tk.Canvas(page5, bg="#4d8c57")
canvas5.pack(fill="both", expand=True)

# Step 2: Try to load Image
try:
    bg5 = ImageTk.PhotoImage(Image.open("05-quiz.png").resize((1200, 700)))
    canvas5.create_image(0, 0, image=bg5, anchor="nw")
except Exception as e:
    print(f"Warning: Quiz Image not found. Using Green Background. {e}")

# Step 3: Create Widgets
# --- TOP SECTION ---
lbl_q_heading = tk.Label(page5, text="Question 1 / 10", font=("Comic Sans MS", 24, "bold"), bg="#FFFFFF", fg="#452929")
canvas5.create_window(600, 135, window=lbl_q_heading)

lbl_score = tk.Label(page5, text="Score: 0", font=("Comic Sans MS", 22, "bold"), bg="#4d8c57", fg="white")
canvas5.create_window(150, 80, window=lbl_score)

lbl_timer = tk.Label(page5, text="Time: 12s", font=("Comic Sans MS", 22, "bold"), bg="#4d8c57", fg="white")
canvas5.create_window(1050, 80, window=lbl_timer)

# --- CENTER SECTION ---
lbl_main_q = tk.Label(page5, text="Ready?", font=("Comic Sans MS", 50, "bold"), bg="#4d8c57", fg="white")
canvas5.create_window(600, 320, window=lbl_main_q)

entry_answer = tk.Entry(page5, font=("Arial", 30), width=12, justify="center")
entry_answer.place(x=450, y=400, width=300, height=60)

# Feedback Label
lbl_feedback = tk.Label(page5, text="", font=("Arial", 18, "bold"), bg="#4d8c57", fg="white")
canvas5.create_window(600, 500, window=lbl_feedback)

# Hint Section
lbl_hint_text = tk.Label(page5, text="", font=("Arial", 16, "italic"), bg="#4d8c57", fg="#FFD700")
canvas5.create_window(600, 260, window=lbl_hint_text)

btn_hint = tk.Button(page5, text="💡 Hint", font=("Arial", 12, "bold"), bg="#FFD700", fg="black", cursor="hand2", command=show_hint)
canvas5.create_window(820, 430, window=btn_hint)
add_button_effects(btn_hint)

# --- BOTTOM SECTION ---
btn_submit = tk.Button(page5, text="Submit", font=("Comic Sans MS", 20, "bold"), width=10, bg="#3b5a2c", fg="white", cursor="hand2", command=check_answer)
canvas5.create_window(600, 580, window=btn_submit)
add_button_effects(btn_submit)

btn_back_p5 = tk.Button(page5, text="Back", font=("Comic Sans MS", 16, "bold"), bg="#5a2c2c", fg="white", width=8, cursor="hand2", command=lambda: show_frame(page4))
canvas5.create_window(100, 620, window=btn_back_p5)
add_button_effects(btn_back_p5)

btn_finish = tk.Button(page5, text="Results", font=("Comic Sans MS", 16, "bold"), bg="#8b0000", fg="white", width=8, cursor="hand2", command=lambda: messagebox.showinfo("Current Status", f"Score: {score}"))
canvas5.create_window(1100, 620, window=btn_finish)
add_button_effects(btn_finish)

root.bind('<Return>', lambda event: check_answer())

# ---------------- START APP -------------------
page1.tkraise()
play_bg_music()
fade_in(root)
root.mainloop()
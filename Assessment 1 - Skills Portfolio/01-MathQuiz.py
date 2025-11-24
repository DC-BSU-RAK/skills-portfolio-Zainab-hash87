import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pygame
import time
import random
import json
import os

# Initialize Pygame Mixer for Audio
pygame.mixer.init()

# ---------------- GLOBAL VARIABLES -------------------
selected_difficulty = None
current_question = 0
score = 0
attempts_left = 2
correct_answer = 0
timer_seconds = 12
timer_running = False
user_name = "Player"

# Canvas Item IDs
id_score = None
id_timer = None
id_heading = None
id_main_q = None
id_feedback = None
id_hint = None

# Result Page IDs
id_final_score = None
id_rank_text = None
id_grade_text = None
id_leaderboard_text = None

# Confetti Data
confetti_particles = []
is_on_result_page = False

# CLOCK SOUND FIX: Store clock sound channel
clock_channel = None

# ---------------- SOUND SYSTEM -------------------
def play_bg_music():
    """Initializes and loops background music."""
    try:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load("welcome.mp3")
            pygame.mixer.music.play(-1) 
            pygame.mixer.music.set_volume(0.4)
    except:
        pass

def play_sfx(file):
    """Plays short sound effects."""
    try:
        sfx = pygame.mixer.Sound(file)
        sfx.set_volume(1.0)
        sfx.play()
    except:
        pass

def stop_clock_sound():
    """FIXED: Stops ONLY the clock sound channel."""
    global clock_channel
    if clock_channel and clock_channel.get_busy():
        clock_channel.stop()

def stop_all_sounds():
    """Stops BOTH background music and all sound effects."""
    pygame.mixer.music.stop()
    pygame.mixer.stop()

# ---------------- UI/UX HELPER FUNCTIONS -------------------
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
    if difficulty == 1: return random.randint(1, 9)
    elif difficulty == 2: return random.randint(10, 99)
    else: return random.randint(1000, 9999)

def decideOperation():
    return random.choice(["+", "-"])

def start_quiz(level):
    global selected_difficulty, current_question, score, is_on_result_page
    selected_difficulty = level
    current_question = 0
    score = 0
    is_on_result_page = False
    show_frame(page5)
    next_question()

def next_question():
    global current_question, attempts_left, correct_answer, timer_seconds, timer_running
    
    # FIXED: Stop clock sound from previous question
    stop_clock_sound()
    
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
            if num1 < num2: num1, num2 = num2, num1 
            correct_answer = num1 - num2
            q_text = f"{num1} - {num2} = ?"
            
        canvas5.itemconfigure(id_heading, text=f"Question {current_question} / 10")
        canvas5.itemconfigure(id_main_q, text=q_text)
        
        entry_answer.delete(0, tk.END)
        entry_answer.config(bg="white")
        entry_answer.focus()
        canvas5.itemconfigure(id_hint, text="")
        canvas5.itemconfigure(id_feedback, text="")
        
        update_score_label()
        countdown_timer()
        
    else:
        # --- GAME OVER ---
        timer_running = False
        stop_clock_sound()  # FIXED: Stop clock
        stop_all_sounds()   # Stop all sounds
        play_sfx("gameover.mp3")
        root.after(2000, show_results)

def countdown_timer():
    global timer_seconds, timer_running, clock_channel
    if timer_running:
        if timer_seconds > 0:
            fg_color = "#ff4444" if timer_seconds <= 5 else "white"
            
            # FIXED: Play clock sound ONLY ONCE when timer hits 5
            if timer_seconds == 5:
                try:
                    clock_sound = pygame.mixer.Sound("clock.wav")
                    clock_channel = clock_sound.play()
                except:
                    pass
            
            canvas5.itemconfigure(id_timer, text=f"Time: {timer_seconds}s", fill=fg_color)
            timer_seconds -= 1
            root.after(1000, countdown_timer)
        else:
            timer_running = False
            stop_clock_sound()  # FIXED: Stop clock when time's up
            canvas5.itemconfigure(id_timer, text="Time's Up!", fill="red")
            play_sfx("wrong.mp3")
            canvas5.itemconfigure(id_feedback, text="Time Up! Moving on...", fill="orange")
            root.after(2000, next_question)

def show_hint():
    if correct_answer % 2 == 0: hint_msg = "Hint: Answer is EVEN"
    else: hint_msg = "Hint: Answer is ODD"
    canvas5.itemconfigure(id_hint, text=hint_msg, fill="#FFD700")

def check_answer():
    global score, attempts_left, timer_running
    user_input = entry_answer.get()
    
    if not user_input.strip(): return

    try:
        user_ans = int(user_input)
    except ValueError:
        canvas5.itemconfigure(id_feedback, text="Numbers only please!", fill="yellow")
        return
    
    if user_ans == correct_answer:
        timer_running = False
        stop_clock_sound()  # FIXED: Stop clock on correct answer
        play_sfx("correct.mp3")
        flash_board("lightgreen")
        
        points = 10 if attempts_left == 2 else 5
        score += points
        
        canvas5.itemconfigure(id_feedback, text=f"Awesome! +{points} Points", fill="#00FF00")
        update_score_label()
        root.after(1500, next_question) 
        
    else:
        attempts_left -= 1
        play_sfx("wrong.mp3")
        shake_entry()
        
        if attempts_left > 0:
            canvas5.itemconfigure(id_feedback, text="Wrong! Try Again (+5 pts left)", fill="#FF4444")
            entry_answer.delete(0, tk.END)
        else:
            timer_running = False
            stop_clock_sound()  # FIXED: Stop clock
            canvas5.itemconfigure(id_feedback, text=f"Wrong! Answer was {correct_answer}", fill="red")
            root.after(2000, next_question)

def update_score_label():
    canvas5.itemconfigure(id_score, text=f"Score: {score}")

def shake_entry():
    original_x = 425
    offsets = [-10, 10, -8, 8, -5, 5, 0]
    delay = 50
    for offset in offsets:
        entry_answer.after(delay, lambda o=offset: entry_answer.place(x=original_x + o))
        delay += 50
    entry_answer.config(bg="#ffcccc")
    entry_answer.after(500, lambda: entry_answer.config(bg="white"))

def flash_board(color):
    try:
        flash = canvas5.create_rectangle(0,0,1200,700, fill=color, stipple="gray50")
        root.update()
        time.sleep(0.2)
        canvas5.delete(flash)
    except: pass

def update_leaderboard():
    leaderboard_file = "leaderboard.json"
    data = []
    
    # Try to read existing data
    if os.path.exists(leaderboard_file):
        try:
            with open(leaderboard_file, "r") as f:
                data = json.load(f)
        except:
            data = []
    
    # Add new score
    new_entry = {"name": user_name, "score": score}
    data.append(new_entry)
    
    # Sort by score (highest first) and keep top 3
    data = sorted(data, key=lambda x: x["score"], reverse=True)[:3]
    
    # Save back to file
    try:
        with open(leaderboard_file, "w") as f:
            json.dump(data, f, indent=4)
    except:
        pass
    
    return data

# ==============================================================================
#  PAGE 6: IMPROVED ANIMATION ENGINE
# ==============================================================================
def create_confetti():
    """Generates random colorful particles."""
    colors = ['#FFD700', '#FF0000', '#00FF00', '#00FFFF', '#FF00FF', '#FFFFFF', '#FFA500']
    for p in confetti_particles: 
        canvas6.delete(p["id"])
    confetti_particles.clear()
    
    for _ in range(80):  # More particles
        x = random.randint(0, 1200)
        y = random.randint(-700, 0)
        size = random.randint(6, 18)
        color = random.choice(colors)
        particle = canvas6.create_oval(x, y, x+size, y+size, fill=color, outline="")
        speed = random.randint(4, 10)
        sway = random.choice([-1, 0, 1])
        confetti_particles.append({"id": particle, "speed": speed, "sway": sway})

def animate_confetti_loop():
    """Enhanced confetti with sideways movement."""
    if not is_on_result_page: return
    
    for p in confetti_particles:
        canvas6.move(p["id"], p["sway"], p["speed"])
        coords = canvas6.coords(p["id"])
        if coords and coords[1] > 700:
            canvas6.move(p["id"], 0, -800)
            canvas6.move(p["id"], random.randint(-100, 100), 0)
            
    root.after(25, animate_confetti_loop)

def show_results():
    """FIXED: Properly stop all timers and sounds before showing results"""
    global is_on_result_page, timer_running
    
    # CRITICAL FIX: Stop timer completely
    timer_running = False
    stop_clock_sound()
    
    show_frame(page6)
    is_on_result_page = True
    
    # Clear previous confetti
    for p in confetti_particles:
        canvas6.delete(p["id"])
    confetti_particles.clear()
    
    if score >= 70:
        play_sfx("yay.mp3")
        create_confetti()
        animate_confetti_loop()
        root.after(3000, lambda: pygame.mixer.music.play(-1))
        
        if score >= 90:
            grade = "A+ (Math Wizard)"
            color = "#FFD700"
            msg = f"Outstanding, {user_name}!"
        else:
            grade = "B (Math Pro)"
            color = "#00FF00"
            msg = f"Excellent Work, {user_name}!"
    else:
        play_sfx("sad.mp3")
        if score >= 50:
            grade = "C (Good Try)"
            color = "#FFA500"
        else:
            grade = "D (Keep Practicing)"
            color = "#FF4444"
        msg = f"Keep Going, {user_name}!"
        root.after(4000, lambda: pygame.mixer.music.play(-1))

    canvas6.itemconfigure(id_rank_text, text=msg)
    canvas6.itemconfigure(id_grade_text, text=f"Grade: {grade}", fill=color)
    
    top_scores = update_leaderboard()
    lb_text = "TOP 3 SCORERS\n\n"
    medals = ["1st", "2nd", "3rd"]
    for idx, player in enumerate(top_scores):
        medal = medals[idx] if idx < 3 else ""
        lb_text += f"{medal} {player['name']} : {player['score']} pts\n"
    
    canvas6.itemconfigure(id_leaderboard_text, text=lb_text)
    animate_score(0, score)

def animate_score(current_val, target_val):
    if current_val <= target_val:
        canvas6.itemconfigure(id_final_score, text=f"Your Score: {current_val} / 100")
        root.after(20, animate_score, current_val + 1, target_val)

# ==============================================================================
#  MAIN WINDOW SETUP
# ==============================================================================
root = tk.Tk()
root.title("Maths Quiz")
root.geometry("1200x700")
root.resizable(False, False)

try: root.iconphoto(False, tk.PhotoImage(file="root-icon.png"))
except: pass

def show_frame(frame): frame.tkraise()

# --- PAGE 1 ---
page1 = tk.Frame(root); page1.place(relwidth=1, relheight=1)
try:
    bg1 = ImageTk.PhotoImage(Image.open("01-welcome.png").resize((1200, 700)))
    canvas1 = tk.Canvas(page1); canvas1.pack(fill="both", expand=True)
    canvas1.create_image(0, 0, image=bg1, anchor="nw")
    start_btn = tk.Button(page1, text="Let's Begin", font=("Comic Sans MS", 24, "bold"), bg="#452929", fg="white", cursor="hand2", command=lambda: show_frame(page2))
    canvas1.create_window(600, 580, window=start_btn); add_button_effects(start_btn)
except: pass

# --- PAGE 2 ---
page2 = tk.Frame(root); page2.place(relwidth=1, relheight=1)
try:
    bg2 = ImageTk.PhotoImage(Image.open("02-instruction.png").resize((1200, 700)))
    canvas2 = tk.Canvas(page2); canvas2.pack(fill="both", expand=True)
    canvas2.create_image(0, 0, image=bg2, anchor="nw")
    font_inst = ("Comic Sans MS", 18, "bold")
    canvas2.create_text(342, 355, text="•10 questions per round\n•10 points-1st try correct\n•5 points-2nd try correct", font=font_inst, fill="white", justify="center")
    canvas2.create_text(608, 512, text=" • Easy-1 digit numbers\n• Moderate-2 digits\n• Advanced-4 digits", font=font_inst, fill="white", justify="center")
    canvas2.create_text(890, 360, text="• Choose difficulty level\n• Solve math problems\n• Type your answer", font=font_inst, fill="white", justify="center")
    next_btn_p2 = tk.Button(page2, text="Next", font=("Comic Sans MS", 22, "bold"), bg="#452929", fg="white", cursor="hand2", command=lambda: show_frame(page3))
    canvas2.create_window(1015, 597, window=next_btn_p2); add_button_effects(next_btn_p2)
except: pass

# --- PAGE 3 ---
page3 = tk.Frame(root); page3.place(relwidth=1, relheight=1)
def save_name_and_next():
    global user_name
    typed = name_entry.get().strip()

    # Prevent empty name
    if typed == "":
        messagebox.showwarning("Name Required", "Please enter your name!")
        return

    user_name = typed  # Save correct name
    print("Name saved:", user_name)  # Debug check

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

# --- PAGE 4 ---
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
    canvas4.create_window(180, 612, window=btn_back_p4); add_button_effects(btn_back_p4)
except: pass

# ==============================================================================
#  PAGE 5 – QUIZ BOARD
# ==============================================================================
page5 = tk.Frame(root); page5.place(relwidth=1, relheight=1)
canvas5 = tk.Canvas(page5, bg="#4d8c57"); canvas5.pack(fill="both", expand=True)
try:
    bg5 = ImageTk.PhotoImage(Image.open("05-quiz.png").resize((1200, 700)))
    canvas5.create_image(0, 0, image=bg5, anchor="nw")
except: pass

id_heading = canvas5.create_text(590, 129, text="Question 1 / 10", font=("Comic Sans MS", 24, "bold"), fill="#452929")
id_score = canvas5.create_text(200, 110, text="Score: 0", font=("Comic Sans MS", 22, "bold"), fill="white")
id_timer = canvas5.create_text(990, 112, text="Time: 12s", font=("Comic Sans MS", 22, "bold"), fill="white")
id_main_q = canvas5.create_text(600, 320, text="Ready?", font=("Comic Sans MS", 50, "bold"), fill="white")
id_hint = canvas5.create_text(569, 260, text="", font=("Arial", 16, "italic"), fill="#FFD700")
id_feedback = canvas5.create_text(593, 500, text="", font=("Arial", 18, "bold"), fill="white")

entry_answer = tk.Entry(page5, font=("Arial", 30), width=12, justify="center")
entry_answer.place(x=425, y=400, width=300, height=60)
btn_hint = tk.Button(page5, text=" Hint", font=("Arial", 12, "bold"), bg="#FFD700", fg="black", cursor="hand2", command=show_hint)
canvas5.create_window(790, 430, window=btn_hint); add_button_effects(btn_hint)
btn_submit = tk.Button(page5, text="Submit", font=("Comic Sans MS", 20, "bold"), width=10, bg="#3b5a2c", fg="white", cursor="hand2", command=check_answer)
canvas5.create_window(580, 576, window=btn_submit); add_button_effects(btn_submit)
btn_back_p5 = tk.Button(page5, text="Back", font=("Comic Sans MS", 16, "bold"), bg="#5a2c2c", fg="white", width=8, cursor="hand2", command=lambda: show_frame(page4))
canvas5.create_window(180, 595, window=btn_back_p5); add_button_effects(btn_back_p5)
btn_finish = tk.Button(page5, text="Results", font=("Comic Sans MS", 16, "bold"), bg="#8b0000", fg="white", width=8, cursor="hand2", command=show_results)
canvas5.create_window(1015, 595, window=btn_finish); add_button_effects(btn_finish)
root.bind('<Return>', lambda event: check_answer())

# ==============================================================================
#  PAGE 6 – ELEGANT MINIMAL FRAME (SEMI-TRANSPARENT)
# ==============================================================================
page6 = tk.Frame(root); page6.place(relwidth=1, relheight=1)
canvas6 = tk.Canvas(page6, bg="#1a3a2a"); canvas6.pack(fill="both", expand=True)

# Background image (Results text visible)
try:
    bg6 = ImageTk.PhotoImage(Image.open("06-results.png").resize((1200, 700)))
    canvas6.create_image(0, 0, image=bg6, anchor="nw")
except Exception as e:
    print(f"Background image error: {e}")
    canvas6.create_rectangle(0, 0, 1200, 700, fill="#1a3a2a", outline="")

# ELEGANT MINIMAL FRAME - Smaller and Semi-transparent
frame_width = 560    # Reduced from 900
frame_height = 375   # Reduced from 500
frame_x = (1210 - frame_width) // 2
frame_y = (740 - frame_height) // 2 + 20  # Slightly lower to show "Results" text

# Semi-transparent effect using lighter colors
frame_bg = "#2d5a3d"  # Lighter background for transparency effect

# Main frame with subtle shadow
canvas6.create_rectangle(frame_x+3, frame_y+3, frame_x+frame_width+3, frame_y+frame_height+3, 
                         fill="#1a2a1a", outline="", stipple="gray50")  # Shadow with pattern

# Main frame - semi-transparent look
canvas6.create_rectangle(frame_x, frame_y, frame_x+frame_width, frame_y+frame_height, 
                         fill=frame_bg, outline="#F3EFD8", width=3)

# Inner glow effect
canvas6.create_rectangle(frame_x+8, frame_y+8, frame_x+frame_width-8, frame_y+frame_height-8, 
                         fill="", outline="#52a16d", width=1)

# Minimal corner accents (smaller)
corners = [
    (frame_x, frame_y), 
    (frame_x+frame_width, frame_y), 
    (frame_x, frame_y+frame_height), 
    (frame_x+frame_width, frame_y+frame_height)
]

for x, y in corners:
    canvas6.create_oval(x-5, y-5, x+5, y+5, fill="#EEEAD4", outline="#EBE5DB", width=1)

# CONTENT - Better spaced and aligned
center_x = frame_x + frame_width // 2

# Rank/Message - Moved higher
id_rank_text = canvas6.create_text(center_x, frame_y + 50, text="Well Done!", 
                                    font=("Comic Sans MS", 28, "bold"), fill="#F3E08A")

# Final Score
id_final_score = canvas6.create_text(center_x, frame_y + 110, text="Your Score: 0 / 100", 
                                      font=("Comic Sans MS", 24, "bold"), fill="white")

# Grade
id_grade_text = canvas6.create_text(center_x, frame_y + 160, text="Grade: A", 
                                     font=("Comic Sans MS", 22, "bold"), fill="#F8E88B")

# Subtle divider
canvas6.create_line(frame_x + 60, frame_y + 190, frame_x + frame_width - 60, frame_y + 190, 
                    fill="#E7E4CF", width=1, dash=(5, 3))

# Leaderboard - More compact
id_leaderboard_text = canvas6.create_text(center_x, frame_y + 270, text="", 
                                           font=("Arial", 14, "bold"), 
                                           fill="white", justify="center")

# PAGE 6 - BUTTONS WITH DIRECT PADDING
btn_play_again = tk.Button(page6, text=" Play Again", 
                           font=("Comic Sans MS", 16, "bold"), 
                           bg="#3b5a2c", fg="white", 
                           width=9,
                           cursor="hand2", 
                           command=lambda: show_frame(page4))
canvas6.create_window(410, 540, window=btn_play_again)
add_button_effects(btn_play_again)

btn_exit = tk.Button(page6, text="Exit", 
                     font=("Comic Sans MS", 16, "bold"), 
                     bg="#8b0000", fg="white",
                     width=9,
                     cursor="hand2", 
                     command=root.quit)
canvas6.create_window(810, 540, window=btn_exit)
add_button_effects(btn_exit)

# ---------------- START APP -------------------
page1.tkraise()
play_bg_music()
fade_in(root)
root.mainloop()
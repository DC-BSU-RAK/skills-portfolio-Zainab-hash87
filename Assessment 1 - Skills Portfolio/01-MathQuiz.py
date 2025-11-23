import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pygame
import time

pygame.mixer.init()

# ---------------- GLOBAL VARIABLES -------------------
selected_difficulty = None  # To store: 1 (Easy), 2 (Moderate), or 3 (Advanced)

# ---------------- SOUND FUNCTIONS (UPDATED) -------------------
def play_sound(file):
    try:
        # Change: Use Sound() instead of music.load() to allow overlapping sounds
        # Is se 'welcome' sound band nahi hoga jab button dabega
        sound = pygame.mixer.Sound(file)
        sound.play()
    except:
        pass 

# ---------------- BUTTON ANIMATION & SOUND HELPER -------------------
def add_button_effects(btn):
    """Adds hover animation and click sound to a button."""
    original_color = btn['bg']
    highlight_color = "#7d4e4e" 

    def on_enter(e):
        # Hover color tabhi aayega agar button abhi Gold (Selected) nahi hai
        if btn['bg'] != "#FFD700":
            btn['background'] = highlight_color

    def on_leave(e):
        if btn['bg'] != "#FFD700":
            btn['background'] = original_color

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
    except Exception as e:
        print(f"Fade in error: {e}")

# ---------------- MAIN APP WINDOW -------------------
root = tk.Tk()
root.title("Maths Quiz")
root.geometry("1200x700")
root.attributes("-alpha", 1.0)
root.resizable(False, False) # Fix window size

# --- ADDING ICON HERE ---
try:
    icon_img = tk.PhotoImage(file="root-icon.png")
    root.iconphoto(False, icon_img)
except Exception as e:
    print(f"Icon error: {e}") # Agar icon.png nahi mili to crash nahi hoga

# ---------------- SWITCH FRAME FUNCTION -------------------
def show_frame(frame):
    frame.tkraise()

# ---------------- DIFFICULTY LOGIC (HIGHLIGHT + JUMP) -------------------
def select_difficulty(level, btn_widget):
    global selected_difficulty
    selected_difficulty = level
    
    # 1. Button ko GOLD color karo (Highlight)
    btn_widget.config(bg="#FFD700", fg="black") # Gold background, Black text
    root.update() # Screen ko force karo update hone ke liye
    
    # 2. Thoda wait karo taake user color dekh sake
    time.sleep(0.3) 
    
    # 3. Move to Page 5
    print(f"Mode Selected: {level}") # Testing
    show_frame(page5)

# ---------------- PAGE 1 – WELCOME PAGE -------------------
page1 = tk.Frame(root)
page1.place(relwidth=1, relheight=1)

try:
    bg1 = Image.open("01-welcome.png").resize((1200, 700))
    bg1 = ImageTk.PhotoImage(bg1)
    canvas1 = tk.Canvas(page1)
    canvas1.pack(fill="both", expand=True)
    canvas1.create_image(0, 0, image=bg1, anchor="nw")
    
    start_btn = tk.Button(
        page1, text="Let's Begin", font=("Comic Sans MS", 24, "bold"),
        bg="#452929", fg="white", activebackground="#452929", activeforeground="white",
        cursor="hand2", command=lambda: show_frame(page2)
    )
    canvas1.create_window(600, 580, window=start_btn)
    add_button_effects(start_btn)
except Exception as e: print(f"Page 1 Error: {e}")

# ---------------- PAGE 2 – INSTRUCTIONS PAGE -------------------
page2 = tk.Frame(root)
page2.place(relwidth=1, relheight=1)

try:
    bg2 = Image.open("02-instruction.png").resize((1200, 700))
    bg2 = ImageTk.PhotoImage(bg2)
    canvas2 = tk.Canvas(page2)
    canvas2.pack(fill="both", expand=True)
    canvas2.create_image(0, 0, image=bg2, anchor="nw")
    
    instruction_font = ("Comic Sans MS", 18, "bold")
    canvas2.create_text(301, 365, text="•10 questions per round\n•10 points-1st try correct\n•5 points-2nd try correct", font=instruction_font, fill="white", justify="center")
    canvas2.create_text(580, 512, text="•Easy-1 digit numbers\n• Moderate-2 digits\n• Advanced-4 digits", font=instruction_font, fill="white", justify="center")
    canvas2.create_text(885, 368, text="• Choose difficulty level\n• Solve math problems\n• Type your answer", font=instruction_font, fill="white", justify="center")
    
    next_btn_page2 = tk.Button(
        page2, text="Next", font=("Comic Sans MS", 22, "bold"),
        bg="#452929", fg="white", cursor="hand2", command=lambda: show_frame(page3)
    )
    canvas2.create_window(1080, 620, window=next_btn_page2)
    add_button_effects(next_btn_page2)
except Exception as e: print(f"Page 2 Error: {e}")

# ---------------- PAGE 3 – ENTER LUCKY NAME -------------------
page3 = tk.Frame(root)
page3.place(relwidth=1, relheight=1)

try:
    bg3 = Image.open("03-name.png").resize((1200, 700))
    bg3 = ImageTk.PhotoImage(bg3)
    canvas3 = tk.Canvas(page3)
    canvas3.pack(fill="both", expand=True)
    canvas3.create_image(0, 0, image=bg3, anchor="nw")
    
    name_entry = tk.Entry(page3, font=("Arial", 24), width=20, justify="center")
    canvas3.create_window(600, 350, window=name_entry)
    
    back_btn_page3 = tk.Button(page3, text="Back to Instructions", font=("Comic Sans MS", 18, "bold"), bg="#5a2c2c", fg="white", cursor="hand2", command=lambda: show_frame(page2))
    next_btn_page3 = tk.Button(page3, text="Next", font=("Comic Sans MS", 18, "bold"), bg="#3b5a2c", fg="white", cursor="hand2", command=lambda: show_frame(page4))
    
    add_button_effects(back_btn_page3)
    add_button_effects(next_btn_page3)
    canvas3.create_window(450, 450, window=back_btn_page3)
    canvas3.create_window(750, 450, window=next_btn_page3)
except Exception as e: print(f"Page 3 Error: {e}")

# ---------------- PAGE 4 – DIFFICULTY SELECTION -------------------
page4 = tk.Frame(root)
page4.place(relwidth=1, relheight=1)

try:
    bg4 = Image.open("04-Difficulty.png").resize((1200, 700))
    bg4 = ImageTk.PhotoImage(bg4)
    
    canvas4 = tk.Canvas(page4)
    canvas4.pack(fill="both", expand=True)
    canvas4.create_image(0, 0, image=bg4, anchor="nw")
    
    # Common settings for buttons
    btn_font = ("Comic Sans MS", 22, "bold")
    btn_bg = "#452929"
    btn_fg = "white"
    
    # 1. Easy Button
    btn_easy = tk.Button(
        page4, text="Easy- 1 digit", font=btn_font, bg=btn_bg, fg=btn_fg,
        activebackground=btn_bg, activeforeground=btn_fg, width=15, cursor="hand2"
    )
    btn_easy.config(command=lambda: select_difficulty(1, btn_easy))
    canvas4.create_window(360, 320, window=btn_easy)
    add_button_effects(btn_easy)

    # 2. Moderate Button
    btn_mod = tk.Button(
        page4, text="Moderate- 2 digits", font=btn_font, bg=btn_bg, fg=btn_fg,
        activebackground=btn_bg, activeforeground=btn_fg, width=15, cursor="hand2"
    )
    btn_mod.config(command=lambda: select_difficulty(2, btn_mod))
    canvas4.create_window(510, 420, window=btn_mod)
    add_button_effects(btn_mod)

    # 3. Advanced Button
    btn_adv = tk.Button(
        page4, text="Advanced- 4 digits", font=btn_font, bg=btn_bg, fg=btn_fg,
        activebackground=btn_bg, activeforeground=btn_fg, width=15, cursor="hand2"
    )
    btn_adv.config(command=lambda: select_difficulty(3, btn_adv))
    canvas4.create_window(690, 510, window=btn_adv)
    add_button_effects(btn_adv)

    # ---------------- NEW BACK BUTTON ADDED HERE ----------------
    # Back Button (Bottom Left - Placed near the Star icon)
    btn_back_p4 = tk.Button(
        page4, 
        text="Back", 
        font=("Comic Sans MS", 16, "bold"), # Slightly smaller font
        bg="#5a2c2c", # Darker brown to distinguish from difficulty buttons
        fg="white", 
        activebackground="#5a2c2c", 
        activeforeground="white", 
        width=10,
        cursor="hand2",
        command=lambda: show_frame(page3) # Navigates back to the Name Page
    )
    # Placing it at coordinates (150, 620) to fill the empty space
    canvas4.create_window(180, 612, window=btn_back_p4)
    add_button_effects(btn_back_p4)
    # ------------------------------------------------------------

except Exception as e:
    print(f"Error loading Page 4: {e}")

# ---------------- PAGE 5 – QUIZ PAGE (Placeholder) -------------------
page5 = tk.Frame(root)
page5.place(relwidth=1, relheight=1)

try:
    # Use your Page 5 image here (e.g., "05-quiz.png")
    # For now, just a label to show it works
    tk.Label(page5, text="QUIZ PAGE LOADED!", font=("Arial", 40)).pack(pady=20)
    
    # Temp back button to test navigation
    tk.Button(page5, text="Back", command=lambda: show_frame(page4)).pack()
except:
    pass

# ---------------- START APP -------------------
page1.tkraise()
play_sound("welcome.mp3")
fade_in(root)
root.mainloop()
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pygame
import time

pygame.mixer.init()

# ---------------- GLOBAL VARIABLES -------------------
selected_difficulty = None  # To store: 1 (Easy), 2 (Moderate), or 3 (Advanced)

# ---------------- SOUND FUNCTIONS -------------------
def play_sound(file):
    try:
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
    except:
        pass  # If sound file is missing, continues without error

# ---------------- BUTTON ANIMATION & SOUND HELPER -------------------
def add_button_effects(btn):
    """Adds hover animation and click sound to a button."""
    original_color = btn['bg']
    
    # Define highlight color (Lighter Brown for all buttons now)
    highlight_color = "#7d4e4e" 

    def on_enter(e):
        btn['background'] = highlight_color

    def on_leave(e):
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

# ---------------- SWITCH FRAME FUNCTION -------------------
def show_frame(frame):
    frame.tkraise()

# ---------------- DIFFICULTY LOGIC -------------------
def select_difficulty(level):
    global selected_difficulty
    selected_difficulty = level
    
    if level == 1:
        mode = "Easy (1 Digit)"
    elif level == 2:
        mode = "Moderate (2 Digits)"
    else:
        mode = "Advanced (4 Digits)"
        
    messagebox.showinfo("Game Start", f"Starting Game in {mode} mode!\n(Page 5 coming soon...)")

# ---------------- PAGE 1 – WELCOME PAGE -------------------
page1 = tk.Frame(root)
page1.place(relwidth=1, relheight=1)

try:
    bg1 = Image.open("01-welcome.png") 
    bg1 = bg1.resize((1200, 700))
    bg1 = ImageTk.PhotoImage(bg1)
    
    canvas1 = tk.Canvas(page1)
    canvas1.pack(fill="both", expand=True)
    canvas1.create_image(0, 0, image=bg1, anchor="nw")
    
    start_btn = tk.Button(
        page1,
        text="Let's Begin",
        font=("Comic Sans MS", 24, "bold"),
        bg="#452929",
        fg="white",
        activebackground="#452929",
        activeforeground="white",
        cursor="hand2",
        command=lambda: show_frame(page2)
    )
    canvas1.create_window(600, 580, window=start_btn)
    add_button_effects(start_btn)
    
except Exception as e:
    print(f"Error loading Page 1: {e}")

# ---------------- PAGE 2 – INSTRUCTIONS PAGE -------------------
page2 = tk.Frame(root)
page2.place(relwidth=1, relheight=1)

try:
    bg2 = Image.open("02-instruction.png")
    bg2 = bg2.resize((1200, 700))
    bg2 = ImageTk.PhotoImage(bg2)
    
    canvas2 = tk.Canvas(page2)
    canvas2.pack(fill="both", expand=True)
    canvas2.create_image(0, 0, image=bg2, anchor="nw")
    
    instruction_font = ("Comic Sans MS", 18, "bold")
    instruction_fill = "#FFFFFF"
    
    # Oval 1 – Left
    canvas2.create_text(
        301, 365,
        text="•10 questions per round\n•10 points-1st try correct\n•5 points-2nd try correct",
        font=instruction_font,
        fill=instruction_fill,
        justify="center"
    )
    
    # Oval 2 – Middle
    canvas2.create_text(
        580, 512,
        text="•Easy-1 digit numbers\n• Moderate-2 digits\n• Advanced-4 digits",
        font=instruction_font,
        fill=instruction_fill,
        justify="center"
    )
    
    # Oval 3 – Right
    canvas2.create_text(
        885, 368, 
        text="• Choose difficulty level\n• Solve math problems\n• Type your answer",
        font=instruction_font,
        fill=instruction_fill,
        justify="center"
    )
    
    next_btn_page2 = tk.Button(
        page2,
        text="Next",
        font=("Comic Sans MS", 22, "bold"),
        bg="#452929",
        fg="white",
        activebackground="#452929",
        activeforeground="white",
        cursor="hand2",
        command=lambda: show_frame(page3)
    )
    canvas2.create_window(1080, 620, window=next_btn_page2)
    add_button_effects(next_btn_page2)

except Exception as e:
    print(f"Error loading Page 2: {e}")

# ---------------- PAGE 3 – ENTER LUCKY NAME -------------------
page3 = tk.Frame(root)
page3.place(relwidth=1, relheight=1)

try:
    bg3 = Image.open("03-name.png")
    bg3 = bg3.resize((1200, 700))
    bg3 = ImageTk.PhotoImage(bg3)
    
    canvas3 = tk.Canvas(page3)
    canvas3.pack(fill="both", expand=True)
    canvas3.create_image(0, 0, image=bg3, anchor="nw")
    
    name_entry = tk.Entry(page3, font=("Arial", 24), width=20, justify="center")
    canvas3.create_window(600, 350, window=name_entry)
    
    # Back Button
    back_btn_page3 = tk.Button(
        page3,
        text="Back to Instructions",
        font=("Comic Sans MS", 18, "bold"),
        bg="#5a2c2c",
        fg="white",
        activebackground="#5a2c2c",
        activeforeground="white",
        cursor="hand2",
        command=lambda: show_frame(page2)
    )
    add_button_effects(back_btn_page3)
    
    # Next Button -> Goes to Page 4
    next_btn_page3 = tk.Button(
        page3,
        text="Next",
        font=("Comic Sans MS", 18, "bold"),
        bg="#3b5a2c",
        fg="white",
        activebackground="#3b5a2c",
        activeforeground="white",
        cursor="hand2",
        command=lambda: show_frame(page4) 
    )
    add_button_effects(next_btn_page3)
    
    canvas3.create_window(450, 450, window=back_btn_page3)
    canvas3.create_window(750, 450, window=next_btn_page3)

except Exception as e:
    print(f"Error loading Page 3: {e}")

# ---------------- PAGE 4 – DIFFICULTY SELECTION -------------------
page4 = tk.Frame(root)
page4.place(relwidth=1, relheight=1)

try:
    # Ensure you have UPDATED this image (deleted white strokes)
    bg4 = Image.open("04-Difficulty.png") 
    bg4 = bg4.resize((1200, 700))
    bg4 = ImageTk.PhotoImage(bg4)
    
    canvas4 = tk.Canvas(page4)
    canvas4.pack(fill="both", expand=True)
    canvas4.create_image(0, 0, image=bg4, anchor="nw")
    
    # STYLE UPDATE: Back to Standard Brown Buttons
    btn_font = ("Comic Sans MS", 22, "bold")
    btn_bg = "#452929"
    btn_fg = "white"
    
    # 1. Easy Button
    btn_easy = tk.Button(
        page4,
        text="Easy- 1 digit",
        font=btn_font,
        bg=btn_bg,
        fg=btn_fg,
        activebackground=btn_bg,
        activeforeground=btn_fg,
        width=15,  # Fixed width for uniform look
        cursor="hand2",
        command=lambda: select_difficulty(1)
    )
    canvas4.create_window(360, 320, window=btn_easy)
    add_button_effects(btn_easy)

    # 2. Moderate Button
    btn_mod = tk.Button(
        page4,
        text="Moderate- 2 digits",
        font=btn_font,
        bg=btn_bg,
        fg=btn_fg,
        activebackground=btn_bg,
        activeforeground=btn_fg,
        width=15,
        cursor="hand2",
        command=lambda: select_difficulty(2)
    )
    canvas4.create_window(510, 420, window=btn_mod)
    add_button_effects(btn_mod)

    # 3. Advanced Button
    btn_adv = tk.Button(
        page4,
        text="Advanced- 4 digits",
        font=btn_font,
        bg=btn_bg,
        fg=btn_fg,
        activebackground=btn_bg,
        activeforeground=btn_fg,
        width=15,
        cursor="hand2",
        command=lambda: select_difficulty(3)
    )
    canvas4.create_window(690, 510, window=btn_adv)
    add_button_effects(btn_adv)

except Exception as e:
    print(f"Error loading Page 4: {e}")

# ---------------- START APP -------------------
page1.tkraise()
play_sound("welcome.mp3")
fade_in(root)
root.mainloop()
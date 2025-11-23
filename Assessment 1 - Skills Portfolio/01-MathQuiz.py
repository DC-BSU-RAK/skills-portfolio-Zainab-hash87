import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pygame
import time

pygame.mixer.init()

# ---------------- SOUND FUNCTIONS -------------------
def play_sound(file):
    try:
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
    except:
        pass  # If sound file is missing, game continues without error

# ---------------- FADE IN EFFECT -------------------
def fade_in(widget, delay=7):
    try:
        # Reset alpha to 0 before fading in
        widget.attributes("-alpha", 0.0)
        for i in range(0, 100, 5):  # Jump by 5 for faster fade
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
root.attributes("-alpha", 1.0)  # Ensure window is visible if fade fails

# ---------------- SWITCH FRAME FUNCTION -------------------
def show_frame(frame):
    frame.tkraise()
    # Optional: Play a click sound here if you have one
    # play_sound("click.mp3")

# ---------------- PAGE 1 – WELCOME PAGE -------------------
page1 = tk.Frame(root)
page1.place(relwidth=1, relheight=1)

# Note: Ensure this file exists as .png
try:
    bg1 = Image.open("01-welcome.png") 
    bg1 = bg1.resize((1200, 700))
    bg1 = ImageTk.PhotoImage(bg1)
    
    canvas1 = tk.Canvas(page1)
    canvas1.pack(fill="both", expand=True)
    canvas1.create_image(0, 0, image=bg1, anchor="nw")
    
    # Button: Let's Begin the Quiz
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
except Exception as e:
    print(f"Error loading Page 1 image: {e}")

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
    
    # ----------- FINAL INSTRUCTIONS INSIDE OVALS -----------
    instruction_font = ("Comic Sans MS", 18, "bold")
    instruction_fill = "#FFFFFF"  # White color as requested
    
   # Oval 1 – Left Side (Coordinates estimated for the left oval)
    canvas2.create_text(
        301, 365,  # x, y coordinates
        text="•10 questions per round\n•10 points-1st try correct\n•5 points-2nd try correct",
        font=instruction_font,
        fill=instruction_fill,
        justify="center"
    )
    
    # Oval 2 – Middle (Logic: Easy/Mod/Adv). 
    # Visual adjustment: The middle oval is lower on the board.
    canvas2.create_text(
        580, 512, # Lower center
        text="•Easy-1 digit numbers\n• Moderate-2 digits\n• Advanced-4 digits",
        font=instruction_font,
        fill=instruction_fill,
        justify="center"
    )
    
    # Oval 3 – Right Side
    canvas2.create_text(
        885, 368, 
        text="• Choose difficulty level\n• Solve math problems\n• Type your answer",
        font=instruction_font,
        fill=instruction_fill,
        justify="center"
    )
    
    # Navigation button – Page 2 -> Page 3
    # Moved to Bottom Right so it doesn't cover the middle text oval
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

except Exception as e:
    print(f"Error loading Page 2 image: {e}")

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
    
    # Title Text (Optional adjustment if needed)
    # Note: Use standard font if 'Lucky Name' isn't baked into image
    # canvas3.create_text(600, 200, text="Enter Your Lucky Name", font=("Comic Sans MS", 36, "bold"), fill="white")
    
    name_entry = tk.Entry(page3, font=("Arial", 24), width=20, justify="center")
    canvas3.create_window(600, 350, window=name_entry)
    
    # BUTTONS for Page 3
    
    # 1. Back to Instructions (Left side)
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
    
    # 2. Next (Right side)
    next_btn_page3 = tk.Button(
        page3,
        text="Next",
        font=("Comic Sans MS", 18, "bold"),
        bg="#3b5a2c",
        fg="white",
        activebackground="#3b5a2c",
        activeforeground="white",
        cursor="hand2",
        command=lambda: messagebox.showinfo("Next Step", f"Hello {name_entry.get()}! Difficulty Selection coming soon.")
    )
    
    # Placing buttons nicely below the entry box
    canvas3.create_window(450, 450, window=back_btn_page3)
    canvas3.create_window(750, 450, window=next_btn_page3)

except Exception as e:
    print(f"Error loading Page 3 image: {e}")

# ---------------- START APP -------------------
# Ensure page1 is shown first
page1.tkraise()
play_sound("welcome.mp3")
fade_in(root)
root.mainloop()
"""
PROGRAMMING SKILLS PORTFOLIO - EXERCISE 3: STUDENT MANAGER SYSTEM
Student Name: Zainab Afzal
University: Bath Spa University

REFERENCES & ACKNOWLEDGEMENTS:
1. CLASS RESOURCES:
   - File handling & GUI structure adapted from Module Lecture Notes.
   
2. EXTERNAL & AI SUPPORT:
   - Pillow Library: Used for advanced image processing (Brightness/Resizing).
   - UI Enhancements: Custom 'RoundedButton' class and Background Overlay logic 
     were developed with the assistance of Generative AI (Google Gemini).
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageEnhance  # External library for image processing
import os
from datetime import datetime

# --- CONSTANTS & THEME CONFIGURATION ---
# Centralized configuration for easy theming and maintenance
OXFORD_BLUE = "#002147"
SIDEBAR_BG = "#111827"
TEXT_WHITE = "#ffffff"
TEXT_DARK = "#1f2937"

# Dashboard Card Colors (Pastel palette for readability)
CARD_BLUE = "#e0f2fe"
CARD_GREEN = "#dcfce7"
CARD_GOLD = "#fef3c7"

# Button Styling
BTN_NORMAL = "#1f2937"
BTN_HOVER = "#374151"
BTN_TEXT_ACTIVE = "#fbbf24" # Gold accent on hover

# --- SMART FILE PATHS ---
# Uses os.path to ensure the application runs correctly on any operating system
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = os.path.join(BASE_DIR, "studentMarks.txt")
LOGO_PATH = os.path.join(BASE_DIR, "oxford-logo.png")
ICON_PATH = os.path.join(BASE_DIR, "uni-icon.png")
BG_PATH   = os.path.join(BASE_DIR, "oxford-bg.jpg")

# --- CUSTOM WIDGET CLASSES ---

class RoundedButton(tk.Canvas):
    """
    A custom UI component that simulates a modern rounded button.
    Inherits from Canvas to draw smooth shapes which standard Tkinter buttons lack.
    """
    def __init__(self, parent, text, command, width=220, height=45, corner_radius=20, color=BTN_NORMAL):
        super().__init__(parent, borderwidth=0, relief="flat", highlightthickness=0, bg=SIDEBAR_BG, width=width, height=height)
        self.command = command
        self.text = text
        self.color = color
        self.hover_color = BTN_HOVER
        self.active_text = BTN_TEXT_ACTIVE
        self.base_text = "#e5e7eb"

        # Draw the button shape and text
        self.rect = self.create_rounded_rect(2, 2, width-2, height-2, corner_radius, fill=color)
        self.text_item = self.create_text(width/2, height/2, text=text, fill=self.base_text, font=("Segoe UI", 11, "bold"))

        # Bind mouse events for hover effects
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        """Helper function to draw a polygon approximating a rounded rectangle."""
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def on_enter(self, event):
        """Changes appearance on mouse hover."""
        self.itemconfig(self.rect, fill=self.hover_color)
        self.itemconfig(self.text_item, fill=self.active_text)
        self.config(cursor="hand2")

    def on_leave(self, event):
        """Restores appearance when mouse leaves."""
        self.itemconfig(self.rect, fill=self.color)
        self.itemconfig(self.text_item, fill=self.base_text)

    def on_click(self, event):
        """Triggers the assigned command."""
        if self.command: self.command()

class StatCard(tk.Frame):
    """
    A reusable dashboard widget to display key metrics (Total, Average, etc.).
    Uses a frame with a colored background and border.
    """
    def __init__(self, parent, title, value, color, icon_char):
        super().__init__(parent, bg="white", bd=2, relief="groove")
        inner = tk.Frame(self, bg=color, padx=20, pady=15)
        inner.pack(fill="both", expand=True)
        
        # Icon
        tk.Label(inner, text=icon_char, font=("Segoe UI", 24), bg=color, fg=TEXT_DARK).pack(side="left", padx=(0, 15))
        
        # Text Data
        text_frame = tk.Frame(inner, bg=color)
        text_frame.pack(side="left")
        tk.Label(text_frame, text=title, font=("Segoe UI", 10, "bold"), bg=color, fg="#4b5563").pack(anchor="w")
        self.value_label = tk.Label(text_frame, text=value, font=("Segoe UI", 18, "bold"), bg=color, fg=TEXT_DARK)
        self.value_label.pack(anchor="w")

    def update_value(self, new_value):
        """Updates the displayed metric dynamically."""
        self.value_label.config(text=new_value)

# --- MAIN APPLICATION CONTROLLER ---

class StudentManagerFinal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("University of Oxford | Student Record System")
        self.geometry("1280x750")
        self.minsize(1100, 650)
        
        # Initialize Application State
        self.students = []
        self.logo_img = None
        self.app_icon = None 
        self.bg_photo = None 
        
        # Load resources before building UI
        self.load_data()
        self.load_assets()

        # Construct UI Hierarchy
        self.setup_header()
        
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.setup_sidebar(container)
        self.setup_dashboard(container)
        
        # Populate views with data
        self.refresh_table()

    def load_assets(self):
        """Loads and processes all external image assets."""
        # 1. Header Logo
        try:
            pil_img = Image.open(LOGO_PATH)
            # Maintain aspect ratio to prevent squeezing
            w, h = pil_img.size
            aspect = w / h
            new_w = int(70 * aspect)
            pil_img = pil_img.resize((new_w, 70), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(pil_img)
        except: self.logo_img = None

        # 2. Application Icon
        try:
            self.app_icon = ImageTk.PhotoImage(file=ICON_PATH)
            self.iconphoto(False, self.app_icon)
        except: pass

        # 3. Background Wallpaper
        try:
            bg_img = Image.open(BG_PATH)
            bg_img = bg_img.resize((1600, 1000), Image.Resampling.LANCZOS)
            
            # Darken image to ensure white text readability (Accessibility)
            enhancer = ImageEnhance.Brightness(bg_img)
            bg_img = enhancer.enhance(0.3) 
            
            self.bg_photo = ImageTk.PhotoImage(bg_img)
        except: self.bg_photo = None

    def setup_header(self):
        """Builds the top navigation bar."""
        header = tk.Frame(self, bg=OXFORD_BLUE, height=100)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        # Branding Section
        left_box = tk.Frame(header, bg=OXFORD_BLUE)
        left_box.pack(side="left", padx=30)

        if self.logo_img:
            tk.Label(left_box, image=self.logo_img, bg=OXFORD_BLUE).pack(side="left", padx=(0, 15))

        title_box = tk.Frame(left_box, bg=OXFORD_BLUE)
        title_box.pack(side="left")
        tk.Label(title_box, text="UNIVERSITY OF", font=("Times New Roman", 10), fg="#9ca3af", bg=OXFORD_BLUE).pack(anchor="w")
        tk.Label(title_box, text="OXFORD", font=("Times New Roman", 22, "bold"), fg=TEXT_WHITE, bg=OXFORD_BLUE).pack(anchor="w")

        # User Profile Section
        right_box = tk.Frame(header, bg=OXFORD_BLUE)
        right_box.pack(side="right", padx=30)
        
        def logout():
            if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
                self.destroy()

        def show_profile():
            now_time = datetime.now().strftime("%H:%M %p | %d %b %Y")
            msg = f"User: Zainab Afzal\nRole: Administrator\n\nCourse Leader: Arshiya S\nCampus: RAK Academic Centre\n\nSystem Time: {now_time}"
            messagebox.showinfo("User Profile", msg)

        tk.Button(right_box, text="Logout ➜", bg=OXFORD_BLUE, fg=TEXT_WHITE, bd=0, font=("Segoe UI", 10, "bold"),
                  activebackground=OXFORD_BLUE, activeforeground="#fbbf24", cursor="hand2",
                  command=logout).pack(side="right")
        
        tk.Label(right_box, text=" | ", fg="gray", bg=OXFORD_BLUE).pack(side="right", padx=10)
        
        tk.Button(right_box, text="👤 Zainab Afzal (Admin)", font=("Segoe UI", 11, "bold"), 
                  bg=OXFORD_BLUE, fg=TEXT_WHITE, bd=0, cursor="hand2",
                  activebackground=OXFORD_BLUE, activeforeground="#fbbf24",
                  command=show_profile).pack(side="right")

    def setup_sidebar(self, parent):
        """Builds the collapsible navigation sidebar."""
        sidebar = tk.Frame(parent, bg=SIDEBAR_BG, width=260)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="DASHBOARD", fg="#6b7280", bg=SIDEBAR_BG, font=("Segoe UI", 9, "bold")).pack(pady=(30, 15))

        # Menu Options
        btns = [
            ("📊 View All Records", self.refresh_table),
            ("🏆 Highest Score", self.show_highest),
            ("📉 Lowest Score", self.show_lowest),
            ("🔃 Sort by Score", lambda: self.sort_data('score')),
            ("🔤 Sort by Name", lambda: self.sort_data('name')),
            ("➕ Add Student", self.add_record),
            ("✏️ Update Record", self.edit_record),
            ("🗑️ Delete Record", self.delete_record)
        ]
        
        for txt, cmd in btns:
            RoundedButton(sidebar, text=txt, command=cmd).pack(pady=10)

    def setup_dashboard(self, parent):
        """Constructs the main dashboard area with background and widgets."""
        self.main_canvas = tk.Canvas(parent, bg="#f3f4f6", highlightthickness=0)
        self.main_canvas.pack(side="right", fill="both", expand=True)

        if self.bg_photo:
            self.main_canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        # --- FLOATING SEARCH BAR ---
        search_card = tk.Frame(self.main_canvas, bg="white", bd=1, relief="solid", padx=10, pady=5)
        tk.Label(search_card, text="Search:", font=("Segoe UI", 10, "bold"), bg="white", fg="#666").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_data)
        tk.Entry(search_card, textvariable=self.search_var, bd=0, bg="white", width=25, font=("Segoe UI", 11)).pack(side="left", padx=5)
        
        self.main_canvas.create_window(950, 30, window=search_card, anchor="ne", width=300, height=45)

        # --- PAGE TITLE ---
        self.main_canvas.create_text(30, 40, text="Student Performance Records", 
                                     font=("Segoe UI", 24, "bold"), fill="white", anchor="nw")

        # --- STATS ROW ---
        self.card_total = StatCard(self.main_canvas, "Total Students", "0", CARD_BLUE, "👥")
        self.main_canvas.create_window(30, 110, window=self.card_total, anchor="nw", width=300, height=100)

        self.card_avg = StatCard(self.main_canvas, "Class Average", "0%", CARD_GREEN, "📊")
        self.main_canvas.create_window(350, 110, window=self.card_avg, anchor="nw", width=300, height=100)

        self.card_top = StatCard(self.main_canvas, "Top Performer", "-", CARD_GOLD, "🏆")
        self.main_canvas.create_window(670, 110, window=self.card_top, anchor="nw", width=300, height=100)

        # --- DATA TABLE AREA ---
        self.table_card = tk.Frame(self.main_canvas, bg="white", bd=2, relief="groove")
        
        # Responsive binding logic
        self.main_canvas.bind("<Configure>", self.on_resize)

        # Initial Placement
        self.table_window = self.main_canvas.create_window(30, 240, window=self.table_card, anchor="nw", width=940, height=450)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=35, font=("Segoe UI", 10), background="white", fieldbackground="white", borderwidth=0)
        style.configure("Treeview.Heading", background="#f8fafc", font=("Segoe UI", 10, "bold"), foreground=TEXT_DARK)
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})]) 

        cols = ("ID", "Name", "CW", "Exam", "Total", "Grade")
        self.tree = ttk.Treeview(self.table_card, columns=cols, show="headings", selectmode="browse")
        
        headers = ["Student ID", "Full Name", "Coursework /60", "Exam /100", "Total %", "Grade"]
        widths = [100, 250, 100, 100, 100, 80]
        for c, h, w in zip(cols, headers, widths):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor="center")
        self.tree.column("Name", anchor="w", width=250)

        sb = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # Conditional Formatting Tags
        self.tree.tag_configure('A', foreground="#16a34a", font=("Segoe UI", 10, "bold"))
        self.tree.tag_configure('F', foreground="#dc2626", font=("Segoe UI", 10, "bold"))

    def on_resize(self, event):
        """Dynamic Resizing of the table when window size changes."""
        new_width = event.width - 60  
        new_height = event.height - 270 
        if new_width > 500 and new_height > 200:
            self.main_canvas.itemconfigure(self.table_window, width=new_width, height=new_height)

    # --- BUSINESS LOGIC & DATA HANDLING ---

    def load_data(self):
        """Reads and parses the studentMarks.txt file."""
        self.students = []
        if not os.path.exists(FILE_NAME):
            with open(FILE_NAME, "w") as f: f.write("0\n")
            return
        try:
            with open(FILE_NAME, "r") as f:
                lines = f.readlines()
                for line in lines[1:]: # Skip header count
                    p = line.strip().split(',')
                    if len(p) >= 6:
                        cw_t = int(p[2])+int(p[3])+int(p[4])
                        ovr = cw_t + int(p[5])
                        perc = (ovr/160)*100
                        gd = self.get_grade(perc)
                        self.students.append({"id":p[0], "name":p[1], "cw":[int(p[2]),int(p[3]),int(p[4])], "exam":int(p[5]), "cw_total":cw_t, "total":ovr, "perc":round(perc,1), "grade":gd})
        except: pass

    def get_grade(self, p):
        """Returns grade letter based on percentage."""
        if p>=70: return 'A'
        elif p>=60: return 'B'
        elif p>=50: return 'C'
        elif p>=40: return 'D'
        else: return 'F'

    def save_data(self):
        """Writes current application state back to the text file."""
        try:
            with open(FILE_NAME, "w") as f:
                f.write(f"{len(self.students)}\n")
                for s in self.students:
                    f.write(f"{s['id']},{s['name']},{s['cw'][0]},{s['cw'][1]},{s['cw'][2]},{s['exam']}\n")
            self.refresh_table()
            messagebox.showinfo("Saved", "Record updated successfully.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def refresh_table(self, data=None):
        """Refreshes the Treeview and updates Summary Statistics."""
        if data is None: data = self.students
        for r in self.tree.get_children(): self.tree.delete(r)
        
        total_sum = 0
        top_student = "-"
        max_score = -1

        for s in data:
            total_sum += s['perc']
            if s['perc'] > max_score:
                max_score = s['perc']
                top_student = s['name'].split()[0] # Display first name only

            # Apply color formatting
            tag = 'A' if s['grade'] == 'A' else ('F' if s['grade'] == 'F' else '')
            self.tree.insert("", "end", values=(s['id'], s['name'], f"{s['cw_total']}", f"{s['exam']}", f"{s['perc']}%", s['grade']), tags=(tag,))

        # Update Dashboard Stats Cards
        count = len(data)
        avg = round(total_sum / count, 1) if count > 0 else 0
        
        self.card_total.update_value(str(count))
        self.card_avg.update_value(f"{avg}%")
        self.card_top.update_value(top_student if count > 0 else "-")

    def filter_data(self, *args):
        """Live search filter functionality."""
        q = self.search_var.get().lower()
        self.refresh_table([s for s in self.students if q in s['name'].lower() or q in str(s['id'])])

    def sort_data(self, key):
        """Sorts list based on key (Score or Name)."""
        if key == 'score': self.students.sort(key=lambda x: x['total'], reverse=True)
        else: self.students.sort(key=lambda x: x['name'])
        self.refresh_table()

    # --- CRUD ACTIONS ---
    def show_highest(self):
        if self.students:
            top = max(self.students, key=lambda x: x['perc'])
            messagebox.showinfo("Top", f"Top Student: {top['name']} ({top['perc']}%)")
            
    def show_lowest(self):
        if self.students:
            low = min(self.students, key=lambda x: x['perc'])
            messagebox.showinfo("Low", f"Lowest Student: {low['name']} ({low['perc']}%)")
            
    def delete_record(self):
        sel = self.tree.selection()
        if sel and messagebox.askyesno("Delete", "Are you sure you want to delete this record?"):
            sid = str(self.tree.item(sel[0])['values'][0])
            self.students = [s for s in self.students if str(s['id']) != sid]
            self.save_data()
            
    def add_record(self): self.open_form("Add New Student")
    
    def edit_record(self):
        sel = self.tree.selection()
        if sel:
            sid = str(self.tree.item(sel[0])['values'][0])
            st = next((s for s in self.students if str(s['id']) == sid), None)
            if st: self.open_form("Update Student", st)
        else: messagebox.showwarning("Warning", "Select a student first")

    def open_form(self, title, data=None):
        """Opens a form window for Add/Edit operations."""
        win = tk.Toplevel(self)
        win.title(title)
        win.geometry("400x600")
        win.configure(bg="white")
        if self.app_icon: win.iconphoto(False, self.app_icon)
        
        tk.Label(win, text=title, font=("Segoe UI", 14, "bold"), bg="white", fg=OXFORD_BLUE).pack(pady=20)
        
        entries = {}
        fields = [("ID (4 digit)", "id"), ("Name", "name"), ("CW1 (0-20)", "c1"), ("CW2", "c2"), ("CW3", "c3"), ("Exam (0-100)", "ex")]
        
        for l, k in fields:
            f = tk.Frame(win, bg="white")
            f.pack(fill="x", padx=40, pady=5)
            tk.Label(f, text=l, bg="white", anchor="w").pack(fill="x")
            e = tk.Entry(f, bd=1, relief="solid")
            e.pack(fill="x")
            entries[k] = e
            
        if data:
            entries['id'].insert(0, data['id'])
            entries['id'].config(state="disabled") # ID cannot be changed in edit mode
            entries['name'].insert(0, data['name'])
            entries['c1'].insert(0, data['cw'][0]); entries['c2'].insert(0, data['cw'][1]); entries['c3'].insert(0, data['cw'][2])
            entries['ex'].insert(0, data['exam'])

        def save():
            """Validates inputs and saves data to list."""
            try:
                nid = entries['id'].get()
                cw = [int(entries['c1'].get()), int(entries['c2'].get()), int(entries['c3'].get())]
                ex = int(entries['ex'].get())
                
                # Validation Logic
                if any(x<0 or x>20 for x in cw) or ex<0 or ex>100: raise ValueError
                
                cw_t = sum(cw); ovr = cw_t + ex; perc = (ovr/160)*100
                rec = {"id":nid, "name":entries['name'].get(), "cw":cw, "exam":ex, "cw_total":cw_t, "total":ovr, "perc":round(perc,1), "grade":self.get_grade(perc)}
                
                if data:
                    for i,s in enumerate(self.students): 
                        if str(s['id'])==str(nid): self.students[i]=rec
                else:
                    if any(s['id']==nid for s in self.students): 
                        messagebox.showerror("Error", "ID Exists"); return
                    self.students.append(rec)
                self.save_data(); win.destroy()
            except: messagebox.showerror("Error", "Check inputs: Marks must be valid numbers within range.")

        tk.Button(win, text="SAVE", bg=OXFORD_BLUE, fg="white", font=("bold"), command=save).pack(side="bottom", pady=20)

if __name__ == "__main__":
    app = StudentManagerFinal()
    app.mainloop()
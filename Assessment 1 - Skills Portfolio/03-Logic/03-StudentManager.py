import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk  # Requires: pip install pillow
import os

# --- COLORS & THEME CONFIGURATION ---
OXFORD_BLUE = "#002147"
HEADER_TEXT = "#ffffff"
SIDEBAR_BG = "#111827"
MAIN_BG = "#f3f4f6"

# Button Colors (Interactive)
BTN_NORMAL = "#1f2937"      # Dark
BTN_HOVER = "#374151"       # Lighter
BTN_TEXT_NORMAL = "#e5e7eb"
BTN_TEXT_ACTIVE = "#fbbf24" # Gold Color for Active/Hover

# --- SMART PATH ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = os.path.join(BASE_DIR, "studentMarks.txt")
LOGO_PATH = os.path.join(BASE_DIR, "oxford-logo.png")

# --- CUSTOM OVAL BUTTON CLASS (For Extra Marks!) ---
class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, width=200, height=45, corner_radius=20, color=BTN_NORMAL, text_color=BTN_TEXT_NORMAL):
        super().__init__(parent, borderwidth=0, relief="flat", highlightthickness=0, bg=SIDEBAR_BG, width=width, height=height)
        self.command = command
        self.text = text
        self.color = color
        self.hover_color = BTN_HOVER
        self.text_color = text_color
        self.active_text_color = BTN_TEXT_ACTIVE
        self.corner_radius = corner_radius

        # Draw the button
        self.rect = self.round_rectangle(2, 2, width-2, height-2, radius=corner_radius, fill=color)
        self.text_item = self.create_text(width/2, height/2, text=text, fill=text_color, font=("Segoe UI", 11, "bold"))

        # Bind Events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.text_item_id = self.find_all()[1] # Get ID of text

    def round_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1+radius,
                  x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def on_enter(self, event):
        self.itemconfig(self.rect, fill=self.hover_color)
        self.itemconfig(self.text_item, fill=self.active_text_color)
        self.config(cursor="hand2")

    def on_leave(self, event):
        self.itemconfig(self.rect, fill=self.color)
        self.itemconfig(self.text_item, fill=self.text_color)

    def on_click(self, event):
        if self.command:
            self.command()

class StudentManagerFinal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("University of Oxford | Student Record System")
        self.geometry("1200x750")
        self.configure(bg=MAIN_BG)
        self.minsize(1000, 650)
        
        self.students = []
        self.logo_img = None
        self.load_data()
        self.load_assets()

        # --- LAYOUT ---
        self.setup_header()
        
        container = tk.Frame(self, bg=MAIN_BG)
        container.pack(fill="both", expand=True)

        self.setup_sidebar(container)
        self.setup_main_content(container)
        
        self.refresh_table()

    def load_assets(self):
        """Loads logo and preserves Aspect Ratio (Fixes Squeezed Logo)."""
        try:
            pil_img = Image.open(LOGO_PATH)
            # Calculate aspect ratio to keep it looking good
            original_width, original_height = pil_img.size
            target_height = 80
            aspect_ratio = original_width / original_height
            new_width = int(target_height * aspect_ratio)
            
            pil_img = pil_img.resize((new_width, target_height), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(pil_img)
        except Exception as e:
            print(f"Logo Error: {e}")
            self.logo_img = None

    def setup_header(self):
        header = tk.Frame(self, bg=OXFORD_BLUE, height=110)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        logo_frame = tk.Frame(header, bg=OXFORD_BLUE)
        logo_frame.pack(side="left", padx=30, pady=10)

        if self.logo_img:
            tk.Label(logo_frame, image=self.logo_img, bg=OXFORD_BLUE).pack(side="left")

        title_frame = tk.Frame(logo_frame, bg=OXFORD_BLUE, padx=20)
        title_frame.pack(side="left")
        tk.Label(title_frame, text="UNIVERSITY OF", font=("Times New Roman", 12), fg=HEADER_TEXT, bg=OXFORD_BLUE).pack(anchor="w")
        tk.Label(title_frame, text="OXFORD", font=("Times New Roman", 26, "bold"), fg=HEADER_TEXT, bg=OXFORD_BLUE).pack(anchor="w")

    def setup_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=SIDEBAR_BG, width=260)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="MAIN MENU", fg="#9ca3af", bg=SIDEBAR_BG, font=("Segoe UI", 10, "bold")).pack(pady=(40, 20))

        # --- USING CUSTOM ROUNDED BUTTONS ---
        # Added spacing (pady) to make sidebar not look "too long" or cluttered
        
        btn_data = [
            ("📊 View All Records", self.refresh_table),
            ("🏆 Highest Score", self.show_highest),
            ("📉 Lowest Score", self.show_lowest),
            ("🔃 Sort by Score", lambda: self.sort_data('score')),
            ("🔤 Sort by Name", lambda: self.sort_data('name')),
            ("➕ Add Student", self.add_record),
            ("✏️ Update Record", self.edit_record),
            ("🗑️ Delete Record", self.delete_record)
        ]

        for text, cmd in btn_data:
            btn = RoundedButton(sidebar, text=text, command=cmd)
            btn.pack(pady=8) # Space between buttons

    def setup_main_content(self, parent):
        content_frame = tk.Frame(parent, bg=MAIN_BG)
        content_frame.pack(side="right", fill="both", expand=True, padx=30, pady=30)

        # Title & Search
        top_bar = tk.Frame(content_frame, bg=MAIN_BG)
        top_bar.pack(fill="x", pady=(0, 20))
        tk.Label(top_bar, text="Student Performance Data", font=("Segoe UI", 24, "bold"), bg=MAIN_BG, fg="#111827").pack(side="left")

        # Search Bar
        search_fr = tk.Frame(top_bar, bg="white", padx=10, pady=5, bd=1, relief="solid")
        search_fr.pack(side="right")
        tk.Label(search_fr, text="🔍", bg="white").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_data)
        tk.Entry(search_fr, textvariable=self.search_var, font=("Segoe UI", 11), bd=0, bg="white", width=25).pack(side="left")

        # Stats
        self.stats_label = tk.Label(content_frame, text="Loading...", font=("Segoe UI", 12), bg=MAIN_BG, fg="#4b5563")
        self.stats_label.pack(anchor="w", pady=(0, 10))

        # Table
        table_frame = tk.Frame(content_frame, bg="white", bd=1, relief="solid")
        table_frame.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=35, font=("Segoe UI", 10), background="white", fieldbackground="white")
        style.configure("Treeview.Heading", background="#f3f4f6", font=("Segoe UI", 10, "bold"), foreground="#111827")
        style.map("Treeview", background=[('selected', OXFORD_BLUE)])
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

        cols = ("ID", "Name", "CW", "Exam", "Total", "Grade")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")
        
        headers = ["Student ID", "Full Name", "Coursework", "Exam", "Total %", "Grade"]
        widths = [100, 200, 100, 100, 100, 80]
        
        for col, h, w in zip(cols, headers, widths):
            self.tree.heading(col, text=h)
            self.tree.column(col, width=w, anchor="center")
        self.tree.column("Name", anchor="w", width=250)

        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # Tags for Colors
        self.tree.tag_configure('A_grade', foreground="#16a34a", font=("Segoe UI", 10, "bold")) # Green
        self.tree.tag_configure('F_grade', foreground="#dc2626", font=("Segoe UI", 10, "bold")) # Red

    # --- DATA LOGIC ---
    def load_data(self):
        self.students = []
        if not os.path.exists(FILE_NAME):
            with open(FILE_NAME, "w") as f: f.write("0\n")
            return
        try:
            with open(FILE_NAME, "r") as f:
                lines = f.readlines()
                for line in lines[1:]:
                    parts = line.strip().split(',')
                    if len(parts) >= 6:
                        cw_tot = int(parts[2]) + int(parts[3]) + int(parts[4])
                        ovr = cw_tot + int(parts[5])
                        perc = (ovr / 160) * 100
                        grade = self.calculate_grade(perc)
                        self.students.append({
                            "id": parts[0], "name": parts[1], "cw": [int(parts[2]), int(parts[3]), int(parts[4])],
                            "exam": int(parts[5]), "cw_total": cw_tot, "total": ovr, "perc": round(perc, 1), "grade": grade
                        })
        except: pass

    def calculate_grade(self, p):
        if p >= 70: return 'A'
        elif p >= 60: return 'B'
        elif p >= 50: return 'C'
        elif p >= 40: return 'D'
        else: return 'F'

    def save_data(self):
        try:
            with open(FILE_NAME, "w") as f:
                f.write(f"{len(self.students)}\n")
                for s in self.students:
                    f.write(f"{s['id']},{s['name']},{s['cw'][0]},{s['cw'][1]},{s['cw'][2]},{s['exam']}\n")
            self.refresh_table()
            messagebox.showinfo("Success", "Data Saved!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_table(self, data=None):
        if data is None: data = self.students
        for row in self.tree.get_children(): self.tree.delete(row)
        
        total_sum = 0
        for s in data:
            total_sum += s['perc']
            tag = 'A_grade' if s['grade'] == 'A' else ('F_grade' if s['grade'] == 'F' else '')
            self.tree.insert("", "end", values=(s['id'], s['name'], f"{s['cw_total']}/60", f"{s['exam']}/100", f"{s['perc']}%", s['grade']), tags=(tag,))
        
        avg = round(total_sum / len(data), 1) if data else 0
        self.stats_label.config(text=f"Total Records: {len(data)}   |   Class Average: {avg}%")

    def filter_data(self, *args):
        q = self.search_var.get().lower()
        self.refresh_table([s for s in self.students if q in s['name'].lower() or q in str(s['id'])])

    def sort_data(self, key):
        if key == 'score': self.students.sort(key=lambda x: x['total'], reverse=True)
        else: self.students.sort(key=lambda x: x['name'])
        self.refresh_table()

    # --- ACTIONS ---
    def delete_record(self):
        sel = self.tree.selection()
        if sel and messagebox.askyesno("Delete", "Are you sure?"):
            sid = str(self.tree.item(sel[0])['values'][0])
            self.students = [s for s in self.students if str(s['id']) != sid]
            self.save_data()

    def show_highest(self):
        if self.students:
            top = max(self.students, key=lambda x: x['perc'])
            messagebox.showinfo("Highest", f"Top Student: {top['name']} ({top['perc']}%)")

    def show_lowest(self):
        if self.students:
            low = min(self.students, key=lambda x: x['perc'])
            messagebox.showinfo("Lowest", f"Lowest Student: {low['name']} ({low['perc']}%)")

    def add_record(self): self.open_form("Add New Student")
    def edit_record(self):
        sel = self.tree.selection()
        if sel:
            sid = str(self.tree.item(sel[0])['values'][0])
            st = next((s for s in self.students if str(s['id']) == sid), None)
            if st: self.open_form("Update Student", st)
        else: messagebox.showwarning("Warning", "Select a student first")

    # --- FORM WINDOW FIXED (ISSUE 1 SOLVED) ---
    def open_form(self, title, data=None):
        win = tk.Toplevel(self)
        win.title(title)
        # Increased Height to 600 so button is visible!
        win.geometry("400x600") 
        win.configure(bg="white")
        
        tk.Label(win, text=title, font=("Segoe UI", 16, "bold"), bg="white", fg=OXFORD_BLUE).pack(pady=20)

        entries = {}
        fields = [("Student ID", "id"), ("Full Name", "name"), ("CW 1 (0-20)", "c1"), ("CW 2 (0-20)", "c2"), ("CW 3 (0-20)", "c3"), ("Exam (0-100)", "ex")]

        for lbl, key in fields:
            f = tk.Frame(win, bg="white")
            f.pack(fill="x", padx=40, pady=5)
            tk.Label(f, text=lbl, bg="white", anchor="w").pack(fill="x")
            e = tk.Entry(f, bd=1, relief="solid", font=("Segoe UI", 11))
            e.pack(fill="x")
            entries[key] = e

        if data:
            entries['id'].insert(0, data['id'])
            entries['id'].config(state="disabled")
            entries['name'].insert(0, data['name'])
            entries['c1'].insert(0, data['cw'][0])
            entries['c2'].insert(0, data['cw'][1])
            entries['c3'].insert(0, data['cw'][2])
            entries['ex'].insert(0, data['exam'])

        def save():
            try:
                new_id = entries['id'].get()
                cw = [int(entries['c1'].get()), int(entries['c2'].get()), int(entries['c3'].get())]
                ex = int(entries['ex'].get())
                
                if any(x < 0 or x > 20 for x in cw) or (ex < 0 or ex > 100):
                    raise ValueError("Marks out of range")

                cw_tot = sum(cw)
                ovr = cw_tot + ex
                perc = (ovr / 160) * 100
                
                rec = {
                    "id": new_id, "name": entries['name'].get(), "cw": cw, "exam": ex,
                    "cw_total": cw_tot, "total": ovr, "perc": round(perc, 1), "grade": self.calculate_grade(perc)
                }

                if data:
                    for i, s in enumerate(self.students):
                        if str(s['id']) == str(new_id): self.students[i] = rec
                else:
                    if any(s['id'] == new_id for s in self.students):
                        messagebox.showerror("Error", "ID Exists")
                        return
                    self.students.append(rec)
                
                self.save_data()
                win.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid Marks")

        # Added plenty of padding at bottom to ensure visibility
        tk.Button(win, text="SAVE RECORD", bg=OXFORD_BLUE, fg="white", font=("Segoe UI", 11, "bold"),
                  padx=20, pady=8, cursor="hand2", command=save).pack(side="bottom", pady=30)

if __name__ == "__main__":
    app = StudentManagerFinal()
    app.mainloop()
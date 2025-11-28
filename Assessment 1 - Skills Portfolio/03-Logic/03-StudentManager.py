import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk  # Requires: pip install pillow
import os

# --- COLORS & FONTS (Oxford + Modern Dark Theme) ---
OXFORD_BLUE = "#002147"       # Official Oxford Blue
SIDEBAR_BG = "#111827"        # Dark modern sidebar
SIDEBAR_BTN_DEFAULT = "#111827"
SIDEBAR_BTN_HOVER = "#374151" # Lighter gray for hover
ACCENT_COLOR = "#fbbf24"      # Gold/Amber accent
TEXT_WHITE = "#ffffff"
MAIN_BG = "#f3f4f6"           # Light gray background
FILE_NAME = "studentMarks.txt"

class StudentManagerPro(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("University of Oxford | Student Manager Portal")
        self.geometry("1100x700")
        self.configure(bg=MAIN_BG)
        
        # --- DATA STORE ---
        self.students = []
        self.load_data()

        # --- ASSETS ---
        self.load_assets()

        # --- LAYOUT SETUP ---
        self.setup_oxford_header()
        self.setup_modern_sidebar()
        self.setup_main_content()
        
        # --- INITIAL LOAD ---
        self.refresh_table()

    def load_assets(self):
        """Loads the Oxford Logo."""
        self.logo_img = None
        try:
            # Resize logo to fit the header height
            pil_img = Image.open("oxford-logo.png") 
            pil_img = pil_img.resize((65, 65), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(pil_img)
        except:
            print("Logo not found. Please ensure 'oxford-logo.png' is in the folder.")

    # =========================================================================
    #  UI CONSTRUCTION
    # =========================================================================

    def setup_oxford_header(self):
        """Creates the Top Bar like the Oxford Website."""
        header_frame = tk.Frame(self, bg=OXFORD_BLUE, height=90)
        header_frame.pack(side="top", fill="x")
        header_frame.pack_propagate(False)

        # 1. Logo (Left)
        if self.logo_img:
            lbl_logo = tk.Label(header_frame, image=self.logo_img, bg=OXFORD_BLUE)
            lbl_logo.pack(side="left", padx=(20, 10))
        
        # 2. University Title
        title_frame = tk.Frame(header_frame, bg=OXFORD_BLUE)
        title_frame.pack(side="left", pady=15)
        
        tk.Label(title_frame, text="UNIVERSITY OF", font=("Times New Roman", 10, "bold"), 
                 fg=TEXT_WHITE, bg=OXFORD_BLUE).pack(anchor="w")
        tk.Label(title_frame, text="OXFORD", font=("Times New Roman", 22, "bold"), 
                 fg=TEXT_WHITE, bg=OXFORD_BLUE).pack(anchor="w")

        # 3. Portal Title (Right)
        tk.Label(header_frame, text="ACADEMIC RECORDS PORTAL", font=("Segoe UI", 12), 
                 fg="#9ca3af", bg=OXFORD_BLUE).pack(side="right", padx=30)

    def setup_modern_sidebar(self):
        """Creates the vertical sidebar."""
        sidebar_frame = tk.Frame(self, bg=SIDEBAR_BG, width=240)
        sidebar_frame.pack(side="left", fill="y")
        sidebar_frame.pack_propagate(False)

        # Dashboard Label
        tk.Label(sidebar_frame, text="MENU", fg="gray", bg=SIDEBAR_BG, 
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=20, pady=(30, 10))

        # --- MENU BUTTONS ---
        self.create_sidebar_btn(sidebar_frame, "📊  View All Records", self.refresh_table)
        self.create_sidebar_btn(sidebar_frame, "🏆  Highest Score", self.show_highest)
        self.create_sidebar_btn(sidebar_frame, "📉  Lowest Score", self.show_lowest)
        
        tk.Frame(sidebar_frame, height=1, bg="#374151").pack(fill="x", padx=20, pady=15) # Divider

        self.create_sidebar_btn(sidebar_frame, "🔃  Sort by Score", lambda: self.sort_records(True))
        self.create_sidebar_btn(sidebar_frame, "🔤  Sort by Name", lambda: self.sort_records(False))
        
        tk.Frame(sidebar_frame, height=1, bg="#374151").pack(fill="x", padx=20, pady=15) # Divider

        self.create_sidebar_btn(sidebar_frame, "➕  Add Student", self.add_record)
        self.create_sidebar_btn(sidebar_frame, "✏️  Update Record", self.edit_record)
        self.create_sidebar_btn(sidebar_frame, "🗑️  Delete Record", self.delete_record)

    def create_sidebar_btn(self, parent, text, command):
        """Helper for hoverable buttons."""
        btn = tk.Button(parent, text=text, bg=SIDEBAR_BTN_DEFAULT, fg=TEXT_WHITE, 
                        font=("Segoe UI", 11), bd=0, cursor="hand2", anchor="w", 
                        padx=20, pady=8, command=command)
        btn.pack(fill="x", pady=2)

        # Hover Effects
        btn.bind("<Enter>", lambda e: btn.config(bg=SIDEBAR_BTN_HOVER, fg=ACCENT_COLOR))
        btn.bind("<Leave>", lambda e: btn.config(bg=SIDEBAR_BTN_DEFAULT, fg=TEXT_WHITE))

    def setup_main_content(self):
        """The White area for the table."""
        main_content = tk.Frame(self, bg=MAIN_BG)
        main_content.pack(side="right", fill="both", expand=True, padx=25, pady=25)

        # Title
        tk.Label(main_content, text="Student Performance Data", font=("Segoe UI", 20, "bold"), 
                 bg=MAIN_BG, fg="#111827").pack(anchor="w", pady=(0, 5))
        
        # Search Bar
        search_frame = tk.Frame(main_content, bg=MAIN_BG)
        search_frame.pack(fill="x", pady=(0, 15))
        tk.Label(search_frame, text="Search by Name/ID:", bg=MAIN_BG, font=("Segoe UI", 10)).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_data)
        entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Segoe UI", 10), width=30)
        entry.pack(side="left", padx=10)

        # Stats Bar
        self.lbl_stats = tk.Label(main_content, text="Total Students: 0", font=("Segoe UI", 10, "bold"), bg=MAIN_BG, fg="#4b5563")
        self.lbl_stats.pack(anchor="w", pady=(0, 10))

        # --- TREEVIEW (TABLE) ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="#374151", rowheight=35, 
                        fieldbackground="white", font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="white", foreground="#111827", 
                        font=("Segoe UI", 10, "bold"))
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})]) # Remove borders

        columns = ("id", "name", "cw", "exam", "total", "grade")
        self.tree = ttk.Treeview(main_content, columns=columns, show="headings", selectmode="browse")
        
        headers = ["ID No.", "Student Name", "Coursework /60", "Exam /100", "Total %", "Grade"]
        widths = [80, 200, 120, 100, 100, 80]
        
        for col, h, w in zip(columns, headers, widths):
            self.tree.heading(col, text=h)
            self.tree.column(col, width=w, anchor="center")
        self.tree.column("name", anchor="w") # Align name left

        scrollbar = ttk.Scrollbar(main_content, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Color Tags
        self.tree.tag_configure('A', foreground='green')
        self.tree.tag_configure('F', foreground='red')

    # =========================================================================
    #  LOGIC & DATA HANDLING (Merged from your original code)
    # =========================================================================

    def load_data(self):
        self.students = []
        if not os.path.exists(FILE_NAME): return

        try:
            with open(FILE_NAME, "r") as f:
                lines = f.readlines()
                for line in lines[1:]: # Skip the first line (count)
                    parts = line.strip().split(',')
                    if len(parts) >= 6:
                        # Parsing Data
                        s_id = parts[0]
                        name = parts[1]
                        cw_scores = [int(parts[2]), int(parts[3]), int(parts[4])]
                        exam_score = int(parts[5])
                        
                        # Calculations
                        cw_total = sum(cw_scores)
                        overall = cw_total + exam_score
                        perc = (overall / 160) * 100
                        grade = self.calculate_grade(perc)
                        
                        self.students.append({
                            "id": s_id, "name": name, "cw": cw_scores, "exam": exam_score,
                            "cw_total": cw_total, "total": overall, 
                            "perc": round(perc, 1), "grade": grade
                        })
        except Exception as e:
            messagebox.showerror("Error", f"Could not load data: {e}")

    def calculate_grade(self, perc):
        if perc >= 70: return 'A'
        elif perc >= 60: return 'B'
        elif perc >= 50: return 'C'
        elif perc >= 40: return 'D'
        else: return 'F'

    def save_to_file(self):
        try:
            with open(FILE_NAME, "w") as f:
                f.write(f"{len(self.students)}\n")
                for s in self.students:
                    f.write(f"{s['id']},{s['name']},{s['cw'][0]},{s['cw'][1]},{s['cw'][2]},{s['exam']}\n")
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def refresh_table(self, data=None):
        if data is None: data = self.students
        
        # Clear table
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        total_perc = 0
        
        for s in data:
            total_perc += s['perc']
            # Determine color tag based on grade
            tag = 'F' if s['grade'] == 'F' else ('A' if s['grade'] == 'A' else '')
            
            self.tree.insert("", "end", values=(
                s['id'], s['name'], s['cw_total'], s['exam'], 
                f"{s['perc']}%", s['grade']
            ), tags=(tag,))

        # Update Summary Stats
        count = len(data)
        avg = round(total_perc / count, 2) if count > 0 else 0
        self.lbl_stats.config(text=f"Total Students: {count}   |   Class Average: {avg}%")

    def filter_data(self, *args):
        query = self.search_var.get().lower()
        filtered = [s for s in self.students if query in s['name'].lower() or query in str(s['id'])]
        self.refresh_table(filtered)

    def sort_records(self, by_score=True):
        if by_score:
            self.students.sort(key=lambda x: x['total'], reverse=True)
        else:
            self.students.sort(key=lambda x: x['name'])
        self.refresh_table()

    # --- CRUD OPERATIONS ---

    def show_highest(self):
        if not self.students: return
        top = max(self.students, key=lambda x: x['total'])
        messagebox.showinfo("Top Performer 🏆", f"Student: {top['name']}\nScore: {top['perc']}% ({top['grade']})")

    def show_lowest(self):
        if not self.students: return
        low = min(self.students, key=lambda x: x['total'])
        messagebox.showinfo("Lowest Performer 📉", f"Student: {low['name']}\nScore: {low['perc']}% ({low['grade']})")

    def delete_record(self):
        sel = self.tree.selection()
        if not sel: return messagebox.showwarning("Selection", "Please select a student to delete.")
        
        sid = str(self.tree.item(sel[0])['values'][0])
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
            self.students = [s for s in self.students if str(s['id']) != sid]
            self.save_to_file()

    def add_record(self):
        self.open_form("Add New Student")

    def edit_record(self):
        sel = self.tree.selection()
        if not sel: return messagebox.showwarning("Selection", "Please select a student to update.")
        
        sid = str(self.tree.item(sel[0])['values'][0])
        # Find student data
        student = next((s for s in self.students if str(s['id']) == sid), None)
        if student:
            self.open_form("Update Student", student)

    def open_form(self, title, data=None):
        """Popup window for Add/Edit."""
        win = tk.Toplevel(self)
        win.title(title)
        win.geometry("400x500")
        win.configure(bg="white")
        
        tk.Label(win, text=title, font=("Segoe UI", 16, "bold"), bg="white", fg=OXFORD_BLUE).pack(pady=20)

        entries = []
        fields = ["Student ID", "Full Name", "CW 1 (0-20)", "CW 2 (0-20)", "CW 3 (0-20)", "Exam (0-100)"]
        
        # Create fields
        for field in fields:
            f_frame = tk.Frame(win, bg="white")
            f_frame.pack(fill="x", padx=40, pady=5)
            tk.Label(f_frame, text=field, width=15, anchor="w", bg="white").pack(side="left")
            e = tk.Entry(f_frame, bd=1, relief="solid")
            e.pack(side="right", expand=True, fill="x")
            entries.append(e)

        # If Editing, fill current data
        if data:
            vals = [data['id'], data['name'], data['cw'][0], data['cw'][1], data['cw'][2], data['exam']]
            for i, val in enumerate(vals):
                entries[i].insert(0, str(val))
            entries[0].config(state="disabled") # Cannot change ID during edit

        def submit():
            try:
                # Gather Data
                new_id = entries[0].get()
                new_name = entries[1].get()
                cw = [int(entries[2].get()), int(entries[3].get()), int(entries[4].get())]
                exam = int(entries[5].get())

                # Validate Ranges
                if any(x < 0 or x > 20 for x in cw) or (exam < 0 or exam > 100):
                    messagebox.showerror("Validation Error", "Marks out of range! CW(0-20), Exam(0-100)")
                    return

                # Calculations
                cw_tot = sum(cw)
                ovr = cw_tot + exam
                perc = (ovr / 160) * 100
                grade = self.calculate_grade(perc)

                new_record = {
                    "id": new_id, "name": new_name, "cw": cw, "exam": exam,
                    "cw_total": cw_tot, "total": ovr, "perc": round(perc, 1), "grade": grade
                }

                if data: # Update Mode
                    # Find index and replace
                    for i, s in enumerate(self.students):
                        if str(s['id']) == str(new_id):
                            self.students[i] = new_record
                else: # Add Mode
                    # Check ID duplicate
                    if any(s['id'] == new_id for s in self.students):
                        messagebox.showerror("Error", "Student ID already exists.")
                        return
                    self.students.append(new_record)

                self.save_to_file()
                win.destroy()
                messagebox.showinfo("Success", "Record Saved Successfully!")

            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for marks.")

        # Save Button
        tk.Button(win, text="SAVE RECORD", bg=OXFORD_BLUE, fg="white", 
                  font=("Segoe UI", 10, "bold"), padx=20, pady=5, 
                  command=submit, cursor="hand2").pack(pady=30)

if __name__ == "__main__":
    app = StudentManagerPro()
    app.mainloop()
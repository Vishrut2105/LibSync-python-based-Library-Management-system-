import tkinter as tk
from tkinter import ttk, messagebox
import database

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("College Library Management System")
        self.root.geometry("980x640")
        self.root.minsize(850, 550)

        # Initialize the database and pre-seed books if needed
        database.initialize_database()

        # Configure Theme and Colors
        self.setup_styles()

        # Create Header Banner
        self.create_header()

        # Create Tabbed Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=10)

        # Tab Frames
        self.tab_inventory = ttk.Frame(self.notebook, padding=10)
        self.tab_issue = ttk.Frame(self.notebook, padding=10)
        self.tab_return = ttk.Frame(self.notebook, padding=10)
        self.tab_history = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.tab_inventory, text=" 📚 Book Inventory ")
        self.notebook.add(self.tab_issue, text=" 📤 Issue Book ")
        self.notebook.add(self.tab_return, text=" 📥 Return Book & Active Issues ")
        self.notebook.add(self.tab_history, text=" 📋 All Records ")

        # Build each tab
        self.build_inventory_tab()
        self.build_issue_tab()
        self.build_return_tab()
        self.build_history_tab()

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w", padding=(10, 4))
        self.status_bar.pack(side="bottom", fill="x")

        # Initial Load
        self.refresh_all_data()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Palette
        primary = "#1E3A8A"  # Deep Navy
        accent = "#2563EB"   # Royal Blue
        bg_light = "#F8FAFC" # Off-white
        text_dark = "#0F172A"

        self.root.configure(bg=bg_light)
        style.configure("TFrame", background=bg_light)
        style.configure("TLabel", background=bg_light, foreground=text_dark, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="white", background=primary)
        style.configure("SubHeader.TLabel", font=("Segoe UI", 9), foreground="#E2E8F0", background=primary)

        style.configure("TNotebook", background=bg_light)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=(15, 8))
        style.map("TNotebook.Tab", background=[("selected", accent)], foreground=[("selected", "white")])

        style.configure("Treeview", font=("Segoe UI", 9), rowheight=26)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#E2E8F0")

        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), background=accent, foreground="white")
        style.map("Accent.TButton", background=[("active", "#1D4ED8")])

    def create_header(self):
        header_frame = tk.Frame(self.root, bg="#1E3A8A", height=70)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        lbl_title = ttk.Label(header_frame, text="📖 College Library Management System", style="Header.TLabel")
        lbl_title.pack(anchor="w", padx=20, pady=(10, 2))

        lbl_sub = ttk.Label(header_frame, text="Simple, fast, and automated book management for students & faculty", style="SubHeader.TLabel")
        lbl_sub.pack(anchor="w", padx=20)

    # ---------------- TAB 1: BOOK INVENTORY ----------------
    def build_inventory_tab(self):
        # Top action bar: Search & Refresh
        top_bar = ttk.Frame(self.tab_inventory)
        top_bar.pack(fill="x", pady=(0, 10))

        ttk.Label(top_bar, text="Search Book:").pack(side="left", padx=(0, 6))
        self.search_entry = ttk.Entry(top_bar, width=30)
        self.search_entry.pack(side="left", padx=(0, 6))
        self.search_entry.bind("<Return>", lambda e: self.search_books_action())

        btn_search = ttk.Button(top_bar, text="🔍 Search", command=self.search_books_action)
        btn_search.pack(side="left", padx=4)

        btn_clear = ttk.Button(top_bar, text="Reset", command=self.load_inventory_table)
        btn_clear.pack(side="left", padx=4)

        btn_add = ttk.Button(top_bar, text="➕ Add New Book", style="Accent.TButton", command=self.open_add_book_dialog)
        btn_add.pack(side="right", padx=4)

        btn_del = ttk.Button(top_bar, text="🗑️ Delete Book", command=self.delete_book_action)
        btn_del.pack(side="right", padx=4)

        # Inventory Table
        columns = ("ID", "Title", "Author", "Category", "Total Copies", "Available")
        self.tree_inventory = ttk.Treeview(self.tab_inventory, columns=columns, show="headings", selectmode="browse")

        self.tree_inventory.heading("ID", text="Book ID")
        self.tree_inventory.heading("Title", text="Book Title")
        self.tree_inventory.heading("Author", text="Author")
        self.tree_inventory.heading("Category", text="Category")
        self.tree_inventory.heading("Total Copies", text="Total Copies")
        self.tree_inventory.heading("Available", text="Available")

        self.tree_inventory.column("ID", width=70, anchor="center")
        self.tree_inventory.column("Title", width=260, anchor="w")
        self.tree_inventory.column("Author", width=180, anchor="w")
        self.tree_inventory.column("Category", width=140, anchor="w")
        self.tree_inventory.column("Total Copies", width=90, anchor="center")
        self.tree_inventory.column("Available", width=90, anchor="center")

        scroll_y = ttk.Scrollbar(self.tab_inventory, orient="vertical", command=self.tree_inventory.yview)
        self.tree_inventory.configure(yscrollcommand=scroll_y.set)

        self.tree_inventory.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

    # ---------------- TAB 2: ISSUE BOOK ----------------
    def build_issue_tab(self):
        container = ttk.Frame(self.tab_issue)
        container.pack(fill="both", expand=True, padx=40, pady=20)

        title = ttk.Label(container, text="Issue a Book to a Student", font=("Segoe UI", 13, "bold"), foreground="#1E3A8A")
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        # Fields
        ttk.Label(container, text="Select Book ID:").grid(row=1, column=0, sticky="w", pady=8)
        self.issue_book_id = ttk.Entry(container, width=35)
        self.issue_book_id.grid(row=1, column=1, sticky="w", pady=8)

        ttk.Label(container, text="Student Name:").grid(row=2, column=0, sticky="w", pady=8)
        self.issue_student_name = ttk.Entry(container, width=35)
        self.issue_student_name.grid(row=2, column=1, sticky="w", pady=8)

        ttk.Label(container, text="Student Roll / ID:").grid(row=3, column=0, sticky="w", pady=8)
        self.issue_student_id = ttk.Entry(container, width=35)
        self.issue_student_id.grid(row=3, column=1, sticky="w", pady=8)

        ttk.Label(container, text="Issue Period (Days):").grid(row=4, column=0, sticky="w", pady=8)
        self.issue_days = ttk.Spinbox(container, from_=1, to=60, width=10)
        self.issue_days.set(14)
        self.issue_days.grid(row=4, column=1, sticky="w", pady=8)

        btn_submit_issue = ttk.Button(container, text="✅ Confirm & Issue Book", style="Accent.TButton", command=self.issue_book_action)
        btn_submit_issue.grid(row=5, column=1, sticky="w", pady=(20, 10))

        # Helpful hint
        hint = ttk.Label(container, text="Tip: You can check available Book IDs in the 'Book Inventory' tab.", foreground="#64748B", font=("Segoe UI", 8, "italic"))
        hint.grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 0))

    # ---------------- TAB 3: RETURN BOOK & ACTIVE ISSUES ----------------
    def build_return_tab(self):
        top_bar = ttk.Frame(self.tab_return)
        top_bar.pack(fill="x", pady=(0, 10))

        btn_return = ttk.Button(top_bar, text="📥 Return Selected Book", style="Accent.TButton", command=self.return_book_action)
        btn_return.pack(side="left", padx=4)

        btn_refresh = ttk.Button(top_bar, text="🔄 Refresh List", command=self.load_active_issues_table)
        btn_refresh.pack(side="left", padx=4)

        columns = ("IssueID", "BookID", "Title", "Student", "RollNo", "IssueDate", "DueDate", "Fine")
        self.tree_active_issues = ttk.Treeview(self.tab_return, columns=columns, show="headings", selectmode="browse")

        self.tree_active_issues.heading("IssueID", text="Issue #")
        self.tree_active_issues.heading("BookID", text="Book ID")
        self.tree_active_issues.heading("Title", text="Book Title")
        self.tree_active_issues.heading("Student", text="Student Name")
        self.tree_active_issues.heading("RollNo", text="Roll No")
        self.tree_active_issues.heading("IssueDate", text="Issue Date")
        self.tree_active_issues.heading("DueDate", text="Due Date")
        self.tree_active_issues.heading("Fine", text="Late Fine")

        self.tree_active_issues.column("IssueID", width=60, anchor="center")
        self.tree_active_issues.column("BookID", width=60, anchor="center")
        self.tree_active_issues.column("Title", width=220, anchor="w")
        self.tree_active_issues.column("Student", width=140, anchor="w")
        self.tree_active_issues.column("RollNo", width=100, anchor="center")
        self.tree_active_issues.column("IssueDate", width=95, anchor="center")
        self.tree_active_issues.column("DueDate", width=95, anchor="center")
        self.tree_active_issues.column("Fine", width=80, anchor="center")

        scroll_y = ttk.Scrollbar(self.tab_return, orient="vertical", command=self.tree_active_issues.yview)
        self.tree_active_issues.configure(yscrollcommand=scroll_y.set)

        self.tree_active_issues.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

    # ---------------- TAB 4: HISTORY & ALL RECORDS ----------------
    def build_history_tab(self):
        top_bar = ttk.Frame(self.tab_history)
        top_bar.pack(fill="x", pady=(0, 10))

        btn_refresh = ttk.Button(top_bar, text="🔄 Refresh All History", command=self.load_history_table)
        btn_refresh.pack(side="left", padx=4)

        columns = ("IssueID", "Title", "Student", "RollNo", "IssueDate", "DueDate", "ReturnDate", "Status", "Fine")
        self.tree_history = ttk.Treeview(self.tab_history, columns=columns, show="headings", selectmode="browse")

        for col in columns:
            self.tree_history.heading(col, text=col)

        self.tree_history.column("IssueID", width=60, anchor="center")
        self.tree_history.column("Title", width=200, anchor="w")
        self.tree_history.column("Student", width=130, anchor="w")
        self.tree_history.column("RollNo", width=90, anchor="center")
        self.tree_history.column("IssueDate", width=90, anchor="center")
        self.tree_history.column("DueDate", width=90, anchor="center")
        self.tree_history.column("ReturnDate", width=90, anchor="center")
        self.tree_history.column("Status", width=90, anchor="center")
        self.tree_history.column("Fine", width=70, anchor="center")

        scroll_y = ttk.Scrollbar(self.tab_history, orient="vertical", command=self.tree_history.yview)
        self.tree_history.configure(yscrollcommand=scroll_y.set)

        self.tree_history.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

    # ---------------- LOGIC & CONTROLLER METHODS ----------------

    def refresh_all_data(self):
        self.load_inventory_table()
        self.load_active_issues_table()
        self.load_history_table()
        self.update_status_bar()

    def load_inventory_table(self):
        for row in self.tree_inventory.get_children():
            self.tree_inventory.delete(row)

        books = database.get_all_books()
        for b in books:
            self.tree_inventory.insert("", "end", values=(
                b["book_id"], b["title"], b["author"], b["category"], b["quantity"], b["available"]
            ))

    def search_books_action(self):
        query = self.search_entry.get().strip()
        if not query:
            self.load_inventory_table()
            return

        for row in self.tree_inventory.get_children():
            self.tree_inventory.delete(row)

        results = database.search_books(query)
        for b in results:
            self.tree_inventory.insert("", "end", values=(
                b["book_id"], b["title"], b["author"], b["category"], b["quantity"], b["available"]
            ))

    def open_add_book_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Add New Book")
        win.geometry("380x300")
        win.resizable(False, False)
        win.grab_set()

        frame = ttk.Frame(win, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Book Title:").grid(row=0, column=0, sticky="w", pady=6)
        entry_title = ttk.Entry(frame, width=28)
        entry_title.grid(row=0, column=1, pady=6)

        ttk.Label(frame, text="Author:").grid(row=1, column=0, sticky="w", pady=6)
        entry_author = ttk.Entry(frame, width=28)
        entry_author.grid(row=1, column=1, pady=6)

        ttk.Label(frame, text="Category:").grid(row=2, column=0, sticky="w", pady=6)
        entry_cat = ttk.Entry(frame, width=28)
        entry_cat.grid(row=2, column=1, pady=6)

        ttk.Label(frame, text="Copies/Qty:").grid(row=3, column=0, sticky="w", pady=6)
        entry_qty = ttk.Spinbox(frame, from_=1, to=100, width=10)
        entry_qty.set(1)
        entry_qty.grid(row=3, column=1, sticky="w", pady=6)

        def save_book():
            title = entry_title.get().strip()
            author = entry_author.get().strip()
            cat = entry_cat.get().strip()
            try:
                qty = int(entry_qty.get())
            except ValueError:
                messagebox.showerror("Error", "Quantity must be an integer.", parent=win)
                return

            if not title or not author or not cat:
                messagebox.showerror("Error", "Please fill in all fields.", parent=win)
                return

            database.add_book(title, author, cat, qty)
            messagebox.showinfo("Success", f"'{title}' added successfully!", parent=win)
            win.destroy()
            self.refresh_all_data()

        btn_save = ttk.Button(frame, text="💾 Save Book", style="Accent.TButton", command=save_book)
        btn_save.grid(row=4, column=0, columnspan=2, pady=15)

    def delete_book_action(self):
        selected = self.tree_inventory.selection()
        if not selected:
            messagebox.showwarning("Select Book", "Please select a book from the table to delete.")
            return

        item = self.tree_inventory.item(selected[0])
        book_id = item["values"][0]
        title = item["values"][1]

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{title}' (ID: {book_id})?")
        if confirm:
            success, msg = database.delete_book(book_id)
            if success:
                messagebox.showinfo("Deleted", msg)
                self.refresh_all_data()
            else:
                messagebox.showerror("Cannot Delete", msg)

    def issue_book_action(self):
        b_id_str = self.issue_book_id.get().strip()
        student_name = self.issue_student_name.get().strip()
        student_id = self.issue_student_id.get().strip()

        if not b_id_str or not student_name or not student_id:
            messagebox.showwarning("Missing Information", "Please enter Book ID, Student Name, and Student Roll No.")
            return

        try:
            b_id = int(b_id_str)
            days = int(self.issue_days.get())
        except ValueError:
            messagebox.showerror("Input Error", "Book ID and Days must be valid numbers.")
            return

        success, msg = database.issue_book(b_id, student_name, student_id, days)
        if success:
            messagebox.showinfo("Success", msg)
            self.issue_book_id.delete(0, "end")
            self.issue_student_name.delete(0, "end")
            self.issue_student_id.delete(0, "end")
            self.refresh_all_data()
            self.notebook.select(self.tab_return) # Jump to active issues to see the record
        else:
            messagebox.showerror("Issue Failed", msg)

    def load_active_issues_table(self):
        for row in self.tree_active_issues.get_children():
            self.tree_active_issues.delete(row)

        records = database.get_issued_records(only_active=True)
        for r in records:
            fine = database.calculate_fine(r["due_date"])
            fine_str = f"${fine:.2f}" if fine > 0 else "$0.00"
            self.tree_active_issues.insert("", "end", values=(
                r["issue_id"], r["book_id"], r["title"], r["student_name"], 
                r["student_id"], r["issue_date"], r["due_date"], fine_str
            ))

    def return_book_action(self):
        selected = self.tree_active_issues.selection()
        if not selected:
            messagebox.showwarning("Select Record", "Please select an active issue record to return.")
            return

        item = self.tree_active_issues.item(selected[0])
        issue_id = item["values"][0]
        title = item["values"][2]
        student = item["values"][3]

        confirm = messagebox.askyesno("Confirm Return", f"Return book '{title}' from {student}?")
        if confirm:
            success, msg, fine = database.return_book(issue_id)
            if success:
                fine_msg = f"\nLate fine assessed: ${fine:.2f}" if fine > 0 else "\nReturned on time! No fine."
                messagebox.showinfo("Book Returned", f"{msg}{fine_msg}")
                self.refresh_all_data()
            else:
                messagebox.showerror("Error", msg)

    def load_history_table(self):
        for row in self.tree_history.get_children():
            self.tree_history.delete(row)

        records = database.get_issued_records(only_active=False)
        for r in records:
            ret_date = r["return_date"] if r["return_date"] else "-"
            fine_str = f"${r['fine']:.2f}"
            self.tree_history.insert("", "end", values=(
                r["issue_id"], r["title"], r["student_name"], r["student_id"],
                r["issue_date"], r["due_date"], ret_date, r["status"], fine_str
            ))

    def update_status_bar(self):
        books = database.get_all_books()
        total_unique_titles = len(books)
        total_available = sum(b["available"] for b in books)
        active_issues = len(database.get_issued_records(only_active=True))

        self.status_var.set(
            f"  System Status: Ready  |  Unique Titles: {total_unique_titles}  |  Total Available Copies: {total_available}  |  Active Issued Books: {active_issues}"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()

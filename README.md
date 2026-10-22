# College Library Management System

A simple, modular desktop application built entirely using **Python** (Standard Library) and **SQLite**. Designed for academic submissions, viva demonstrations, and practical record tracking.

---

## 📌 Project Overview
This system allows college librarians and students to manage library operations without requiring any external software, cloud connections, or third-party web frameworks. It runs out-of-the-box on any machine with Python installed.

---

## ✨ Features
1. **Book Inventory Management:**
   - View all books in real time with total and available copies.
   - Search books instantly by title, author, or category.
   - Add new books with custom categories and quantities.
   - Delete books (with safety checks preventing deletion of currently issued books).

2. **Issue Book:**
   - Issue any available book to a student by entering Book ID, Student Name, and Roll Number.
   - Configurable issue duration (default: 14 days).
   - Automatically decrements the available copy count.

3. **Return Book & Active Issues:**
   - Lists all active borrowings with due dates.
   - Real-time late fine calculator ($2 / ₹2 per day overdue).
   - One-click return processing that restores the book's available stock.

4. **Transaction History & Audit Log:**
   - Complete record of all past issues and returns with timestamps, status, and fines paid.

---

## 🛠️ Technology Stack
* **Language:** Python 3.8+ (Pure Python)
* **GUI Framework:** `tkinter` and `ttk` (Native desktop interface)
* **Database:** `sqlite3` (Embedded SQL relational database, file: `library.db`)
* **Time & Date:** `datetime` (for issue dates, due dates, and fine calculation)
* **Zero external dependencies:** No `pip install` required!

---

## 📂 Project Structure
```text
python project/
│
├── main.py          # Tkinter GUI interface, tabs, and user interactions
├── database.py      # SQLite schema, queries, CRUD, issue, return & fine logic
├── library.db       # Auto-created SQLite database file
└── README.md        # Documentation and viva preparation guide
```

---

## 🚀 How to Run

1. Open your terminal or Command Prompt.
2. Navigate to the project directory:
   ```bash
   cd "d:/Personal/python project"
   ```
3. Run the application:
   ```bash
   python main.py
   ```

---

## 💡 Top Viva Questions & Answers (For Evaluation)

**Q1: What database is used and why?**
> **Answer:** We used SQLite via Python’s built-in `sqlite3` module. It is serverless, zero-configuration, and stores all tables and data inside a single local file (`library.db`).

**Q2: How does the system handle book availability when a copy is issued?**
> **Answer:** In `database.py`, `available` is decremented by 1 when a book is issued, and incremented by 1 when the book is returned. If `available <= 0`, the system blocks any further issue attempts.

**Q3: How is the late fine calculated?**
> **Answer:** In `database.calculate_fine()`, the current date is compared with the record's `due_date`. If `today > due_date`, the overdue days are multiplied by the daily fine rate.

**Q4: Can a book be deleted while a student has it borrowed?**
> **Answer:** No. Foreign key logic and integrity checks in `delete_book()` query the `issued_books` table. If there are active records with status `'ISSUED'`, deletion is rejected.

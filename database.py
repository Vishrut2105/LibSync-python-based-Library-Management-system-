import sqlite3
from datetime import datetime, timedelta

DB_NAME = "library.db"

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Initializes tables and seeds sample data if empty."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create books table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        category TEXT NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        available INTEGER NOT NULL DEFAULT 1
    )
    """)

    # Create issued_books table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS issued_books (
        issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        student_name TEXT NOT NULL,
        student_id TEXT NOT NULL,
        issue_date TEXT NOT NULL,
        due_date TEXT NOT NULL,
        return_date TEXT,
        status TEXT NOT NULL DEFAULT 'ISSUED',
        fine REAL NOT NULL DEFAULT 0.0,
        FOREIGN KEY (book_id) REFERENCES books (book_id)
    )
    """)

    # Seed sample books if database is newly created
    cursor.execute("SELECT COUNT(*) FROM books")
    if cursor.fetchone()[0] == 0:
        sample_books = [
            ("Python Crash Course", "Eric Matthes", "Computer Science", 5, 5),
            ("Introduction to Algorithms", "Thomas H. Cormen", "Computer Science", 3, 3),
            ("Clean Code", "Robert C. Martin", "Software Engineering", 4, 4),
            ("Artificial Intelligence: A Modern Approach", "Stuart Russell", "AI & ML", 2, 2),
            ("Database System Concepts", "Abraham Silberschatz", "Database", 4, 4),
            ("Operating System Concepts", "Abraham Silberschatz", "Computer Science", 3, 3)
        ]
        cursor.executemany("""
            INSERT INTO books (title, author, category, quantity, available)
            VALUES (?, ?, ?, ?, ?)
        """, sample_books)

    conn.commit()
    conn.close()

# ---------------- Book Operations ----------------

def add_book(title, author, category, quantity):
    """Adds a new book or updates existing quantity."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO books (title, author, category, quantity, available)
        VALUES (?, ?, ?, ?, ?)
    """, (title.strip(), author.strip(), category.strip(), int(quantity), int(quantity)))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def get_all_books():
    """Fetches all books from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT book_id, title, author, category, quantity, available FROM books ORDER BY book_id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def search_books(keyword):
    """Searches books by title, author, or category."""
    conn = get_connection()
    cursor = conn.cursor()
    search_term = f"%{keyword.strip()}%"
    cursor.execute("""
        SELECT book_id, title, author, category, quantity, available 
        FROM books
        WHERE title LIKE ? OR author LIKE ? OR category LIKE ?
        ORDER BY book_id ASC
    """, (search_term, search_term, search_term))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_book(book_id):
    """Deletes a book only if not currently issued."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if there are active issues
    cursor.execute("SELECT COUNT(*) FROM issued_books WHERE book_id = ? AND status = 'ISSUED'", (book_id,))
    if cursor.fetchone()[0] > 0:
        conn.close()
        return False, "Cannot delete book: Copies are currently issued to students."
    
    cursor.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
    conn.commit()
    conn.close()
    return True, "Book deleted successfully."

# ---------------- Issue & Return Operations ----------------

def issue_book(book_id, student_name, student_id, days=14):
    """Issues a book to a student if copies are available."""
    conn = get_connection()
    cursor = conn.cursor()

    # Check availability
    cursor.execute("SELECT available, title FROM books WHERE book_id = ?", (book_id,))
    book = cursor.fetchone()
    if not book:
        conn.close()
        return False, "Book ID not found."
    
    if book["available"] <= 0:
        conn.close()
        return False, f"No copies available for '{book['title']}'."

    # Decrement available count
    cursor.execute("UPDATE books SET available = available - 1 WHERE book_id = ?", (book_id,))

    # Insert issue record
    today = datetime.now()
    due = today + timedelta(days=days)
    cursor.execute("""
        INSERT INTO issued_books (book_id, student_name, student_id, issue_date, due_date, status)
        VALUES (?, ?, ?, ?, ?, 'ISSUED')
    """, (book_id, student_name.strip(), student_id.strip(), today.strftime("%Y-%m-%d"), due.strftime("%Y-%m-%d")))

    conn.commit()
    conn.close()
    return True, f"Book '{book['title']}' successfully issued to {student_name}."

def calculate_fine(due_date_str, daily_rate=2.0):
    """Calculates late fine (default $2 / ₹2 per day overdue)."""
    try:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        if today > due_date:
            days_overdue = (today - due_date).days
            return float(days_overdue * daily_rate)
    except Exception:
        pass
    return 0.0

def return_book(issue_id):
    """Processes return of an issued book and updates book inventory."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM issued_books WHERE issue_id = ? AND status = 'ISSUED'", (issue_id,))
    record = cursor.fetchone()
    if not record:
        conn.close()
        return False, "Active issue record not found.", 0.0

    fine = calculate_fine(record["due_date"])
    today_str = datetime.now().strftime("%Y-%m-%d")

    # Update issue record
    cursor.execute("""
        UPDATE issued_books 
        SET return_date = ?, status = 'RETURNED', fine = ?
        WHERE issue_id = ?
    """, (today_str, fine, issue_id))

    # Increase available book count
    cursor.execute("UPDATE books SET available = available + 1 WHERE book_id = ?", (record["book_id"],))

    conn.commit()
    conn.close()
    return True, "Book returned successfully.", fine

def get_issued_records(only_active=True):
    """Fetches all issued records with book title details."""
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT i.issue_id, i.book_id, b.title, i.student_name, i.student_id, 
               i.issue_date, i.due_date, i.return_date, i.status, i.fine
        FROM issued_books i
        JOIN books b ON i.book_id = b.book_id
    """
    if only_active:
        query += " WHERE i.status = 'ISSUED' ORDER BY i.issue_id DESC"
    else:
        query += " ORDER BY i.issue_id DESC"

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

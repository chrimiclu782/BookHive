"""
Student Dashboard Window

This module provides the student interface for the BookHive library system.
Students can search for books, view available books, borrow books, and view
their borrowing history through this window.
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QScrollArea
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from db import connect_db
from datetime import datetime, timedelta
from app import AuthApp

class StudentWindow(QWidget):
    """
    Student dashboard for book borrowing and management.

    Provides functionality for students to:
    - Search and browse available books
    - Borrow books with automatic due date calculation
    - View their active borrowed books
    - Return to login screen
    """

    BORROW_PERIOD_DAYS = 7  # Standard borrowing period in days

    def __init__(self, student_no=None):
        """
        Initialize the student window.

        Args:
            student_no: The authenticated student's number (optional)
        """
        super().__init__()
        self.student_no = str(student_no) if student_no else None
        self.setWindowTitle("Student Dashboard")
        self.setGeometry(150, 150, 700, 500)
        self.setWindowIcon(QIcon("python_codes/assets/BookHive_Logo.png"))
        self.setStyleSheet("""
            QWidget {
                background-color: #f7b918;
                color: #402c12;
            }
            QLabel {
                color: #402c12;
                font-size: 16px;
                font-family: "Arial Black";
            }
            QLineEdit {
                background-color: white;
                color: #402c12;
                border: 1px solid #ccc;
                padding: 5px;
                font-size: 16px;
                font-family: "Arial Black";
            }
            QPushButton {
                background-color: #808080;
                color: #402c12;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
                font-family: "Arial Black";
            }
            QPushButton:hover {
                background-color: #A9A9A9;
            }
        """)
        self.init_ui()

    def init_ui(self):
        """Set up the user interface components for the student dashboard."""
        self.search_label = QLabel("Search Book:")
        self.search_input = QLineEdit()
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search_books)

        self.books_label = QLabel("Available Books:")
        self.books_display = QLabel()
        self.books_display.setWordWrap(True)
        self.books_scroll = QScrollArea()
        self.books_scroll.setWidget(self.books_display)
        self.books_scroll.setWidgetResizable(True)
        self.books_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.books_scroll.setMinimumHeight(150)

        self.book_id_label = QLabel("Book ID (ISBN) to borrow:")
        self.book_id_input = QLineEdit()

        self.borrow_btn = QPushButton("Borrow Book")
        self.borrow_btn.clicked.connect(self.borrow_book)

        self.student_no_label = QLabel("Student No:")
        self.student_no_display = QLabel(self.student_no if self.student_no else "Not signed in")

        self.borrowed_label = QLabel("Your Active Borrowed Books:")
        self.borrowed_display = QLabel()
        self.borrowed_display.setWordWrap(True)
        self.borrowed_scroll = QScrollArea()
        self.borrowed_scroll.setWidget(self.borrowed_display)
        self.borrowed_scroll.setWidgetResizable(True)
        self.borrowed_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.borrowed_scroll.setMinimumHeight(150)

        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.logout)

        # Logo at the top center
        self.logo_label = QLabel()
        pixmap = QPixmap("python_codes/assets/BookHive_Logo.png")
        if not pixmap.isNull():
            self.logo_label.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio))
        self.logo_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.logo_label)
        layout.addWidget(QLabel("Welcome, student!"))
        layout.addWidget(self.search_label)
        layout.addWidget(self.search_input)
        layout.addWidget(self.search_btn)
        layout.addWidget(self.books_label)
        layout.addWidget(self.books_scroll)
        layout.addWidget(self.book_id_label)
        layout.addWidget(self.book_id_input)

        h = QHBoxLayout()
        h.addWidget(self.borrow_btn)
        layout.addLayout(h)

        layout.addWidget(self.student_no_label)
        layout.addWidget(self.student_no_display)
        layout.addWidget(self.borrowed_label)
        layout.addWidget(self.borrowed_scroll)
        layout.addWidget(self.logout_btn)
        self.setLayout(layout)

        # Disable borrowing features if student not logged in
        if not self.student_no:
            self.borrow_btn.setDisabled(True)
            self.borrowed_display.setText("Student number not provided. Please log in to use borrowing features.")
        else:
            self.load_books()
            self.load_borrowed_books()

    def _get_student_no(self):
        """
        Get the current student's number with validation.

        Returns:
            str or None: Student number if available, None otherwise
        """
        if not self.student_no:
            QMessageBox.warning(self, "Not signed in", "Student number not available. Please log in.")
            return None
        return self.student_no

    def load_books(self):
        """Load and display all available (unborrowed) books from the database."""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT book_id, title, author, genre FROM Books
                WHERE book_id NOT IN (
                    SELECT book_id FROM Borrowed WHERE borrow_status = 'Borrowed'
                )
            """)
            books = cursor.fetchall()
        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))
            books = []
        finally:
            try: conn.close()
            except Exception: pass

        if books:
            table_html = """
            <table border="1" style="border-collapse: collapse; width: 100%; margin: 10px 0;">
                <tr style="background-color: #f0f0f0; height: 35px;">
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Book ID</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Title</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Author</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Genre</th>
                </tr>
            """
            for b in books:
                table_html += f"""
                <tr style="background-color: white; height: 35px;">
                    <td style="padding: 8px;">{b[0]}</td>
                    <td style="padding: 8px;">{b[1]}</td>
                    <td style="padding: 8px;">{b[2]}</td>
                    <td style="padding: 8px;">{b[3]}</td>
                </tr>
                """
            table_html += "</table>"
            self.books_display.setText(table_html)
        else:
            self.books_display.setText("No books found.")

    def search_books(self):
        """Search for books by title or author and display results."""
        keyword = self.search_input.text().strip()
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT book_id, title, author, genre FROM Books
                WHERE (title LIKE %s OR author LIKE %s) AND book_id NOT IN (
                    SELECT book_id FROM Borrowed WHERE borrow_status = 'Borrowed'
                )
            """, (f"%{keyword}%", f"%{keyword}%"))
            books = cursor.fetchall()
        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))
            books = []
        finally:
            try: conn.close()
            except Exception: pass

        if books:
            table_html = """
            <table border="1" style="border-collapse: collapse; width: 100%; margin: 10px 0;">
                <tr style="background-color: #f0f0f0; height: 35px;">
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Book ID</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Title</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Author</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Genre</th>
                </tr>
            """
            for b in books:
                table_html += f"""
                <tr style="background-color: white; height: 35px;">
                    <td style="padding: 8px;">{b[0]}</td>
                    <td style="padding: 8px;">{b[1]}</td>
                    <td style="padding: 8px;">{b[2]}</td>
                    <td style="padding: 8px;">{b[3]}</td>
                </tr>
                """
            table_html += "</table>"
            self.books_display.setText(table_html)
        else:
            self.books_display.setText("No results.")

    def borrow_book(self):
        """
        Process book borrowing with validation and database updates.

        Performs multiple validations:
        - Book exists in catalog
        - Student hasn't already borrowed this book
        - Book is currently available (not borrowed by others)
        Calculates due date and updates database accordingly.
        """
        student_no = self._get_student_no()
        if not student_no:
            return

        book_id = self.book_id_input.text().strip()
        if not book_id:
            QMessageBox.warning(self, "Missing Data", "Please enter a Book ID to borrow.")
            return

        # Calculate borrow and due dates
        date_borrowed = datetime.now()
        date_due = date_borrowed + timedelta(days=self.BORROW_PERIOD_DAYS)

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Verify book exists in catalog
            cursor.execute("SELECT 1 FROM Books WHERE book_id = %s", (book_id,))
            if not cursor.fetchone():
                QMessageBox.warning(self, "Not found", "Book ID not found.")
                conn.close()
                return

            # Check if the student already has this book borrowed
            cursor.execute("""
                SELECT 1 FROM Borrowed
                WHERE student_no = %s AND book_id = %s AND borrow_status = 'Borrowed'
            """, (student_no, book_id))
            if cursor.fetchone():
                QMessageBox.warning(self, "Already Borrowed", "You have already borrowed this book. Please return it first.")
                conn.close()
                return

            # Check if the book is currently borrowed by someone else
            cursor.execute("""
                SELECT date_due FROM Borrowed
                WHERE book_id = %s AND borrow_status = 'Borrowed'
            """, (book_id,))
            due_row = cursor.fetchone()
            if due_row:
                due_date = due_row[0]
                QMessageBox.warning(self, "Unavailable", f"Book is unavailable. It will be available after {due_date}.")
                conn.close()
                return

            # Insert new borrow record
            cursor.execute("""
                INSERT INTO Borrowed (student_no, book_id, date_borrowed, date_due, borrow_status)
                VALUES (%s, %s, %s, %s, 'Borrowed')
            """, (student_no, book_id, date_borrowed, date_due))

            conn.commit()
            QMessageBox.information(self, "Success", f"Book borrowed. Due on {date_due.date()}.")
            # Refresh displays to show updated availability and borrowed books
            self.load_books()
            self.load_borrowed_books()
        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))
        finally:
            try: conn.close()
            except Exception: pass

    def load_borrowed_books(self):
        """
        Load and display the student's currently borrowed books.

        Queries the Borrowed table for active loans, joins with Books table
        to get titles, and formats the display with borrow/due dates.
        """
        student_no = self._get_student_no()
        if not student_no:
            self.borrowed_display.setText("Enter your Student No to see borrowed books.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            # Query active borrowed books with book details
            cursor.execute("""
                SELECT borrow_id, book_id,
                (SELECT title FROM Books WHERE Books.book_id = Borrowed.book_id) AS title,
                date_borrowed, date_due
                FROM Borrowed
                WHERE student_no = %s AND borrow_status = 'Borrowed'
                ORDER BY date_borrowed DESC
            """, (student_no,))
            rows = cursor.fetchall()
        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))
            rows = []
        finally:
            try: conn.close()
            except Exception: pass

        if not rows:
            self.borrowed_display.setText("No active borrowed books.")
            return

        if rows:
            table_html = """
            <table border="1" style="border-collapse: collapse; width: 100%; margin: 10px 0;">
                <tr style="background-color: #f0f0f0; height: 35px;">
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Book ID</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Title</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Borrowed Date</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Due Date</th>
                </tr>
            """
            for r in rows:
                book_id = r[1] if len(r) > 1 else ""
                title = r[2] if len(r) > 2 else ""
                date_borrowed = r[3] if len(r) > 3 else None
                date_due = r[4] if len(r) > 4 else None

                # Format dates safely, handling potential None or different types
                try:
                    borrow_str = date_borrowed.date().isoformat() if hasattr(date_borrowed, "date") else str(date_borrowed)
                except Exception:
                    borrow_str = "N/A"
                try:
                    due_str = date_due.date().isoformat() if hasattr(date_due, "date") else str(date_due)
                except Exception:
                    due_str = "N/A"

                table_html += f"""
                <tr style="background-color: white; height: 35px;">
                    <td style="padding: 8px;">{book_id}</td>
                    <td style="padding: 8px;">{title}</td>
                    <td style="padding: 8px;">{borrow_str}</td>
                    <td style="padding: 8px;">{due_str}</td>
                </tr>
                """
            table_html += "</table>"
            self.borrowed_display.setText(table_html)
        else:
            self.borrowed_display.setText("No active borrowed books.")

    def logout(self):
        """Return to the authentication screen."""
        self.auth_app = AuthApp()
        self.auth_app.show()
        self.close()

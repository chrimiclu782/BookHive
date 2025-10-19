from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from db import connect_db
from datetime import datetime, timedelta

class StudentWindow(QWidget):
    BORROW_PERIOD_DAYS = 7

    def __init__(self, student_no=None):
        super().__init__()
        self.student_no = str(student_no) if student_no is not None else None
        self.setWindowTitle("Student Dashboard")
        self.setGeometry(150, 150, 700, 500)
        self.init_ui()

    def init_ui(self):
        self.search_label = QLabel("Search Book:")
        self.search_input = QLineEdit()
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search_books)

        self.books_label = QLabel("Available Books:")
        self.books_display = QLabel()
        self.books_display.setWordWrap(True)

        # Borrow controls
        self.book_id_label = QLabel("Book ID (ISBN) to borrow:")
        self.book_id_input = QLineEdit()

        self.borrow_btn = QPushButton("Borrow Book")
        self.borrow_btn.clicked.connect(self.borrow_book)

        # Student number display (from login)
        self.student_no_label = QLabel("Student No:")
        self.student_no_display = QLabel(self.student_no if self.student_no else "Not signed in")

        # Borrowed books display — show only active borrowings for this student
        self.borrowed_label = QLabel("Your Active Borrowed Books:")
        self.borrowed_display = QLabel()
        self.borrowed_display.setWordWrap(True)

        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Welcome, student!"))
        layout.addWidget(self.search_label)
        layout.addWidget(self.search_input)
        layout.addWidget(self.search_btn)
        layout.addWidget(self.books_label)
        layout.addWidget(self.books_display)

        layout.addWidget(self.book_id_label)
        layout.addWidget(self.book_id_input)

        h = QHBoxLayout()
        h.addWidget(self.borrow_btn)
        layout.addLayout(h)

        layout.addWidget(self.student_no_label)
        layout.addWidget(self.student_no_display)

        layout.addWidget(self.borrowed_label)
        layout.addWidget(self.borrowed_display)

        layout.addWidget(self.logout_btn)
        self.setLayout(layout)

        if not self.student_no:
            self.borrow_btn.setDisabled(True)
            self.borrowed_display.setText("Student number not provided. Please log in to use borrowing features.")
        else:
            self.load_books()
            self.load_borrowed_books()

    def _get_student_no(self):
        if not self.student_no:
            QMessageBox.warning(self, "Not signed in", "Student number not available. Please log in.")
            return None
        return self.student_no

    def load_books(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT book_id, title, author, genre FROM Books")
            books = cursor.fetchall()
        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))
            books = []
        finally:
            try: conn.close()
            except Exception: pass

        display = "\n".join([f"{b[0]} | {b[1]} by {b[2]} ({b[3]})" for b in books])
        self.books_display.setText(display or "No books found.")

    def search_books(self):
        keyword = self.search_input.text().strip()
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT book_id, title, author, genre FROM Books WHERE title LIKE %s OR author LIKE %s",
                (f"%{keyword}%", f"%{keyword}%")
            )
            books = cursor.fetchall()
        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))
            books = []
        finally:
            try: conn.close()
            except Exception: pass

        display = "\n".join([f"{b[0]} | {b[1]} by {b[2]} ({b[3]})" for b in books])
        self.books_display.setText(display or "No results.")

    def borrow_book(self):
        student_no = self._get_student_no()
        if not student_no:
            return

        book_id = self.book_id_input.text().strip()
        if not book_id:
            QMessageBox.warning(self, "Missing Data", "Please enter a Book ID to borrow.")
            return

        date_borrowed = datetime.now()
        date_due = date_borrowed + timedelta(days=self.BORROW_PERIOD_DAYS)

        try:
            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("SELECT 1 FROM Books WHERE book_id = %s", (book_id,))
            if not cursor.fetchone():
                QMessageBox.warning(self, "Not found", "Book ID not found.")
                try: conn.close()
                except Exception: pass
                return

            # insert only borrow-related fields; no return/lost/fine handling here
            try:
                cursor.execute(
                    "INSERT INTO borrowed (student_no, book_id, date_borrowed, date_due) VALUES (%s, %s, %s, %s)",
                    (student_no, book_id, date_borrowed, date_due)
                )
            except Exception:
                # try variant if DB requires explicit NULLs for other columns
                cursor.execute(
                    "INSERT INTO borrowed (student_no, book_id, date_borrowed, date_due, return_date) VALUES (%s, %s, %s, %s, NULL)",
                    (student_no, book_id, date_borrowed, date_due)
                )

            conn.commit()
            QMessageBox.information(self, "Success", f"Book borrowed. Due on {date_due.date()}.")
            self.load_borrowed_books()
        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))
        finally:
            try: conn.close()
            except Exception: pass

    def load_borrowed_books(self):
        """Show only active borrows for the logged-in student and display date_borrowed and date_due."""
        student_no = self._get_student_no()
        if not student_no:
            self.borrowed_display.setText("Enter your Student No to see borrowed books.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            # Prefer schema that has return_date and filter active borrows only
            try:
                cursor.execute(
                    "SELECT borrow_id, book_id, (SELECT title FROM Books WHERE Books.book_id = borrowed.book_id) AS title, "
                    "date_borrowed, date_due "
                    "FROM borrowed WHERE student_no = %s AND (return_date IS NULL OR return_date = '') "
                    "ORDER BY date_borrowed DESC",
                    (student_no,)
                )
            except Exception:
                # Fallback to schema that uses date_returned or doesn't have a return column
                try:
                    cursor.execute(
                        "SELECT borrow_id, book_id, (SELECT title FROM Books WHERE Books.book_id = borrowed.book_id) AS title, "
                        "date_borrowed, date_due "
                        "FROM borrowed WHERE student_no = %s AND (date_returned IS NULL OR date_returned = '') "
                        "ORDER BY date_borrowed DESC",
                        (student_no,)
                    )
                except Exception:
                    # Last resort: select by student_no only (if DB has no return columns)
                    cursor.execute(
                        "SELECT borrow_id, book_id, (SELECT title FROM Books WHERE Books.book_id = borrowed.book_id) AS title, "
                        "date_borrowed, date_due "
                        "FROM borrowed WHERE student_no = %s ORDER BY date_borrowed DESC",
                        (student_no,)
                    )
            rows = cursor.fetchall()
        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))
            rows = []
        finally:
            try:
                conn.close()
            except Exception:
                pass

        if not rows:
            self.borrowed_display.setText("No active borrowed books.")
            return

        lines = []
        for r in rows:
            # indices: 0=borrow_id,1=book_id,2=title,3=date_borrowed,4=date_due
            book_id = r[1] if len(r) > 1 else ""
            title = r[2] if len(r) > 2 else ""
            date_borrowed = r[3] if len(r) > 3 else None
            date_due = r[4] if len(r) > 4 else None

            # format dates for display
            try:
                borrow_str = date_borrowed.date().isoformat() if hasattr(date_borrowed, "date") else str(date_borrowed)
            except Exception:
                borrow_str = "N/A"
            try:
                due_str = date_due.date().isoformat() if hasattr(date_due, "date") else str(date_due)
            except Exception:
                due_str = "N/A"

            lines.append(f"{book_id} | {title} — Borrowed: {borrow_str} — Due: {due_str}")

        self.borrowed_display.setText("\n".join(lines))
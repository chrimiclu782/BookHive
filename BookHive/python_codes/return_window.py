"""
Return Book Window

This module handles book returns and lost book processing for the library system.
It allows librarians to process returns, calculate fines for overdue books,
and mark books as lost with appropriate charges.
"""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit, QMessageBox, QHBoxLayout, QScrollArea, QTableWidget, QTableWidgetItem, QCheckBox, QHeaderView, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from db import connect_db
from datetime import datetime

class ReturnWindow(QWidget):
    """
    Window for processing book returns and handling lost books.

    Provides functionality to:
    - Load borrow details by borrow ID
    - Process normal returns with fine calculation
    - Mark books as lost with full price charges
    - Display current borrowed books list
    """

    def __init__(self):
        """Initialize the return window."""
        super().__init__()
        self.setWindowTitle("Return Book")
        screen = QApplication.desktop().screenGeometry()
        self.setGeometry((screen.width() - 700) // 2, 50, 700, 400)
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
            QTableWidget {
                background-color: white;
                color: #402c12;
                gridline-color: #ccc;
            }
            QHeaderView::section {
                background-color: gray;
                color: #402c12;
                padding: 5px;
                border: 1px solid #ccc;
                font-weight: bold;
                font-family: "Arial Black";
            }
        """)
        self.init_ui()

    def init_ui(self):
        """Set up the user interface components."""
        layout = QVBoxLayout()
        layout.addWidget(QLabel("📖 Return Book"))

        self.borrow_id_input = QLineEdit()
        self.borrow_id_input.setPlaceholderText("Borrow ID")
        layout.addWidget(QLabel("Borrow ID:"))
        layout.addWidget(self.borrow_id_input)

        self.load_btn = QPushButton("Load Borrow Details")
        self.load_btn.clicked.connect(self.load_borrow_details)
        layout.addWidget(self.load_btn)

        self.details_display = QLabel()
        self.details_display.setWordWrap(True)
        layout.addWidget(self.details_display)

        self.borrowed_books_display = QLabel()
        self.borrowed_books_display.setWordWrap(True)
        self.borrowed_scroll = QScrollArea()
        self.borrowed_scroll.setWidget(self.borrowed_books_display)
        self.borrowed_scroll.setWidgetResizable(True)
        self.borrowed_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.borrowed_scroll.setMinimumHeight(150)
        layout.addWidget(QLabel("Currently Borrowed Books:"))
        layout.addWidget(self.borrowed_scroll)

        self.unpaid_students_table = QTableWidget()
        self.unpaid_students_table.setColumnCount(5)
        self.unpaid_students_table.setHorizontalHeaderLabels(["Select", "Student No", "Name", "Fine Amount", "Reason"])
        self.unpaid_students_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.unpaid_students_table.setMinimumHeight(150)
        layout.addWidget(QLabel("Unpaid Students:"))
        layout.addWidget(self.unpaid_students_table)

        self.mark_paid_btn = QPushButton("Mark Selected as Paid")
        self.mark_paid_btn.clicked.connect(self.mark_selected_paid)
        layout.addWidget(self.mark_paid_btn)

        btn_layout = QHBoxLayout()
        self.return_btn = QPushButton("Return Book")
        self.return_btn.clicked.connect(self.return_book)
        self.lost_btn = QPushButton("Mark as Lost")
        self.lost_btn.clicked.connect(self.mark_lost)
        btn_layout.addWidget(self.return_btn)
        btn_layout.addWidget(self.lost_btn)
        layout.addLayout(btn_layout)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn)

        self.setLayout(layout)

        self.borrow_details = None  # To store loaded borrow details

        # Load currently borrowed books on window open
        self.load_borrowed_books()
        self.load_unpaid_students()

    def load_borrow_details(self):
        """
        Load and display details of a specific borrow record.

        Validates input, queries the database for active borrow records,
        and displays the borrow information for processing.
        """
        borrow_id = self.borrow_id_input.text().strip()
        if not borrow_id:
            QMessageBox.warning(self, "Missing Data", "Please enter Borrow ID.")
            return

        try:
            borrow_id_int = int(borrow_id)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Borrow ID must be an integer.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        try:
            # Query active borrow record with book details
            cursor.execute("""
                SELECT b.borrow_id, b.student_no, b.book_id, bk.title, b.date_borrowed, b.date_due, b.borrow_status
                FROM Borrowed b
                JOIN Books bk ON b.book_id = bk.book_id
                WHERE b.borrow_id = %s AND b.borrow_status = 'Borrowed'
            """, (borrow_id_int,))
            row = cursor.fetchone()
            if not row:
                QMessageBox.warning(self, "Not Found", "Borrow record not found or already returned.")
                self.details_display.setText("")
                self.borrow_details = None
                return

            self.borrow_details = {
                'borrow_id': row[0],
                'student_no': row[1],
                'book_id': row[2],
                'title': row[3],
                'date_borrowed': row[4],
                'date_due': row[5],
                'borrow_status': row[6]
            }

            display = f"""
Borrow ID: {self.borrow_details['borrow_id']}
Student No: {self.borrow_details['student_no']}
Book ID: {self.borrow_details['book_id']}
Title: {self.borrow_details['title']}
Borrowed: {self.borrow_details['date_borrowed']}
Due: {self.borrow_details['date_due']}
Status: {self.borrow_details['borrow_status']}
"""
            self.details_display.setText(display.strip())

            # Load currently borrowed books
            self.load_borrowed_books()

        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            conn.close()

    def mark_selected_paid(self):
        """
        Mark selected unpaid students as paid.

        Updates the return_status of selected students from 'Returned (Unpaid)' to 'Paid'.
        """
        selected_rows = []
        for row in range(self.unpaid_students_table.rowCount()):
            checkbox = self.unpaid_students_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                selected_rows.append(row)

        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select at least one student to mark as paid.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        try:
            for row in selected_rows:
                student_no = self.unpaid_students_table.item(row, 1).text()
                # Update all unpaid returns for this student to 'Paid'
                cursor.execute("""
                    UPDATE Returned
                    SET return_status = 'Paid'
                    WHERE borrow_id IN (
                        SELECT borrow_id FROM Borrowed WHERE student_no = %s
                    ) AND return_status = 'Returned (Unpaid)'
                """, (student_no,))
            conn.commit()
            QMessageBox.information(self, "Success", f"Marked {len(selected_rows)} student(s) as paid.")
            self.load_unpaid_students()  # Refresh the table
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            conn.close()

    def load_unpaid_students(self):
        """
        Load and display all students with unpaid fines in a table with checkboxes.

        Queries the database for return records with 'Returned (Unpaid)' status
        and displays them in a QTableWidget with checkboxes for selection.
        """
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT DISTINCT s.student_no, s.st_name, r.fine_amount, r.fine_reason
                FROM Returned r
                JOIN Borrowed b ON r.borrow_id = b.borrow_id
                JOIN Students s ON b.student_no = s.student_no
                WHERE r.return_status = 'Returned (Unpaid)'
            """)
            rows = cursor.fetchall()
            self.unpaid_students_table.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                # Checkbox for selection
                checkbox = QCheckBox()
                checkbox.setStyleSheet("margin-left: 50%; margin-right: 50%; background-color: white;")
                self.unpaid_students_table.setCellWidget(row_idx, 0, checkbox)
                # Student No
                self.unpaid_students_table.setItem(row_idx, 1, QTableWidgetItem(str(row[0])))
                # Name
                self.unpaid_students_table.setItem(row_idx, 2, QTableWidgetItem(row[1]))
                # Fine Amount
                self.unpaid_students_table.setItem(row_idx, 3, QTableWidgetItem(f"₱{row[2]:.2f}"))
                # Reason
                self.unpaid_students_table.setItem(row_idx, 4, QTableWidgetItem(row[3]))
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            conn.close()

    def load_borrowed_books(self):
        """
        Load and display all currently borrowed books.

        Queries the database for active borrow records and displays
        them in a formatted list for librarian reference.
        """
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT b.borrow_id, b.student_no, bk.title, b.date_borrowed, b.date_due
                FROM Borrowed b
                JOIN Books bk ON b.book_id = bk.book_id
                WHERE b.borrow_status = 'Borrowed'
            """)
            rows = cursor.fetchall()
            if rows:
                table_html = """
                <table border="1" style="border-collapse: collapse; width: 100%; margin: 10px 0;">
                    <tr style="background-color: #f0f0f0; height: 35px;">
                        <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Borrow ID</th>
                        <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Student</th>
                        <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Title</th>
                        <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Borrowed</th>
                        <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Due</th>
                    </tr>
                """
                for row in rows:
                    table_html += f"""
                    <tr style="background-color: white; height: 35px;">
                        <td style="padding: 8px;">{row[0]}</td>
                        <td style="padding: 8px;">{row[1]}</td>
                        <td style="padding: 8px;">{row[2]}</td>
                        <td style="padding: 8px;">{row[3]}</td>
                        <td style="padding: 8px;">{row[4]}</td>
                    </tr>
                    """
                table_html += "</table>"
                self.borrowed_books_display.setText(table_html)
            else:
                self.borrowed_books_display.setText("No books currently borrowed.")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            conn.close()

    def return_book(self):
        """
        Process a normal book return with fine calculation.

        Calculates overdue days and applies fine of ₱10 per day,
        then processes the return through the common method.
        """
        if not self.borrow_details:
            QMessageBox.warning(self, "No Details", "Please load borrow details first.")
            return

        date_returned = datetime.now().date()
        date_due = self.borrow_details['date_due']
        overdue_days = max(0, (date_returned - date_due).days)
        fine_amount = min(overdue_days * 10.0, 100.0)
        fine_reason = f"Overdue by {overdue_days} days" if overdue_days > 0 else "Returned on time"

        self.process_return(fine_amount, fine_reason, 'Returned')

    def mark_lost(self):
        """
        Mark a book as lost, charge the full book price as fine, and automatically delete the book.

        Retrieves the book's price from the database, processes
        the loss as a special return with full price fine, and
        automatically removes the book from the catalog.
        """
        if not self.borrow_details:
            QMessageBox.warning(self, "No Details", "Please load borrow details first.")
            return

        # Get book price for fine calculation
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT price FROM Books WHERE book_id = %s", (self.borrow_details['book_id'],))
            row = cursor.fetchone()
            if not row:
                QMessageBox.warning(self, "Error", "Book price not found.")
                return
            fine_amount = float(row[0])
            fine_reason = "Book lost - charged full price"
            self.process_return(fine_amount, fine_reason, 'Lost')
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            conn.close()

    def process_return(self, fine_amount, fine_reason, status):
        """
        Common method to process book returns and losses.

        Inserts return record into Returned table, updates borrow status,
        and refreshes the UI to reflect changes. If the book is lost,
        automatically deletes it from the catalog. For returns with fines,
        confirms payment before setting return status.

        Args:
            fine_amount: Amount of fine to charge
            fine_reason: Reason for the fine
            status: New status for the borrow record ('Returned' or 'Lost')
        """
        date_returned = datetime.now().date()

        # Determine return status based on fine and payment confirmation
        if fine_amount > 0:
            reply = QMessageBox.question(self, 'Payment Confirmation',
                                         f"Fine: ₱{fine_amount:.2f} ({fine_reason})\n\nDid the student pay the fine?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                return_status = 'Paid'
            else:
                return_status = 'Returned (Unpaid)'
        else:
            return_status = 'Returned'

        conn = connect_db()
        cursor = conn.cursor()
        try:
            # Insert return record with fine details and return status
            cursor.execute("""
                INSERT INTO Returned (borrow_id, book_id, date_returned, fine_amount, fine_reason, return_status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (self.borrow_details['borrow_id'], self.borrow_details['book_id'], date_returned, fine_amount, fine_reason, return_status))

            # Update borrow status to reflect return/loss
            cursor.execute("UPDATE Borrowed SET borrow_status = %s WHERE borrow_id = %s", (status, self.borrow_details['borrow_id']))

            # If the book is lost, automatically delete it from the catalog
            if status == 'Lost':
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                cursor.execute("DELETE FROM Books WHERE book_id = %s", (self.borrow_details['book_id'],))
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

            conn.commit()
            QMessageBox.information(self, "Success", f"Book {status.lower()}. Fine: ₱{fine_amount:.2f} ({fine_reason}). Status: {return_status}")
            self.details_display.setText("")
            self.borrow_details = None
            self.borrow_id_input.clear()
            # Refresh the borrowed books list
            self.load_borrowed_books()
            self.load_unpaid_students()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            conn.close()

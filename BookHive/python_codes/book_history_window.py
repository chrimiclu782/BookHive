"""
Book History Window

This module displays the complete borrowing history for a specific book,
including all past and current loans, return dates, and any associated fines.
"""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QMessageBox, QScrollArea
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from db import connect_db

class BookHistoryWindow(QWidget):
    """
    Window for displaying the complete borrowing history of a specific book.

    Shows all borrow records for the book, including student information,
    dates, status, return information, and fines.
    """

    def __init__(self, book_id):
        """
        Initialize the book history window.

        Args:
            book_id: The ISBN or ID of the book to show history for
        """
        super().__init__()
        self.book_id = book_id
        self.setWindowTitle(f"History for Book ID: {book_id}")
        self.setGeometry(200, 200, 600, 400)
        self.setWindowIcon(QIcon("python_codes/assets/BookHive_Logo.png"))
        self.setStyleSheet("""
            QWidget {
                background-color: #f7b918;
                color: #402c12;
            }
            QLabel {
                color: #402c12;
                font-size: 16px;
            }
            QPushButton {
                background-color: #808080;
                color: #402c12;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #A9A9A9;
            }
        """)
        self.init_ui()
        self.load_history()

    def init_ui(self):
        """Set up the user interface components."""
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"📖 Borrow History for Book ID: {self.book_id}"))

        self.history_display = QLabel()
        self.history_display.setWordWrap(True)
        self.history_scroll = QScrollArea()
        self.history_scroll.setWidget(self.history_display)
        self.history_scroll.setWidgetResizable(True)
        self.history_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.history_scroll.setMinimumHeight(200)
        layout.addWidget(self.history_scroll)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn)

        self.setLayout(layout)

    def load_history(self):
        """
        Load and display the borrowing history for the book.

        Queries the Borrowed table joined with Returned table to get
        complete history including return dates and fines.
        """
        conn = connect_db()
        cursor = conn.cursor()
        # Query complete borrow history with return information
        cursor.execute("""
            SELECT br.student_no, br.date_borrowed, br.date_due, br.borrow_status,
                   r.date_returned, r.fine_amount, r.fine_reason
            FROM Borrowed br
            LEFT JOIN Returned r ON br.borrow_id = r.borrow_id
            WHERE br.book_id = %s
            ORDER BY br.date_borrowed DESC
        """, (self.book_id,))
        history = cursor.fetchall()
        conn.close()

        if not history:
            display = "No borrow history found for this book."
        else:
            table_html = """
            <table border="1" style="border-collapse: collapse; width: 100%; margin: 10px 0;">
                <tr style="background-color: #f0f0f0; height: 35px;">
                    <th style="padding: 8px; font-size: 16px; font-weight: bold;">Student</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold;">Borrowed</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold;">Due</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold;">Status</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold;">Returned</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold;">Fine</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold;">Reason</th>
                </tr>
            """
            for h in history:
                table_html += f"""
                <tr style="background-color: white; height: 35px;">
                    <td style="padding: 8px;">{h[0]}</td>
                    <td style="padding: 8px;">{h[1]}</td>
                    <td style="padding: 8px;">{h[2]}</td>
                    <td style="padding: 8px;">{h[3]}</td>
                    <td style="padding: 8px;">{h[4] or 'N/A'}</td>
                    <td style="padding: 8px;">₱{h[5] or 0}</td>
                    <td style="padding: 8px;">{h[6] or 'N/A'}</td>
                </tr>
                """
            table_html += "</table>"
            self.history_display.setText(table_html)

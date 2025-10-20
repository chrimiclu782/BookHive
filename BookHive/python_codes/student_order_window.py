"""
Student Order Window

This module provides the student interface for ordering books from the library system.
Students can add multiple books to an order, view the total amount, and finalize the order.
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QScrollArea, QListWidget, QListWidgetItem
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from db import connect_db
from datetime import datetime

class StudentOrderWindow(QWidget):
    """
    Student order window for purchasing books.

    Allows students to:
    - Add books to order by book ID
    - View order list with prices
    - Calculate total amount
    - Finalize the order
    """

    def __init__(self, student_no=None):
        """
        Initialize the student order window.

        Args:
            student_no: The authenticated student's number
        """
        super().__init__()
        self.student_no = str(student_no) if student_no else None
        self.order_list = []  # List of (book_id, title, price) tuples
        self.setWindowTitle("Order Books")
        self.setGeometry(150, 150, 600, 500)
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
            QListWidget {
                background-color: white;
                color: #402c12;
                border: 1px solid #ccc;
                font-size: 14px;
                font-family: "Arial Black";
            }
        """)
        self.init_ui()

    def init_ui(self):
        """Set up the user interface components."""
        # Logo
        self.logo_label = QLabel()
        pixmap = QPixmap("python_codes/assets/BookHive_Logo.png")
        if not pixmap.isNull():
            self.logo_label.setPixmap(pixmap.scaled(60, 60, Qt.KeepAspectRatio))
        self.logo_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.logo_label)
        layout.addWidget(QLabel("📚 Order Books"))

        # Book ID input
        self.book_id_label = QLabel("Book ID to Order:")
        self.book_id_input = QLineEdit()
        self.add_btn = QPushButton("Add to Order")
        self.add_btn.clicked.connect(self.add_to_order)

        layout.addWidget(self.book_id_label)
        layout.addWidget(self.book_id_input)
        layout.addWidget(self.add_btn)

        # Order list
        self.order_label = QLabel("Your Order:")
        self.order_list_widget = QListWidget()
        layout.addWidget(self.order_label)
        layout.addWidget(self.order_list_widget)

        # Total amount
        self.total_label = QLabel("Total Amount: ₱0.00")
        layout.addWidget(self.total_label)

        # Buttons
        btn_layout = QHBoxLayout()
        self.finalize_btn = QPushButton("Finalize Order")
        self.finalize_btn.clicked.connect(self.finalize_order)
        self.clear_btn = QPushButton("Clear Order")
        self.clear_btn.clicked.connect(self.clear_order)
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.finalize_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Disable if no student
        if not self.student_no:
            self.add_btn.setDisabled(True)
            self.finalize_btn.setDisabled(True)

    def add_to_order(self):
        """Add a book to the order list."""
        book_id = self.book_id_input.text().strip()
        if not book_id:
            QMessageBox.warning(self, "Missing Data", "Please enter a Book ID.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT title, price, supplier_id FROM Books WHERE book_id = %s", (book_id,))
            book = cursor.fetchone()
            if not book:
                QMessageBox.warning(self, "Not Found", "Book ID not found.")
                return

            title, price, supplier_id = book
            price = float(price)  # Convert Decimal to float
            self.order_list.append((book_id, title, price, supplier_id))
            self.update_order_display()
            self.book_id_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))
        finally:
            try: conn.close()
            except Exception: pass

    def update_order_display(self):
        """Update the order list display and total amount."""
        self.order_list_widget.clear()
        total = 0.0
        for book_id, title, price, supplier_id in self.order_list:
            item_text = f"{book_id} - {title} - ₱{price:.2f}"
            self.order_list_widget.addItem(QListWidgetItem(item_text))
            total += price
        self.total_label.setText(f"Total Amount: ₱{total:.2f}")

    def finalize_order(self):
        """Finalize the order by inserting into database."""
        if not self.order_list:
            QMessageBox.warning(self, "Empty Order", "Please add books to your order first.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            date_ordered = datetime.now().date()
            total_amount = sum(price for _, _, price, _ in self.order_list)

            for book_id, title, price, supplier_id in self.order_list:
                cursor.execute("""
                    INSERT INTO BookOrders (student_no, supplier_id, title, total_amount, date_ordered)
                    VALUES (%s, %s, %s, %s, %s)
                """, (self.student_no, supplier_id, title, price, date_ordered))

            conn.commit()
            QMessageBox.information(self, "Success", f"Order placed successfully! Total: ₱{total_amount:.2f}")
            self.clear_order()
        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))
        finally:
            try: conn.close()
            except Exception: pass

    def clear_order(self):
        """Clear the order list."""
        self.order_list.clear()
        self.update_order_display()

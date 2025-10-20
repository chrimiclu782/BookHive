"""
Student Order View Window

This module provides the student interface for viewing their book orders.
Students can view all their orders, including status and details.
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QScrollArea, QLineEdit
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from db import connect_db

class StudentOrderViewWindow(QWidget):
    """
    Student order view window.

    Allows students to:
    - View all their orders sorted by order_id DESC (newest first)
    - Search orders by order ID
    """

    def __init__(self, student_no=None):
        """Initialize the student order view window."""
        super().__init__()
        self.student_no = str(student_no) if student_no else None
        self.setWindowTitle("View My Orders")
        self.setGeometry(150, 150, 800, 600)
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
            QLineEdit {
                background-color: white;
                color: #402c12;
                border: 1px solid #ccc;
                padding: 5px;
                font-size: 16px;
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
        layout.addWidget(QLabel("📋 My Orders"))

        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search Order ID:"))
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.filter_orders)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Orders list
        self.orders_label = QLabel("Orders:")
        self.orders_scroll_area = QScrollArea()
        self.orders_widget = QWidget()
        self.orders_layout = QVBoxLayout()
        self.orders_widget.setLayout(self.orders_layout)
        self.orders_scroll_area.setWidget(self.orders_widget)
        self.orders_scroll_area.setWidgetResizable(True)
        layout.addWidget(self.orders_label)
        layout.addWidget(self.orders_scroll_area)

        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn)

        self.setLayout(layout)
        self.load_orders()

    def load_orders(self):
        """Load and display all orders for the student sorted by order_id DESC."""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT order_id, title, order_status, payment_status, total_amount, date_ordered
                FROM BookOrders
                WHERE student_no = %s
                ORDER BY order_id DESC
            """, (self.student_no,))
            orders = cursor.fetchall()
        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))
            orders = []
        finally:
            try: conn.close()
            except Exception: pass

        # Clear existing orders
        for i in reversed(range(self.orders_layout.count())):
            widget = self.orders_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if not orders:
            self.orders_layout.addWidget(QLabel("No orders found."))
            return

        for order in orders:
            order_id, title, order_status, payment_status, total_amount, date_ordered = order
            order_text = f"Order {order_id} - {title} - {order_status} - {payment_status} - ₱{total_amount:.2f} - {date_ordered}"
            order_label = QLabel(order_text)
            order_label.setStyleSheet("""
                QLabel {
                    background-color: white;
                    color: #402c12;
                    border: 1px solid #ccc;
                    padding: 10px;
                    margin: 5px 0;
                    font-size: 14px;
                    font-family: "Arial Black";
                }
            """)
            self.orders_layout.addWidget(order_label)

    def filter_orders(self):
        """Filter orders based on search input."""
        search_text = self.search_input.text().strip()
        for i in range(self.orders_layout.count()):
            widget = self.orders_layout.itemAt(i).widget()
            if isinstance(widget, QLabel) and widget.text() != "No orders found.":
                # Extract order_id from the label text (format: "Order {order_id} - ...")
                text = widget.text()
                if text.startswith("Order "):
                    order_id_str = text.split(" - ")[0].replace("Order ", "")
                    try:
                        order_id = int(order_id_str)
                        if search_text and str(order_id).startswith(search_text):
                            widget.show()
                        elif not search_text:
                            widget.show()
                        else:
                            widget.hide()
                    except ValueError:
                        widget.hide()  # Hide if parsing fails
                else:
                    widget.hide()

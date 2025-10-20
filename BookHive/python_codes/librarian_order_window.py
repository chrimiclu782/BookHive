"""
Librarian Order Window

This module provides the librarian interface for managing book orders.
Librarians can view all orders, update order status and payment status.
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QScrollArea, QComboBox, QListWidget, QListWidgetItem
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from db import connect_db

class LibrarianOrderWindow(QWidget):
    """
    Librarian order management window.

    Allows librarians to:
    - View all orders sorted by order_id ASC (oldest first)
    - Update order_status and payment_status for selected orders
    """

    def __init__(self):
        """Initialize the librarian order window."""
        super().__init__()
        self.selected_order_id = None
        self.setWindowTitle("Manage Orders")
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
            QListWidget {
                background-color: white;
                color: #402c12;
                border: 1px solid #ccc;
                font-size: 14px;
                font-family: "Arial Black";
            }
            QComboBox {
                background-color: white;
                color: #402c12;
                border: 1px solid #ccc;
                padding: 5px;
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
        layout.addWidget(QLabel("📋 Manage Orders"))

        # Orders list
        self.orders_label = QLabel("Orders:")
        self.orders_list_widget = QListWidget()
        self.orders_list_widget.itemClicked.connect(self.select_order)
        layout.addWidget(self.orders_label)
        layout.addWidget(self.orders_list_widget)

        # Update section
        update_layout = QVBoxLayout()
        self.selected_label = QLabel("Selected Order: None")
        update_layout.addWidget(self.selected_label)

        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Order Status:"))
        self.order_status_combo = QComboBox()
        self.order_status_combo.addItems(["Pending", "Processing", "Shipped", "Delivered", "Cancelled"])
        status_layout.addWidget(self.order_status_combo)

        payment_layout = QHBoxLayout()
        payment_layout.addWidget(QLabel("Payment Status:"))
        self.payment_status_combo = QComboBox()
        self.payment_status_combo.addItems(["Unpaid", "Paid", "Refunded"])
        payment_layout.addWidget(self.payment_status_combo)

        update_layout.addLayout(status_layout)
        update_layout.addLayout(payment_layout)

        self.update_btn = QPushButton("Update Order")
        self.update_btn.clicked.connect(self.update_order)
        update_layout.addWidget(self.update_btn)

        layout.addLayout(update_layout)

        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn)

        self.setLayout(layout)
        self.load_orders()

    def load_orders(self):
        """Load and display all orders sorted by date_ordered ASC."""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT order_id, student_no, title, order_status, payment_status, total_amount, date_ordered
                FROM BookOrders
                ORDER BY order_id ASC
            """)
            orders = cursor.fetchall()
        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))
            orders = []
        finally:
            try: conn.close()
            except Exception: pass

        self.orders_list_widget.clear()
        for order in orders:
            order_id, student_no, title, order_status, payment_status, total_amount, date_ordered = order
            item_text = f"Order {order_id} - {student_no} - {title} - {order_status} - {payment_status} - ₱{total_amount:.2f} - {date_ordered}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, order_id)
            self.orders_list_widget.addItem(item)

    def select_order(self, item):
        """Select an order and populate the update fields."""
        self.selected_order_id = item.data(Qt.UserRole)
        self.selected_label.setText(f"Selected Order: {self.selected_order_id}")

        # Load current status
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT order_status, payment_status FROM BookOrders WHERE order_id = %s", (self.selected_order_id,))
            status = cursor.fetchone()
            if status:
                self.order_status_combo.setCurrentText(status[0])
                self.payment_status_combo.setCurrentText(status[1])
        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))
        finally:
            try: conn.close()
            except Exception: pass

    def update_order(self):
        """Update the selected order's status."""
        if not self.selected_order_id:
            QMessageBox.warning(self, "No Selection", "Please select an order to update.")
            return

        order_status = self.order_status_combo.currentText()
        payment_status = self.payment_status_combo.currentText()

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE BookOrders
                SET order_status = %s, payment_status = %s
                WHERE order_id = %s
            """, (order_status, payment_status, self.selected_order_id))
            conn.commit()
            QMessageBox.information(self, "Success", "Order updated successfully.")
            self.load_orders()
            self.selected_order_id = None
            self.selected_label.setText("Selected Order: None")
        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))
        finally:
            try: conn.close()
            except Exception: pass

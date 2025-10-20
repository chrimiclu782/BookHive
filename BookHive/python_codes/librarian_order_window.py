"""
Librarian Order Window

This module provides the librarian interface for managing book orders.
Librarians can view all orders, update order status and payment status.
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QScrollArea, QComboBox, QCheckBox, QGroupBox
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
        self.selected_orders = []  # List of selected order_ids
        self.order_checkboxes = []  # List of checkboxes with their order_ids and amounts
        self.total_amount = 0.0
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
            QCheckBox {
                background-color: white;
                color: #402c12;
                border: 1px solid #ccc;
                padding: 5px;
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

        # Orders list with checkboxes
        self.orders_label = QLabel("Orders:")
        self.orders_scroll_area = QScrollArea()
        self.orders_widget = QWidget()
        self.orders_layout = QVBoxLayout()
        self.orders_widget.setLayout(self.orders_layout)
        self.orders_scroll_area.setWidget(self.orders_widget)
        self.orders_scroll_area.setWidgetResizable(True)
        layout.addWidget(self.orders_label)
        layout.addWidget(self.orders_scroll_area)

        # Total amount label
        self.total_label = QLabel("Total Amount: ₱0.00")
        layout.addWidget(self.total_label)

        # Update section
        update_layout = QVBoxLayout()

        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Order Status:"))
        self.order_status_combo = QComboBox()
        self.order_status_combo.addItems(["Pending", "Arrived", "Received", "Returned", "Cancelled"])
        status_layout.addWidget(self.order_status_combo)

        payment_layout = QHBoxLayout()
        payment_layout.addWidget(QLabel("Payment Status:"))
        self.payment_status_combo = QComboBox()
        self.payment_status_combo.addItems(["Unpaid", "Paid", "Refunded"])
        payment_layout.addWidget(self.payment_status_combo)

        update_layout.addLayout(status_layout)
        update_layout.addLayout(payment_layout)

        self.update_btn = QPushButton("Update Selected Orders")
        self.update_btn.clicked.connect(self.update_orders)
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

        # Clear existing checkboxes
        for checkbox, _, _ in self.order_checkboxes:
            checkbox.setParent(None)
        self.order_checkboxes.clear()
        self.selected_orders.clear()
        self.total_amount = 0.0
        self.total_label.setText("Total Amount: ₱0.00")

        for order in orders:
            order_id, student_no, title, order_status, payment_status, total_amount, date_ordered = order
            checkbox_text = f"Order {order_id} - {student_no} - {title} - {order_status} - {payment_status} - ₱{total_amount:.2f} - {date_ordered}"
            checkbox = QCheckBox(checkbox_text)
            checkbox.stateChanged.connect(lambda state, oid=order_id, amt=total_amount: self.on_checkbox_changed(state, oid, amt))
            self.orders_layout.addWidget(checkbox)
            self.order_checkboxes.append((checkbox, order_id, total_amount))

    def on_checkbox_changed(self, state, order_id, amount):
        """Handle checkbox state changes to update selected orders and total amount."""
        if state == 2:  # Checked
            if order_id not in self.selected_orders:
                self.selected_orders.append(order_id)
                self.total_amount += float(amount)
        else:  # Unchecked
            if order_id in self.selected_orders:
                self.selected_orders.remove(order_id)
                self.total_amount -= float(amount)
        self.total_label.setText(f"Total Amount: ₱{self.total_amount:.2f}")

    def update_orders(self):
        """Update the selected orders' status in batch."""
        if not self.selected_orders:
            QMessageBox.warning(self, "No Selection", "Please select at least one order to update.")
            return

        order_status = self.order_status_combo.currentText()
        payment_status = self.payment_status_combo.currentText()

        try:
            conn = connect_db()
            cursor = conn.cursor()
            for order_id in self.selected_orders:
                cursor.execute("""
                    UPDATE BookOrders
                    SET order_status = %s, payment_status = %s
                    WHERE order_id = %s
                """, (order_status, payment_status, order_id))
            conn.commit()
            QMessageBox.information(self, "Success", f"{len(self.selected_orders)} order(s) updated successfully.")
            self.load_orders()
        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))
        finally:
            try: conn.close()
            except Exception: pass

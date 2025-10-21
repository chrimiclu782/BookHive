"""
Supplier Management Window

This module provides a dedicated interface for managing library suppliers.
Librarians can view, add, update, delete suppliers, and search by name or ID.
"""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit, QMessageBox, QHBoxLayout, QScrollArea, QComboBox, QApplication, QDialog, QFormLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from db import connect_db

class SupplierWindow(QWidget):
    """
    Supplier management window for comprehensive supplier operations.

    Provides functionality for:
    - Viewing all suppliers
    - Adding new suppliers
    - Updating existing supplier information
    - Deleting suppliers
    - Searching suppliers by name or ID
    """

    def __init__(self):
        """Initialize the supplier management window."""
        super().__init__()
        self.setWindowTitle("Supplier Management")
        self.setWindowIcon(QIcon("python_codes/assets/BookHive_Logo.png"))
        screen = QApplication.desktop().screenGeometry()
        self.setGeometry((screen.width() - 900) // 2, 50, 900, 600)
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
            QComboBox {
                background-color: white;
                color: #402c12;
                border: 1px solid #ccc;
                padding: 5px;
                font-size: 16px;
                font-family: "Arial Black";
            }
            QComboBox::down-arrow {
                color: gray;
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
        """Set up the user interface components for supplier management."""
        # Logo at the top center
        self.logo_label = QLabel()
        pixmap = QPixmap("python_codes/assets/BookHive_Logo.png")
        if not pixmap.isNull():
            self.logo_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
        self.logo_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.logo_label)
        layout.addWidget(QLabel("🏢 Supplier Management"))

        self.supplier_id_input = QLineEdit()
        self.supplier_id_input.setPlaceholderText("Supplier ID (for update/delete)")
        self.supplier_name_input = QLineEdit()
        self.supplier_name_input.setPlaceholderText("Supplier Name")
        self.supplier_contact_input = QLineEdit()
        self.supplier_contact_input.setPlaceholderText("Contact (optional)")
        self.supplier_location_input = QLineEdit()
        self.supplier_location_input.setPlaceholderText("Location (optional)")

        layout.addWidget(self.supplier_id_input)
        layout.addWidget(self.supplier_name_input)
        layout.addWidget(self.supplier_contact_input)
        layout.addWidget(self.supplier_location_input)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Supplier")
        self.update_btn = QPushButton("Update Supplier")
        self.delete_btn = QPushButton("Delete Supplier")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        self.search_label = QLabel("Search Supplier:")
        self.search_input = QLineEdit()
        self.search_attribute = QComboBox()
        self.search_attribute.addItems(["Name", "ID"])
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search_suppliers)
        self.view_all_btn = QPushButton("View All")
        self.view_all_btn.clicked.connect(self.load_suppliers)
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_attribute)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.view_all_btn)
        layout.addLayout(search_layout)

        self.suppliers_display = QLabel()
        self.suppliers_display.setWordWrap(True)
        self.suppliers_scroll = QScrollArea()
        self.suppliers_scroll.setWidget(self.suppliers_display)
        self.suppliers_scroll.setWidgetResizable(True)
        self.suppliers_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.suppliers_scroll.setMinimumHeight(200)
        layout.addWidget(self.suppliers_scroll)

        self.back_btn = QPushButton("Back")
        self.back_btn.clicked.connect(self.close)
        layout.addWidget(self.back_btn)

        self.setLayout(layout)

        self.add_btn.clicked.connect(self.add_supplier)
        self.update_btn.clicked.connect(self.update_supplier)
        self.delete_btn.clicked.connect(self.delete_supplier)

        self.load_suppliers()

    def load_suppliers(self):
        """
        Load and display all suppliers.

        Queries the Suppliers table and displays supplier information
        in a formatted table.
        """
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT supplier_id, supplier_name, supplier_contact, supplier_location FROM Suppliers ORDER BY supplier_id")
        suppliers = cursor.fetchall()
        conn.close()
        if suppliers:
            table_html = """
            <table border="1" style="border-collapse: collapse; width: 100%; margin: 10px 0; font-family: 'Arial Black';">
                <tr style="background-color: #f0f0f0; height: 35px;">
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Supplier ID</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Name</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Contact</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Location</th>
                </tr>
            """
            for s in suppliers:
                table_html += f"""
                <tr style="background-color: white; height: 35px;">
                    <td style="padding: 8px;">{s[0]}</td>
                    <td style="padding: 8px;">{s[1]}</td>
                    <td style="padding: 8px;">{s[2] or 'N/A'}</td>
                    <td style="padding: 8px;">{s[3] or 'N/A'}</td>
                </tr>
                """
            table_html += "</table>"
            self.suppliers_display.setText(table_html)
        else:
            self.suppliers_display.setText("No suppliers found.")

    def search_suppliers(self):
        """
        Search for suppliers by selected attribute.

        Performs a partial match search based on the selected attribute and displays matching results.
        If no keyword is provided, loads all suppliers.
        """
        keyword = self.search_input.text().strip()
        attribute = self.search_attribute.currentText()
        column_map = {
            "Name": "supplier_name",
            "ID": "supplier_id"
        }
        column = column_map.get(attribute, "supplier_name")
        if not keyword:
            self.load_suppliers()
            return
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(f"SELECT supplier_id, supplier_name, supplier_contact, supplier_location FROM Suppliers WHERE {column} LIKE %s ORDER BY supplier_id", (f"%{keyword}%",))
        suppliers = cursor.fetchall()
        conn.close()
        if suppliers:
            table_html = """
            <table border="1" style="border-collapse: collapse; width: 100%; margin: 10px 0; font-family: 'Arial Black';">
                <tr style="background-color: #f0f0f0; height: 35px;">
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Supplier ID</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Name</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Contact</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Location</th>
                </tr>
            """
            for s in suppliers:
                table_html += f"""
                <tr style="background-color: white; height: 35px;">
                    <td style="padding: 8px;">{s[0]}</td>
                    <td style="padding: 8px;">{s[1]}</td>
                    <td style="padding: 8px;">{s[2] or 'N/A'}</td>
                    <td style="padding: 8px;">{s[3] or 'N/A'}</td>
                </tr>
                """
            table_html += "</table>"
            self.suppliers_display.setText(table_html)
        else:
            self.suppliers_display.setText("No suppliers found.")

    def add_supplier(self):
        """
        Add a new supplier to the database.

        Validates required fields and inserts the supplier record.
        """
        name = self.supplier_name_input.text().strip()
        contact = self.supplier_contact_input.text().strip()
        location = self.supplier_location_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Missing Data", "Supplier Name is required.")
            self.supplier_name_input.setFocus()
            return

        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Suppliers (supplier_name, supplier_contact, supplier_location) VALUES (%s, %s, %s)",
                (name, contact or None, location or None)
            )
            conn.commit()
            QMessageBox.information(self, "Success", "Supplier added successfully.")
            self.load_suppliers()
            self.clear_inputs()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            conn.close()

    def update_supplier(self):
        """
        Update an existing supplier's information.

        Validates supplier ID and updates the record.
        """
        supplier_id = self.supplier_id_input.text().strip()
        name = self.supplier_name_input.text().strip()
        contact = self.supplier_contact_input.text().strip()
        location = self.supplier_location_input.text().strip()

        if not supplier_id:
            QMessageBox.warning(self, "Missing Data", "Supplier ID is required for update.")
            self.supplier_id_input.setFocus()
            return

        try:
            supplier_id_int = int(supplier_id)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Supplier ID must be an integer.")
            self.supplier_id_input.setFocus()
            return

        if not name:
            QMessageBox.warning(self, "Missing Data", "Supplier Name is required.")
            self.supplier_name_input.setFocus()
            return

        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE Suppliers SET supplier_name=%s, supplier_contact=%s, supplier_location=%s WHERE supplier_id=%s",
                (name, contact or None, location or None, supplier_id_int)
            )
            conn.commit()
            QMessageBox.information(self, "Success", "Supplier updated successfully.")
            self.load_suppliers()
            self.clear_inputs()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            conn.close()

    def delete_supplier(self):
        """
        Delete a supplier from the database.

        Validates supplier ID and deletes the record.
        """
        supplier_id = self.supplier_id_input.text().strip()

        if not supplier_id:
            QMessageBox.warning(self, "Missing Data", "Supplier ID is required for delete.")
            self.supplier_id_input.setFocus()
            return

        try:
            supplier_id_int = int(supplier_id)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Supplier ID must be an integer.")
            self.supplier_id_input.setFocus()
            return

        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this supplier?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return

        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Suppliers WHERE supplier_id=%s", (supplier_id_int,))
            conn.commit()
            QMessageBox.information(self, "Success", "Supplier deleted successfully.")
            self.load_suppliers()
            self.clear_inputs()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            conn.close()

    def clear_inputs(self):
        """Clear all input fields."""
        self.supplier_id_input.clear()
        self.supplier_name_input.clear()
        self.supplier_contact_input.clear()
        self.supplier_location_input.clear()

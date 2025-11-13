"""
Librarian Registration Window

This module provides the user interface for librarian registration in the BookHive system.
It handles user input validation, password hashing, and database insertion for new librarians.
"""

from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QApplication
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
import bcrypt
from db import connect_db
from app import AuthApp

class LibrarianRegisterWindow(QWidget):
    """
    Window for registering new librarians in the library system.

    Collects librarian information including ID, name, email, and password,
    validates input, hashes passwords, and stores librarian data in the database.
    """

    def __init__(self):
        """Initialize the librarian registration window."""
        super().__init__()
        self.setWindowTitle("Librarian Registration")
        screen = QApplication.desktop().screenGeometry()
        self.setGeometry((screen.width() - 350) // 2, 50, 350, 300)
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
        """Set up the user interface components for registration form."""
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full name")
        self.librarian_id_input = QLineEdit()
        self.librarian_id_input.setPlaceholderText("Librarian ID")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Password")

        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.register_librarian)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_registration)

        # Logo at the top center
        self.logo_label = QLabel()
        pixmap = QPixmap("python_codes/assets/BookHive_Logo.png")
        if not pixmap.isNull():
            self.logo_label.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio))
        self.logo_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.logo_label)
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Librarian ID:"))
        layout.addWidget(self.librarian_id_input)
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.register_btn)
        layout.addWidget(self.cancel_btn)
        self.setLayout(layout)

    def register_librarian(self):
        """
        Process librarian registration with validation and database insertion.

        Validates all required fields, hashes the password for security,
        and inserts the new librarian record into the database.
        """
        name = self.name_input.text().strip()
        librarian_id = self.librarian_id_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not (name and librarian_id and email and password):
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        # Hash password using bcrypt for secure storage
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        conn = connect_db()
        cursor = conn.cursor()
        try:
            # Insert new librarian record into database
            cursor.execute(
                "INSERT INTO Librarians (librarian_id, lib_name, lib_email, lib_password) VALUES (%s, %s, %s, %s)",
                (librarian_id, name, email, hashed)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "DB Error", str(e))
            return
        finally:
            conn.close()

        QMessageBox.information(self, "Success", "Registration completed.")
        self.auth_app = AuthApp()
        self.auth_app.show()
        self.close()

    def cancel_registration(self):
        """
        Cancel registration and return to the login page.
        """
        self.auth_app = AuthApp()
        self.auth_app.show()
        self.close()

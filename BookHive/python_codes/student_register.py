"""
Student Registration Window

This module provides the user interface for student registration in the BookHive system.
It handles user input validation, password hashing, and database insertion for new students.
"""

from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QApplication
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
import bcrypt
from db import connect_db
from app import AuthApp

class RegisterWindow(QWidget):
    """
    Window for registering new students in the library system.

    Collects student information including number, name, email, and password,
    validates input, hashes passwords, and stores student data in the database.
    """

    def __init__(self):
        """Initialize the registration window."""
        super().__init__()
        self.setWindowTitle("Student Registration")
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
        self.student_no_input = QLineEdit()
        self.student_no_input.setPlaceholderText("Student No")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Password")

        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.register_student)

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
        layout.addWidget(QLabel("Student No:"))
        layout.addWidget(self.student_no_input)
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.register_btn)
        layout.addWidget(self.cancel_btn)
        self.setLayout(layout)

    def register_student(self):
        """
        Process student registration with validation and database insertion.

        Validates all required fields, hashes the password for security,
        and inserts the new student record into the database.
        """
        name = self.name_input.text().strip()
        student_no = self.student_no_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not (name and student_no and email and password):
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        # Hash password using bcrypt for secure storage
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        conn = connect_db()
        cursor = conn.cursor()
        try:
            # Insert new student record into database
            cursor.execute(
                "INSERT INTO Students (student_no, st_name, st_email, st_password) VALUES (%s, %s, %s, %s)",
                (student_no, name, email, hashed)
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

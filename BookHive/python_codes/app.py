"""
BookHive Authentication Application

This module provides the main login interface for the BookHive library management system.
It handles user authentication for both students and librarians, with password verification
and navigation to appropriate dashboards.
"""

import sys
import bcrypt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from db import connect_db

class AuthApp(QWidget):
    """
    Main authentication window for BookHive.

    Provides login functionality for students and librarians, with options to register
    new student accounts. Handles password verification and redirects to appropriate
    user dashboards upon successful authentication.
    """

    def __init__(self):
        """Initialize the authentication window with UI components."""
        super().__init__()
        self.setWindowTitle("BookHive Login")
        self.setGeometry(100, 100, 320, 260)
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
        """Set up the user interface components for login and registration."""
        # Logo at the top center
        self.logo_label = QLabel()
        pixmap = QPixmap("python_codes/assets/BookHive_Logo.png")
        if not pixmap.isNull():
            self.logo_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
        self.logo_label.setAlignment(Qt.AlignCenter)

        self.label = QLabel("Email or Student No:")
        self.email_input = QLineEdit()

        self.label2 = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_btn = QPushButton("Login")
        self.register_btn = QPushButton("Register")

        self.login_btn.clicked.connect(self.login)
        self.register_btn.clicked.connect(self.open_register_window)

        layout = QVBoxLayout()
        layout.addWidget(self.logo_label)
        layout.addWidget(self.label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.label2)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn)

        self.setLayout(layout)

    def _verify_hash(self, stored_hash, plain_password):
        """
        Verify a plain password against a stored bcrypt hash.

        Handles different database storage formats (bytes, memoryview, str)
        and ensures compatibility with bcrypt verification.

        Args:
            stored_hash: The hashed password from database
            plain_password: The plain text password to verify

        Returns:
            bool: True if password matches, False otherwise
        """
        if not stored_hash:
            return False
        # Handle different DB types (bytes, memoryview, str)
        if isinstance(stored_hash, memoryview):
            stored_hash = bytes(stored_hash)
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode("utf-8")
        if isinstance(stored_hash, bytes):
            try:
                return bcrypt.checkpw(plain_password.encode("utf-8"), stored_hash)
            except ValueError:
                return False
        return False

    def login(self):
        """
        Authenticate user credentials and redirect to appropriate dashboard.

        Queries both Students and Librarians tables to find matching credentials.
        Uses bcrypt to verify passwords securely.
        """
        identifier = self.email_input.text().strip()
        password = self.password_input.text()

        if not identifier or not password:
            QMessageBox.warning(self, "Input required", "Please enter identifier and password.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        try:
            # Query student credentials - include student_no for passing to StudentWindow
            cursor.execute("""
                SELECT student_no, st_password, st_name FROM Students
                WHERE student_no = %s OR st_email = %s
            """, (identifier, identifier))
            student = cursor.fetchone()

            # Query librarian credentials
            cursor.execute("""
                SELECT lib_password, lib_name FROM Librarians
                WHERE librarian_id = %s OR lib_email = %s
            """, (identifier, identifier))
            librarian = cursor.fetchone()
        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))
            return
        finally:
            try:
                conn.close()
            except Exception:
                pass

        # Verify student credentials and open student dashboard
        if student and self._verify_hash(student[1], password):
            QMessageBox.information(self, "Success", f"Welcome {student[2]} (Student)!")
            # Ensure student_no is passed as string to StudentWindow
            self.open_student_window(student_no=str(student[0]))
        # Verify librarian credentials and open librarian dashboard
        elif librarian and self._verify_hash(librarian[0], password):
            QMessageBox.information(self, "Success", f"Welcome {librarian[1]} (Librarian)!")
            self.open_librarian_window()
        else:
            QMessageBox.warning(self, "Login failed", "Invalid credentials.")

    def open_student_window(self, student_no=None):
        """
        Open the student dashboard window.

        Uses lazy import to avoid circular import issues. Passes the authenticated
        student number to the StudentWindow for personalized functionality.

        Args:
            student_no: The authenticated student's number (optional)
        """
        # Lazy import to avoid circular import errors
        try:
            from student_window import StudentWindow
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Cannot import StudentWindow:\n{e}")
            return
        # Pass student_no so the student window uses the logged-in student number
        # Ensure a non-empty string is passed
        self.student_win = StudentWindow(student_no=str(student_no) if student_no is not None else None)
        self.student_win.show()
        self.close()

    def open_librarian_window(self):
        """Open the librarian dashboard window."""
        try:
            from librarian_window import LibrarianWindow
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Cannot import LibrarianWindow:\n{e}")
            return
        self.librarian_win = LibrarianWindow()
        self.librarian_win.show()
        self.close()

    def open_register_window(self):
        """Open the student registration window."""
        try:
            from student_register import RegisterWindow
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Cannot import RegisterWindow:\n{e}")
            return
        self.register_win = RegisterWindow()
        self.register_win.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AuthApp()
    win.show()
    sys.exit(app.exec())
"""
Role Selection Window

This module provides the user interface for selecting user role during registration.
It allows choosing between Student and Librarian registration, with password protection
for Librarian registration.
"""

from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox, QApplication, QLineEdit
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt

class RoleSelectionWindow(QWidget):
    """
    Window for selecting user role during registration.

    Provides buttons to register as Student or Librarian. Librarian registration
    requires entering a specific password.
    """

    def __init__(self):
        """Initialize the role selection window."""
        super().__init__()
        self.setWindowTitle("Select Role")
        screen = QApplication.desktop().screenGeometry()
        self.setGeometry((screen.width() - 320) // 2, 50, 320, 260)
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
        """)
        self.init_ui()

    def init_ui(self):
        """Set up the user interface components."""
        # Logo at the top center
        self.logo_label = QLabel()
        pixmap = QPixmap("python_codes/assets/BookHive_Logo.png")
        if not pixmap.isNull():
            self.logo_label.setPixmap(pixmap.scaled(500, 500, Qt.KeepAspectRatio))
        self.logo_label.setAlignment(Qt.AlignCenter)

        self.label = QLabel("Select your role to register:")

        self.student_btn = QPushButton("Register as Student")
        self.librarian_btn = QPushButton("Register as Librarian")
        self.cancel_btn = QPushButton("Cancel")

        self.student_btn.clicked.connect(self.register_student)
        self.librarian_btn.clicked.connect(self.register_librarian)
        self.cancel_btn.clicked.connect(self.cancel)

        layout = QVBoxLayout()
        layout.addWidget(self.logo_label)
        layout.addWidget(self.label)
        layout.addWidget(self.student_btn)
        layout.addWidget(self.librarian_btn)
        layout.addWidget(self.cancel_btn)

        self.setLayout(layout)

    def register_student(self):
        """Open the student registration window."""
        try:
            from student_register import RegisterWindow
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Cannot import RegisterWindow:\n{e}")
            return
        self.register_win = RegisterWindow()
        self.register_win.show()
        self.close()

    def register_librarian(self):
        """Prompt for librarian password and open librarian registration if correct."""
        # Create a custom dialog with password input matching registration style
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout

        dialog = QDialog(self)
        dialog.setWindowTitle("Librarian Password")
        dialog.setStyleSheet("""
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

        layout = QVBoxLayout()
        label = QLabel("Enter librarian password:")
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")

        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addWidget(label)
        layout.addWidget(password_input)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        def on_ok():
            password = password_input.text()
            if password == "IamalibrarianatTIP":
                try:
                    from librarian_register import LibrarianRegisterWindow
                except Exception as e:
                    QMessageBox.critical(self, "Import Error", f"Cannot import LibrarianRegisterWindow:\n{e}")
                    return
                self.lib_register_win = LibrarianRegisterWindow()
                self.lib_register_win.show()
                self.close()
                dialog.accept()
            else:
                QMessageBox.warning(self, "Incorrect Password", "The password is incorrect.")

        def on_cancel():
            dialog.reject()

        ok_btn.clicked.connect(on_ok)
        cancel_btn.clicked.connect(on_cancel)

        dialog.exec_()

    def cancel(self):
        """Cancel and return to login."""
        try:
            from app import AuthApp
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Cannot import AuthApp:\n{e}")
            return
        self.auth_app = AuthApp()
        self.auth_app.show()
        self.close()

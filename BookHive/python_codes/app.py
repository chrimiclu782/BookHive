import sys
import bcrypt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
)
from db import connect_db

class AuthApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BookHive Login")
        self.setGeometry(100, 100, 320, 260)
        self.init_ui()

    def init_ui(self):
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
        layout.addWidget(self.label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.label2)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn)

        self.setLayout(layout)

    def _verify_hash(self, stored_hash, plain_password):
        if not stored_hash:
            return False
        # handle different DB types (bytes, memoryview, str)
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
        identifier = self.email_input.text().strip()
        password = self.password_input.text()

        if not identifier or not password:
            QMessageBox.warning(self, "Input required", "Please enter identifier and password.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        try:
            # include student_no so we can pass it to StudentWindow
            cursor.execute("""
                SELECT student_no, st_password, st_name FROM Students 
                WHERE student_no = %s OR st_email = %s
            """, (identifier, identifier))
            student = cursor.fetchone()

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

        if student and self._verify_hash(student[1], password):
            QMessageBox.information(self, "Success", f"Welcome {student[2]} (Student)!")
            # ensure student_no is a string and pass it to StudentWindow
            self.open_student_window(student_no=str(student[0]))
        elif librarian and self._verify_hash(librarian[0], password):
            QMessageBox.information(self, "Success", f"Welcome {librarian[1]} (Librarian)!")
            self.open_librarian_window()
        else:
            QMessageBox.warning(self, "Login failed", "Invalid credentials.")

    def open_student_window(self, student_no=None):
        # lazy import and fallback names to avoid circular/import errors
        try:
            from student_window import StudentWindow
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Cannot import StudentWindow:\n{e}")
            return
        # pass student_no so the student window uses the logged-in student number
        # ensure a non-empty string is passed
        self.student_win = StudentWindow(student_no=str(student_no) if student_no is not None else None)
        self.student_win.show()
        self.close()

    def open_librarian_window(self):
        try:
            from librarian_window import LibrarianWindow
        except Exception:
            try:
                from librarian_window import LibrarianWindow
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Cannot import LibrarianWindow:\n{e}")
                return
        self.librarian_win = LibrarianWindow()
        self.librarian_win.show()
        self.close()

    def open_register_window(self):
        try:
            from student_register import RegisterWindow
        except Exception:
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
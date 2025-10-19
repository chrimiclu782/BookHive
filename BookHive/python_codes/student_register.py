from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
import bcrypt
from db import connect_db

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Registration")
        self.setGeometry(150, 150, 350, 300)
        self.init_ui()

    def init_ui(self):
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

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Student No:"))
        layout.addWidget(self.student_no_input)
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.register_btn)
        self.setLayout(layout)

    def register_student(self):
        name = self.name_input.text().strip()
        student_no = self.student_no_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not (name and student_no and email and password):
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        conn = connect_db()
        cursor = conn.cursor()
        try:
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
        self.close()
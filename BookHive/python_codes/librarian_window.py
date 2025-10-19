from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit, QMessageBox, QHBoxLayout
from db import connect_db

class LibrarianWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Librarian Dashboard")
        self.setGeometry(150, 150, 600, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("📚 Book Management"))

        self.book_id_input = QLineEdit()
        self.book_id_input.setPlaceholderText("Book ID (ISBN)")
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Title")
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Author")
        self.genre_input = QLineEdit()
        self.genre_input.setPlaceholderText("Genre")
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Location")
        self.supplier_input = QLineEdit()
        self.supplier_input.setPlaceholderText("Supplier ID")
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Price")

        layout.addWidget(self.book_id_input)
        layout.addWidget(self.title_input)
        layout.addWidget(self.author_input)
        layout.addWidget(self.genre_input)
        layout.addWidget(self.location_input)
        layout.addWidget(self.supplier_input)
        layout.addWidget(self.price_input)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Book")
        self.update_btn = QPushButton("Update Book")
        self.delete_btn = QPushButton("Delete Book")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by title")
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search_books)
        layout.addWidget(self.search_input)
        layout.addWidget(self.search_btn)

        self.books_display = QLabel()
        self.books_display.setWordWrap(True)
        layout.addWidget(self.books_display)

        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.close)
        layout.addWidget(self.logout_btn)

        self.setLayout(layout)

        self.add_btn.clicked.connect(self.add_book)
        self.update_btn.clicked.connect(self.update_book)
        self.delete_btn.clicked.connect(self.delete_book)

        self.load_books()

    def load_books(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT book_id, title, author, genre, location, supplier_id, price FROM Books")
        books = cursor.fetchall()
        conn.close()
        display = "\n".join([
            f"{b[0]} | {b[1]} by {b[2]} ({b[3]}) @ {b[4]} | Supplier: {b[5]} | ₱{b[6]}"
            for b in books
        ])
        self.books_display.setText(display)

    def search_books(self):
        keyword = self.search_input.text()
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT book_id, title, author, genre, location, supplier_id, price FROM Books WHERE title LIKE %s", (f"%{keyword}%",))
        books = cursor.fetchall()
        conn.close()
        display = "\n".join([
            f"{b[0]} | {b[1]} by {b[2]} ({b[3]}) @ {b[4]} | Supplier: {b[5]} | ₱{b[6]}"
            for b in books
        ])
        self.books_display.setText(display)

    def add_book(self):
        book_id = self.book_id_input.text().strip()
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        genre = self.genre_input.text().strip()
        location = self.location_input.text().strip()
        supplier_id = self.supplier_input.text().strip()
        price = self.price_input.text().strip()

        # strict missing-field validation
        fields = {
            "Book ID": book_id,
            "Title": title,
            "Author": author,
            "Genre": genre,
            "Location": location,
            "Supplier ID": supplier_id,
            "Price": price
        }
        missing = [name for name, val in fields.items() if not val]
        if missing:
            QMessageBox.warning(self, "Missing Data", "Please fill these fields before adding a book:\n- " + "\n- ".join(missing))
            # focus first missing field
            first = missing[0]
            focus_map = {
                "Book ID": self.book_id_input,
                "Title": self.title_input,
                "Author": self.author_input,
                "Genre": self.genre_input,
                "Location": self.location_input,
                "Supplier ID": self.supplier_input,
                "Price": self.price_input
            }
            focus_map.get(first, self.book_id_input).setFocus()
            return

        # validate numeric fields
        try:
            supplier_id_int = int(supplier_id)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Supplier ID must be an integer.")
            self.supplier_input.setFocus()
            return

        try:
            price_val = float(price)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Price must be a number.")
            self.price_input.setFocus()
            return

        conn = connect_db()
        cursor = conn.cursor()
        try:
            # prevent duplicate book_id
            cursor.execute("SELECT 1 FROM Books WHERE book_id = %s", (book_id,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Duplicate", "A book with this Book ID already exists.")
                return

            cursor.execute(
                "INSERT INTO Books (book_id, title, author, genre, location, supplier_id, price) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (book_id, title, author, genre, location, supplier_id_int, price_val)
            )
            conn.commit()
            QMessageBox.information(self, "Success", "Book added successfully.")
            self.load_books()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            conn.close()

    def update_book(self):
        book_id = self.book_id_input.text().strip()
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        genre = self.genre_input.text().strip()
        location = self.location_input.text().strip()
        supplier_id = self.supplier_input.text().strip()
        price = self.price_input.text().strip()

        if not all([book_id, title, author, genre, location, supplier_id, price]):
            QMessageBox.warning(self, "Missing Data", "All fields must be filled before updating a book.")
            return

        try:
            supplier_id = int(supplier_id)
            price = float(price)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Supplier ID must be an integer and price must be a number.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE Books SET title=%s, author=%s, genre=%s, location=%s, supplier_id=%s, price=%s WHERE book_id=%s",
                (title, author, genre, location, supplier_id, price, book_id)
            )
            conn.commit()
            QMessageBox.information(self, "Success", "Book updated successfully.")
            self.load_books()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            conn.close()

    def delete_book(self):
        book_id = self.book_id_input.text().strip()
        if not book_id:
            QMessageBox.warning(self, "Missing Data", "Book ID is required to delete a book.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Books WHERE book_id=%s", (book_id,))
            conn.commit()
            QMessageBox.information(self, "Success", "Book deleted successfully.")
            self.load_books()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            conn.close()
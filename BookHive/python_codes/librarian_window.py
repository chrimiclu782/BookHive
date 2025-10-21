"""
Librarian Dashboard Window

This module provides the librarian interface for managing the library's book collection.
Librarians can add, update, delete books, process returns, and view borrowing history.
"""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit, QMessageBox, QHBoxLayout, QScrollArea, QComboBox, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from db import connect_db
from return_window import ReturnWindow
from app import AuthApp
from librarian_order_window import LibrarianOrderWindow
from supplier_window import SupplierWindow

class LibrarianWindow(QWidget):
    """
    Librarian dashboard for comprehensive book management operations.

    Provides functionality for:
    - Adding new books to the catalog
    - Updating existing book information
    - Deleting lost books from the system
    - Processing book returns and handling fines
    - Searching and viewing book borrowing history
    """

    def __init__(self):
        """Initialize the librarian dashboard window."""
        super().__init__()
        self.setWindowTitle("Librarian Dashboard")
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
        """Set up the user interface components for book management."""
        # Logo at the top center
        self.logo_label = QLabel()
        pixmap = QPixmap("python_codes/assets/BookHive_Logo.png")
        if not pixmap.isNull():
            self.logo_label.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio))
        self.logo_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.logo_label)
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
        self.return_btn = QPushButton("Return Book")
        self.manage_orders_btn = QPushButton("Manage Orders")
        self.suppliers_btn = QPushButton("Suppliers")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.return_btn)
        btn_layout.addWidget(self.manage_orders_btn)
        btn_layout.addWidget(self.suppliers_btn)
        layout.addLayout(btn_layout)

        self.search_label = QLabel("Search Book:")
        self.search_input = QLineEdit()
        self.search_attribute = QComboBox()
        self.search_attribute.addItems(["Book ID", "Title", "Author", "Genre", "Location", "Supplier ID"])
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search_books)
        self.history_btn = QPushButton("View History")
        self.history_btn.clicked.connect(self.view_history)
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_attribute)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.history_btn)
        layout.addLayout(search_layout)

        self.books_display = QLabel()
        self.books_display.setWordWrap(True)
        self.books_scroll = QScrollArea()
        self.books_scroll.setWidget(self.books_display)
        self.books_scroll.setWidgetResizable(True)
        self.books_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.books_scroll.setMinimumHeight(200)
        layout.addWidget(self.books_scroll)

        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.logout)
        layout.addWidget(self.logout_btn)

        self.setLayout(layout)

        self.add_btn.clicked.connect(self.add_book)
        self.update_btn.clicked.connect(self.update_book)
        self.delete_btn.clicked.connect(self.delete_book)
        self.return_btn.clicked.connect(self.open_return_window)
        self.manage_orders_btn.clicked.connect(self.open_manage_orders_window)
        self.suppliers_btn.clicked.connect(self.open_supplier_window)

        self.load_books()

    def load_books(self):
        """
        Load and display all books in the catalog.

        Queries the Books table and displays book information
        in a formatted list for librarian reference.
        """
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT book_id, title, author, genre, location, supplier_id, price FROM Books ORDER BY book_id")
        books = cursor.fetchall()
        conn.close()
        if books:
            table_html = """
            <table border="1" style="border-collapse: collapse; width: 100%; margin: 10px 0; font-family: 'Arial Black';">
                <tr style="background-color: #f0f0f0; height: 35px;">
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Book ID</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Title</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Author</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Genre</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Location</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Supplier</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Price</th>
                </tr>
            """
            for b in books:
                table_html += f"""
                <tr style="background-color: white; height: 35px;">
                    <td style="padding: 8px;">{b[0]}</td>
                    <td style="padding: 8px;">{b[1]}</td>
                    <td style="padding: 8px;">{b[2]}</td>
                    <td style="padding: 8px;">{b[3]}</td>
                    <td style="padding: 8px;">{b[4]}</td>
                    <td style="padding: 8px;">{b[5]}</td>
                    <td style="padding: 8px;">₱{b[6]}</td>
                </tr>
                """
            table_html += "</table>"
            self.books_display.setText(table_html)
        else:
            self.books_display.setText("No books found.")

    def search_books(self):
        """
        Search for books by selected attribute.

        Performs a partial match search based on the selected attribute and displays matching results.
        If no keyword is provided, loads all books.
        """
        keyword = self.search_input.text().strip()
        attribute = self.search_attribute.currentText()
        column_map = {
            "Book ID": "book_id",
            "Title": "title",
            "Author": "author",
            "Genre": "genre",
            "Location": "location",
            "Supplier ID": "supplier_id"
        }
        column = column_map.get(attribute, "title")
        if not keyword:
            self.load_books()
            return
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(f"SELECT book_id, title, author, genre, location, supplier_id, price FROM Books WHERE {column} LIKE %s ORDER BY book_id", (f"%{keyword}%",))
        books = cursor.fetchall()
        conn.close()
        if books:
            table_html = """
            <table border="1" style="border-collapse: collapse; width: 100%; margin: 10px 0; font-family: 'Arial Black';">
                <tr style="background-color: #f0f0f0; height: 35px;">
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Book ID</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Title</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Author</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Genre</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Location</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Supplier</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Price</th>
                </tr>
            """
            for b in books:
                table_html += f"""
                <tr style="background-color: white; height: 35px;">
                    <td style="padding: 8px;">{b[0]}</td>
                    <td style="padding: 8px;">{b[1]}</td>
                    <td style="padding: 8px;">{b[2]}</td>
                    <td style="padding: 8px;">{b[3]}</td>
                    <td style="padding: 8px;">{b[4]}</td>
                    <td style="padding: 8px;">{b[5]}</td>
                    <td style="padding: 8px;">₱{b[6]}</td>
                </tr>
                """
            table_html += "</table>"
            self.books_display.setText(table_html)
        else:
            self.books_display.setText("No books found.")

    def add_book(self):
        """
        Add a new book to the library catalog.

        Validates all required fields, checks for duplicates,
        and inserts the book record into the database.
        """
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
        """
        Update an existing book's information in the catalog.

        Validates all fields and updates the book record
        in the database with new information.
        """
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
        """
        Delete a lost book from the catalog.

        Only allows deletion of books marked as lost to prevent
        accidental removal of active books.
        """
        book_id = self.book_id_input.text().strip()
        if not book_id:
            QMessageBox.warning(self, "Missing Data", "Book ID is required to delete a book.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        try:
            # Check if the book is lost
            cursor.execute("SELECT borrow_status FROM Borrowed WHERE book_id = %s ORDER BY date_borrowed DESC LIMIT 1", (book_id,))
            status_row = cursor.fetchone()
            if not status_row or status_row[0] != 'Lost':
                QMessageBox.warning(self, "Cannot Delete", "Only lost books can be deleted.")
                return

            cursor.execute("DELETE FROM Books WHERE book_id=%s", (book_id,))
            conn.commit()
            QMessageBox.information(self, "Success", "Book deleted successfully.")
            self.load_books()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            conn.close()

    def open_return_window(self):
        """Open the return book window for processing returns and losses."""
        self.return_window = ReturnWindow()
        self.return_window.show()

    def view_history(self):
        """
        View the borrowing history for a specific book.

        Displays all borrow records for the book, including
        return dates and fines if applicable.
        """
        book_id = self.search_input.text().strip()
        if not book_id:
            QMessageBox.warning(self, "Missing Data", "Book ID is required to view history.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM Books WHERE book_id = %s", (book_id,))
        exists = cursor.fetchone()
        if not exists:
            QMessageBox.warning(self, "Book Not Found", "The book does not exist.")
            self.load_books()
            conn.close()
            return

        # Load history
        cursor.execute("""
            SELECT br.student_no, br.date_borrowed, br.date_due, br.borrow_status,
                   r.date_returned, r.fine_amount, r.fine_reason
            FROM Borrowed br
            LEFT JOIN Returned r ON br.borrow_id = r.borrow_id
            WHERE br.book_id = %s
            ORDER BY br.date_borrowed DESC
        """, (book_id,))
        history = cursor.fetchall()
        conn.close()

        if not history:
            display = "No borrow history found for this book."
        else:
            table_html = """
            <table border="1" style="border-collapse: collapse; width: 100%; margin: 10px 0; font-family: 'Arial Black';">
                <tr style="background-color: #f0f0f0; height: 35px;">
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Student</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Borrowed</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Due</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Status</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Returned</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Fine</th>
                    <th style="padding: 8px; font-size: 16px; font-weight: bold; font-family: 'Arial Black';">Reason</th>
                </tr>
            """
            for h in history:
                table_html += f"""
                <tr style="background-color: white; height: 35px;">
                    <td style="padding: 8px;">{h[0]}</td>
                    <td style="padding: 8px;">{h[1]}</td>
                    <td style="padding: 8px;">{h[2]}</td>
                    <td style="padding: 8px;">{h[3]}</td>
                    <td style="padding: 8px;">{h[4] or 'N/A'}</td>
                    <td style="padding: 8px;">₱{h[5] or 0}</td>
                    <td style="padding: 8px;">{h[6] or 'N/A'}</td>
                </tr>
                """
            table_html += "</table>"
            self.books_display.setText(table_html)

    def open_manage_orders_window(self):
        """Open the manage orders window for librarians to handle book orders."""
        self.manage_orders_window = LibrarianOrderWindow()
        self.manage_orders_window.show()

    def open_supplier_window(self):
        """Open the supplier management window."""
        self.supplier_window = SupplierWindow()
        self.supplier_window.show()

    def logout(self):
        """Log out the librarian and return to the authentication screen."""
        self.auth_app = AuthApp()
        self.auth_app.show()
        self.close()

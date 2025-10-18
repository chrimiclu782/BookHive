from datetime import datetime
from config import db, bcrypt

class Librarian(db.Model):
    __tablename__ = 'librarians'
    librarian_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)


class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True)
    student_number = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)


class Book(db.Model):
    __tablename__ = 'books'
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    shelf_location = db.Column(db.String(50), nullable=False)
    total_copies = db.Column(db.Integer, nullable=False)
    available_copies = db.Column(db.Integer, nullable=False)


class Borrowed(db.Model):
    __tablename__ = 'borrowed'
    borrow_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
    borrow_date = db.Column(db.DateTime, default=datetime.now)
    due_date = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime, nullable=True)
    fine = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='borrowed')

    book = db.relationship('Book', backref='borrowed_books')
    student = db.relationship('Student', backref='borrow_history')


class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
    book_title = db.Column(db.String(255), nullable=False)
    book_author = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, available, received
    order_date = db.Column(db.DateTime, default=datetime.now)

    student = db.relationship('Student', backref='orders')


class Payment(db.Model):
    __tablename__ = 'payments'
    payment_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=True)
    borrow_id = db.Column(db.Integer, db.ForeignKey('borrowed.borrow_id'), nullable=True)
    amount = db.Column(db.Integer, nullable=False)
    paid_date = db.Column(db.DateTime, nullable=True)
    type = db.Column(db.String(20))  # 'fine' or 'purchase'

    student = db.relationship('Student', backref='payments')
    order = db.relationship('Order', backref='payment')
    borrow = db.relationship('Borrowed', backref='payment')

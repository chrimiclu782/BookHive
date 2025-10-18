from flask import render_template, request, redirect, url_for, flash, session
from functools import wraps
from datetime import datetime, timedelta
from config import app, db
from models import Student, Librarian, Book, Borrowed, Order, Payment

# ------------------------ Helper ------------------------
def login_required(role=None):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session:
                flash("Please log in first.")
                return redirect(url_for('home'))
            if role and session['role'] != role:
                flash("Access denied.")
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper

# ------------------------ Home / Login / Logout ------------------------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student_number = request.form['student_number']
        name = request.form['name']
        password = request.form['password']

        if Student.query.filter_by(student_number=student_number).first():
            flash("Student number already exists.")
            return redirect(url_for('register'))

        student = Student(student_number=student_number, name=name)
        student.set_password(password)

        db.session.add(student)
        db.session.commit()
        flash("Registration successful. You can now log in.")
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    user_type = request.form['user_type']
    username = request.form['username']
    password = request.form['password']

    user = None
    if user_type == 'student':
        user = Student.query.filter_by(student_number=username).first()
    else:
        user = Librarian.query.filter_by(username=username).first()

    if user and user.check_password(password):
        session['user_id'] = user.student_id if user_type == 'student' else user.librarian_id
        session['role'] = user_type
        flash("Login successful.")
        return redirect(url_for('student_dashboard' if user_type=='student' else 'librarian_dashboard'))
    else:
        flash("Invalid credentials.")
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for('home'))

# ------------------------ Student ------------------------
@app.route('/student_dashboard')
@login_required('student')
def student_dashboard():
    books = Book.query.all()
    borrowed = Borrowed.query.filter_by(student_id=session['user_id']).all()
    payments = Payment.query.filter_by(student_id=session['user_id'], paid_date=None).all()
    orders = Order.query.filter_by(student_id=session['user_id']).all()
    return render_template('student_dashboard.html', books=books, borrowed=borrowed, payments=payments, orders=orders)

@app.route('/borrow/<int:book_id>')
@login_required('student')
def borrow(book_id):
    book = Book.query.get(book_id)
    if not book or book.available_copies <= 0:
        flash("Book not available.")
        return redirect(url_for('student_dashboard'))

    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=7)
    borrowed = Borrowed(book_id=book_id, student_id=session['user_id'], borrow_date=borrow_date, due_date=due_date)
    book.available_copies -= 1
    db.session.add(borrowed)
    db.session.commit()
    flash("Book borrowed successfully.")
    return redirect(url_for('student_dashboard'))

@app.route('/order_book', methods=['GET', 'POST'])
@login_required('student')
def order_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        order = Order(student_id=session['user_id'], book_title=title, book_author=author)
        db.session.add(order)
        db.session.commit()
        flash("Book order submitted.")
        return redirect(url_for('student_dashboard'))
    return render_template('order_book.html')

@app.route('/pay/<int:payment_id>')
@login_required('student')
def pay(payment_id):
    payment = Payment.query.get(payment_id)
    if payment:
        payment.paid_date = datetime.now()
        db.session.commit()
        flash(f"Payment of ₱{payment.amount} successful.")
    return redirect(url_for('student_dashboard'))

# ------------------------ Librarian ------------------------
@app.route('/librarian_dashboard')
@login_required('librarian')
def librarian_dashboard():
    books = Book.query.all()
    borrowed_books = Borrowed.query.all()
    orders = Order.query.all()
    return render_template('librarian_dashboard.html', books=books, borrowed_books=borrowed_books, orders=orders)

@app.route('/add_book', methods=['POST'])
@login_required('librarian')
def add_book():
    title = request.form['title']
    author = request.form['author']
    shelf = request.form['shelf']
    total = int(request.form['total'])
    book = Book(title=title, author=author, shelf_location=shelf, total_copies=total, available_copies=total)
    db.session.add(book)
    db.session.commit()
    flash("Book added successfully.")
    return redirect(url_for('librarian_dashboard'))

@app.route('/return/<int:borrow_id>')
@login_required('librarian')
def return_book(borrow_id):
    borrow = Borrowed.query.get(borrow_id)
    if not borrow:
        flash("Borrow record not found.")
        return redirect(url_for('librarian_dashboard'))

    borrow.return_date = datetime.now()
    borrow.status = 'returned'
    days_late = (borrow.return_date.date() - borrow.due_date.date()).days
    fine = min(max(days_late * 10, 0), 100)
    borrow.fine = fine
    borrow.book.available_copies += 1

    if fine > 0:
        payment = Payment(student_id=borrow.student_id, borrow_id=borrow.borrow_id, amount=fine, type='fine')
        db.session.add(payment)

    db.session.commit()
    flash(f"Book returned. Fine: ₱{fine}")
    return redirect(url_for('librarian_dashboard'))

# ------------------------ Orders ------------------------
@app.route('/orders')
@login_required('librarian')
def orders():
    orders = Order.query.all()
    return render_template('orders.html', orders=orders)

@app.route('/order/<int:order_id>/mark/<string:status>')
@login_required('librarian')
def mark_order(order_id, status):
    order = Order.query.get(order_id)
    if order and status in ['available', 'received']:
        order.status = status
        db.session.commit()
        flash(f"Order marked as {status}.")
    return redirect(url_for('orders'))

# ------------------------ Run App ------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

DROP DATABASE IF EXISTS BookHiveDB;
CREATE DATABASE BookHiveDB;
USE BookHiveDB;

CREATE TABLE Suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    supplier_contact VARCHAR(50),
    supplier_location VARCHAR(150)
);

CREATE TABLE Books (
    book_id VARCHAR(30) PRIMARY KEY,  -- ISBN used as book_id
    title VARCHAR(150) NOT NULL,
    author VARCHAR(100),
    genre VARCHAR(50),
    location VARCHAR(50),
    supplier_id INT,
    price DECIMAL(10,2),
    FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id)
);

CREATE TABLE Students (
    student_no VARCHAR(20) PRIMARY KEY,
    st_name VARCHAR(100) NOT NULL,
    st_email VARCHAR(100) UNIQUE,
    st_password VARCHAR(255) NOT NULL
);

CREATE TABLE Librarians (
    librarian_id VARCHAR(20) PRIMARY KEY,
    lib_name VARCHAR(100) NOT NULL,
    lib_email VARCHAR(100) UNIQUE,
    lib_password VARCHAR(255) NOT NULL
);

CREATE TABLE BookOrders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    student_no VARCHAR(20),
    supplier_id INT,
    title VARCHAR(150) NOT NULL,
    order_status VARCHAR(50) DEFAULT 'Pending',
    payment_status VARCHAR(50) DEFAULT 'Unpaid',
    total_amount DECIMAL(10,2),
    date_ordered DATE,
    FOREIGN KEY (student_no) REFERENCES Students(student_no),
    FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id)
);

CREATE TABLE Borrowed (
    borrow_id INT AUTO_INCREMENT PRIMARY KEY,
    student_no VARCHAR(20),
    book_id VARCHAR(30),
    date_borrowed DATE NOT NULL,
    date_due DATE,
    borrow_status VARCHAR(50) DEFAULT 'Borrowed',
    FOREIGN KEY (student_no) REFERENCES Students(student_no),
    FOREIGN KEY (book_id) REFERENCES Books(book_id)
);

CREATE TABLE Returned (
    return_id INT AUTO_INCREMENT PRIMARY KEY,
    borrow_id INT,
    book_id VARCHAR(30),
    date_returned DATE NOT NULL,
    fine_amount DECIMAL(10 , 2 ) DEFAULT 0.00,
    fine_reason VARCHAR(255),
    FOREIGN KEY (borrow_id) REFERENCES Borrowed(borrow_id),
    FOREIGN KEY (book_id) REFERENCES Books(book_id)
);
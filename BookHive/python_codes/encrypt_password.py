"""
Password Encryption Module

This module handles the encryption of plain text passwords in the database
using bcrypt hashing for secure storage. It processes both student and librarian passwords.
"""

import bcrypt
from db import connect_db

def encrypt_students(cursor):
    """
    Encrypt plain text student passwords in the database.

    Retrieves all student passwords, checks if they are already hashed,
    and updates plain text passwords with bcrypt hashes.
    """
    cursor.execute("SELECT student_no, st_password FROM Students")
    students = cursor.fetchall()

    for student_no, plain_pw in students:
        # Skip if already encrypted (bcrypt hashes start with $2a$ or $2b$)
        if plain_pw.startswith("$2b$") or plain_pw.startswith("$2a$"):
            continue  # Already encrypted

        # Hash the plain text password using bcrypt
        hashed_pw = bcrypt.hashpw(plain_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "UPDATE Students SET st_password = %s WHERE student_no = %s",
            (hashed_pw, student_no)
        )
    print("✅ Student passwords encrypted.")

def encrypt_librarians(cursor):
    """
    Encrypt plain text librarian passwords in the database.

    Retrieves all librarian passwords, checks if they are already hashed,
    and updates plain text passwords with bcrypt hashes.
    """
    cursor.execute("SELECT librarian_id, lib_password FROM Librarians")
    librarians = cursor.fetchall()

    for librarian_id, plain_pw in librarians:
        # Skip if already encrypted (bcrypt hashes start with $2a$ or $2b$)
        if plain_pw.startswith("$2b$") or plain_pw.startswith("$2a$"):
            continue  # Already encrypted

        # Hash the plain text password using bcrypt
        hashed_pw = bcrypt.hashpw(plain_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "UPDATE Librarians SET lib_password = %s WHERE librarian_id = %s",
            (hashed_pw, librarian_id)
        )
    print("✅ Librarian passwords encrypted.")

def main():
    """
    Main function to encrypt all passwords in the database.

    Establishes database connection, encrypts student and librarian passwords,
    commits changes, and closes the connection.
    """
    conn = connect_db()
    cursor = conn.cursor()

    encrypt_students(cursor)
    encrypt_librarians(cursor)

    conn.commit()
    conn.close()
    print("🎉 All passwords encrypted successfully.")

if __name__ == "__main__":
    main()

import mysql.connector
import bcrypt

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="BookHiveDB"
    )

def encrypt_students(cursor):
    cursor.execute("SELECT student_no, st_password FROM Students")
    students = cursor.fetchall()

    for student_no, plain_pw in students:
        if plain_pw.startswith("$2b$") or plain_pw.startswith("$2a$"):
            continue  # Already encrypted

        hashed_pw = bcrypt.hashpw(plain_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "UPDATE Students SET st_password = %s WHERE student_no = %s",
            (hashed_pw, student_no)
        )
    print("✅ Student passwords encrypted.")

def encrypt_librarians(cursor):
    cursor.execute("SELECT librarian_id, lib_password FROM Librarians")
    librarians = cursor.fetchall()

    for librarian_id, plain_pw in librarians:
        if plain_pw.startswith("$2b$") or plain_pw.startswith("$2a$"):
            continue  # Already encrypted

        hashed_pw = bcrypt.hashpw(plain_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "UPDATE Librarians SET lib_password = %s WHERE librarian_id = %s",
            (hashed_pw, librarian_id)
        )
    print("✅ Librarian passwords encrypted.")

def main():
    conn = connect_db()
    cursor = conn.cursor()

    encrypt_students(cursor)
    encrypt_librarians(cursor)

    conn.commit()
    conn.close()
    print("🎉 All passwords encrypted successfully.")

if __name__ == "__main__":
    main()
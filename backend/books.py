from database import get_connection
from mysql.connector import Error

def get_all_books(search=None):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        if search:
            query = """
                SELECT * FROM books 
                WHERE title LIKE %s OR author LIKE %s OR isbn LIKE %s OR category LIKE %s
                ORDER BY book_id
            """
            s = f"%{search}%"
            cursor.execute(query, (s, s, s, s))
        else:
            query = "SELECT * FROM books ORDER BY book_id"
            cursor.execute(query)
        books = cursor.fetchall()
        cursor.close()
        conn.close()
        return books, None
    except Error as e:
        return None, str(e)

def get_book_by_id(book_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
        book = cursor.fetchone()
        cursor.close()
        conn.close()
        return book, None
    except Error as e:
        return None, str(e)

def add_book(title, author, isbn, category, total_copies):
    try:
        available_copies = int(total_copies)
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO books (title, author, isbn, category, total_copies, available_copies)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (title, author, isbn, category, total_copies, available_copies))
        conn.commit()
        book_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return book_id, None
    except Error as e:
        return None, str(e)

def update_book(book_id, title, author, isbn, category, total_copies):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT available_copies FROM books WHERE book_id = %s", (book_id,))
        book = cursor.fetchone()
        if not book:
            cursor.close()
            conn.close()
            return False, "Book not found"
        available_copies = book['available_copies']
        if int(total_copies) < int(available_copies):
            cursor.close()
            conn.close()
            return False, "Total copies cannot be less than available copies"
        query = """
            UPDATE books SET title=%s, author=%s, isbn=%s, category=%s, total_copies=%s
            WHERE book_id=%s
        """
        cursor.execute(query, (title, author, isbn, category, total_copies, book_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True, None
    except Error as e:
        return False, str(e)

def delete_book(book_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as active FROM loans WHERE book_id=%s AND return_date IS NULL", (book_id,))
        result = cursor.fetchone()
        if result and result['active'] > 0:
            cursor.close()
            conn.close()
            return False, "Cannot delete book with active loans"
        cursor.execute("DELETE FROM books WHERE book_id=%s", (book_id,))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        return affected > 0, None
    except Error as e:
        return False, str(e)

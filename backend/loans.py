from database import get_connection
from mysql.connector import Error, IntegrityError

def issue_book(book_id, member_id, issue_date, due_date):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        conn.start_transaction()
        cursor.execute("SELECT * FROM members WHERE member_id=%s", (member_id,))
        member = cursor.fetchone()
        if not member:
            conn.rollback()
            cursor.close()
            conn.close()
            return False, "Member not found"
        cursor.execute("SELECT * FROM books WHERE book_id=%s", (book_id,))
        book = cursor.fetchone()
        if not book:
            conn.rollback()
            cursor.close()
            conn.close()
            return False, "Book not found"
        if book['available_copies'] <= 0:
            conn.rollback()
            cursor.close()
            conn.close()
            return False, "No available copies"
        cursor.execute("INSERT INTO loans (book_id, member_id, issue_date, due_date, return_date) VALUES (%s, %s, %s, %s, NULL)",
                       (book_id, member_id, issue_date, due_date))
        cursor.execute("UPDATE books SET available_copies = available_copies - 1 WHERE book_id=%s", (book_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True, None
    except Error as e:
        try:
            conn.rollback()
        except:
            pass
        return False, str(e)

def return_book(loan_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        conn.start_transaction()
        cursor.execute("SELECT * FROM loans WHERE loan_id=%s", (loan_id,))
        loan = cursor.fetchone()
        if not loan:
            conn.rollback()
            cursor.close()
            conn.close()
            return False, "Loan not found"
        if loan['return_date'] is not None:
            conn.rollback()
            cursor.close()
            conn.close()
            return False, "Book already returned"
        from datetime import date
        cursor.execute("UPDATE loans SET return_date=%s WHERE loan_id=%s", (date.today(), loan_id))
        cursor.execute("UPDATE books SET available_copies = available_copies + 1 WHERE book_id=%s", (loan['book_id'],))
        conn.commit()
        cursor.close()
        conn.close()
        return True, None
    except Error as e:
        try:
            conn.rollback()
        except:
            pass
        return False, str(e)

def get_all_loans():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT l.*, b.title, b.author, b.isbn, m.name, m.email
            FROM loans l
            JOIN books b ON l.book_id = b.book_id
            JOIN members m ON l.member_id = m.member_id
            ORDER BY l.loan_id DESC
        """
        cursor.execute(query)
        loans = cursor.fetchall()
        cursor.close()
        conn.close()
        return loans, None
    except Error as e:
        return None, str(e)

def get_overdue_loans():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT l.*, b.title, b.author, b.isbn, m.name, m.email
            FROM loans l
            JOIN books b ON l.book_id = b.book_id
            JOIN members m ON l.member_id = m.member_id
            WHERE l.return_date IS NULL AND l.due_date < CURDATE()
            ORDER BY l.due_date ASC
        """
        cursor.execute(query)
        loans = cursor.fetchall()
        cursor.close()
        conn.close()
        return loans, None
    except Error as e:
        return None, str(e)

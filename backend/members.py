from database import get_connection
from mysql.connector import Error

def get_all_members(search=None):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        if search:
            query = """
                SELECT * FROM members 
                WHERE member_id LIKE %s OR name LIKE %s OR email LIKE %s OR phone LIKE %s
                ORDER BY member_id
            """
            s = f"%{search}%"
            cursor.execute(query, (s, s, s, s))
        else:
            query = "SELECT * FROM members ORDER BY member_id"
            cursor.execute(query)
        members = cursor.fetchall()
        cursor.close()
        conn.close()
        return members, None
    except Error as e:
        return None, str(e)

def add_member(name, email, phone, join_date):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "INSERT INTO members (name, email, phone, join_date) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, email, phone, join_date))
        conn.commit()
        member_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return member_id, None
    except Error as e:
        return None, str(e)

def update_member(member_id, name, email, phone, join_date):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "UPDATE members SET name=%s, email=%s, phone=%s, join_date=%s WHERE member_id=%s"
        cursor.execute(query, (name, email, phone, join_date, member_id))
        conn.commit()
        cursor.close()
        conn.close()
        return cursor.rowcount > 0 if False else True  # simple
    except Error as e:
        return False, str(e)

def delete_member(member_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as active FROM loans WHERE member_id=%s AND return_date IS NULL", (member_id,))
        result = cursor.fetchone()
        if result and result['active'] > 0:
            cursor.close()
            conn.close()
            return False, "Cannot delete member with active loans"
        cursor.execute("DELETE FROM members WHERE member_id=%s", (member_id,))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        return affected > 0, None
    except Error as e:
        return False, str(e)

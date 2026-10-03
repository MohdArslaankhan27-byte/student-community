import re
from flask import redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from Database.db import get_cursor,db
from functools import wraps


# Email validation
def is_valid_email(email):

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    return re.match(pattern, email) is not None


# Check whether email already exists
def email_exists(email):

    cursor = get_cursor()

    cursor.execute(
        "SELECT id FROM users WHERE email = %s",
        (email,)
    )

    user = cursor.fetchone()

    cursor.close()

    return user is not None


# Hash password
def hash_password(password):

    return generate_password_hash(password)


# Check password
def check_password(password, hashed_password):

    return check_password_hash(hashed_password, password)


# =========================================================
# Get User By email
# =========================================================

def get_user_by_email(email):
    cursor = get_cursor()

    cursor.execute(
        """
        SELECT id, name, email, password
        FROM users
        WHERE email = %s
        """,
        (email,)
    )

    user = cursor.fetchone()
    cursor.close()

    return user



def get_user_by_id(user_id):

    cursor = get_cursor()

    sql = """
        SELECT *
        FROM users
        WHERE id = %s
    """

    cursor.execute(sql, (user_id,))

    user = cursor.fetchone()

    cursor.close()

    return user


def get_peers(user_id, query='', course='', semester=''):

    cursor = get_cursor()

    sql = """
        SELECT *
        FROM users
        WHERE id != %s
    """

    params = [user_id]

    # Search by name
    if query:
        sql += " AND name LIKE %s"
        params.append(f"%{query}%")

    # Course filter
    if course:
        sql += " AND course = %s"
        params.append(course)

    # Semester filter
    if semester:
        sql += " AND semester = %s"
        params.append(semester)

    # Random results when nothing is searched or filtered
    if not query and not course and not semester:
        sql += " ORDER BY RAND()"
    else:
        sql += " ORDER BY name ASC"

    cursor.execute(sql, params)

    peers = cursor.fetchall()

    cursor.close()

    return peers



def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if 'user_id' not in session:
            return redirect(url_for('login'))

        return f(*args, **kwargs)

    return decorated_function



def admin_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):

            user_id = session.get('user_id')
            user = get_user_by_id(user_id)

            if not user or user['role'] not in roles:
                flash('Access denied.', 'danger')
                return redirect(url_for('home'))

            return f(*args, **kwargs)

        return wrapper
    return decorator


def delete_old_messages():
    cursor = get_cursor()

    cursor.execute("""
        DELETE FROM messages
        WHERE created_at < NOW() - INTERVAL 7 DAY
    """)

    db.commit()
    cursor.close()
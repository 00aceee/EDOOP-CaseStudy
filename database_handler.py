# database_handler.py

import mysql.connector 
import hashlib # Used for a placeholder password hashing function
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

# --- Helper Function for DB Connection ---
def get_db_connection():
    """Returns a MySQL database connection object."""
    try:
        # NOTE: If your connection fails, ensure your MySQL server (XAMPP/WAMP/etc.) is running.
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        # In a real app, you might raise an exception or log the error instead of returning None
        return None

# --- New Function to Get User ID (Needed for Appointments) ---
def get_user_id(username):
    """Fetches the user's ID for linking appointments."""
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(dictionary=True) 
    
    query = "SELECT id FROM tbl_users WHERE username = %s" 
    
    try:
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        return user['id'] if user else None
    except Exception as e:
        print(f"Database error while fetching user ID: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


# --- Updated Function to Get User Details ---
def get_user_details(username):
    """Fetches full user record for a given username."""
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(dictionary=True) 
    
    # NOTE: Assuming your user table is 'tbl_users' and password column is 'hash_pass'
    query = "SELECT id, fullname, username, email, hash_pass FROM tbl_users WHERE username = %s" 
    
    try:
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        return user if user else None
    except Exception as e:
        print(f"Database error while fetching user details: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# --- New Function to Get User Appointments ---
def get_user_appointments(user_id):
    import mysql.connector
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="marmudb"
    )
    cursor = conn.cursor(dictionary=True)

    # ✅ This query fetches ALL appointments for the user (Approved, Pending, Denied, etc.)
    query = """
        SELECT id, service, appointment_date, time, status
        FROM tbl_appointment
        WHERE user_id = %s
        ORDER BY appointment_date ASC, time ASC
    """
    cursor.execute(query, (user_id,))
    appointments = cursor.fetchall()

    cursor.close()
    conn.close()
    return appointments

# --- Updated Function to Update Password ---
def update_password(username, new_password):
    """Hashes the new password and updates the user record."""
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    
    hashed_password = hashlib.sha256(new_password.encode()).hexdigest() 

    query = "UPDATE tbl_users SET hash_pass = %s WHERE username = %s"
    
    try:
        cursor.execute(query, (hashed_password, username))
        conn.commit()
        return True
    except Exception as e:
        print(f"Database error during password update: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "online_exam_db")
DB_PORT = int(os.getenv("DB_PORT", 3306))

pool = None

def get_pool():
    global pool
    if pool is None:
        try:
            pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="exam_pool",
                pool_size=5,
                pool_reset_session=True,
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                port=DB_PORT,
                autocommit=True
            )
        except mysql.connector.Error as err:
            print(f"Error creating connection pool: {err}")
            raise err
    return pool

def get_db_connection():
    """Acquires a database connection from pool or creates a direct connection."""
    try:
        p = get_pool()
        return p.get_connection()
    except Exception as e:
        # Fallback to direct connection if pool fails or DB not created yet
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            autocommit=True
        )

def execute_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    """
    Executes parameterized SQL queries safely.
    Prevents SQL injection vulnerabilities.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        if commit:
            conn.commit()
            last_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return last_id

        if fetchone:
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result

        if fetchall:
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result

        cursor.close()
        conn.close()
        return None
    except Exception as err:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print(f"Database Query Error: {err} | Query: {query}")
        raise err
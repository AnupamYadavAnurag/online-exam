import os
import mysql.connector
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "online_exam_db")
DB_PORT = int(os.getenv("DB_PORT", 3306))

def init_database():
    """Initializes and seeds the MySQL database."""
    print("Connecting to MySQL server...")
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cursor = conn.cursor()
        
        print(f"Creating database {DB_NAME} if not exists...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cursor.execute(f"USE {DB_NAME};")

        # Read schema.sql
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        schema_path = os.path.join(base_dir, "schema.sql")
        
        print(f"Executing schema from {schema_path}...")
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        for statement in schema_sql.split(";"):
            stmt = statement.strip()
            if stmt and not stmt.lower().startswith("create database") and not stmt.lower().startswith("use"):
                cursor.execute(stmt)

        # Generate fresh Werkzeug password hashes for seed users
        admin_pass = generate_password_hash("Admin@123")
        subadmin_pass = generate_password_hash("Admin@456")
        student_pass = generate_password_hash("Student@123")

        # Read seed.sql and insert statements
        seed_path = os.path.join(base_dir, "seed.sql")
        print(f"Executing seed data from {seed_path}...")
        with open(seed_path, "r", encoding="utf-8") as f:
            seed_sql = f.read()

        for statement in seed_sql.split(";"):
            stmt = statement.strip()
            if stmt and not stmt.lower().startswith("use"):
                cursor.execute(stmt)

        # Update default user passwords to exact local hashes
        cursor.execute("UPDATE users SET password = %s WHERE role = 'admin' AND username = 'admin'", (admin_pass,))
        cursor.execute("UPDATE users SET password = %s WHERE role = 'admin' AND username = 'subadmin'", (subadmin_pass,))
        cursor.execute("UPDATE users SET password = %s WHERE role = 'student'", (student_pass,))

        conn.commit()
        cursor.close()
        conn.close()
        print("[OK] Database successfully initialized and seeded!")
        return True
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    init_database()

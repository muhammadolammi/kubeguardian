# db_helper.py
import psycopg2
from psycopg2 import sql
from cryptography.fernet import Fernet

class AuthDBHelper:
    def __init__(self, db_url: str, crypt_key: bytes):
        self.db_url = db_url
        self.conn = psycopg2.connect(db_url)
        self.fernet = Fernet(crypt_key)
        self.init_db()

    def init_db(self):
        """Create users table if it doesn't exist."""
        with self.conn.cursor() as cur:
            # Enable the extension 
            cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
            cur.execute("""

                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_name TEXT,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            self.conn.commit()

    # --- CRUD Operations ---
    def create_user(self, user_name, email, password):
        enc_password = self.fernet.encrypt(password.encode()).decode()
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (user_name, email, password)
                VALUES ( %s, %s, %s)
                RETURNING id
            """, (user_name, email, enc_password))
            user_id = cur.fetchone()[0]
            self.conn.commit()
            return user_id

    def get_user_by_email(self, email):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, user_name, email, password FROM users WHERE email = %s", (email,))
            row = cur.fetchone()
            if row:
                return {
                    "id": row[0],
                    "user_name": row[1],
                    "email": row[2],
                    "password": row[3],
                }
            return None

    def get_user_by_id(self, user_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, user_name, email, password FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            if row:
                return {
                    "id": row[0],
                    "user_name": row[1],
                    "email": row[2],
                    "password": row[3],
                }
            return None

    def delete_user(self, user_id):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
            self.conn.commit()

    # --- Verify password ---
    def verify_password(self, email, password):
        user = self.get_user_by_email(email)
        if not user:
            return None
        decrypted = self.fernet.decrypt(user["password"].encode()).decode()
        return decrypted == password

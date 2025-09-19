
import psycopg2
from psycopg2 import sql
from cryptography.fernet import Fernet
from typing import List, Dict, Any
class AlertDB:
    def __init__(self, db_url: str, crypt_key: bytes):
        self.db_url = db_url
        self.conn = psycopg2.connect(db_url)
        self.fernet = Fernet(crypt_key)
        self.init_db()

    def init_db(self):
        """Create the alerts table if it doesn't exist."""
        with self.conn.cursor() as cur:
            # Enable the UUID extension
            cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
            cur.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    description TEXT NOT NULL,
                    body TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    session_id TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    time_stamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP  -- fixed creation time
                );
            """)
            self.conn.commit()

    # --- CRUD Operations ---
    def create_alert(self, description: str, body: str, session_id: str, severity: str):
        """
        Creates a new alert and ensures the total count doesn't exceed 100.
        """
        self._enforce_limit()

        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO alerts (description, body, session_id, severity)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """, (description, body, session_id, severity))
            alert_id = cur.fetchone()[0]
            self.conn.commit()
            return str(alert_id)

    def update_alert(self, body: str, session_id: str, severity: str) -> str:
        """
        Updates an alert if the session_id exists, otherwise creates a new one.
        """
        description = " ".join(body.split()[:15])

        with self.conn.cursor() as cur:
            cur.execute("SELECT id FROM alerts WHERE session_id = %s;", (session_id,))
            existing_alert = cur.fetchone()

            if existing_alert:
                cur.execute("""
                    UPDATE alerts
                    SET description = %s,
                        body = %s,
                        severity = %s,
                        created_at = CURRENT_TIMESTAMP
                    WHERE session_id = %s
                    RETURNING id;
                """, (description, body, severity, session_id))
                updated_id = cur.fetchone()[0]
                self.conn.commit()
                return str(updated_id)
            else:
                return self.create_alert(description, body, session_id, severity)

    def _enforce_limit(self, limit: int = 100):
        """
        Deletes the oldest alerts to enforce the specified limit.
        """
        with self.conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM alerts;")
            count = cur.fetchone()[0]

            if count >= limit:
                num_to_delete = count - limit + 1
                cur.execute(sql.SQL("""
                    DELETE FROM alerts
                    WHERE id IN (
                        SELECT id FROM alerts
                        ORDER BY created_at ASC
                        LIMIT %s
                    );
                """), (num_to_delete,))
                self.conn.commit()
                print(f"Removed {num_to_delete} oldest alerts to enforce limit.")

    def get_all_alerts(self) -> List[Dict[str, Any]]:
        """
        Retrieves all alerts from the database, sorted by creation date.
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, description, body, session_id, severity, created_at, time_stamp
                FROM alerts
                ORDER BY created_at DESC;
            """)
            alerts = []
            for row in cur.fetchall():
                alerts.append({
                    "id": str(row[0]),
                    "description": row[1],
                    "body": row[2],
                    "session_id": row[3],
                    "severity": row[4],
                    "created_at": row[5].isoformat(),
                    "time_stamp": row[6].isoformat()
                })
            return alerts

    def get_alert_by_id(self, alert_id: str) -> Dict[str, Any] | None:
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, description, body, session_id, severity, created_at, time_stamp
                FROM alerts
                WHERE id = %s;
            """, (alert_id,))
            row = cur.fetchone()
            if row:
                return {
                    "id": str(row[0]),
                    "description": row[1],
                    "body": row[2],
                    "session_id": row[3],
                    "severity": row[4],
                    "created_at": row[5].isoformat(),
                    "time_stamp": row[6].isoformat()
                }
            return None

    def delete_alert(self, alert_id: str):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM alerts WHERE id = %s;", (alert_id,))
            self.conn.commit()


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

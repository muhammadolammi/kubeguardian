# db_helper.py
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
                    session_id TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            self.conn.commit()

    # --- CRUD Operations ---
    def create_alert(self, description: str, body: str, session_id: str):
        """
        Creates a new alert and ensures the total count doesn't exceed 100.
        
        Args:
            description (str): A brief description of the alert.
            body (str): The full alert body.
            session_id (str): The unique session identifier.

        Returns:
            str: The ID of the newly created alert.
        """
        # First, delete the oldest alerts if the count is over the limit.
        self._enforce_limit()

        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO alerts (description, body, session_id)
                VALUES (%s, %s, %s)
                RETURNING id;
            """, (description, body, session_id))
            alert_id = cur.fetchone()[0]
            self.conn.commit()
            return str(alert_id)
    
    def update_alert(self, body: str, session_id: str) -> str:
        """
        Updates an alert if the session_id exists, otherwise creates a new one.
        
        Args:
            body (str): The new alert body.
            session_id (str): The unique session identifier.

        Returns:
            str: The ID of the updated or newly created alert.
        """
        description = " ".join(body.split()[:15])

        with self.conn.cursor() as cur:
            # Check if the session_id already exists
            cur.execute("SELECT id FROM alerts WHERE session_id = %s;", (session_id,))
            existing_alert = cur.fetchone()

            if existing_alert:
                # Update the existing alert
                alert_id = existing_alert[0]
                cur.execute("""
                    UPDATE alerts
                    SET description = %s, body = %s, created_at = CURRENT_TIMESTAMP
                    WHERE session_id = %s
                    RETURNING id;
                """, (description, body, session_id))
                updated_id = cur.fetchone()[0]
                self.conn.commit()
                return str(updated_id)
            else:
                # Create a new alert since it doesn't exist
                return self.create_alert(description, body, session_id)

    def _enforce_limit(self, limit: int = 100):
        """
        Deletes the oldest alerts to enforce the specified limit.
        This is a private helper method.
        """
        with self.conn.cursor() as cur:
            # Get the total count of alerts
            cur.execute("SELECT count(*) FROM alerts;")
            count = cur.fetchone()[0]
            
            if count >= limit:
                # Find and delete the oldest alerts
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
        
        Returns:
            A list of dictionaries, where each dictionary represents an alert.
        """
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, description, body, session_id, created_at FROM alerts ORDER BY created_at DESC;")
            alerts = []
            for row in cur.fetchall():
                alerts.append({
                    "id": str(row[0]),
                    "description": row[1],
                    "body": row[2],
                    "session_id": row[3],
                    "created_at": row[4].isoformat()
                })
            return alerts

    def get_alert_by_id(self, alert_id: str) -> Dict[str, Any] | None:
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, description, body, session_id, created_at FROM alerts WHERE id = %s;", (alert_id,))
            row = cur.fetchone()
            if row:
                return {
                    "id": str(row[0]),
                    "description": row[1],
                    "body": row[2],
                    "session_id": row[3],
                    "created_at": row[4].isoformat()
                }
            return None

    def delete_alert(self, alert_id: str):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM alerts WHERE id = %s;", (alert_id,))
            self.conn.commit()
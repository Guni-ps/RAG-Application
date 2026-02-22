import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

class ChatHistoryManager:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            print("Warning: DATABASE_URL not found in environment variables.")
        else:
            self._init_db()

    def _get_connection(self):
        try:
            if self.db_url:
                return psycopg2.connect(self.db_url)
        except Exception as e:
            print(f"Database connection failed: {e}")
        return None

    def _init_db(self):
        """Initialize the chat history table if it doesn't exist."""
        conn = self._get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS chat_history (
                        id SERIAL PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
                cur.close()
                conn.close()
            except Exception as e:
                print(f"Error initializing database: {e}")

    def add_message(self, session_id, role, content):
        """Add a message to the database."""
        conn = self._get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO chat_history (session_id, role, content) VALUES (%s, %s, %s)",
                    (session_id, role, content)
                )
                conn.commit()
                cur.close()
                conn.close()
            except Exception as e:
                print(f"Error adding message: {e}")

    def get_history(self, session_id):
        """Retrieve chat history for a specific session."""
        messages = []
        conn = self._get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT role, content FROM chat_history WHERE session_id = %s ORDER BY timestamp ASC",
                    (session_id,)
                )
                rows = cur.fetchall()
                for row in rows:
                    messages.append({"role": row[0], "content": row[1]})
                cur.close()
                conn.close()
            except Exception as e:
                print(f"Error retrieving history: {e}")
        return messages

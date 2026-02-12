import sqlite3
import os
import psycopg2
from datetime import datetime
from urllib.parse import urlparse

class DatabaseManager:
    def __init__(self):
        # 1. Detect Environment (Cloud vs Local)
        self.db_url = os.getenv("DATABASE_URL")
        self.is_postgres = bool(self.db_url)

        # 2. Set SQL Dialect (The Translator)
        if self.is_postgres:
            print("🚀 [DATABASE] Detected Cloud Mode (PostgreSQL)")
            self.placeholder = "%s"
            self.id_type = "SERIAL PRIMARY KEY"
        else:
            print("🏠 [DATABASE] Detected Local Mode (SQLite)")
            self.db_name = "protocol_zero.db"
            self.placeholder = "?"
            self.id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"

        self.initialize_db()

    def get_connection(self):
        """Establishes a connection to either Neon (Cloud) or SQLite (Local)."""
        if self.is_postgres:
            # Connect to Neon
            return psycopg2.connect(self.db_url, sslmode='require')
        else:
            # Connect to Local File
            return sqlite3.connect(self.db_name)

    def initialize_db(self):
        """Creates the table if it doesn't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # SQL SPELL: Create the Log Table (Adaptive)
        # We use 'self.id_type' to handle the difference between DBs
        create_query = f'''
            CREATE TABLE IF NOT EXISTS interactions (
                id {self.id_type},
                user_name TEXT NOT NULL,
                verdict TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        '''
        cursor.execute(create_query)
        
        conn.commit()
        conn.close()

    def log_interaction(self, user_name, verdict):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # SQL SPELL: Insert Data (Adaptive)
        # We use 'self.placeholder' (%s or ?)
        query = f'''
            INSERT INTO interactions (user_name, verdict, timestamp)
            VALUES ({self.placeholder}, {self.placeholder}, {self.placeholder})
        '''
        cursor.execute(query, (user_name, verdict, current_time))
        
        conn.commit()
        conn.close()
        print(f"[LOG] {user_name} -> {verdict}")

    def get_total_count(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM interactions")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count

    def get_recent_history(self, limit=5):
        conn = self.get_connection()
        cursor = conn.cursor()

        # We use 'self.placeholder' for the LIMIT clause
        query = f"SELECT user_name, verdict, timestamp FROM interactions ORDER BY id DESC LIMIT {self.placeholder}"
        cursor.execute(query, (limit,))

        rows = cursor.fetchall()
        conn.close()

        history = []
        for row in rows:
            history.append({
                "user": row[0],
                "verdict": row[1],
                "time": row[2]
            })
        return history

    def get_verdict_counts(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT verdict, COUNT(*) FROM interactions GROUP BY verdict")
        rows = cursor.fetchall()
        conn.close()

        stats = {}
        for row in rows:
            stats[row[0]] = row[1]
        return stats

    def get_hourly_activity(self):
        """Returns activity per hour. Handles the syntax difference."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # SQL SPELL: Time Extraction (The Tricky Part)
        if self.is_postgres:
            # Postgres: Turn text to timestamp, then extract hour
            query = "SELECT TO_CHAR(timestamp::timestamp, 'HH24'), COUNT(*) FROM interactions GROUP BY 1"
        else:
            # SQLite: Use string formatting
            query = "SELECT strftime('%H', timestamp), COUNT(*) FROM interactions GROUP BY 1"

        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        hourly_data = {str(i).zfill(2): 0 for i in range(24)}
        
        for row in rows:
            hour = row[0]
            if hour in hourly_data:
                hourly_data[hour] = row[1]
                
        return list(hourly_data.values())

# TEST AREA
if __name__ == "__main__":
    db = DatabaseManager()
    db.log_interaction("Cloud_Test", "Infinite Burpees")
    print(f"Total Logs: {db.get_total_count()}")
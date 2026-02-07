import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="protocol_zero.db"):
        self.db_name = db_name
        self.initialize_db()

    def get_connection(self):
        # Opens a tunnel to the database file
        return sqlite3.connect(self.db_name)

    def initialize_db(self):
        # Create the tables if they don't exist yet
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # SQL SPELL: Create the Log Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                verdict TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"[DATABASE] Connected to {self.db_name}")

    def log_interaction(self, user_name, verdict):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Insert the data (The Safe Way, to prevent SQL Injection)
        cursor.execute('''
            INSERT INTO interactions (user_name, verdict, timestamp)
            VALUES (?, ?, ?)
        ''', (user_name, verdict, current_time))
        
        conn.commit()
        conn.close()
        print(f"[DATABASE] Logged: {user_name} -> {verdict}")

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

        # Select EVERYTHING from the 'interactions' shelf.
        # Order them by ID (newest numbers first).
        # Only give me the top 5.
        cursor.execute("SELECT user_name, verdict, timestamp FROM interactions ORDER BY id DESC LIMIT ?", (limit,))

        rows = cursor.fetchall() # Grab the data
        conn.close()

        # Convert the raw database rows into a nice list of dictionaries
        history = []
        for row in rows:
            history.append({
                "user": row[0],
                "verdict": row[1],
                "time": row[2]
                })
        return history

    def get_verdict_counts(self):
        """Returns the count of each punishment type for the graph."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # SQL MAGIC: Group by the verdict name and count them
        cursor.execute("SELECT verdict, COUNT(*) FROM interactions GROUP BY verdict")
        rows = cursor.fetchall()
        conn.close()

        # Transform into a dictionary
        stats = {}
        for row in rows:
            stats[row[0]] = row[1]
        return stats

    def get_hourly_activity(self):
        """Returns a list of 24 integers representing activity per hour of the day."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Extract the Hour ('%H') from the timestamp string and count groups
        # Note: This assumes your timestamps are stored as 'YYYY-MM-DD HH:MM:SS'
        query = "SELECT strftime('%H', timestamp), COUNT(*) FROM interactions GROUP BY 1"
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        # 1. Create a bucket for every hour (0 to 23) initialized to 0
        hourly_data = {str(i).zfill(2): 0 for i in range(24)}
        
        # 2. Fill the buckets with actual data
        for row in rows:
            hour = row[0] # e.g., "14"
            count = row[1]
            if hour in hourly_data:
                hourly_data[hour] = count
                
        # 3. Return just the values as a list [0, 0, ..., 5, 2, ...]
        return list(hourly_data.values())


# TEST AREA (Run this file directly to check if it works)
if __name__ == "__main__":
    db = DatabaseManager()
    db.log_interaction("Test_User", "Do 10 Burpees")
    print(f"Total Logs: {db.get_total_count()}")
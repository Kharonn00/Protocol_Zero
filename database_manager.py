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

        # 2. Set SQL Dialect
        if self.is_postgres:
            print("🚀 [DATABASE] Cloud Mode (PostgreSQL)")
            self.placeholder = "%s"
            self.id_type = "SERIAL PRIMARY KEY"
            self.text_type = "TEXT"
        else:
            print("🏠 [DATABASE] Local Mode (SQLite)")
            self.db_name = "protocol_zero.db"
            self.placeholder = "?"
            self.id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"
            self.text_type = "TEXT"

        self.initialize_db()

    def get_connection(self):
        if self.is_postgres:
            return psycopg2.connect(self.db_url, sslmode='require')
        else:
            return sqlite3.connect(self.db_name)

    def initialize_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # TABLE 1: INTERACTIONS (The Logs)
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS interactions (
                id {self.id_type},
                user_id {self.text_type},
                user_name {self.text_type},
                verdict {self.text_type},
                timestamp {self.text_type}
            )
        ''')

        # TABLE 2: USERS (The RPG Stats) - NEW!
        # We use discord_id as the primary key so we don't have duplicates
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS users (
                discord_id {self.text_type} PRIMARY KEY,
                username {self.text_type},
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                streak INTEGER DEFAULT 0,
                last_active {self.text_type}
            )
        ''')
        
        conn.commit()
        conn.close()

    # --- LOGGING ---
    def log_interaction(self, user_id, user_name, verdict):
        conn = self.get_connection()
        cursor = conn.cursor()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Log the event
        query = f'''
            INSERT INTO interactions (user_id, user_name, verdict, timestamp)
            VALUES ({self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder})
        '''
        cursor.execute(query, (str(user_id), user_name, verdict, current_time))
        
        conn.commit()
        conn.close()
        print(f"[LOG] {user_name} ({user_id}) -> {verdict}")

    # --- GAMIFICATION (NEW) ---
    def update_xp(self, user_id, user_name, xp_amount):
        """Adds XP to a user and handles leveling up."""
        conn = self.get_connection()
        cursor = conn.cursor()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if user exists, if not create them
        # (Upsert logic is complex in SQL, so we do "Try Insert, Then Update")
        
        # 1. Try to find the user
        cursor.execute(f"SELECT xp, level FROM users WHERE discord_id = {self.placeholder}", (str(user_id),))
        result = cursor.fetchone()

        if result is None:
            # New User! Welcome to the game.
            print(f"[RPG] New Challenger: {user_name}")
            cursor.execute(f'''
                INSERT INTO users (discord_id, username, xp, level, streak, last_active)
                VALUES ({self.placeholder}, {self.placeholder}, {self.placeholder}, 1, 0, {self.placeholder})
            ''', (str(user_id), user_name, xp_amount, current_time))
            new_level = 1
            current_xp = xp_amount
        else:
            # Existing User
            current_xp = result[0] + xp_amount
            current_level = result[1]
            
            # Simple Leveling Curve: Level * 100 XP required for next level
            # e.g., Level 1 -> 2 needs 100 XP. Level 2 -> 3 needs 200 XP.
            xp_needed = current_level * 100
            
            new_level = current_level
            if current_xp >= xp_needed:
                new_level += 1
                current_xp = current_xp - xp_needed # Reset XP for next level bracket (optional style)
                # OR keep total XP and just calc level. Let's keep it simple: Total XP accumulates.
                # Actually, let's just increment level if threshold met.
                print(f"🎉 LEVEL UP! {user_name} is now Lvl {new_level}!")

            cursor.execute(f'''
                UPDATE users 
                SET xp = {self.placeholder}, level = {self.placeholder}, last_active = {self.placeholder}, username = {self.placeholder}
                WHERE discord_id = {self.placeholder}
            ''', (current_xp, new_level, current_time, user_name, str(user_id)))

        conn.commit()
        conn.close()
        return new_level, current_xp

    def get_user_stats(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT level, xp, streak FROM users WHERE discord_id = {self.placeholder}", (str(user_id),))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {"level": result[0], "xp": result[1], "streak": result[2]}
        else:
            return {"level": 1, "xp": 0, "streak": 0}

    # --- ANALYTICS ---
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
        query = f"SELECT user_name, verdict, timestamp FROM interactions ORDER BY id DESC LIMIT {self.placeholder}"
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [{"user": r[0], "verdict": r[1], "time": r[2]} for r in rows]

    def get_verdict_counts(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT verdict, COUNT(*) FROM interactions GROUP BY verdict")
        rows = cursor.fetchall()
        conn.close()
        return {r[0]: r[1] for r in rows}

    def get_hourly_activity(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        if self.is_postgres:
            query = "SELECT TO_CHAR(timestamp::timestamp, 'HH24'), COUNT(*) FROM interactions GROUP BY 1"
        else:
            query = "SELECT strftime('%H', timestamp), COUNT(*) FROM interactions GROUP BY 1"
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        hourly_data = {str(i).zfill(2): 0 for i in range(24)}
        for row in rows:
            if row[0] in hourly_data:
                hourly_data[row[0]] = row[1]
        return list(hourly_data.values())

if __name__ == "__main__":
    db = DatabaseManager()
    print("Database Schema Updated.")
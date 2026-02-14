import sqlite3  # SQLite database - lightweight, file-based, good for local dev
import os  # For accessing environment variables
import psycopg2  # PostgreSQL database - robust, cloud-ready, good for production
from datetime import datetime  # For timestamps
from urllib.parse import urlparse  # For parsing database URLs (not used but imported)


# ============================================================================
# DATABASE MANAGER CLASS
# ============================================================================
class DatabaseManager:
    """
    A database abstraction layer that works with both SQLite and PostgreSQL.
    
    Why support both?
    - SQLite: Perfect for local development (no setup needed, just a file)
    - PostgreSQL: Used by cloud platforms like Render, Railway, Heroku
    
    This class automatically detects which database to use based on
    environment variables, making it easy to develop locally and deploy
    to the cloud without changing code.
    
    Key Concepts:
    - Database abstraction: Write once, run on multiple databases
    - Environment-based configuration: Different settings for dev vs prod
    - SQL dialect compatibility: Handle differences between databases
    """
    
    def __init__(self):
        """
        Constructor - sets up database configuration and creates tables.
        
        This runs when you create a DatabaseManager instance.
        It detects the environment and initializes the database schema.
        """
        
        # ====================================================================
        # STEP 1: DETECT ENVIRONMENT (Cloud vs Local)
        # ====================================================================
        # Check if DATABASE_URL environment variable exists
        # Cloud platforms (Render, Railway, Heroku) provide this automatically
        self.db_url = os.getenv("DATABASE_URL")
        
        # If DATABASE_URL exists, we're in the cloud using PostgreSQL
        # If not, we're local using SQLite
        self.is_postgres = bool(self.db_url)

        # ====================================================================
        # STEP 2: SET SQL DIALECT - Handle database differences
        # ====================================================================
        # Different databases use different SQL syntax for some operations
        # We set the correct syntax based on which database we're using
        
        if self.is_postgres:
            # PostgreSQL Configuration
            print("🚀 [DATABASE] Cloud Mode (PostgreSQL)")
            
            # PostgreSQL uses %s for parameterized queries (SQL injection protection)
            # Example: "SELECT * FROM users WHERE id = %s"
            self.placeholder = "%s"
            
            # PostgreSQL auto-incrementing ID syntax
            self.id_type = "SERIAL PRIMARY KEY"
            
            # PostgreSQL text column type
            self.text_type = "TEXT"
            
        else:
            # SQLite Configuration
            print("🏠 [DATABASE] Local Mode (SQLite)")
            
            # SQLite database filename (created in current directory)
            self.db_name = "protocol_zero.db"
            
            # SQLite uses ? for parameterized queries
            # Example: "SELECT * FROM users WHERE id = ?"
            self.placeholder = "?"
            
            # SQLite auto-incrementing ID syntax
            self.id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"
            
            # SQLite text column type
            self.text_type = "TEXT"

        # ====================================================================
        # STEP 3: CREATE TABLES IF THEY DON'T EXIST
        # ====================================================================
        # Initialize the database schema (tables, columns)
        self.initialize_db()

    def get_connection(self):
        """
        Creates and returns a database connection.
        
        This is a factory method - it creates the right kind of connection
        based on what database we're using.
        
        Returns:
            Connection object (either sqlite3.Connection or psycopg2.Connection)
        
        Important: Always close connections when done to avoid resource leaks!
        Pattern: conn = db.get_connection() → use it → conn.close()
        """
        if self.is_postgres:
            # Connect to PostgreSQL using the DATABASE_URL
            # sslmode='require' ensures encrypted connection (required by most cloud providers)
            return psycopg2.connect(self.db_url, sslmode='require')
        else:
            # Connect to SQLite file
            # If file doesn't exist, SQLite creates it automatically
            return sqlite3.connect(self.db_name)

    def initialize_db(self):
        """
        Creates the database schema (tables and columns).
        
        This only runs once when the DatabaseManager is first created.
        The "IF NOT EXISTS" clause prevents errors if tables already exist.
        
        Schema Design:
        - interactions table: Logs every punishment/interaction
        - users table: Stores user stats (XP, level, streak)
        
        This is called "database migration" - setting up your data structure
        """
        # Get a database connection
        conn = self.get_connection()
        
        # Create a cursor - this executes SQL commands
        cursor = conn.cursor()
        
        # ====================================================================
        # TABLE 1: INTERACTIONS - The Activity Log
        # ====================================================================
        # This table records every time someone uses the Oracle
        # It's append-only (we never delete or update records)
        
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS interactions (
                id {self.id_type},              -- Auto-incrementing unique ID
                user_id {self.text_type},       -- Discord ID or "Ariel_Web"
                user_name {self.text_type},     -- Display name
                verdict {self.text_type},       -- The punishment assigned
                timestamp {self.text_type}      -- When it happened
            )
        ''')
        # Note: We use f-strings to insert the correct SQL syntax for each database

        # ====================================================================
        # TABLE 2: USERS - The RPG Stats System
        # ====================================================================
        # This table stores persistent user data for gamification
        # Each user has ONE row identified by their Discord ID
        
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS users (
                discord_id {self.text_type} PRIMARY KEY,  -- Unique user identifier
                username {self.text_type},                -- Display name (can change)
                xp INTEGER DEFAULT 0,                     -- Experience points
                level INTEGER DEFAULT 1,                  -- Current level
                streak INTEGER DEFAULT 0,                 -- Current resistance streak
                last_active {self.text_type}              -- Last interaction timestamp
            )
        ''')
        # PRIMARY KEY means discord_id must be unique (no duplicate users)
        # DEFAULT values are used when creating new users
        
        # ====================================================================
        # COMMIT AND CLOSE
        # ====================================================================
        # commit() saves all changes to disk (makes them permanent)
        conn.commit()
        
        # close() releases the database connection
        # Important: Always close connections to avoid resource leaks!
        conn.close()

    # ========================================================================
    # LOGGING METHODS - Recording interactions
    # ========================================================================
    
    def log_interaction(self, user_id, user_name, verdict):
        """
        Records a punishment/interaction to the database.
        
        This creates a permanent record of every Oracle consultation.
        Used for analytics and history display.
        
        Parameters:
            user_id (str): Discord ID or "Ariel_Web"
            user_name (str): Display name
            verdict (str): The punishment that was assigned
        
        This is a CREATE operation (the C in CRUD)
        """
        # Get a fresh database connection
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get current timestamp in standard format
        # Format: "2027-01-15 14:30:45"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # ====================================================================
        # INSERT THE RECORD - Parameterized Query for Security
        # ====================================================================
        # We use placeholders (? or %s) instead of string concatenation
        # This prevents SQL injection attacks
        # UNSAFE: f"INSERT ... VALUES ('{user_id}')" - can be hacked!
        # SAFE: Uses placeholders and passes values separately
        
        query = f'''
            INSERT INTO interactions (user_id, user_name, verdict, timestamp)
            VALUES ({self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder})
        '''
        
        # Execute the query with actual values
        # Values are automatically escaped/sanitized by the database library
        cursor.execute(query, (str(user_id), user_name, verdict, current_time))
        
        # Save changes and close connection
        conn.commit()
        conn.close()
        
        # Log to console for debugging
        print(f"[LOG] {user_name} ({user_id}) -> {verdict}")

    # ========================================================================
    # GAMIFICATION METHODS - XP, Levels, and Progression
    # ========================================================================
    
    def update_xp(self, user_id, user_name, xp_amount):
        """
        Adds XP to a user and handles leveling up.
        
        This implements the RPG-style progression system:
        - New users start at Level 1 with 0 XP
        - XP accumulates with each interaction
        - When XP threshold is reached, user levels up
        
        Parameters:
            user_id (str): Discord ID
            user_name (str): Display name (updates if changed)
            xp_amount (int): How much XP to add (10 for failure, 50 for resist)
        
        Returns:
            tuple: (new_level, current_xp)
        
        This combines CREATE and UPDATE operations (upsert pattern)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get current timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ====================================================================
        # UPSERT LOGIC - Update if exists, Insert if new
        # ====================================================================
        # "Upsert" = Update + Insert
        # We check if the user exists, then either create or update them
        # (Some databases have native UPSERT, but we do it manually for compatibility)
        
        # Step 1: Try to find the user
        cursor.execute(
            f"SELECT xp, level FROM users WHERE discord_id = {self.placeholder}", 
            (str(user_id),)
        )
        result = cursor.fetchone()  # Returns None if user doesn't exist

        if result is None:
            # ================================================================
            # NEW USER - Create their account
            # ================================================================
            print(f"[RPG] New Challenger: {user_name}")
            
            # Insert a new user with starting stats
            cursor.execute(f'''
                INSERT INTO users (discord_id, username, xp, level, streak, last_active)
                VALUES ({self.placeholder}, {self.placeholder}, {self.placeholder}, 1, 0, {self.placeholder})
            ''', (str(user_id), user_name, xp_amount, current_time))
            
            # Return their starting stats
            new_level = 1
            current_xp = xp_amount
            
        else:
            # ================================================================
            # EXISTING USER - Update their stats
            # ================================================================
            # Extract current stats from database result
            # result is a tuple: (xp, level)
            current_xp = result[0] + xp_amount  # Add new XP to existing XP
            current_level = result[1]  # Current level
            
            # ================================================================
            # LEVELING SYSTEM - Check if user should level up
            # ================================================================
            # Simple leveling curve: Each level requires Level × 100 XP
            # Level 1→2: 100 XP needed
            # Level 2→3: 200 XP needed
            # Level 3→4: 300 XP needed
            # This creates exponential growth (gets harder to level up)
            
            xp_needed = current_level * 100
            
            new_level = current_level  # Start with current level
            
            # Check if user has enough XP to level up
            if current_xp >= xp_needed:
                new_level += 1  # Level up!
                
                # Option A: Subtract XP for next level (XP resets each level)
                # current_xp = current_xp - xp_needed
                
                # Option B: Keep total XP (what we're doing - simpler)
                # Total XP just keeps accumulating
                
                # Celebrate the level up!
                print(f"🎉 LEVEL UP! {user_name} is now Lvl {new_level}!")

            # ================================================================
            # UPDATE THE DATABASE
            # ================================================================
            # Update all fields (including username in case it changed)
            cursor.execute(f'''
                UPDATE users 
                SET xp = {self.placeholder}, 
                    level = {self.placeholder}, 
                    last_active = {self.placeholder}, 
                    username = {self.placeholder}
                WHERE discord_id = {self.placeholder}
            ''', (current_xp, new_level, current_time, user_name, str(user_id)))

        # Save changes and close
        conn.commit()
        conn.close()
        
        # Return the user's new stats
        return new_level, current_xp

    def get_user_stats(self, user_id):
        """
        Retrieves a user's current stats.
        
        This is a READ operation (the R in CRUD)
        
        Parameters:
            user_id (str): Discord ID to look up
        
        Returns:
            dict: {"level": int, "xp": int, "streak": int}
                  Returns default values if user doesn't exist
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Query for user's stats
        cursor.execute(
            f"SELECT level, xp, streak FROM users WHERE discord_id = {self.placeholder}", 
            (str(user_id),)
        )
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            # User exists - return their actual stats
            # result is a tuple: (level, xp, streak)
            return {
                "level": result[0], 
                "xp": result[1], 
                "streak": result[2]
            }
        else:
            # User doesn't exist - return default values
            # This prevents errors when displaying stats for new users
            return {
                "level": 1, 
                "xp": 0, 
                "streak": 0
            }

    def get_leaderboard(self):
        """
        Retrieves the top 5 users based on Level and XP.
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # We need to order by Level (highest first), then XP (highest first)
        query = "SELECT username, level, xp FROM users ORDER BY level DESC, xp DESC LIMIT 5"

        cursor.execute(query)
        rows = cursor.fetchall()

        conn.close()

        # Convert list of tuples [(Name, Lvl, XP), ...] into a clean list of dictionaries
        return [{"username": r[0], "level": r[1], "xp": r[2]} for r in rows]

    # ========================================================================
    # ANALYTICS METHODS - Data aggregation and reporting
    # ========================================================================
    
    def get_total_count(self):
        """
        Returns the total number of punishments ever served.
        
        This is a simple aggregation query using COUNT().
        COUNT(*) counts all rows in the table.
        
        Returns:
            int: Total number of interaction records
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Count all rows
        cursor.execute("SELECT COUNT(*) FROM interactions")
        
        # fetchone() returns a tuple with one element: (count,)
        # [0] extracts just the number
        count = cursor.fetchone()[0]
        
        conn.close()
        return count

    def get_recent_history(self, limit=5):
        """
        Returns the most recent punishments.
        
        Used for displaying history on the dashboard.
        
        Parameters:
            limit (int): How many recent records to return
        
        Returns:
            list: List of dicts with keys: user, verdict, time
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # ====================================================================
        # SQL QUERY BREAKDOWN:
        # ====================================================================
        # SELECT: Which columns to retrieve
        # FROM: Which table
        # ORDER BY id DESC: Sort by ID descending (newest first)
        # LIMIT: Only return this many rows
        
        query = f"SELECT user_name, verdict, timestamp FROM interactions ORDER BY id DESC LIMIT {self.placeholder}"
        cursor.execute(query, (limit,))
        
        # fetchall() returns a list of tuples
        # Each tuple represents one row: (user_name, verdict, timestamp)
        rows = cursor.fetchall()
        
        conn.close()
        
        # Convert list of tuples to list of dicts (easier to work with)
        # This is called "data transformation"
        # r[0] = user_name, r[1] = verdict, r[2] = timestamp
        return [{"user": r[0], "verdict": r[1], "time": r[2]} for r in rows]

    def get_verdict_counts(self):
        """
        Returns how many times each punishment type was given.
        
        Used for the donut chart on the dashboard.
        This is an aggregation query using GROUP BY.
        
        Returns:
            dict: {"Do 10 Pushups": 15, "Drink water": 8, ...}
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # ====================================================================
        # SQL QUERY BREAKDOWN:
        # ====================================================================
        # SELECT verdict, COUNT(*): Get verdict and count of each
        # GROUP BY verdict: Combine rows with same verdict
        # Result: One row per unique verdict with count
        
        cursor.execute("SELECT verdict, COUNT(*) FROM interactions GROUP BY verdict")
        
        # fetchall() returns: [("Do 10 Pushups", 15), ("Drink water", 8), ...]
        rows = cursor.fetchall()
        
        conn.close()
        
        # Convert to dictionary for easy lookup
        # r[0] = verdict, r[1] = count
        return {r[0]: r[1] for r in rows}

    def get_hourly_activity(self):
        """
        Returns punishment counts for each hour of the day (0-23).
        
        Used for the bar chart showing hourly activity patterns.
        This shows which hours see the most Oracle consultations.
        
        Returns:
            list: 24 numbers, one for each hour [0, 3, 5, 2, ...]
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # ====================================================================
        # DATABASE-SPECIFIC DATE FORMATTING
        # ====================================================================
        # Different databases extract hours from timestamps differently
        
        if self.is_postgres:
            # PostgreSQL: TO_CHAR() formats timestamps
            # 'HH24' = hour in 24-hour format (00-23)
            # ::timestamp casts to timestamp type
            # GROUP BY 1 means "group by the first selected column"
            query = "SELECT TO_CHAR(timestamp::timestamp, 'HH24'), COUNT(*) FROM interactions GROUP BY 1"
        else:
            # SQLite: strftime() formats timestamps
            # '%H' = hour in 24-hour format
            query = "SELECT strftime('%H', timestamp), COUNT(*) FROM interactions GROUP BY 1"
        
        cursor.execute(query)
        
        # fetchall() returns: [("08", 5), ("14", 12), ("20", 3), ...]
        rows = cursor.fetchall()
        
        conn.close()
        
        # ====================================================================
        # DATA PROCESSING - Fill in missing hours
        # ====================================================================
        # Create a dictionary with all 24 hours initialized to 0
        # zfill(2) pads single digits: 0 → "00", 9 → "09"
        hourly_data = {str(i).zfill(2): 0 for i in range(24)}
        
        # Fill in actual counts from database
        for row in rows:
            hour = row[0]  # Hour as string: "08", "14", etc.
            count = row[1]  # Count for that hour
            
            if hour in hourly_data:
                hourly_data[hour] = count
        
        # Convert dictionary to list in order (00, 01, 02, ..., 23)
        # Chart.js expects a simple list, not a dictionary
        return list(hourly_data.values())


# ============================================================================
# TESTING BLOCK - Only runs when file is executed directly
# ============================================================================
if __name__ == "__main__":
    # Create a DatabaseManager instance
    # This will detect environment and initialize tables
    db = DatabaseManager()
    
    print("Database Schema Updated.")
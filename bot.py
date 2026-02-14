import os  # For accessing environment variables
import random  # For random selection (backup roasts)

# Third-Party Libraries
import discord  # Discord API library - for creating Discord bots
from dotenv import load_dotenv  # For loading secrets from .env file
from google import genai  # Google's Gemini AI library

# Custom Modules (your own code files)
from oracle import ProtocolZero, datetime  # Import Oracle system and datetime
from database_manager import DatabaseManager  # Import database operations


# ============================================================================
# STEP 1: LOAD ENVIRONMENT VARIABLES (API Keys & Tokens)
# ============================================================================
# Load secrets from .env file (not uploaded to GitHub for security)
load_dotenv()

# Get the Discord bot token - this authenticates your bot with Discord
# Without this, the bot can't connect to Discord servers
TOKEN = os.getenv('DISCORD_TOKEN')

# Get the Gemini API key for AI-generated roasts and praise
GOOGLE_KEY = os.getenv('GEMINI_API_KEY')


# ============================================================================
# STEP 2: CONFIGURE THE AI CLIENT (The Roaster)
# ============================================================================
# Set up connection to Google's Gemini AI
# If it fails, we'll use backup roasts instead (graceful degradation)

ai_client = None  # Start with no AI client

if GOOGLE_KEY:
    # If we have an API key, try to connect
    try:
        # Create a Gemini client instance
        ai_client = genai.Client(api_key=GOOGLE_KEY)
        print("✅ [BOT] AI Connected")
    except Exception as e:
        # If connection fails, log the error but continue running
        print(f"⚠️ [BOT] AI Config Error: {e}")
        # ai_client stays None, so we'll use backup roasts


# ============================================================================
# BACKUP ROASTS - Used when AI is unavailable
# ============================================================================
# Always have a fallback! These are used when Gemini API fails
BACKUP_ROASTS = [
    "Even the AI refuses to talk to you.",
    "Just do the punishment. Don't cry.",
    "404: Willpower Not Found."
]


# ============================================================================
# STEP 3: INITIALIZE DISCORD BOT CAPABILITIES
# ============================================================================
# Intents specify what events the bot can receive from Discord
# Think of intents as "permissions" for what data the bot can access

intents = discord.Intents.default()  # Start with default permissions

# Enable message content intent - allows bot to read message text
# Required for command detection (like !oracle, !resist, !stats)
# Note: You must also enable this in Discord Developer Portal
intents.message_content = True 

# Create the Discord client (the actual bot instance)
# This is the main bot object that connects to Discord
client = discord.Client(intents=intents)


# ============================================================================
# STEP 4: INITIALIZE CORE SYSTEMS
# ============================================================================

# Set the target date for the Oracle (your goal/deadline)
apocalypse = datetime.date(2027, 1, 1)

# Create the Oracle engine instance
# This generates punishments and calculates days remaining
engine = ProtocolZero("Commander Ariel", apocalypse)

# Create database manager instance
# This handles all data storage (users, XP, streaks, etc.)
db = DatabaseManager()


# ============================================================================
# HELPER FUNCTIONS - Reusable utility functions
# ============================================================================

def update_streak(user_id, reset=False):
    """
    Manually updates a user's streak in the database.
    
    The streak tracks consecutive successful resistances.
    When a user fails (uses !oracle), their streak resets to 0.
    When they resist (uses !resist), their streak increments by 1.
    
    Parameters:
        user_id (str): Discord user ID
        reset (bool): If True, set streak to 0. If False, increment by 1.
    
    Why this exists:
        The DatabaseManager class focuses on XP/level management,
        so we handle streaks separately here for flexibility.
    """
    print(f"[DEBUG] Updating streak for {user_id} (Reset={reset})...")
    
    try:
        # Get a connection to the database
        conn = db.get_connection()
        
        # Create a cursor - used to execute SQL queries
        cursor = conn.cursor()
        
        if reset:
            # Reset streak to 0 (user failed)
            # We use db.placeholder for SQL injection protection
            # It's "?" for SQLite, "%s" for PostgreSQL, etc.
            query = f"UPDATE users SET streak = 0 WHERE discord_id = {db.placeholder}"
            cursor.execute(query, (str(user_id),))
        else:
            # Increment streak by 1 (user resisted)
            query = f"UPDATE users SET streak = streak + 1 WHERE discord_id = {db.placeholder}"
            cursor.execute(query, (str(user_id),))
        
        # Commit the changes (make them permanent)
        conn.commit()
        
        # Close the connection (free up resources)
        conn.close()
        
        print("[DEBUG] Streak updated successfully.")
        
    except Exception as e:
        # If anything goes wrong, log the error
        print(f"[ERROR] Streak Update Failed: {e}")


def get_ai_roast(verdict):
    """
    Generates an AI-powered roast for when a user fails.
    
    Parameters:
        verdict (str): The punishment assigned by the Oracle
    
    Returns:
        str: A motivational (brutal) roast from the AI
    
    How it works:
        1. Check if AI client is available
        2. If yes, send a prompt to Gemini asking for a roast
        3. If no or if it fails, use a random backup roast
        
    This is called "prompt engineering" - crafting the right
    instructions to get the AI to respond how we want.
    """
    # Check if we have a working AI client
    if not ai_client:
        print("[DEBUG] No AI Client, using backup roast.")
        return random.choice(BACKUP_ROASTS)
    
    print("[DEBUG] Sending request to Gemini...")
    
    try:
        # Craft the prompt - this is critical!
        # We tell the AI:
        # 1. What role to play (ruthless drill sergeant)
        # 2. The context (user failed, got this punishment)
        # 3. What we want (one-sentence roast)
        # 4. Tone guidance (not polite)
        prompt = f"You are a ruthless, cynical AI drill sergeant. The user just failed a willpower check and was sentenced to: '{verdict}'. Write a brutal, one-sentence roast. Do not be polite."
        
        # Send the prompt to Gemini
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash-lite',  # Which AI model to use
            contents=prompt  # The actual prompt
        )
        
        print("[DEBUG] Gemini responded.")
        
        # Extract the text from the response and clean it up
        return response.text.strip()
        
    except Exception as e:
        # If AI generation fails, fall back to backup roasts
        print(f"[ERROR] Gemini Failed: {e}")
        return random.choice(BACKUP_ROASTS)


def get_ai_praise(streak):
    """
    Generates AI-powered praise for when a user resists.
    
    Parameters:
        streak (int): The user's current resistance streak
    
    Returns:
        str: A cyberpunk-style compliment from the AI
    
    Similar to get_ai_roast(), but with a positive tone.
    Still maintains the dark cyberpunk aesthetic though!
    """
    # Check if we have a working AI client
    if not ai_client:
        return "Not bad. Do it again."
    
    print("[DEBUG] Asking Gemini for praise...")
    
    try:
        # Craft a prompt asking for praise
        # We include the streak count so the AI can reference it
        prompt = f"The user just successfully resisted a craving. Their streak is now {streak}. Give them a dark, cyberpunk-style compliment. Keep it brief."
        
        # Send the prompt to Gemini
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt
        )
        
        return response.text.strip()
        
    except Exception as e:
        # Fallback praise if AI fails
        print(f"[ERROR] Gemini Praise Failed: {e}")
        return "Target destroyed. Well done."


# ============================================================================
# EVENT HANDLERS - Functions that run when Discord events occur
# ============================================================================

@client.event
async def on_ready():
    """
    Event: Triggered when the bot successfully connects to Discord.
    
    This runs once when the bot starts up and logs in.
    It's useful for confirming the bot is online and ready.
    
    The @client.event decorator tells Discord this is an event handler.
    "async def" means this is an asynchronous function (can wait for things).
    """
    print(f'--- {client.user} IS ONLINE & DEBUGGING ---')


@client.event
async def on_message(message):
    """
    Event: Triggered every time ANY message is sent in a server the bot is in.
    
    This is the main event handler - it processes all commands.
    
    Parameters:
        message: A discord.Message object containing all message data
                 (content, author, channel, etc.)
    
    How it works:
        1. Check if bot sent the message (ignore if so)
        2. Check message content for commands (!oracle, !resist, !stats)
        3. Execute appropriate command logic
        4. Send response back to Discord
    """
    
    # ========================================================================
    # IGNORE BOT'S OWN MESSAGES
    # ========================================================================
    # Without this check, the bot could respond to itself infinitely!
    if message.author == client.user:
        return  # Exit early if bot sent the message

    # ========================================================================
    # EXTRACT USER INFORMATION
    # ========================================================================
    # Get the Discord user ID (unique identifier for each user)
    # Convert to string because database expects string format
    user_id = str(message.author.id)
    
    # Get the user's display name
    user_name = message.author.name

    # ========================================================================
    # COMMAND: !oracle (FAILURE - User gave in to temptation)
    # ========================================================================
    if message.content.startswith('!oracle'):
        print(f"\n[DEBUG] 1. Request received from {user_name}")

        # --------------------------------------------------------------------
        # STEP 1: GENERATE THE PUNISHMENT VERDICT
        # --------------------------------------------------------------------
        try:
            # Ask the Oracle for a punishment
            # This also logs to the database automatically
            verdict = engine.consult_oracle()
            print(f"[DEBUG] 2. Verdict generated: {verdict}")
        except Exception as e:
            # If Oracle fails, log error and exit
            print(f"[ERROR] Engine Failed: {e}")
            return

        # --------------------------------------------------------------------
        # STEP 2: GENERATE AI ROAST
        # --------------------------------------------------------------------
        roast = get_ai_roast(verdict)

        # --------------------------------------------------------------------
        # STEP 3: DATABASE OPERATIONS
        # --------------------------------------------------------------------
        print("[DEBUG] 3. Starting Database Operations...")
        try:
            # A. Log this failure to the database
            print("[DEBUG] 3a. Logging Interaction...")
            db.log_interaction(user_id, user_name, verdict)
            
            # B. Reset the user's streak to 0 (they failed)
            print("[DEBUG] 3b. Resetting Streak...")
            update_streak(user_id, reset=True)
            
            # C. Award 10 XP (even failures give some XP)
            # Returns the user's new level and current XP
            print("[DEBUG] 3c. Updating XP...")
            new_level, current_xp = db.update_xp(user_id, user_name, 10)
            print(f"[DEBUG] 4. DB Success. Lvl: {new_level}, XP: {current_xp}")
            
        except Exception as e:
            # If database fails, log error but continue
            # Set level and XP to 0 as fallback
            print(f"[ERROR] Database CRITICAL FAILURE: {e}")
            new_level, current_xp = 0, 0

        # --------------------------------------------------------------------
        # STEP 4: CREATE AND SEND DISCORD EMBED
        # --------------------------------------------------------------------
        # Embeds are rich messages with formatting, colors, and fields
        # They look much better than plain text
        
        print("[DEBUG] 5. Sending Embed to Discord...")
        
        # Create a red embed for failures
        embed = discord.Embed(
            title="⚠️ PROTOCOL ZERO BREACH",  # Title text
            color=0xff0000  # Red color (hex code)
        )
        
        # Add the punishment verdict as a field
        embed.add_field(
            name="The Verdict",  # Field label
            value=f"**{verdict}**",  # Field content (bold)
            inline=False  # Take up full width (not side-by-side)
        )
        
        # Add the AI roast as a field
        embed.add_field(
            name="Oracle says:", 
            value=f"_{roast}_",  # Italicized text
            inline=False
        )
        
        # Add footer with stats
        embed.set_footer(text=f"Streak Reset | XP: {current_xp} | Lvl: {new_level}")
        
        # Send the embed to the same channel where the command was used
        await message.channel.send(embed=embed)
        print("[DEBUG] 6. Message Sent.\n")

    # ========================================================================
    # COMMAND: !resist (VICTORY - User resisted temptation)
    # ========================================================================
    elif message.content.startswith('!resist'):
        print(f"\n[DEBUG] Resistance Request from {user_name}")

        # --------------------------------------------------------------------
        # STEP 1: UPDATE USER STATS
        # --------------------------------------------------------------------
        # Award 50 XP for resisting (5x more than failing!)
        print("[DEBUG] Updating XP (+50)...")
        new_level, current_xp = db.update_xp(user_id, user_name, 50)
        
        # Increment the user's streak
        print("[DEBUG] Incrementing Streak...")
        update_streak(user_id, reset=False)
        
        # --------------------------------------------------------------------
        # STEP 2: GET CURRENT STREAK
        # --------------------------------------------------------------------
        # Fetch the user's stats from the database
        stats = db.get_user_stats(user_id)
        current_streak = stats['streak']
        
        # Get AI-generated praise based on streak
        praise = get_ai_praise(current_streak)

        # --------------------------------------------------------------------
        # STEP 3: CREATE AND SEND DISCORD EMBED
        # --------------------------------------------------------------------
        # Create a green embed for victories
        embed = discord.Embed(
            title="🛡️ RESISTANCE CONFIRMED", 
            color=0x00ff41  # Green color (terminal green)
        )
        
        # Add status field
        embed.add_field(
            name="Status", 
            value=f"**Craving Neutralized.**", 
            inline=False
        )
        
        # Add AI praise field
        embed.add_field(
            name="Oracle says:", 
            value=f"_{praise}_", 
            inline=False
        )
        
        # Add footer with stats
        # 🔥 emoji makes the streak look more impactful
        embed.set_footer(text=f"Streak: {current_streak} 🔥 | XP: +50 | Lvl: {new_level}")

        await message.channel.send(embed=embed)

    # ========================================================================
    # COMMAND: !leaderboard (Top 5 Agents)
    # ========================================================================
    elif message.content.startswith('!leaderboard'):
        print(f"[DEBUG] Leaderboard Request from {user_name}")
        
        # 1. Get the Raw Data from Database
        # Remember: It returns a list like [{'username': 'Kharonn', 'level': 10...}, ...]
        top_agents = db.get_leaderboard()
        
        # 2. Build the Message String
        # We start with an empty string and add lines to it
        description_text = ""
        
        for i, agent in enumerate(top_agents):
            # i+1 makes it start at 1 instead of 0
            # \n creates a new line
            rank = i + 1
            name = agent['username']
            lvl = agent['level']
            xp = agent['xp']
            
            # Format: "1. Kharonn (Lvl 10 | 1050 XP)"
            description_text += f"**#{rank}** {name} — Lvl {lvl} ({xp} XP)\n"
            
        # 3. Create the Embed
        embed = discord.Embed(
            title="🏆 PROTOCOL ZERO ELITE 🏆",
            description=description_text,
            color=0xFFD700  # Gold Color
        )
        
        await message.channel.send(embed=embed)

    # ========================================================================
    # COMMAND: !stats (STATUS - Check user's progress)
    # ========================================================================
    elif message.content.startswith('!stats'):
        print(f"[DEBUG] Stats Request from {user_name}")
        
        # Get all user statistics from the database
        stats = db.get_user_stats(user_id)
        
        # Create a blue embed for stats display
        embed = discord.Embed(
            title=f"👤 AGENT: {user_name.upper()}",  # Uppercase for impact
            color=0x0088ff  # Blue color
        )
        
        # Add stats as separate fields (side-by-side layout)
        embed.add_field(
            name="Level", 
            value=str(stats['level']), 
            inline=True  # Display inline (side-by-side)
        )
        
        embed.add_field(
            name="XP", 
            value=str(stats['xp']), 
            inline=True
        )
        
        embed.add_field(
            name="Current Streak", 
            value=f"{stats['streak']} 🔥", 
            inline=True
        )
        
        await message.channel.send(embed=embed)


# ============================================================================
# STEP 5: SAFETY LATCH - Main Execution Block
# ============================================================================
# This only runs if you execute this file directly (python bot.py)
# It won't run if you import this file into another program

if __name__ == "__main__":
    # Check if we have a Discord token
    if TOKEN:
        print("[INIT] Launching Bot...")
        
        # Start the bot and connect to Discord
        # This is a blocking call - it runs forever until stopped
        # The bot will stay online and respond to events
        client.run(TOKEN)
    else:
        # If no token found, the bot can't connect to Discord
        print("❌ CRITICAL: No DISCORD_TOKEN found.")
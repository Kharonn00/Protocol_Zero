import os
import discord
import random
from dotenv import load_dotenv
from google import genai
from oracle import ProtocolZero, datetime 
from database_manager import DatabaseManager

# 1. Load the Vault
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GOOGLE_KEY = os.getenv('GEMINI_API_KEY')

# 2. Configure AI (The Roaster)
ai_client = None
if GOOGLE_KEY:
    try:
        ai_client = genai.Client(api_key=GOOGLE_KEY)
        print("✅ [BOT] AI Connected")
    except Exception as e:
        print(f"⚠️ [BOT] AI Config Error: {e}")

# Backup Roasts
BACKUP_ROASTS = [
    "Even the AI refuses to talk to you.",
    "Just do the punishment. Don't cry.",
    "404: Willpower Not Found."
]

# 3. Initialize Capabilities
intents = discord.Intents.default()
intents.message_content = True 
client = discord.Client(intents=intents)

# 4. Connect to the Brains
apocalypse = datetime.date(2027, 1, 1)
engine = ProtocolZero("Commander Ariel", apocalypse)
db = DatabaseManager()

# --- HELPER FUNCTIONS ---
def update_streak(user_id, reset=False):
    """Manually updates the streak since DB manager focuses on XP."""
    print(f"[DEBUG] Updating streak for {user_id} (Reset={reset})...")
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        if reset:
            query = f"UPDATE users SET streak = 0 WHERE discord_id = {db.placeholder}"
            cursor.execute(query, (str(user_id),))
        else:
            query = f"UPDATE users SET streak = streak + 1 WHERE discord_id = {db.placeholder}"
            cursor.execute(query, (str(user_id),))
        conn.commit()
        conn.close()
        print("[DEBUG] Streak updated successfully.")
    except Exception as e:
        print(f"[ERROR] Streak Update Failed: {e}")

def get_ai_roast(verdict):
    """Asks Gemini for a roast."""
    if not ai_client:
        print("[DEBUG] No AI Client, using backup roast.")
        return random.choice(BACKUP_ROASTS)
    
    print("[DEBUG] Sending request to Gemini...")
    try:
        prompt = f"You are a ruthless, cynical AI drill sergeant. The user just failed a willpower check and was sentenced to: '{verdict}'. Write a brutal, one-sentence roast. Do not be polite."
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt
        )
        print("[DEBUG] Gemini responded.")
        return response.text.strip()
    except Exception as e:
        print(f"[ERROR] Gemini Failed: {e}")
        return random.choice(BACKUP_ROASTS)

def get_ai_praise(streak):
    if not ai_client:
        return "Not bad. Do it again."
    print("[DEBUG] Asking Gemini for praise...")
    try:
        prompt = f"The user just successfully resisted a craving. Their streak is now {streak}. Give them a dark, cyberpunk-style compliment. Keep it brief."
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"[ERROR] Gemini Praise Failed: {e}")
        return "Target destroyed. Well done."

# --- EVENTS ---
@client.event
async def on_ready():
    print(f'--- {client.user} IS ONLINE & DEBUGGING ---')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    user_id = str(message.author.id)
    user_name = message.author.name

    # --- COMMAND: !oracle (FAILURE) ---
    if message.content.startswith('!oracle'):
        print(f"\n[DEBUG] 1. Request received from {user_name}")

        # 1. Get Verdict
        try:
            verdict = engine.consult_oracle()
            print(f"[DEBUG] 2. Verdict generated: {verdict}")
        except Exception as e:
            print(f"[ERROR] Engine Failed: {e}")
            return

        # 2. Get Roast
        roast = get_ai_roast(verdict)

        # 3. Database Operations
        print("[DEBUG] 3. Starting Database Operations...")
        try:
            # A. Log the Failure
            print("[DEBUG] 3a. Logging Interaction...")
            db.log_interaction(user_id, user_name, verdict)
            
            # B. Reset Streak
            print("[DEBUG] 3b. Resetting Streak...")
            update_streak(user_id, reset=True)
            
            # C. Award XP
            print("[DEBUG] 3c. Updating XP...")
            new_level, current_xp = db.update_xp(user_id, user_name, 10)
            print(f"[DEBUG] 4. DB Success. Lvl: {new_level}, XP: {current_xp}")
            
        except Exception as e:
            print(f"[ERROR] Database CRITICAL FAILURE: {e}")
            new_level, current_xp = 0, 0

        # 4. Output
        print("[DEBUG] 5. Sending Embed to Discord...")
        embed = discord.Embed(title="⚠️ PROTOCOL ZERO BREACH", color=0xff0000)
        embed.add_field(name="The Verdict", value=f"**{verdict}**", inline=False)
        embed.add_field(name="Oracle says:", value=f"_{roast}_", inline=False)
        embed.set_footer(text=f"Streak Reset | XP: {current_xp} | Lvl: {new_level}")
        
        await message.channel.send(embed=embed)
        print("[DEBUG] 6. Message Sent.\n")

    # --- COMMAND: !resist (VICTORY) ---
    elif message.content.startswith('!resist'):
        print(f"\n[DEBUG] Resistance Request from {user_name}")

        # 1. Update Stats
        print("[DEBUG] Updating XP (+50)...")
        new_level, current_xp = db.update_xp(user_id, user_name, 50)
        
        print("[DEBUG] Incrementing Streak...")
        update_streak(user_id, reset=False)
        
        # 2. Get Current Streak
        stats = db.get_user_stats(user_id)
        current_streak = stats['streak']
        
        praise = get_ai_praise(current_streak)

        # 3. Output
        embed = discord.Embed(title="🛡️ RESISTANCE CONFIRMED", color=0x00ff41)
        embed.add_field(name="Status", value=f"**Craving Neutralized.**", inline=False)
        embed.add_field(name="Oracle says:", value=f"_{praise}_", inline=False)
        embed.set_footer(text=f"Streak: {current_streak} 🔥 | XP: +50 | Lvl: {new_level}")

        await message.channel.send(embed=embed)

    # --- COMMAND: !stats (STATUS) ---
    elif message.content.startswith('!stats'):
        print(f"[DEBUG] Stats Request from {user_name}")
        stats = db.get_user_stats(user_id)
        
        embed = discord.Embed(title=f"👤 AGENT: {user_name.upper()}", color=0x0088ff)
        embed.add_field(name="Level", value=str(stats['level']), inline=True)
        embed.add_field(name="XP", value=str(stats['xp']), inline=True)
        embed.add_field(name="Current Streak", value=f"{stats['streak']} 🔥", inline=True)
        
        await message.channel.send(embed=embed)

# 5. Safety Latch
if __name__ == "__main__":
    if TOKEN:
        print("[INIT] Launching Bot...")
        client.run(TOKEN)
    else:
        print("❌ CRITICAL: No DISCORD_TOKEN found.")
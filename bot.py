import os
import random
import discord
from dotenv import load_dotenv
from google import genai
from oracle import ProtocolZero  # Assumes you updated this to V2!
from database_manager import DatabaseManager

# ============================================================================
# CONFIGURATION
# ============================================================================
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GOOGLE_KEY = os.getenv('GEMINI_API_KEY')

# Initialize Clients
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# AI Client (Graceful Degradation)
ai_client = None
if GOOGLE_KEY:
    try:
        ai_client = genai.Client(api_key=GOOGLE_KEY)
        print("✅ [LOKI] AI Connected. The Oracle speaks.")
    except Exception as e:
        print(f"⚠️ [LOKI] AI Silenced: {e}")

# Core Systems
db = DatabaseManager()
# Note: Oracle V2 takes a username, but here we init with a default. 
# We will create per-user instances dynamically if needed, or just use one generic.
oracle = ProtocolZero("Agent") 

# ============================================================================
# HELPER: THE VOICE OF THE GODS (AI)
# ============================================================================
def get_ai_response(prompt_type, context_data):
    """
    Centralized AI Handler.
    prompt_type: 'roast' or 'praise'
    context_data: verdict (for roast) or streak (for praise)
    """
    if not ai_client:
        # Fallbacks for when the AI is sleeping
        if prompt_type == 'roast':
            return random.choice([
                "The Oracle has spoken. Obey.", 
                "Weakness is a choice.", 
                "Do it, or I delete your save file."
            ])
        else:
            return random.choice([
                "Acceptable performance.", 
                "You have survived another day.", 
                "Do not get cocky."
            ])

    try:
        if prompt_type == 'roast':
            prompt = f"You are a cruel, cyberpunk drill sergeant. User failed. Penalty: '{context_data}'. Roast them in one sentence."
        else:
            prompt = f"User resisted a craving. Streak: {context_data}. Give a dark, elite cyberpunk compliment. One sentence."

        response = ai_client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"⚠️ [AI ERROR]: {e}")
        return "The AI is silently judging you."

# ============================================================================
# DISCORD EVENTS
# ============================================================================
@client.event
async def on_ready():
    print(f'⚡ {client.user} IS ONLINE. PROTOCOL ZERO ENGAGED.')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    user_id = str(message.author.id)
    user_name = message.author.name
    
    # ------------------------------------------------------------------
    # COMMAND: !oracle (FAILURE)
    # ------------------------------------------------------------------
    if message.content.startswith('!oracle'):
        # 1. Get User Stats to see if they are a chronic failure
        stats = db.get_user_stats(user_id)
        current_streak = stats.get('streak', 0)
        
        # 2. Consult the Oracle (V2 Logic)
        # We pass the streak so the Oracle can judge severity
        verdict = oracle.consult_oracle(streak=current_streak)
        
        # 3. Log the Shame
        db.log_interaction(user_id, user_name, verdict)
        
        # 4. Reset Streak (The Fall) & Award Pity XP (10)
        # Note: update_xp handles the DB update. 
        # We might need a separate method to RESET streak if update_xp only adds?
        # A simple SQL query is better here for the specific "Reset" action.
        
        conn = db.get_connection()
        cursor = conn.cursor()
        # Reset streak, Add 10 XP
        cursor.execute(f"UPDATE users SET streak = 0, xp = xp + 10 WHERE discord_id = {db.placeholder}", (user_id,))
        conn.commit()
        conn.close()
        
        # 5. Get the Roast
        roast = get_ai_response('roast', verdict)
        
        # 6. Embed of Shame
        embed = discord.Embed(title="⚠️ PROTOCOL ZERO BREACH", color=0xff0000)
        embed.add_field(name="The Verdict", value=f"**{verdict}**", inline=False)
        embed.add_field(name="Oracle says:", value=f"_{roast}_", inline=False)
        embed.set_footer(text="Streak: 0 | Shame Level: Maximum")
        
        await message.channel.send(embed=embed)

    # ------------------------------------------------------------------
    # COMMAND: !resist (VICTORY)
    # ------------------------------------------------------------------
    elif message.content.startswith('!resist'):
        # 1. Attempt Atomic XP Update (Gatekeeper Check included)
        result = db.update_xp(user_id, user_name, 50)
        
        # Handle Spam Rejection
        if result[0] is None:
            # The Gatekeeper has spoken
            await message.channel.send(f"🚫 **{user_name}**, you are spamming. Discipline requires patience.")
            return

        new_level, new_xp = result
        
        # 2. Increment Streak Manually (Since update_xp is generic)
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET streak = streak + 1 WHERE discord_id = {db.placeholder}", (user_id,))
        conn.commit()
        
        # Fetch new streak for display
        cursor.execute(f"SELECT streak FROM users WHERE discord_id = {db.placeholder}", (user_id,))
        current_streak = cursor.fetchone()[0]
        conn.close()

        # 3. Get Praise
        praise = get_ai_response('praise', current_streak)

        # 4. Embed of Glory
        embed = discord.Embed(title="🛡️ RESISTANCE CONFIRMED", color=0x00ff41)
        embed.add_field(name="Status", value="**Craving Neutralized.**", inline=False)
        embed.add_field(name="Oracle says:", value=f"_{praise}_", inline=False)
        embed.set_footer(text=f"Streak: {current_streak} 🔥 | Lvl: {new_level}")

        await message.channel.send(embed=embed)

    # ------------------------------------------------------------------
    # COMMAND: !stats
    # ------------------------------------------------------------------
    elif message.content.startswith('!stats'):
        stats = db.get_user_stats(user_id)
        
        embed = discord.Embed(title=f"👤 AGENT: {user_name.upper()}", color=0x0088ff)
        embed.add_field(name="Level", value=str(stats['level']), inline=True)
        embed.add_field(name="XP", value=str(stats['xp']), inline=True)
        embed.add_field(name="Streak", value=f"{stats['streak']} 🔥", inline=True)
        
        await message.channel.send(embed=embed)

    # ------------------------------------------------------------------
    # COMMAND: !leaderboard
    # ------------------------------------------------------------------
    elif message.content.startswith('!leaderboard'):
        top_agents = db.get_leaderboard()
        
        description = ""
        for i, agent in enumerate(top_agents):
             description += f"**#{i+1}** {agent['username']} — Lvl {agent['level']} ({agent['xp']} XP)\n"
        
        embed = discord.Embed(title="🏆 ELITE AGENTS", description=description, color=0xFFD700)
        await message.channel.send(embed=embed)

# ============================================================================
# EXECUTION
# ============================================================================
if __name__ == "__main__":
    if TOKEN:
        client.run(TOKEN)
    else:
        print("❌ CRITICAL: No DISCORD_TOKEN found. The bot is soulless.")
import os
import random
import discord
from dotenv import load_dotenv
from google import genai
from oracle import ProtocolZero
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
        print("The Oracle speaks.")
    except Exception as e:
        print(f"AI Silenced: {e}")

# Core Systems
db = DatabaseManager()
oracle = ProtocolZero("Agent") 

# ============================================================================
# HELPER: THE VOICE OF THE GODS (AI)
# ============================================================================
def get_ai_response(prompt_type, context_data):
    if not ai_client:
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
        stats = db.get_user_stats(user_id)
        current_streak = stats.get('streak', 0)
        
        verdict = oracle.consult_oracle(streak=current_streak)
        
        # LOKI'S REFACTOR: The One True Function
        new_level, current_xp = db.register_failure(user_id, user_name, verdict)
        
        roast = get_ai_response('roast', verdict)
        
        embed = discord.Embed(title="⚠️ PROTOCOL ZERO BREACH", color=0xff0000)
        embed.add_field(name="The Verdict", value=f"**{verdict}**", inline=False)
        embed.add_field(name="Oracle says:", value=f"_{roast}_", inline=False)
        embed.set_footer(text=f"Streak: 0 | Lvl: {new_level}")
        
        await message.channel.send(embed=embed)

    # ------------------------------------------------------------------
    # COMMAND: !resist (VICTORY)
    # ------------------------------------------------------------------
    elif message.content.startswith('!resist'):
        result = db.update_xp(user_id, user_name, 50)
        
        if result[0] is None:
            await message.channel.send(f"🚫 **{user_name}**, you are spamming. Discipline requires patience.")
            return

        new_level, new_xp = result
        
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET streak = streak + 1 WHERE discord_id = {db.placeholder}", (user_id,))
        conn.commit()
        
        cursor.execute(f"SELECT streak FROM users WHERE discord_id = {db.placeholder}", (user_id,))
        current_streak = cursor.fetchone()[0]
        conn.close()

        praise = get_ai_response('praise', current_streak)

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

if __name__ == "__main__":
    if TOKEN:
        client.run(TOKEN)
    else:
        print("❌ CRITICAL: No DISCORD_TOKEN found. The bot is soulless.")
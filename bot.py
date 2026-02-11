import os
import discord
import random
from dotenv import load_dotenv
from google import genai
from oracle import ProtocolZero, datetime 

# 1. Load the Vault
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GOOGLE_KEY = os.getenv('GEMINI_API_KEY')

# 2. Configure AI (The Roaster)
ai_client = None
if GOOGLE_KEY:
    try:
        ai_client = genai.Client(api_key=GOOGLE_KEY)
        print("✅ AI Connected to Discord Bot")
    except Exception as e:
        print(f"⚠️ AI Config Error: {e}")

# Backup Roasts (If AI fails)
BACKUP_ROASTS = [
    "Even the AI refuses to talk to you right now.",
    "Just do the punishment. Don't cry.",
    "404: Dignity Not Found."
]

# 3. Setup the Client
intents = discord.Intents.default()
intents.message_content = True 
client = discord.Client(intents=intents)

# 4. Initialize The Engine
apocalypse = datetime.date(2027, 1, 1)
engine = ProtocolZero("Commander Ariel", apocalypse)

@client.event
async def on_ready():
    print(f'--- {client.user} IS LISTENING ---')

@client.event
async def on_message(message):
    # Don't let the bot reply to itself
    if message.author == client.user:
        return

    # The Summoning Command
    if message.content.startswith('!oracle'):
        print(f"[LOG] Request received from {message.author}")

        # A. Get the Verdict (The Punishment)
        verdict = engine.consult_oracle()

        # B. Get the Roast (The Insult)
        roast = ""
        if ai_client:
            try:
                # We ask Gemini to be mean
                prompt = f"You are a ruthless, cynical AI drill sergeant. The user just failed a willpower check and was sentenced to: '{verdict}'. Write a brutal, one-sentence roast. Do not be polite."
                response = ai_client.models.generate_content(
                    model='gemini-2.5-flash-lite',  # <--- Make sure this matches your working model ID
                    contents=prompt
                )
                roast = response.text.strip()
            except Exception as e:
                print(f"AI Failure: {e}")
                roast = random.choice(BACKUP_ROASTS)
        else:
            roast = random.choice(BACKUP_ROASTS)

        # C. Deliver the Pain
        embed = discord.Embed(title="⚠️ PROTOCOL ZERO BREACH", color=0xff0000)
        embed.add_field(name="The Verdict", value=f"**{verdict}**", inline=False)
        embed.add_field(name="The Oracle says:", value=f"_{roast}_", inline=False)
        
        await message.channel.send(embed=embed)

# 5. THE SAFETY LATCH (Crucial for Cloud Fusion)
if __name__ == "__main__":
    if TOKEN:
        client.run(TOKEN)
    else:
        print("❌ CRITICAL: No DISCORD_TOKEN found.")
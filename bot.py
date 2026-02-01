import os
import discord
from dotenv import load_dotenv
from oracle import ProtocolZero, datetime # Importing the Brain

# 1. Load the Vault
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 2. Setup the Client (The Bot's Ears)
intents = discord.Intents.default()
intents.message_content = True # Crucial: Allows bot to read the chat
client = discord.Client(intents=intents)

# 3. Initialize The Engine
# We set the target date here again for the bot.
apocalypse = datetime.date(2027, 1, 1)
engine = ProtocolZero("Commander Ariel", apocalypse)

@client.event
async def on_ready():
	print(f'--- {client.user} HAS RISEN ---')
	print('The Oracle is listening...')

@client.event
async def on_message(message):
	# Don't let the bot reply to itself (infinite loop of stupidity)
	if message.author == client.user:
		return

	# The Summoning Command
	if message.content.startswith('!oracle'):
		print(f"[LOG] Request received from {message.author}")

		# Consult the Engine
		verdict = engine.consult_oracle()

		# Speak to the Server
		await message.channel.send(f"**The Oracle Speaks:**\n{verdict}")

# 4. IGNITION
client.run(TOKEN)
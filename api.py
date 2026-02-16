import os           # Allows us to interact with the operating system (e.g., read environment variables)
import datetime     # Tools for working with dates and times
import random       # Generates random selections
import json         # Handles JSON data (converting Python objects to JSON format)
import asyncio      # Enables asynchronous programming (running tasks concurrently)

# Custom modules (files in the same project)
from bot import client as discord_bot              # Imports the Discord bot client
from oracle import ProtocolZero                    # Imports our Oracle class
from database_manager import DatabaseManager       # Imports our database handler

# Third-party web framework and tools
from fastapi import FastAPI                        # The main web framework for building APIs
from fastapi.responses import HTMLResponse         # Allows us to return HTML content
from dotenv import load_dotenv                     # Loads environment variables from a .env file
from google import genai                           # Google's Gemini AI library

# ==============================================================
# STEP 1: Load Secret Keys from Environment Variables
# ==============================================================
load_dotenv()
GOOGLE_KEY = os.getenv("GEMINI_API_KEY")

# ==============================================================
# STEP 2: Configure the AI Client (Google Gemini)
# ==============================================================
client = None
if GOOGLE_KEY:
    try:
        client = genai.Client(api_key=GOOGLE_KEY)
    except Exception as e:
        print(f"AI Config Error: {e}")
else:
    print("WARNING: No Gemini Key found. Using backup roasts.")

# ==============================================================
# STEP 3: Initialize the Web Application and Database
# ==============================================================
app = FastAPI()
db = DatabaseManager()

# ==============================================================
# STEP 4: Background Task - Start Discord Bot (CONDITIONAL)
# ==============================================================
@app.on_event("startup")
async def start_discord_bot():
    """
    Starts the Discord bot in the background.
    
    CRITICAL FIX FOR RATE LIMITS:
    We check if a special env var 'DISABLE_BOT' is set.
    If you are testing the website locally, set DISABLE_BOT=True in your .env
    so you don't spam Discord connections.
    """
    discord_token = os.getenv("DISCORD_TOKEN")
    disable_bot = os.getenv("DISABLE_BOT") # <--- NEW CHECK

    if disable_bot == "True":
        print("🛑 [CONFIG] Discord Bot is DISABLED locally (Safe Mode).")
        return

    if discord_token:
        print("🤖 Oracle is connecting to Discord...")
        asyncio.create_task(discord_bot.start(discord_token))
    else:
        print("⚠️ Warning: No DISCORD_TOKEN found. Bot will not start.")

# ==============================================================
# STEP 5: Backup Roasts
# ==============================================================
BACKUP_ROASTS = [
    "The AI is offline, but you are still weak.",
    "Even the servers are disappointed in you.",
    "Just do the reps, human."
]

# ==============================================================
# API ENDPOINTS (Routes)
# ==============================================================

@app.get("/", methods=["GET", "HEAD"])
def read_root():
    return {"status": "Protocol Zero API is Online"}

@app.get("/stats")
def get_stats():
    return {"total_punishments_served": db.get_total_count()}

@app.get("/history")
def get_history():
    return {"recent_punishments": db.get_recent_history(limit=5)}

@app.get("/leaderboard")
def get_leaderboard():
    return {"leaderboard": db.get_leaderboard()}

# ==============================================================
# THE FIX IS HERE: /summon
# ==============================================================
@app.post("/summon")
def summon_oracle():
    """
    Generates a punishment, logs it to DB, and returns it.
    """
    # 1. Define the Web User
    # We use a generic name for web users for now
    web_user_id = "WEB_USER_01"
    web_user_name = "Web_Agent"
    
    # 2. Summon the Oracle (V2 Syntax)
    # OLD & BROKEN: engine = ProtocolZero(web_user_name, apocalypse)
    # NEW & SHINY: Just the name. The Oracle knows what to do.
    engine = ProtocolZero(web_user_name) 
    
    # 3. Consult the Oracle
    # We pass streak=0 because web users are anonymous and have no shame (yet).
    verdict = engine.consult_oracle(streak=0)
    
    # 4. Generate AI Roast
    roast = ""
    if client:
        try:
            # Centralized prompt logic could go here, but this works for now.
            prompt = f"You are a ruthless, cynical AI drill sergeant. The user just failed a willpower check and was sentenced to: '{verdict}'. Write a brutal, one-sentence roast. Do not be polite."
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=prompt
            )
            roast = response.text.strip()
        except Exception as e:
            print(f"AI Failure: {e}")
            roast = random.choice(BACKUP_ROASTS)
    else:
        roast = random.choice(BACKUP_ROASTS)
    
    # 5. SAVE TO DATABASE
    try:
        # A. Log the interaction
        db.log_interaction(web_user_id, web_user_name, verdict)
        
        # B. Update XP (Pity XP for the weak)
        # Note: We aren't handling streaks on web yet, just XP/History
        db.update_xp(web_user_id, web_user_name, 10)
        
        print(f"✅ [WEB] Saved interaction for {web_user_name}")
    except Exception as e:
        print(f"❌ [WEB] Database Error: {e}")

    return {"verdict": verdict, "roast": roast}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    # 1. Gather Data
    count = db.get_total_count()
    history = db.get_recent_history(limit=5)
    leaderboard = db.get_leaderboard()  # Fetch the top 5 users
    distribution = db.get_verdict_counts()
    hourly_stats = db.get_hourly_activity()
    
    # 2. Prepare Charts
    donut_labels = list(distribution.keys())
    donut_values = list(distribution.values())
    bar_labels = [f"{i:02d}:00" for i in range(24)]
    
    # 3. Build History Table HTML
    history_html = ""
    for row in history:
        history_html += f"<tr><td>{row['time']}</td><td>{row['user']}</td><td style='color: #ff3333;'>{row['verdict']}</td></tr>"

    # 4. Build Leaderboard Table HTML
    leaderboard_html = ""
    for i, row in enumerate(leaderboard):
        # i+1 gives us Rank #1 instead of #0
        leaderboard_html += f"<tr><td>#{i+1}</td><td>{row['username']}</td><td>Lvl {row['level']}</td><td>{row['xp']} XP</td></tr>"

    # 5. The Frontend Interface
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Protocol Zero // Pocket</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ background-color: #050505; color: #00ff41; font-family: 'Courier New', monospace; display: flex; flex-direction: column; align-items: center; padding: 10px; margin: 0; overflow-x: hidden; }}
            .scanlines {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,0) 50%, rgba(0,0,0,0.2) 50%, rgba(0,0,0,0.2)); background-size: 100% 4px; pointer-events: none; z-index: 999; opacity: 0.6; }}
            .container {{ text-align: center; border: 1px solid #00ff41; padding: 20px; width: 100%; max-width: 800px; background: #000; box-shadow: 0 0 15px #00ff41; box-sizing: border-box; }}
            h1 {{ font-size: 2rem; margin: 10px 0; letter-spacing: 2px; }}
            .counter {{ font-size: 4rem; font-weight: bold; margin: 10px 0; text-shadow: 0 0 10px #00ff41; }}
            .ball-container {{ display: flex; justify-content: center; margin-top: 20px; perspective: 1000px; }}
            .magic-8-ball {{ width: 140px; height: 140px; background: radial-gradient(circle at 30% 30%, #444, #000); border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 5px 20px rgba(0,0,0,0.8); transition: transform 0.1s; -webkit-tap-highlight-color: transparent; }}
            .face-8 {{ font-size: 60px; font-family: sans-serif; color: black; background: white; border-radius: 50%; width: 70px; height: 70px; display: flex; align-items: center; justify-content: center; }}
            @keyframes shake {{ 0% {{ transform: translate(1px, 1px) rotate(0deg); }} 10% {{ transform: translate(-1px, -2px) rotate(-1deg); }} 20% {{ transform: translate(-3px, 0px) rotate(1deg); }} 30% {{ transform: translate(3px, 2px) rotate(0deg); }} 40% {{ transform: translate(1px, -1px) rotate(1deg); }} 50% {{ transform: translate(-1px, 2px) rotate(-1deg); }} 60% {{ transform: translate(-3px, 1px) rotate(0deg); }} 70% {{ transform: translate(3px, 1px) rotate(-1deg); }} 80% {{ transform: translate(-1px, -1px) rotate(1deg); }} 90% {{ transform: translate(1px, 2px) rotate(0deg); }} 100% {{ transform: translate(1px, -2px) rotate(-1deg); }} }}
            .shaking {{ animation: shake 0.5s; animation-iteration-count: infinite; }}
            #verdict-box {{ margin: 20px 0; padding: 15px; border: 2px dashed #ff3333; background-color: #1a0505; color: #ff3333; font-size: 1.5rem; font-weight: bold; text-transform: uppercase; display: none; animation: flicker 1.5s infinite alternate; }}
            .roast-text {{ display: block; margin-top: 10px; font-size: 1rem; color: #fff; font-style: italic; opacity: 0.8; text-transform: none; }}
            @keyframes flicker {{ 0% {{ opacity: 0.8; box-shadow: 0 0 10px #ff3333; }} 100% {{ opacity: 1; box-shadow: 0 0 25px #ff3333; }} }}
            .charts-wrapper {{ display: flex; flex-wrap: wrap; justify-content: space-between; gap: 20px; margin: 20px 0; }}
            .chart-box {{ width: 48%; height: 250px; position: relative; }}
            @media (max-width: 600px) {{ .chart-box {{ width: 100%; height: 200px; }} h1 {{ font-size: 1.5rem; }} .counter {{ font-size: 3rem; }} table {{ font-size: 10px; }} }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px; border-top: 1px solid #00ff41; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #333; }}
            h3 {{ border-bottom: 1px solid #00ff41; padding-bottom: 5px; margin-bottom: 5px; }}
        </style>
    </head>
    <body>
        <div class="scanlines"></div>
        <div class="container">
            <h1>PROTOCOL ZERO</h1>
            <div class="counter">{count}</div>
            <div class="ball-container"><div class="magic-8-ball" onclick="shakeBall()"><div class="face-8">8</div></div></div>
            <div id="verdict-box"><span id="verdict-text"></span><span id="roast-text" class="roast-text"></span></div>
            
            <div class="charts-wrapper">
                <div class="chart-box"><canvas id="donutChart"></canvas></div>
                <div class="chart-box"><canvas id="barChart"></canvas></div>
            </div>

            <div style="display: flex; gap: 20px; flex-wrap: wrap; width: 100%; justify-content: center; margin-top: 20px;">
                <div style="flex: 1; min-width: 300px;">
                    <h3>RECENT ACTIVITY</h3>
                    <table><tr><th>Time</th><th>Agent</th><th>Verdict</th></tr>{history_html}</table>
                </div>
                <div style="flex: 1; min-width: 300px;">
                    <h3>TOP AGENTS</h3>
                    <table><tr><th>Rank</th><th>Agent</th><th>Level</th><th>XP</th></tr>{leaderboard_html}</table>
                </div>
            </div>

        </div>
        <script>
            function speak(text) {{ window.speechSynthesis.cancel(); const utterance = new SpeechSynthesisUtterance(text); utterance.pitch = 0.8; utterance.rate = 0.9; window.speechSynthesis.speak(utterance); }}
            async function shakeBall() {{
                const ball = document.querySelector('.magic-8-ball');
                const box = document.getElementById('verdict-box');
                const vText = document.getElementById('verdict-text');
                const rText = document.getElementById('roast-text');
                box.style.display = 'none';
                ball.classList.add('shaking');
                const response = await fetch('/summon', {{ method: 'POST' }});
                const data = await response.json();
                setTimeout(() => {{
                    ball.classList.remove('shaking');
                    vText.innerText = data.verdict;
                    rText.innerText = '"' + data.roast + '"';
                    box.style.display = 'block';
                    speak(data.verdict + ". " + data.roast);
                    setTimeout(() => {{ location.reload(); }}, 6000);
                }}, 1000);
            }}
            new Chart(document.getElementById('donutChart'), {{ type: 'doughnut', data: {{ labels: {json.dumps(donut_labels)}, datasets: [{{ data: {json.dumps(donut_values)}, backgroundColor: ['#ff3333', '#00ff41', '#0088ff', '#ffaa00', '#aa00ff'], borderColor: '#0d0d0d', borderWidth: 2 }}] }}, options: {{ plugins: {{ legend: {{ display: false }} }}, maintainAspectRatio: false }} }});
            new Chart(document.getElementById('barChart'), {{ type: 'bar', data: {{ labels: {json.dumps(bar_labels)}, datasets: [{{ label: 'Failures', data: {json.dumps(hourly_stats)}, backgroundColor: '#00ff41', borderColor: '#00ff41', borderWidth: 1 }}] }}, options: {{ scales: {{ x: {{ ticks: {{ color: '#00ff41' }}, grid: {{ color: '#333' }} }}, y: {{ ticks: {{ color: '#00ff41' }}, grid: {{ color: '#333' }} }} }}, plugins: {{ legend: {{ display: false }} }}, maintainAspectRatio: false }} }});
        </script>
    </body>
    </html>
    """
    return html_content
    
# ==============================================================
# THE RED BUTTON (Database Reset)
# ==============================================================
"""
@app.get("/nuke_protocol_zero")
def nuke_database():
    
    WARNING: This endpoint deletes the entire database and rebuilds it.
    Visit this URL once to fix the 'column does not exist' error.
    
    print("☢️ NUKING DATABASE...")
    try:
        # 1. Get a direct connection
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # 2. Drop the old broken tables
        cursor.execute("DROP TABLE IF EXISTS interactions;")
        cursor.execute("DROP TABLE IF EXISTS users;")
        
        conn.commit()
        conn.close()
        print("✅ Old tables destroyed.")
        
        # 3. Rebuild them with the new schema
        db.initialize_db()
        print("🏗️ New tables created.")
        
        return {"status": "SUCCESS. Database was nuked and rebuilt. You may now use the app."}
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}
"""
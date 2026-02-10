from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from database_manager import DatabaseManager
import json
import datetime
from oracle import ProtocolZero
import random

# --- THE INSULT LIBRARY ---
ROASTS = [
    "Do it, or remain weak forever.",
    "Your ancestors are watching, and they are disappointed.",
    "Pain is just weakness leaving the body.",
    "I bet you can't even finish this set.",
    "You promised yourself you would be better.",
    "Ariel, focus. Do not fail me.",
    "If you quit now, you have learned nothing.",
    "Execute the protocol, human.",
    "Suffering is the currency of growth. Pay up."
]

app = FastAPI()
db = DatabaseManager()

@app.get("/")
def read_root():
    return {"status": "Protocol Zero API is Online", "god": "Loki"}

@app.get("/stats")
def get_stats():
    return {"total_punishments_served": db.get_total_count()}

@app.get("/history")
def get_history():
    return {"recent_punishments": db.get_recent_history(limit=5)}

# --- THE NEW TRIGGER ---
@app.post("/summon")
def summon_oracle():
    """Calculates a punishment, logs it, and adds a roast."""
    # 1. Initialize Engine
    apocalypse = datetime.date(2027, 1, 1)
    engine = ProtocolZero("Ariel_Web", apocalypse)
    
    # 2. Get Verdict
    verdict = engine.consult_oracle()
    
    # 3. Pick a Roast
    insult = random.choice(ROASTS)
    
    # 4. Return both
    return {"verdict": verdict, "roast": insult}

# --- THE UPGRADED DASHBOARD ---
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    count = db.get_total_count()
    history = db.get_recent_history(limit=5)
    distribution = db.get_verdict_counts()
    hourly_stats = db.get_hourly_activity()
    
    donut_labels = list(distribution.keys())
    donut_values = list(distribution.values())
    bar_labels = [f"{i:02d}:00" for i in range(24)] 
    
    history_html = ""
    for row in history:
        history_html += f"<tr><td>{row['time']}</td><td>{row['user']}</td><td style='color: #ff3333;'>{row['verdict']}</td></tr>"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Protocol Zero // Pocket</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ 
                background-color: #050505; 
                color: #00ff41; 
                font-family: 'Courier New', monospace; 
                display: flex; 
                flex-direction: column; 
                align-items: center; 
                padding: 10px; 
                margin: 0;
                overflow-x: hidden; /* Prevent scrollbar from scanlines */
            }}

            /* --- THE CRT EFFECT --- */
            .scanlines {{
                position: fixed;
                top: 0; left: 0; width: 100%; height: 100%;
                background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,0) 50%, rgba(0,0,0,0.2) 50%, rgba(0,0,0,0.2));
                background-size: 100% 4px;
                pointer-events: none; /* Let clicks pass through */
                z-index: 999;
                opacity: 0.6;
            }}
            
            .container {{ 
                text-align: center; 
                border: 1px solid #00ff41; 
                padding: 20px; 
                width: 100%; 
                max-width: 800px; /* Responsive Cap */
                background: #000; 
                box-shadow: 0 0 15px #00ff41; 
                box-sizing: border-box; /* Padding doesn't break width */
            }}
            
            h1 {{ font-size: 2rem; margin: 10px 0; letter-spacing: 2px; }}
            .counter {{ font-size: 4rem; font-weight: bold; margin: 10px 0; text-shadow: 0 0 10px #00ff41; }}
            
            /* ORB */
            .ball-container {{ display: flex; justify-content: center; margin-top: 20px; perspective: 1000px; }}
            .magic-8-ball {{ width: 140px; height: 140px; background: radial-gradient(circle at 30% 30%, #444, #000); border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 5px 20px rgba(0,0,0,0.8); transition: transform 0.1s; -webkit-tap-highlight-color: transparent; }}
            .face-8 {{ font-size: 60px; font-family: sans-serif; color: black; background: white; border-radius: 50%; width: 70px; height: 70px; display: flex; align-items: center; justify-content: center; }}
            
            /* ANIMATIONS */
            @keyframes shake {{ 0% {{ transform: translate(1px, 1px) rotate(0deg); }} 10% {{ transform: translate(-1px, -2px) rotate(-1deg); }} 20% {{ transform: translate(-3px, 0px) rotate(1deg); }} 30% {{ transform: translate(3px, 2px) rotate(0deg); }} 40% {{ transform: translate(1px, -1px) rotate(1deg); }} 50% {{ transform: translate(-1px, 2px) rotate(-1deg); }} 60% {{ transform: translate(-3px, 1px) rotate(0deg); }} 70% {{ transform: translate(3px, 1px) rotate(-1deg); }} 80% {{ transform: translate(-1px, -1px) rotate(1deg); }} 90% {{ transform: translate(1px, 2px) rotate(0deg); }} 100% {{ transform: translate(1px, -2px) rotate(-1deg); }} }}
            .shaking {{ animation: shake 0.5s; animation-iteration-count: infinite; }}

            /* VERDICT BOX */
            #verdict-box {{ margin: 20px 0; padding: 15px; border: 2px dashed #ff3333; background-color: #1a0505; color: #ff3333; font-size: 1.5rem; font-weight: bold; text-transform: uppercase; display: none; animation: flicker 1.5s infinite alternate; }}
            .roast-text {{ display: block; margin-top: 10px; font-size: 1rem; color: #fff; font-style: italic; opacity: 0.8; text-transform: none; }}
            @keyframes flicker {{ 0% {{ opacity: 0.8; box-shadow: 0 0 10px #ff3333; }} 100% {{ opacity: 1; box-shadow: 0 0 25px #ff3333; }} }}

            /* RESPONSIVE CHARTS */
            .charts-wrapper {{ 
                display: flex; 
                flex-wrap: wrap; /* Allow stacking */
                justify-content: space-between; 
                gap: 20px; 
                margin: 20px 0; 
            }}
            .chart-box {{ 
                width: 48%; 
                height: 250px; 
                position: relative; 
            }}
            
            /* MOBILE OVERRIDE */
            @media (max-width: 600px) {{
                .chart-box {{ width: 100%; height: 200px; }} /* Stack full width on phone */
                h1 {{ font-size: 1.5rem; }}
                .counter {{ font-size: 3rem; }}
                table {{ font-size: 10px; }}
            }}

            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 12px; border-top: 1px solid #00ff41; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #333; }}
        </style>
    </head>
    <body>
        <div class="scanlines"></div> <div class="container">
            <h1>PROTOCOL ZERO</h1>
            <div class="counter">{count}</div>
            
            <div class="ball-container">
                <div class="magic-8-ball" onclick="shakeBall()">
                    <div class="face-8">8</div>
                </div>
            </div>

            <div id="verdict-box">
                <span id="verdict-text"></span>
                <span id="roast-text" class="roast-text"></span>
            </div>

            <div class="charts-wrapper">
                <div class="chart-box"><canvas id="donutChart"></canvas></div>
                <div class="chart-box"><canvas id="barChart"></canvas></div>
            </div>
            
            <table>
                <tr><th>Time</th><th>Subject</th><th>Verdict</th></tr>
                {history_html}
            </table>
        </div>

        <script>
            // --- THE VOICE ---
            function speak(text) {{
                window.speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.pitch = 0.8; 
                utterance.rate = 0.9;
                window.speechSynthesis.speak(utterance);
            }}

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

            // Charts
            new Chart(document.getElementById('donutChart'), {{
                type: 'doughnut',
                data: {{ labels: {json.dumps(donut_labels)}, datasets: [{{ data: {json.dumps(donut_values)}, backgroundColor: ['#ff3333', '#00ff41', '#0088ff', '#ffaa00', '#aa00ff'], borderColor: '#0d0d0d', borderWidth: 2 }}] }},
                options: {{ plugins: {{ legend: {{ display: false }} }}, maintainAspectRatio: false }}
            }});

            new Chart(document.getElementById('barChart'), {{
                type: 'bar',
                data: {{ labels: {json.dumps(bar_labels)}, datasets: [{{ label: 'Failures', data: {json.dumps(hourly_stats)}, backgroundColor: '#00ff41', borderColor: '#00ff41', borderWidth: 1 }}] }},
                options: {{ scales: {{ x: {{ ticks: {{ color: '#00ff41' }}, grid: {{ color: '#333' }} }}, y: {{ ticks: {{ color: '#00ff41' }}, grid: {{ color: '#333' }} }} }}, plugins: {{ legend: {{ display: false }} }}, maintainAspectRatio: false }}
            }});
        </script>
    </body>
    </html>
    """
    return html_content
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from database_manager import DatabaseManager
import json
import datetime
from oracle import ProtocolZero

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
    """Calculates a punishment and logs it."""
    # 1. Initialize the Engine (Just like in the terminal)
    apocalypse = datetime.date(2027, 1, 1)
    engine = ProtocolZero("Ariel_Web", apocalypse)
    
    # 2. Pull the Trigger
    # Note: consult_oracle() already talks to the DB, so we just call it.
    result = engine.consult_oracle()
    
    # 3. Return the verdict to the browser
    return {"verdict": result}

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
        <title>Protocol Zero // Oracle</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ background-color: #0d0d0d; color: #00ff41; font-family: 'Courier New', monospace; display: flex; flex-direction: column; align-items: center; padding: 20px; }}
            .container {{ text-align: center; border: 2px solid #00ff41; padding: 30px; width: 800px; background: #000; box-shadow: 0 0 20px #00ff41; }}
            .counter {{ font-size: 60px; font-weight: bold; margin: 10px 0; }}
            
            /* --- THE MAGIC 8-BALL --- */
            .ball-container {{ display: flex; justify-content: center; margin-top: 20px; perspective: 1000px; }}
            
            .magic-8-ball {{
                width: 150px;
                height: 150px;
                background: radial-gradient(circle at 30% 30%, #444, #000);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                box-shadow: 0 10px 30px rgba(0,0,0,0.8), inset 0 0 20px rgba(255,255,255,0.1);
                transition: transform 0.1s;
            }}

            .face-8 {{
                font-size: 80px;
                font-family: sans-serif;
                color: black;
                background: white;
                border-radius: 50%;
                width: 80px;
                height: 80px;
                display: flex;
                align-items: center;
                justify-content: center;
            }}

            /* --- THE VERDICT BOX (Hidden by default) --- */
            #verdict-box {{
                margin-top: 30px;
                margin-bottom: 20px;
                padding: 20px;
                border: 2px dashed #ff3333;
                background-color: #1a0505;
                color: #ff3333;
                font-size: 24px;
                font-weight: bold;
                text-transform: uppercase;
                display: none; /* Hidden until shaken */
                box-shadow: 0 0 15px #ff3333;
                animation: flicker 1.5s infinite alternate;
            }}

            @keyframes flicker {{
                0% {{ opacity: 0.8; box-shadow: 0 0 10px #ff3333; }}
                100% {{ opacity: 1; box-shadow: 0 0 25px #ff3333; }}
            }}

            @keyframes shake {{
                0% {{ transform: translate(1px, 1px) rotate(0deg); }}
                10% {{ transform: translate(-1px, -2px) rotate(-1deg); }}
                20% {{ transform: translate(-3px, 0px) rotate(1deg); }}
                30% {{ transform: translate(3px, 2px) rotate(0deg); }}
                40% {{ transform: translate(1px, -1px) rotate(1deg); }}
                50% {{ transform: translate(-1px, 2px) rotate(-1deg); }}
                60% {{ transform: translate(-3px, 1px) rotate(0deg); }}
                70% {{ transform: translate(3px, 1px) rotate(-1deg); }}
                80% {{ transform: translate(-1px, -1px) rotate(1deg); }}
                90% {{ transform: translate(1px, 2px) rotate(0deg); }}
                100% {{ transform: translate(1px, -2px) rotate(-1deg); }}
            }}
            .shaking {{ animation: shake 0.5s; animation-iteration-count: infinite; }}

            /* Layout */
            .charts-wrapper {{ display: flex; justify-content: space-between; gap: 20px; margin: 20px 0; height: 250px; }}
            .chart-box {{ width: 48%; position: relative; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 12px; border-top: 1px solid #00ff41; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #333; }}

        </style>
    </head>
    <body>
        <div class="container">
            <h1>PROTOCOL ZERO</h1>
            <div class="counter">{count}</div>
            
            <div class="ball-container">
                <div class="magic-8-ball" onclick="shakeBall()">
                    <div class="face-8">8</div>
                </div>
            </div>

            <div id="verdict-box"></div>

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
            async function shakeBall() {{
                const ball = document.querySelector('.magic-8-ball');
                const box = document.getElementById('verdict-box');
                
                // 1. Reset
                box.style.display = 'none';
                
                // 2. Shake
                ball.classList.add('shaking');
                
                // 3. Fetch
                const response = await fetch('/summon', {{ method: 'POST' }});
                const data = await response.json();
                
                // 4. Reveal
                setTimeout(() => {{
                    ball.classList.remove('shaking');
                    
                    // Show the box with the text
                    box.innerText = data.verdict;
                    box.style.display = 'block';
                    
                    // Wait 4 seconds to read, then reload
                    setTimeout(() => {{ location.reload(); }}, 4000);
                    
                }}, 1000);
            }}

            // Charts
            new Chart(document.getElementById('donutChart'), {{
                type: 'doughnut',
                data: {{
                    labels: {json.dumps(donut_labels)}, 
                    datasets: [{{ data: {json.dumps(donut_values)}, backgroundColor: ['#ff3333', '#00ff41', '#0088ff', '#ffaa00', '#aa00ff'], borderColor: '#0d0d0d', borderWidth: 2 }}]
                }},
                options: {{ plugins: {{ legend: {{ display: false }} }}, maintainAspectRatio: false }}
            }});

            new Chart(document.getElementById('barChart'), {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(bar_labels)},
                    datasets: [{{ label: 'Failures', data: {json.dumps(hourly_stats)}, backgroundColor: '#00ff41', borderColor: '#00ff41', borderWidth: 1 }}]
                }},
                options: {{ 
                    scales: {{ x: {{ ticks: {{ color: '#00ff41' }}, grid: {{ color: '#333' }} }}, y: {{ ticks: {{ color: '#00ff41' }}, grid: {{ color: '#333' }} }} }},
                    plugins: {{ legend: {{ display: false }} }},
                    maintainAspectRatio: false
                }}
            }});
        </script>
    </body>
    </html>
    """
    return html_content
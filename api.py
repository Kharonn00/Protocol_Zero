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
    
    labels = list(distribution.keys())
    values = list(distribution.values())
    
    history_html = ""
    for row in history:
        history_html += f"<tr><td>{row['time']}</td><td>{row['user']}</td><td style='color: #ff3333;'>{row['verdict']}</td></tr>"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Protocol Zero // Command</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ background-color: #0d0d0d; color: #00ff41; font-family: 'Courier New', monospace; display: flex; flex-direction: column; align-items: center; padding: 20px; }}
            .container {{ text-align: center; border: 2px solid #00ff41; padding: 30px; width: 700px; background: #000; box-shadow: 0 0 20px #00ff41; }}
            .counter {{ font-size: 60px; font-weight: bold; margin: 10px 0; }}
            .chart-container {{ position: relative; height: 200px; width: 100%; margin: 20px 0; display: flex; justify-content: center; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 12px; border-top: 1px solid #00ff41; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #333; }}
            
            /* THE RED BUTTON */
            .btn-summon {{
                background-color: #ff3333;
                color: #000;
                border: none;
                padding: 15px 30px;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Courier New', monospace;
                cursor: pointer;
                margin-top: 20px;
                box-shadow: 0 0 10px #ff3333;
                transition: 0.2s;
            }}
            .btn-summon:hover {{ background-color: #ff0000; box-shadow: 0 0 20px #ff0000; transform: scale(1.05); }}
            .btn-summon:active {{ transform: scale(0.95); }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>PROTOCOL ZERO</h1>
            <div class="counter">{count}</div>
            
            <button class="btn-summon" onclick="summonOracle()">SUMMON ORACLE</button>

            <div class="chart-container"><canvas id="painChart"></canvas></div>
            
            <table>
                <tr><th>Time</th><th>Subject</th><th>Verdict</th></tr>
                {history_html}
            </table>
        </div>

        <script>
            // 1. The Chart Logic
            new Chart(document.getElementById('painChart'), {{
                type: 'doughnut',
                data: {{
                    labels: {json.dumps(labels)}, 
                    datasets: [{{ label: 'Punishments', data: {json.dumps(values)}, backgroundColor: ['#ff3333', '#00ff41', '#0088ff', '#ffaa00', '#aa00ff'], borderColor: '#0d0d0d', borderWidth: 2 }}]
                }},
                options: {{ plugins: {{ legend: {{ position: 'right', labels: {{ color: '#00ff41', font: {{ family: 'Courier New' }} }} }} }} }}
            }});

            // 2. The Button Logic
            async function summonOracle() {{
                const btn = document.querySelector('.btn-summon');
                btn.innerText = "CALCULATING...";
                
                // Call the API
                const response = await fetch('/summon', {{ method: 'POST' }});
                const data = await response.json();
                
                // Show Verdict
                alert(data.verdict);
                
                // Reload page to see new stats
                location.reload();
            }}
        </script>
    </body>
    </html>
    """
    return html_content
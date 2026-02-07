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
    # 1. Fetch Data
    count = db.get_total_count()
    history = db.get_recent_history(limit=5)
    distribution = db.get_verdict_counts()
    hourly_stats = db.get_hourly_activity() # <--- NEW DATA
    
    # Data Prep for Charts
    donut_labels = list(distribution.keys())
    donut_values = list(distribution.values())
    
    # Hours 00 through 23 for the Bar Chart labels
    bar_labels = [f"{i:02d}:00" for i in range(24)] 
    
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
            .container {{ text-align: center; border: 2px solid #00ff41; padding: 30px; width: 800px; background: #000; box-shadow: 0 0 20px #00ff41; }}
            .counter {{ font-size: 60px; font-weight: bold; margin: 10px 0; }}
            
            /* Grid for 2 Charts */
            .charts-wrapper {{ display: flex; justify-content: space-between; gap: 20px; margin: 20px 0; height: 250px; }}
            .chart-box {{ width: 48%; position: relative; }}
            
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 12px; border-top: 1px solid #00ff41; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #333; }}
            
            .btn-summon {{ background-color: #ff3333; color: #000; border: none; padding: 15px 30px; font-size: 18px; font-weight: bold; cursor: pointer; margin-top: 20px; transition: 0.2s; }}
            .btn-summon:hover {{ background-color: #ff0000; box-shadow: 0 0 20px #ff0000; transform: scale(1.05); }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>PROTOCOL ZERO</h1>
            <div class="counter">{count}</div>
            
            <button class="btn-summon" onclick="summonOracle()">SUMMON ORACLE</button>

            <div class="charts-wrapper">
                <div class="chart-box">
                    <canvas id="donutChart"></canvas>
                </div>
                <div class="chart-box">
                    <canvas id="barChart"></canvas>
                </div>
            </div>
            
            <table>
                <tr><th>Time</th><th>Subject</th><th>Verdict</th></tr>
                {history_html}
            </table>
        </div>

        <script>
            // 1. Donut Chart (Punishment Types)
            new Chart(document.getElementById('donutChart'), {{
                type: 'doughnut',
                data: {{
                    labels: {json.dumps(donut_labels)}, 
                    datasets: [{{ 
                        data: {json.dumps(donut_values)}, 
                        backgroundColor: ['#ff3333', '#00ff41', '#0088ff', '#ffaa00', '#aa00ff'], 
                        borderColor: '#0d0d0d', borderWidth: 2 
                    }}]
                }},
                options: {{ plugins: {{ legend: {{ display: false }} }}, maintainAspectRatio: false }}
            }});

            // 2. Bar Chart (Hourly Weakness)
            new Chart(document.getElementById('barChart'), {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(bar_labels)},
                    datasets: [{{
                        label: 'Failures by Hour',
                        data: {json.dumps(hourly_stats)},
                        backgroundColor: '#00ff41',
                        borderColor: '#00ff41',
                        borderWidth: 1
                    }}]
                }},
                options: {{ 
                    scales: {{ 
                        x: {{ ticks: {{ color: '#00ff41' }}, grid: {{ color: '#333' }} }},
                        y: {{ ticks: {{ color: '#00ff41' }}, grid: {{ color: '#333' }} }}
                    }},
                    plugins: {{ legend: {{ display: false }} }},
                    maintainAspectRatio: false
                }}
            }});

            // 3. Summon Logic
            async function summonOracle() {{
                const btn = document.querySelector('.btn-summon');
                btn.innerText = "CALCULATING...";
                await fetch('/summon', {{ method: 'POST' }});
                location.reload();
            }}
        </script>
    </body>
    </html>
    """
    return html_content
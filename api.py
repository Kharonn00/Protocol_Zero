from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from database_manager import DatabaseManager
import json

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

# --- THE UPGRADED DASHBOARD ---
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    # 1. Fetch Data
    count = db.get_total_count()
    history = db.get_recent_history(limit=5)
    distribution = db.get_verdict_counts() # <--- NEW DATA
    
    # 2. Prepare Data for JavaScript (Convert to JSON strings)
    labels = list(distribution.keys())
    values = list(distribution.values())
    
    # 3. Build History Rows
    history_html = ""
    for row in history:
        history_html += f"""
        <tr>
            <td>{row['time']}</td>
            <td>{row['user']}</td>
            <td style="color: #ff3333;">{row['verdict']}</td>
        </tr>
        """

    # 4. The HTML + Chart.js Magic
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Protocol Zero // War Room</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{
                background-color: #0d0d0d;
                color: #00ff41;
                font-family: 'Courier New', Courier, monospace;
                display: flex;
                flex-direction: column;
                align-items: center;
                height: 100vh;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                text-align: center;
                border: 2px solid #00ff41;
                padding: 30px;
                box-shadow: 0 0 20px #00ff41;
                width: 700px;
                background: #000;
            }}
            h1 {{ letter-spacing: 5px; margin-bottom: 5px; }}
            .counter {{ font-size: 60px; font-weight: bold; text-shadow: 0 0 10px #00ff41; margin: 10px 0; }}
            
            /* Graph Container */
            .chart-container {{
                position: relative;
                height: 250px;
                width: 100%;
                margin: 20px 0;
                display: flex;
                justify-content: center;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                font-size: 12px;
                border-top: 1px solid #00ff41;
            }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #333; }}
            th {{ color: #fff; text-transform: uppercase; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>PROTOCOL ZERO</h1>
            <div style="opacity: 0.7; font-size: 12px;">STOCHASTIC BEHAVIOR MODIFICATION</div>
            
            <div class="counter">{count}</div>
            <div>INTERVENTIONS DEPLOYED</div>

            <div class="chart-container">
                <canvas id="painChart"></canvas>
            </div>
            
            <table>
                <tr>
                    <th>Time</th>
                    <th>Subject</th>
                    <th>Verdict</th>
                </tr>
                {history_html}
            </table>
        </div>

        <script>
            // The JavaScript that draws the chart
            const ctx = document.getElementById('painChart').getContext('2d');
            new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: {json.dumps(labels)}, 
                    datasets: [{{
                        label: 'Punishments',
                        data: {json.dumps(values)},
                        backgroundColor: [
                            '#ff3333', // Red
                            '#00ff41', // Green
                            '#0088ff', // Blue
                            '#ffaa00', // Orange
                            '#aa00ff'  // Purple
                        ],
                        borderColor: '#0d0d0d',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'right',
                            labels: {{ color: '#00ff41', font: {{ family: 'Courier New' }} }}
                        }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    return html_content
from fastapi import FastAPI
from fastapi.responses import HTMLResponse # <--- NEW WEAPON
from database_manager import DatabaseManager

app = FastAPI()
db = DatabaseManager()

@app.get("/")
def read_root():
    return {"status": "Protocol Zero API is Online", "god": "Loki"}

@app.get("/stats")
def get_stats():
    count = db.get_total_count()
    return {"total_punishments_served": count}

@app.get("/history")
def get_history():
    """Returns the last 5 punishments served."""
    recent_logs = db.get_recent_history(limit=5)
    return {"recent_punishments": recent_logs}

# --- THE NEW DASHBOARD ---
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    # 1. Get the Data
    count = db.get_total_count()
    history = db.get_recent_history(limit=5)
    
    # 2. Build the History Rows (HTML Loop)
    history_html = ""
    for row in history:
        history_html += f"""
        <tr>
            <td>{row['time']}</td>
            <td>{row['user']}</td>
            <td style="color: #ff3333;">{row['verdict']}</td>
        </tr>
        """

    # 3. The HTML Template (With Table)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Protocol Zero // Dashboard</title>
        <style>
            body {{
                background-color: #0d0d0d;
                color: #00ff41;
                font-family: 'Courier New', Courier, monospace;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }}
            .container {{
                text-align: center;
                border: 2px solid #00ff41;
                padding: 40px;
                box-shadow: 0 0 20px #00ff41;
                width: 600px;
            }}
            h1 {{ letter-spacing: 5px; margin-bottom: 10px; }}
            .counter {{ font-size: 80px; font-weight: bold; text-shadow: 0 0 10px #00ff41; margin: 20px 0; }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                font-size: 14px;
                border-top: 1px solid #00ff41;
            }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #333; }}
            th {{ color: #fff; text-transform: uppercase; }}
            tr:hover {{ background-color: #1a1a1a; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>PROTOCOL ZERO</h1>
            <div>TOTAL INTERVENTIONS</div>
            <div class="counter">{count}</div>
            
            <table>
                <tr>
                    <th>Time</th>
                    <th>Subject</th>
                    <th>Verdict</th>
                </tr>
                {history_html}
            </table>
        </div>
    </body>
    </html>
    """
    return html_content
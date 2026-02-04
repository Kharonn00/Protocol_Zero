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
    # 1. Get the data
    count = db.get_total_count()
    
    # 2. The HTML Template (Dark Mode, Cyberpunk Style)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Protocol Zero // Dashboard</title>
        <style>
            body {{
                background-color: #0d0d0d;
                color: #00ff41; /* Hacker Green */
                font-family: 'Courier New', Courier, monospace;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }}
            .container {{
                text-align: center;
                border: 2px solid #00ff41;
                padding: 50px;
                box-shadow: 0 0 20px #00ff41;
            }}
            h1 {{
                font-size: 24px;
                text-transform: uppercase;
                letter-spacing: 5px;
                margin-bottom: 20px;
            }}
            .counter {{
                font-size: 120px;
                font-weight: bold;
                text-shadow: 0 0 10px #00ff41;
            }}
            .footer {{
                margin-top: 20px;
                font-size: 14px;
                opacity: 0.7;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Protocol Zero // Punishment Log</h1>
            <div class="counter">{count}</div>
            <div class="footer">INTERVENTIONS DEPLOYED</div>
        </div>
    </body>
    </html>
    """
    return html_content
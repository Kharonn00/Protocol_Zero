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
# load_dotenv() reads a .env file and makes its contents available as environment variables
# This keeps sensitive information (like API keys) out of the code
load_dotenv()

# os.getenv() retrieves the value of an environment variable
# If the variable doesn't exist, it returns None
GOOGLE_KEY = os.getenv("GEMINI_API_KEY")

# ==============================================================
# STEP 2: Configure the AI Client (Google Gemini)
# ==============================================================
# We start with client = None (no AI configured)
client = None

# Only try to configure the AI if we found an API key
if GOOGLE_KEY:
    try:
        # Attempt to create a Gemini AI client with the API key
        client = genai.Client(api_key=GOOGLE_KEY)
    except Exception as e:
        # If something goes wrong, print the error
        # The program continues running with client = None
        print(f"AI Config Error: {e}")
else:
    # If no API key was found, print a warning
    # The app will use backup roasts instead of AI-generated ones
    print("WARNING: No Gemini Key found. Using backup roasts.")

# ==============================================================
# STEP 3: Initialize the Web Application and Database
# ==============================================================
# FastAPI() creates a new web application instance
# This object will handle all our web routes (URLs)
app = FastAPI()

# DatabaseManager() creates an instance of our database handler
# This will track punishment history, stats, etc.
db = DatabaseManager()

# ==============================================================
# STEP 4: Background Task - Start Discord Bot
# ==============================================================
@app.on_event("startup")
async def start_discord_bot():
    """
    This function runs automatically when the FastAPI server starts up.
    It launches the Discord bot in the background.
    
    The @app.on_event("startup") decorator tells FastAPI to run this
    when the application starts.
    
    'async def' means this is an asynchronous function - it can run
    alongside other tasks without blocking them.
    """
    # Get the Discord bot token from environment variables
    discord_token = os.getenv("DISCORD_TOKEN")
    
    # Only start the bot if we found a token
    if discord_token:
        print("🤖 Oracle is connecting to Discord...")
        
        # asyncio.create_task() runs the bot in the background
        # This allows the web server to continue running while the bot operates
        # Without create_task, the bot would block the entire application
        asyncio.create_task(discord_bot.start(discord_token))
    else:
        # If no token found, print a warning but continue running the web app
        print("⚠️ Warning: No DISCORD_TOKEN found. Bot will not start.")

# ==============================================================
# STEP 5: Backup Roasts (Fallback Messages)
# ==============================================================
# This list stores pre-written insults to use when the AI is unavailable
# It's a safety net in case the Gemini API fails or isn't configured
BACKUP_ROASTS = [
    "The AI is offline, but you are still weak.",
    "Even the servers are disappointed in you.",
    "Just do the reps, human."
]

# ==============================================================
# API ENDPOINTS (Routes)
# ==============================================================
# These are the different URLs users can visit to interact with the app
# Each @app.get() or @app.post() decorator creates a new route

@app.get("/")
def read_root():
    """
    The root endpoint (homepage of the API).
    When someone visits http://yourserver.com/ they get this response.
    
    @app.get() means this responds to GET requests (standard browser visits)
    The "/" means this is the root path
    
    Returns:
        dict: A simple JSON object confirming the API is running
    """
    return {"status": "Protocol Zero API is Online"}

@app.get("/stats")
def get_stats():
    """
    Returns overall statistics about punishments served.
    Access at: http://yourserver.com/stats
    
    Returns:
        dict: JSON object with total punishment count
    """
    # db.get_total_count() queries the database for the total number of punishments
    return {"total_punishments_served": db.get_total_count()}

@app.get("/history")
def get_history():
    """
    Returns recent punishment history.
    Access at: http://yourserver.com/history
    
    Returns:
        dict: JSON object with the 5 most recent punishments
    """
    # db.get_recent_history(limit=5) gets the last 5 punishment records
    return {"recent_punishments": db.get_recent_history(limit=5)}

@app.post("/summon")
def summon_oracle():
    """
    The main punishment endpoint - generates a random punishment and AI roast.
    This uses POST (not GET) because it creates/changes data in the database.
    Access by sending a POST request to: http://yourserver.com/summon
    
    Returns:
        dict: JSON with the punishment verdict and AI-generated roast
    """
    # ==============================================================
    # PART 1: Generate the Punishment
    # ==============================================================
    # Set a target date (the "apocalypse" - could be any goal date)
    apocalypse = datetime.date(2027, 1, 1)
    
    # Create an instance of our Oracle class
    # "Ariel_Web" is the username, apocalypse is the target date
    engine = ProtocolZero("Ariel_Web", apocalypse)
    
    # Call the oracle to get a random punishment
    verdict = engine.consult_oracle()
    
    # ==============================================================
    # PART 2: Generate the AI Roast
    # ==============================================================
    # Start with an empty roast
    roast = ""
    
    # Check if we have a working AI client
    if client:
        try:
            # Create a prompt telling the AI how to behave
            # The AI will be given the punishment and asked to write a harsh motivational message
            prompt = f"You are a ruthless, cynical AI drill sergeant from a cyberpunk future. The user just failed a willpower check and was sentenced to: '{verdict}'. Write a brutal, one-sentence roast to motivate them. Do not be polite."
            
            # Send the prompt to the Gemini AI model
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite',  # The specific AI model to use
                contents=prompt                  # Our instruction text
            )
            
            # Extract the text response and remove extra whitespace
            roast = response.text.strip()
            
        except Exception as e:
            # If the AI fails for any reason, print the error
            print(f"AI Failure: {e}")
            # Fall back to using a random backup roast
            roast = random.choice(BACKUP_ROASTS)
    else:
        # If we don't have an AI client, use a backup roast
        roast = random.choice(BACKUP_ROASTS)
    
    # ==============================================================
    # PART 3: Return the Results
    # ==============================================================
    # Return both the punishment and the roast as a JSON object
    return {"verdict": verdict, "roast": roast}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    """
    Generates an interactive HTML dashboard with stats and visualizations.
    This is a full web page, not just JSON data.
    Access at: http://yourserver.com/dashboard
    
    response_class=HTMLResponse tells FastAPI we're returning HTML, not JSON
    
    Returns:
        str: Complete HTML page with embedded JavaScript and CSS
    """
    # ==============================================================
    # STEP 1: Gather Data from Database
    # ==============================================================
    # Get total count of all punishments
    count = db.get_total_count()
    
    # Get the 5 most recent punishment records
    history = db.get_recent_history(limit=5)
    
    # Get counts of how many times each punishment type has been given
    distribution = db.get_verdict_counts()
    
    # Get activity breakdown by hour of day (0-23)
    hourly_stats = db.get_hourly_activity()
    
    # ==============================================================
    # STEP 2: Prepare Data for Charts
    # ==============================================================
    # Convert distribution dictionary into separate lists for chart labels and values
    # Example: {"Push-ups": 5, "Squats": 3} → labels=["Push-ups", "Squats"], values=[5, 3]
    donut_labels = list(distribution.keys())
    donut_values = list(distribution.values())
    
    # Create labels for bar chart (00:00, 01:00, ..., 23:00)
    # f"{i:02d}:00" formats the number with leading zeros (e.g., 01, 02, 03)
    bar_labels = [f"{i:02d}:00" for i in range(24)]
    
    # ==============================================================
    # STEP 3: Build HTML Table for Recent History
    # ==============================================================
    # Start with an empty string
    history_html = ""
    
    # Loop through each punishment record and create table rows
    for row in history:
        # Each row contains time, user, and verdict
        # The verdict is styled in red (#ff3333)
        history_html += f"<tr><td>{row['time']}</td><td>{row['user']}</td><td style='color: #ff3333;'>{row['verdict']}</td></tr>"

    # ==============================================================
    # STEP 4: Create the Complete HTML Page
    # ==============================================================
    # This is a multi-line string (f-string) containing the entire HTML page
    # {variables} are replaced with actual values from Python
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Protocol Zero // Pocket</title>
        <!-- Make the page responsive on mobile devices -->
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        
        <!-- Import Chart.js library for creating graphs -->
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        
        <style>
            /* ============================================== */
            /* CSS STYLES - Controls how the page looks */
            /* ============================================== */
            
            /* Body: Dark background with green "hacker" text */
            body {{ 
                background-color: #050505;          /* Nearly black background */
                color: #00ff41;                      /* Bright green text (Matrix style) */
                font-family: 'Courier New', monospace; /* Monospace font for retro feel */
                display: flex;                       /* Use flexbox for layout */
                flex-direction: column;              /* Stack elements vertically */
                align-items: center;                 /* Center horizontally */
                padding: 10px; 
                margin: 0;
                overflow-x: hidden;                  /* Prevent horizontal scrolling */
            }}
            
            /* Scanlines: Creates a retro CRT monitor effect */
            .scanlines {{
                position: fixed;                     /* Stay in place when scrolling */
                top: 0; left: 0; 
                width: 100%; 
                height: 100%;
                /* Creates alternating transparent and dark lines */
                background: linear-gradient(to bottom, 
                    rgba(255,255,255,0), 
                    rgba(255,255,255,0) 50%, 
                    rgba(0,0,0,0.2) 50%, 
                    rgba(0,0,0,0.2));
                background-size: 100% 4px;           /* 4px tall scanlines */
                pointer-events: none;                /* Allow clicks to pass through */
                z-index: 999;                        /* Display above other elements */
                opacity: 0.6;
            }}
            
            /* Main container: Holds all content */
            .container {{ 
                text-align: center; 
                border: 1px solid #00ff41;           /* Green border */
                padding: 20px; 
                width: 100%; 
                max-width: 800px;                    /* Don't get too wide on large screens */
                background: #000;                    /* Solid black background */
                box-shadow: 0 0 15px #00ff41;        /* Glowing green shadow */
                box-sizing: border-box; 
            }}
            
            /* Main heading */
            h1 {{ 
                font-size: 2rem; 
                margin: 10px 0; 
                letter-spacing: 2px;                 /* Space out letters for effect */
            }}
            
            /* Large counter display */
            .counter {{ 
                font-size: 4rem; 
                font-weight: bold; 
                margin: 10px 0; 
                text-shadow: 0 0 10px #00ff41;       /* Glowing text effect */
            }}
            
            /* Container for the magic 8-ball */
            .ball-container {{ 
                display: flex; 
                justify-content: center; 
                margin-top: 20px; 
                perspective: 1000px;                 /* Enables 3D transforms */
            }}
            
            /* The magic 8-ball itself */
            .magic-8-ball {{ 
                width: 140px; 
                height: 140px; 
                /* Creates a spherical gradient (light at top-left, dark at bottom-right) */
                background: radial-gradient(circle at 30% 30%, #444, #000); 
                border-radius: 50%;                  /* Makes it circular */
                display: flex; 
                align-items: center; 
                justify-content: center; 
                cursor: pointer;                     /* Show it's clickable */
                box-shadow: 0 5px 20px rgba(0,0,0,0.8); 
                transition: transform 0.1s;          /* Smooth transform animations */
                -webkit-tap-highlight-color: transparent; /* Remove blue highlight on mobile */
            }}
            
            /* The "8" in the center of the ball */
            .face-8 {{ 
                font-size: 60px; 
                font-family: sans-serif; 
                color: black; 
                background: white; 
                border-radius: 50%;                  /* Circular background */
                width: 70px; 
                height: 70px; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
            }}
            
            /* Shake animation keyframes - defines how the shake looks at each step */
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
            
            /* Apply the shake animation */
            .shaking {{ 
                animation: shake 0.5s;               /* 0.5 second duration */
                animation-iteration-count: infinite;  /* Loop forever */
            }}

            /* Verdict display box (hidden by default) */
            #verdict-box {{ 
                margin: 20px 0; 
                padding: 15px; 
                border: 2px dashed #ff3333;          /* Red dashed border */
                background-color: #1a0505;           /* Dark red background */
                color: #ff3333;                      /* Red text */
                font-size: 1.5rem; 
                font-weight: bold; 
                text-transform: uppercase; 
                display: none;                       /* Hidden until JavaScript shows it */
                animation: flicker 1.5s infinite alternate; /* Flickering effect */
            }}
            
            /* The AI roast text */
            .roast-text {{ 
                display: block; 
                margin-top: 10px; 
                font-size: 1rem; 
                color: #fff; 
                font-style: italic; 
                opacity: 0.8; 
                text-transform: none;                /* Don't uppercase the roast */
            }}
            
            /* Flicker animation for dramatic effect */
            @keyframes flicker {{ 
                0% {{ opacity: 0.8; box-shadow: 0 0 10px #ff3333; }} 
                100% {{ opacity: 1; box-shadow: 0 0 25px #ff3333; }} 
            }}

            /* Container for charts - displays side by side */
            .charts-wrapper {{ 
                display: flex; 
                flex-wrap: wrap;                     /* Wrap on small screens */
                justify-content: space-between; 
                gap: 20px; 
                margin: 20px 0; 
            }}
            
            /* Individual chart boxes */
            .chart-box {{ 
                width: 48%;                          /* Two charts side by side */
                height: 250px; 
                position: relative; 
            }}
            
            /* Mobile responsive styles - activate on screens smaller than 600px */
            @media (max-width: 600px) {{
                .chart-box {{ 
                    width: 100%;                     /* Stack charts vertically on mobile */
                    height: 200px; 
                }}
                h1 {{ font-size: 1.5rem; }}
                .counter {{ font-size: 3rem; }}
                table {{ font-size: 10px; }}
            }}

            /* Table styles */
            table {{ 
                width: 100%; 
                border-collapse: collapse;           /* Remove gaps between cells */
                margin-top: 20px; 
                font-size: 12px; 
                border-top: 1px solid #00ff41; 
            }}
            
            /* Table cells */
            th, td {{ 
                padding: 8px; 
                text-align: left; 
                border-bottom: 1px solid #333; 
            }}
        </style>
    </head>
    <body>
        <!-- The scanline overlay effect -->
        <div class="scanlines"></div>
        
        <!-- Main content container -->
        <div class="container">
            <!-- Title -->
            <h1>PROTOCOL ZERO</h1>
            
            <!-- Total punishment counter (filled in from Python) -->
            <div class="counter">{count}</div>
            
            <!-- The clickable magic 8-ball -->
            <div class="ball-container">
                <div class="magic-8-ball" onclick="shakeBall()">
                    <div class="face-8">8</div>
                </div>
            </div>

            <!-- Verdict box (hidden initially, shown by JavaScript) -->
            <div id="verdict-box">
                <span id="verdict-text"></span>
                <span id="roast-text" class="roast-text"></span>
            </div>

            <!-- Charts container -->
            <div class="charts-wrapper">
                <!-- Donut chart showing punishment distribution -->
                <div class="chart-box"><canvas id="donutChart"></canvas></div>
                <!-- Bar chart showing activity by hour -->
                <div class="chart-box"><canvas id="barChart"></canvas></div>
            </div>
            
            <!-- Recent history table -->
            <table>
                <tr><th>Time</th><th>Subject</th><th>Verdict</th></tr>
                {history_html}
            </table>
        </div>

        <script>
            /* ============================================== */
            /* JAVASCRIPT - Makes the page interactive */
            /* ============================================== */
            
            /**
             * Text-to-speech function
             * Uses the browser's built-in speech synthesis API
             */
            function speak(text) {{
                // Cancel any ongoing speech
                window.speechSynthesis.cancel();
                
                // Create a new speech utterance (thing to say)
                const utterance = new SpeechSynthesisUtterance(text);
                
                // Adjust voice characteristics
                utterance.pitch = 0.8;  // Slightly lower pitch (more ominous)
                utterance.rate = 0.9;   // Slightly slower speech
                
                // Speak the text
                window.speechSynthesis.speak(utterance);
            }}

            /**
             * Main function - called when user clicks the magic 8-ball
             * Makes an async request to get a punishment and displays it
             */
            async function shakeBall() {{
                // Get references to HTML elements we need to manipulate
                const ball = document.querySelector('.magic-8-ball');
                const box = document.getElementById('verdict-box');
                const vText = document.getElementById('verdict-text');
                const rText = document.getElementById('roast-text');
                
                // Hide the verdict box (in case it's visible from a previous click)
                box.style.display = 'none';
                
                // Start the shaking animation
                ball.classList.add('shaking');
                
                // Make an asynchronous POST request to the /summon endpoint
                // await means "wait for this to complete before continuing"
                const response = await fetch('/summon', {{ method: 'POST' }});
                
                // Parse the JSON response
                const data = await response.json();
                
                // After 1 second (1000 milliseconds), display the results
                setTimeout(() => {{
                    // Stop the shaking animation
                    ball.classList.remove('shaking');
                    
                    // Fill in the verdict text
                    vText.innerText = data.verdict;
                    
                    // Fill in the roast text (with quotes around it)
                    rText.innerText = '"' + data.roast + '"';
                    
                    // Show the verdict box
                    box.style.display = 'block';
                    
                    // Speak the verdict and roast out loud
                    speak(data.verdict + ". " + data.roast);
                    
                    // After 6 seconds, reload the page (to update stats)
                    setTimeout(() => {{ location.reload(); }}, 6000);
                }}, 1000);
            }}

            /* ============================================== */
            /* CHART CREATION - Using Chart.js library */
            /* ============================================== */
            
            /**
             * Donut Chart - Shows distribution of punishment types
             * The data comes from Python via json.dumps()
             */
            new Chart(document.getElementById('donutChart'), {{
                type: 'doughnut',  // Donut/pie chart
                data: {{ 
                    labels: {json.dumps(donut_labels)},  // Punishment names
                    datasets: [{{ 
                        data: {json.dumps(donut_values)},  // How many times each occurred
                        // Color scheme for different segments
                        backgroundColor: ['#ff3333', '#00ff41', '#0088ff', '#ffaa00', '#aa00ff'], 
                        borderColor: '#0d0d0d',  // Dark borders between segments
                        borderWidth: 2 
                    }}] 
                }},
                options: {{ 
                    plugins: {{ 
                        legend: {{ display: false }}  // Hide the legend
                    }}, 
                    maintainAspectRatio: false  // Allow custom sizing
                }}
            }});

            /**
             * Bar Chart - Shows activity by hour of day
             * X-axis: Hours (00:00 - 23:00)
             * Y-axis: Number of punishments
             */
            new Chart(document.getElementById('barChart'), {{
                type: 'bar',  // Vertical bar chart
                data: {{ 
                    labels: {json.dumps(bar_labels)},  // Hour labels
                    datasets: [{{ 
                        label: 'Failures',  // Dataset label
                        data: {json.dumps(hourly_stats)},  // Punishment counts by hour
                        backgroundColor: '#00ff41',  // Green bars
                        borderColor: '#00ff41', 
                        borderWidth: 1 
                    }}] 
                }},
                options: {{ 
                    scales: {{ 
                        x: {{ 
                            ticks: {{ color: '#00ff41' }},  // Green text
                            grid: {{ color: '#333' }}  // Dark gray grid lines
                        }}, 
                        y: {{ 
                            ticks: {{ color: '#00ff41' }}, 
                            grid: {{ color: '#333' }} 
                        }} 
                    }}, 
                    plugins: {{ 
                        legend: {{ display: false }}  // Hide legend
                    }}, 
                    maintainAspectRatio: false 
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    # Return the complete HTML page
    return html_content
# Protocol Zero: Stochastic Behavioral Modification Engine

> *"Chaos is the only cure for habit."*

## 📜 Overview
**Protocol Zero** is a Python-based utility designed to disrupt dopamine-driven feedback loops (specifically nicotine dependency) via stochastic intervention.

Built with an **Object-Oriented Architecture**, this engine treats "Willpower" not as a feeling, but as a computable class. It outsources executive decision-making to a pseudo-random number generator, introducing friction and gamified penalties to break the "Trigger-Action-Reward" cycle.

## ⚡ Features
* **OOP Architecture:** Modular `ProtocolZero` class design for scalability and easy integration.
* **Discord Bot Interface:** Remote access to the Oracle via a dedicated Discord bot. Users can summon judgment with `!oracle` from any server.
* **Cyberpunk Command Center:** A **FastAPI**-powered dashboard featuring:
    * **Real-time Statistics:** Live counter of total interventions.
    * **Data Visualization:** A **Chart.js** Donut Chart showing punishment distribution.
    * **Interactive Control:** A "SUMMON" button to trigger the Oracle directly from the browser.
* **Enterprise-Grade Storage:** Implements a **SQLite Database** (`protocol_zero.db`) for robust data persistence.
* **Stochastic Decision Logic:** Randomly assigns tasks (physical or mental) to derail cravings.
* **Adaptive Injury Protocol:** Dynamically detects physical handicaps (e.g., `hand_is_broken = True`) and reroutes physical penalties.
* **The Singularity Timer:** Calculates the precise `timedelta` remaining until the estimated arrival of AGI (2027).

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Kharonn00/Protocol_Zero.git](https://github.com/Kharonn00/Protocol_Zero.git)
    ```
2.  **Navigate to the directory:**
    ```bash
    cd Protocol_Zero
    ```
3.  **Install Dependencies:**
    ```bash
    pip install discord.py python-dotenv fastapi uvicorn
    ```

## ⚙️ Configuration (The Vault)

To run the Discord Bot, you must configure your environment variables.

1.  Create a file named `.env` in the root directory.
2.  Add your Discord Bot Token inside:
    ```env
    DISCORD_TOKEN=your_token_goes_here_no_quotes
    ```
    *(Note: The `.env` file is git-ignored to protect your secrets.)*

## 🎮 Usage

### Option A: Terminal Mode (Local)
Run the engine directly in your command prompt:
```bash
python oracle.py

```

### Option B: Discord Bot Mode (Remote)

Bring the bot online to listen for commands in your server:

```bash
python bot.py

```

### Option C: Web Command Center (Visual)

Launch the FastAPI server to control the engine from your browser:

```bash
uvicorn api:app --reload

```

* **Dashboard:** Open `http://127.0.0.1:8000/dashboard`
* *Click the Red **SUMMON ORACLE** Button to generate a verdict.*


* **Raw Stats:** Open `http://127.0.0.1:8000/stats`
* **Raw History:** Open `http://127.0.0.1:8000/history`

## 🗄️ The Archives (Data Persistence)

Protocol Zero utilizes a **SQLite Backend** (`protocol_zero.db`).

* **Legacy Mode:** Text file logging has been deprecated.
* **Current Mode:** Every verdict is stored as a structured row in the `interactions` table.
* **Privacy Protocol:** The `.db` file is strictly **git-ignored** to prevent binary bloat and secure personal logs locally.

## 🧠 The Philosophy

This tool relies on the **"Friction Theory"** of habit breaking. By inserting a coding challenge or a physical exercise between the "Urge" and the "Action," Protocol Zero forces the brain to disengage from the craving loop.

## 🚀 Future Roadmap

* **Cloud Deployment:** Migrate the bot from local hosting to a 24/7 Virtual Private Server (VPS).
* **Multi-User Support:** Scale the database schema to track progress for multiple users in a single server.
* **AI Shaming:** Integrate a local LLM to generate unique, context-aware insults based on the user's failure rate.

---

*Built by [Kharonn00](https://github.com/Kharonn00). Powered by Python, Spite, and a 2027 Deadline.*

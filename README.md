# Protocol Zero: Stochastic Behavioral Modification Engine

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge&logo=render&logoColor=white)](https://protocol-zero.onrender.com/dashboard)
[![Storage](https://img.shields.io/badge/Storage-PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://neon.tech)
[![System](https://img.shields.io/badge/System-RPG_Mode-purple?style=for-the-badge)](https://discord.com)

> *"Chaos is the only cure for habit."*

## 📜 Overview
**Protocol Zero** is a Python-based utility designed to disrupt dopamine-driven feedback loops (specifically nicotine/THC dependency) via stochastic intervention.

Built with an **Object-Oriented Architecture**, this engine treats "Willpower" not as a fleeting emotion, but as a computable class. It outsources executive decision-making to a pseudo-random number generator, introducing friction and gamified penalties to break the "Trigger-Action-Reward" cycle.

## ⚡ Core Features
* **Hybrid Cloud Architecture:**
    * **Local:** Runs on lightweight **SQLite** for rapid development.
    * **Cloud:** Automatically switches to **PostgreSQL (Neon)** for immortal data persistence in production.
* **Unified Process Management:** The **FastAPI** server and **Discord Bot** are fused into a single asynchronous event loop.
* **DRY Business Logic:** Centralized database routing ensures web endpoints and Discord commands share a single, uncorrupted source of truth.
* **RPG Progression System:**
    * **XP & Leveling:** Gain XP for honesty (`!oracle`) and massive XP for resistance (`!resist`).
    * **Atomic Transactions & Anti-Spam:** Database row-locking and timestamp-based cooldowns prevent users from "spamming" the resist command to farm XP. You cannot cheat the system.
    * **Streak Tracking:** The engine tracks consecutive victories. One failure shatters the streak to zero.
    * **Live Leaderboard:** Real-time ranking of the Top 5 Agents based on Level and XP.
* **The Oracle V2 (Dynamic Judgement):**
    * **Tiered Punishments:** The system reads your current failure streak and assigns physical or mental tasks from dynamically weighted severity tiers.
    * **AI-Powered Roasts:** Connects to **Google Gemini** to generate context-aware, cyberpunk-themed insults or grudging praise based on your willpower checks.
* **Cyberpunk Command Center:** A **FastAPI**-powered web dashboard featuring:
    * **The Mystic 8-Ball:** An animated, interactive orb to summon punishments on the web.
    * **Split-View Analytics:** Side-by-side tables of recent server failures and the Elite Leaderboard.
    * **Activity Graphs:** Uses `Chart.js` to visualize punishment distributions and hourly failure rates.

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
    pip install -r requirements.txt
    ```

## ⚙️ Configuration (The Vault)

To run the full stack locally, securely configure your `.env` file. Do not commit this file to version control.

1.  Create a file named `.env` in the root directory.
2.  Add your API tokens:
    ```env
    DISCORD_TOKEN=your_discord_token_here
    GEMINI_API_KEY=your_google_ai_key_here
    
    # SAFE MODE (Optional)
    # Set to True to work on the FastAPI dashboard without connecting the Discord Bot.
    # Prevents rate limit bans during rapid local reloading.
    DISABLE_BOT=True 
    
    # CLOUD DB (Optional)
    # Add DATABASE_URL to connect to Cloud PostgreSQL locally
    # DATABASE_URL=postgresql://...
    ```

## 🎮 Usage

### Option A: The Cloud (Global Access)
The Oracle and the Discord Bot are live and fused.
* **Dashboard:** [Launch Protocol Zero](https://protocol-zero.onrender.com/dashboard)
* **Discord Commands:**
    * `!oracle` -> **Failure.** You felt the urge and gave in. The bot assigns a tiered punishment, resets your streak, and awards pity XP.
    * `!resist` -> **Victory.** You felt the urge but said NO. The bot praises you, increments your streak, and awards massive XP.
    * `!stats` -> **Status.** Displays your current Level, Total XP, and Active Streak.
    * `!leaderboard` -> **Elite.** Displays the Top 5 Agents in the server.

### Option B: Local Development
Launch the stack locally on your machine.

```bash
uvicorn api:app --reload

```

* **Dashboard:** `http://127.0.0.1:8000/dashboard`
* *Note: If `DISABLE_BOT=True`, the Discord commands are silenced, but the Dashboard remains fully functional.*

## 🗄️ The Archives (Data Persistence)

Protocol Zero utilizes a **Bilingual Database Manager**:

* **Cloud Mode (Render/Heroku):** Detects `DATABASE_URL` and connects to **Neon PostgreSQL**.
* **Local Mode (Laptop):** Defaults to **SQLite** (`protocol_zero.db`) for isolated testing.
* **Universal Adapter:** The system automatically swaps SQL syntax (`?` vs `%s`) based on the active environment, making deployments seamless.

## 🧠 The Philosophy

This tool relies on the **"Friction Theory"** of habit breaking. By inserting a coding challenge, mental block, or physical exercise between the "Urge" and the "Action," Protocol Zero forces the brain to disengage from the automatic craving loop.

## 🚀 Future Roadmap

* **Boss Battles:** Special events where multiple users must resist together to defeat a "Server Boss."
* **Achievements:** Unlockable badges for hitting milestones (e.g., "7 Day Streak", "Level 10").
* **Visual Graphs:** Line charts tracking XP growth over time.

---

*Built by [Kharonn00](https://github.com/Kharonn00). Powered by Python, Spite, and the pursuit of mastery.*

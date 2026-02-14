# Protocol Zero: Stochastic Behavioral Modification Engine

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge&logo=render&logoColor=white)](https://protocol-zero.onrender.com/dashboard)
[![Storage](https://img.shields.io/badge/Storage-PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://neon.tech)
[![System](https://img.shields.io/badge/System-RPG_Mode-purple?style=for-the-badge)](https://discord.com)

> *"Chaos is the only cure for habit."*

## 📜 Overview
**Protocol Zero** is a Python-based utility designed to disrupt dopamine-driven feedback loops (specifically nicotine/THC dependency) via stochastic intervention.

Built with an **Object-Oriented Architecture**, this engine treats "Willpower" not as a feeling, but as a computable class. It outsources executive decision-making to a pseudo-random number generator, introducing friction and gamified penalties to break the "Trigger-Action-Reward" cycle.

## ⚡ Features
* **Hybrid Cloud Architecture:**
    * **Local:** Runs on lightweight **SQLite**.
    * **Cloud:** Automatically switches to **PostgreSQL (Neon)** for immortal data persistence.
* **Unified Process Management:** The **FastAPI** server and **Discord Bot** are fused into a single asynchronous event loop.
* **RPG Progression System:**
    * **XP & Leveling:** Gain XP for honesty (`!oracle`) and massive XP for resistance (`!resist`).
    * **Streak Tracking:** The engine tracks your consecutive victories. One failure resets the counter to zero.
    * **Live Leaderboard:** Real-time ranking of the Top 5 Agents based on Level and XP.
* **Discord Bot Interface:**
    * **AI-Powered Roasts:** Connects to **Google Gemini** to generate context-aware insults or grudging praise.
    * **Stochastic Judgement:** Randomly assigns physical or mental tasks to derail cravings.
* **Cyberpunk Command Center:** A **FastAPI**-powered dashboard featuring:
    * **The Mystic 8-Ball:** An animated orb that shakes to reveal your fate.
    * **Split-View Analytics:** Side-by-side view of recent failures and the server Leaderboard.
    * **The Voice of Judgment:** Browser-native **Text-to-Speech (TTS)**.

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

To run the full stack locally, configure your `.env` file.

1.  Create a file named `.env` in the root directory.
2.  Add your Tokens inside:
    ```env
    DISCORD_TOKEN=your_discord_token_here
    GEMINI_API_KEY=your_google_ai_key_here
    
    # SAFE MODE (Optional)
    # Set to True if you want to work on the website without connecting to Discord
    # This prevents Rate Limit bans during development.
    DISABLE_BOT=True 
    
    # CLOUD DB (Optional)
    # Add DATABASE_URL if connecting to Cloud DB locally
    # DATABASE_URL=postgresql://...
    ```

## 🎮 Usage

### Option A: The Cloud (Global Access)
The Oracle and the Discord Bot are live and fused.
* **Dashboard:** [Launch Protocol Zero](https://protocol-zero.onrender.com/dashboard)
* **Discord Commands:**
    * `!oracle` -> **Failure.** You felt the urge and gave in. The bot assigns a punishment, resets your streak, and awards pity XP.
    * `!resist` -> **Victory.** You felt the urge but said NO. The bot praises you, increments your streak, and awards massive XP.
    * `!stats` -> **Status.** Displays your current Level, Total XP, and Active Streak.
    * `!leaderboard` -> **Elite.** Displays the Top 5 Agents in the server.

### Option B: Local Development
Launch the stack on your machine.

```bash
uvicorn api:app --reload

```

* **Dashboard:** `http://127.0.0.1:8000/dashboard`
* *Note: If `DISABLE_BOT=True`, the Discord commands will not work, but the Dashboard will be fully functional.*

## 🗄️ The Archives (Data Persistence)

Protocol Zero utilizes a **Bilingual Database Manager**:

* **Cloud Mode (Render):** Detects `DATABASE_URL` and connects to **Neon PostgreSQL**.
* **Local Mode (Laptop):** Defaults to **SQLite** (`protocol_zero.db`) for easy testing.
* **Universal Adapter:** The system automatically swaps SQL syntax (`?` vs `%s`) based on the environment.

## 🧠 The Philosophy

This tool relies on the **"Friction Theory"** of habit breaking. By inserting a coding challenge or a physical exercise between the "Urge" and the "Action," Protocol Zero forces the brain to disengage from the craving loop.

## 🚀 Future Roadmap

* **Boss Battles:** Special events where multiple users must resist together to defeat a "Server Boss."
* **Achievements:** Badges for hitting milestones (e.g., "7 Day Streak", "Level 10").
* **Visual Graphs:** Line charts tracking XP growth over time.

---

*Built by [Kharonn00](https://github.com/Kharonn00). Powered by Python, Spite, and a 2027 Deadline.*

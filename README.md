# Protocol Zero: Stochastic Behavioral Modification Engine

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge&logo=render&logoColor=white)](https://protocol-zero.onrender.com/dashboard)
[![Storage](https://img.shields.io/badge/Storage-PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://neon.tech)

> *"Chaos is the only cure for habit."*

## 📜 Overview
**Protocol Zero** is a Python-based utility designed to disrupt dopamine-driven feedback loops (specifically nicotine/THC dependency) via stochastic intervention.

Built with an **Object-Oriented Architecture**, this engine treats "Willpower" not as a feeling, but as a computable class. It outsources executive decision-making to a pseudo-random number generator, introducing friction and gamified penalties to break the "Trigger-Action-Reward" cycle.

## ⚡ Features
* **Hybrid Cloud Architecture:**
    * **Local:** Runs on lightweight **SQLite**.
    * **Cloud:** Automatically switches to **PostgreSQL (Neon)** for immortal data persistence.
* **Unified Process Management:** The **FastAPI** server and **Discord Bot** are fused into a single asynchronous event loop, allowing both to run 24/7 on a single free cloud instance.
* **Discord Bot Interface:**
    * Remote access via `!oracle`.
    * **AI-Powered Roasts:** The bot now connects to Gemini to generate context-aware insults along with your punishment.
* **Cyberpunk Command Center:** A **FastAPI**-powered dashboard featuring:
    * **The Mystic 8-Ball:** An animated orb that shakes to reveal your fate.
    * **The Voice of Judgment:** Browser-native **Text-to-Speech (TTS)** that reads the AI's insults aloud.
    * **Temporal Analytics:** A Bar Chart heat-mapping your weakest hours.
    * **Mobile-Responsive UI:** Optimized with CRT scanline aesthetics.
* **Stochastic Decision Logic:** Randomly assigns tasks (physical or mental) to derail cravings.
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
    pip install -r requirements.txt
    ```

## ⚙️ Configuration (The Vault)

To run the full stack locally, configure your `.env` file.

1.  Create a file named `.env` in the root directory.
2.  Add your Tokens inside:
    ```env
    DISCORD_TOKEN=your_discord_token_here
    GEMINI_API_KEY=your_google_ai_key_here
    # Optional: Add DATABASE_URL if connecting to Cloud DB locally
    # DATABASE_URL=postgresql://...
    ```

## 🎮 Usage

### Option A: The Cloud (Global Access)
The Oracle and the Discord Bot are live and fused.
* **Dashboard:** [Launch Protocol Zero](https://protocol-zero.onrender.com/dashboard)
* **Discord:** Type `!oracle` in your server. The bot never sleeps.

### Option B: Local Development
Launch the stack on your machine. This will start both the Website and the Bot.

```bash
uvicorn api:app --reload

```

* **Dashboard:** `http://127.0.0.1:8000/dashboard`
* **Note:** The database will default to `protocol_zero.db` (SQLite) unless a `DATABASE_URL` is present.

### Option C: The Scout (Legacy)

Run the engine directly in the terminal for a quick check:

```bash
python oracle.py

```

## 🗄️ The Archives (Data Persistence)

Protocol Zero utilizes a **Bilingual Database Manager**:

* **Cloud Mode (Render):** Detects `DATABASE_URL` and connects to **Neon PostgreSQL**. Data survives redeployments.
* **Local Mode (Laptop):** Defaults to **SQLite** (`protocol_zero.db`) for easy testing without internet.
* **Privacy Protocol:** The `.db` file is strictly **git-ignored**.

## 🧠 The Philosophy

This tool relies on the **"Friction Theory"** of habit breaking. By inserting a coding challenge or a physical exercise between the "Urge" and the "Action," Protocol Zero forces the brain to disengage from the craving loop.

## 🚀 Future Roadmap

* **Multi-User Support:** Scale the database schema to track progress for multiple users in a single server.
* **Gamification 2.0:** Add XP, Levels, and "Streaks" to the database.

---

*Built by [Kharonn00](https://github.com/Kharonn00). Powered by Python, Spite, and a 2027 Deadline.*

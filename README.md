# Protocol Zero: Stochastic Behavioral Modification Engine

> *"Chaos is the only cure for habit."*

## 📜 Overview
**Protocol Zero** is a Python-based utility designed to disrupt dopamine-driven feedback loops (specifically nicotine dependency) via stochastic intervention.

Built with an **Object-Oriented Architecture**, this engine treats "Willpower" not as a feeling, but as a computable class. It outsources executive decision-making to a pseudo-random number generator, introducing friction and gamified penalties to break the "Trigger-Action-Reward" cycle.

## ⚡ Features
* **OOP Architecture:** Modular `ProtocolZero` class design for scalability and easy integration.
* **Discord Bot Interface:** Remote access to the Oracle via a dedicated Discord bot. Users can summon judgment with `!oracle` from any server.
* **Enterprise-Grade Storage:** Implements a **SQLite Database** (`protocol_zero.db`) for robust data persistence, enabling future analytics and complex querying beyond simple text logs.
* **Stochastic Decision Logic:** Randomly assigns tasks (physical or mental) to derail cravings.
* **Adaptive Injury Protocol:** Dynamically detects physical handicaps (e.g., `hand_is_broken = True`) and reroutes physical penalties (swaps Pushups for Squats).
* **The Singularity Timer:** Calculates the precise `timedelta` remaining until the estimated arrival of AGI (2027), providing existential urgency to every execution.

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
    pip install discord.py python-dotenv
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

**Discord Commands:**

* `!oracle` - Summon the engine. The bot will query Protocol Zero and reply with a verdict.

**Sample Output (Discord):**

> **Protocol_Zero_Oracle** *BOT*
> **The Oracle Speaks:**
> Oracle redirected: Do 20 Squats instead (Hand Injury Protocol).

## 📜 The Journal (Legacy)

Every time the Oracle is consulted, it stamps the verdict into `oracle_journal.txt`.
*(Note: Migration to SQLite `protocol_zero.db` is currently in progress).*

## 🧠 The Philosophy

This tool relies on the **"Friction Theory"** of habit breaking. By inserting a coding challenge or a physical exercise between the "Urge" and the "Action," Protocol Zero forces the brain to disengage from the craving loop.

It is not just a script; it is a digital accountability partner that never sleeps and never negotiates.

---

*Built by [Kharonn00](https://github.com/Kharonn00). Powered by Python, Spite, and a 2027 Deadline.*
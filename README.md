# Protocol Zero: Stochastic Behavioral Modification Engine

> *"Chaos is the only cure for habit."*

## 📜 Overview
**Protocol Zero** is a Python-based utility designed to disrupt dopamine-driven feedback loops (specifically nicotine dependency) via stochastic intervention.

Built with an **Object-Oriented Architecture**, this engine treats "Willpower" not as a feeling, but as a computable class. It outsources executive decision-making to a pseudo-random number generator, introducing friction and gamified penalties to break the "Trigger-Action-Reward" cycle.

## ⚡ Features
* **OOP Architecture:** Modular `ProtocolZero` class design for scalability and easy integration.
* **Stochastic Decision Logic:** Randomly assigns tasks (physical or mental) to derail cravings.
* **Adaptive Injury Protocol:** Dynamically detects physical handicaps (e.g., `hand_is_broken = True`) and reroutes physical penalties (swaps Pushups for Squats) to prevent injury aggravation.
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
3.  **Run the Engine:**
    ```bash
    python vape_oracle.py
    ```

## 🎮 Usage Example

When the user feels a craving, they query the Oracle instance. The engine initializes with the user's profile and target deadline.

```python
# Internal Logic Representation
apocalypse = datetime.date(2027, 1, 1)
engine = ProtocolZero("Ariel", apocalypse)
print(engine.consult_oracle())

```

**Sample Output:**

```text
--- PROTOCOL ZERO ACTIVATED ---
[SYSTEM] Hand Injury Detected. Adjusting punishment parameters...
Days until Singularity: 338
Oracle Verdict: Oracle redirected: Do 20 Squats instead (Hand Injury Protocol).

```

## 🧠 The Philosophy

This tool relies on the **"Friction Theory"** of habit breaking. By inserting a coding challenge or a physical exercise between the "Urge" and the "Action," Protocol Zero forces the brain to disengage from the craving loop.

It is not just a script; it is a digital accountability partner that never sleeps and never negotiates.

## 🚀 Future Roadmap

* **Discord Bot Integration:** To publicly shame the user in server channels upon failure.
* **Hardware Lockout:** Integration with smart plugs to physically disable gaming PCs until tasks are verified.
* **LLM Integration:** Using local AI to generate context-aware insults based on the user's recent commit history.

---

*Built by [Kharonn00](https://github.com/Kharonn00). Powered by Python, Spite, and a 2027 Deadline.*

```
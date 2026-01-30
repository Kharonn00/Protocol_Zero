import random
import datetime

class ProtocolZero:
    def __init__(self, user_name, target_date):
        self.user_name = user_name
        self.target_date = target_date
        self.hand_is_broken = True  # The current physical handicap
        self.log_file = "oracle_journal.txt" # New Logbook

    def get_days_remaining(self):
        today = datetime.date.today()
        delta = self.target_date - today
        return delta.days

    def consult_oracle(self):
        options = [
            "Do 10 Pushups.",
            "Write 10 lines of clean Python code.",
            "Drink a glass of water and stare at a wall for 5 minutes.",
            "Read one page of technical documentation."
        ]

        # Injury Adjustment
        result = random.choice(options)
        
        if "Pushups" in result and self.hand_is_broken:
            return "Oracle redirected: Do 20 Squats instead (Hand Injury Protocol)."
        
        # NEW: Record the verdict before returning it
        self.log_interaction(result)
        return result

        # The Scribe
    def log_interaction(self, verdict):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] User: {self.user_name} | Verdict: {verdict}\n"

        # 'a' mode means APPEND. It adds to the end without erasing history.
        with open(self.log_file, "a") as file:
            file.write(entry)
            print(f"[SYSTEM] Interaction recorded in {self.log_file}")

# Initialize the Engine
apocalypse = datetime.date(2027, 1, 1)
engine = ProtocolZero("Ariel", apocalypse)

print(f"--- PROTOCOL ZERO ACTIVATED ---")
print(f"Days until Singularity: {engine.get_days_remaining()}")
print(f"Oracle Verdict: {engine.consult_oracle()}")
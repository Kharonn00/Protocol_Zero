import random
import datetime
from database_manager import DatabaseManager  # <--- The New Neural Link

class ProtocolZero:
    def __init__(self, user_name, target_date):
        self.user_name = user_name
        self.target_date = target_date
        
        # INJURY PROTOCOL (Hardcoded for now, until we make a setting for it)
        self.hand_is_broken = True 
        
        # Initialize the Connection to the Warehouse
        self.db = DatabaseManager() 

    def calculate_time_remaining(self):
        """Calculates days until the Singularity (Target Date)."""
        today = datetime.date.today()
        remaining = self.target_date - today
        return remaining.days

    def get_punishment(self):
        """Stochastic punishment generator."""
        punishments = [
            "Do 10 Pushups",
            "Do 20 Situps",
            "Drink a glass of water",
            "Take a 5-minute walk (No phone)",
            "Write 10 lines of clean Python code",
            "Do 10 Squats",
            "Plank for 60 seconds"
        ]
        
        # The Injury Override Logic
        selection = random.choice(punishments)
        
        if self.hand_is_broken and "Pushups" in selection:
            return "Oracle redirected: Do 20 Squats instead (Hand Injury Protocol)."
        
        return selection

    def consult_oracle(self):
        """The Main Public Method."""
        days_left = self.calculate_time_remaining()
        verdict = self.get_punishment()
        
        # THE UPGRADE: We no longer write to txt. We talk to Steve.
        self.db.log_interaction(self.user_name, verdict)
        
        return (f"Days until Singularity: {days_left}\n"
                f"Oracle Verdict: {verdict}")

# TEST AREA (Local Execution)
if __name__ == "__main__":
    # Set the date for AGI (or your goal)
    apocalypse = datetime.date(2027, 1, 1)
    
    # Initialize
    engine = ProtocolZero("Ariel", apocalypse)
    
    # Run
    print("--- PROTOCOL ZERO ACTIVATED ---")
    print(engine.consult_oracle())
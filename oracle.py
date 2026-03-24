import random
import datetime

class ProtocolZero:
    """
    The Oracle V2. Now with 100% more judgment.
    """
    
    def __init__(self, user_name):
        self.user_name = user_name
        
        # Tiered Punishments
        self.penance_tier_1 = [ # Light (For first offense)
            "Drink a glass of water.",
            "Take 3 deep breaths.",
            "Stretch for 1 minute."
        ]
        
        self.penance_tier_2 = [ # Medium (Standard)
            "20 Push-ups. Now.",
            "Wall Sit (60 seconds).",
            "Write 'I have no discipline' 10 times.",
            "Clean your toilet."
        ]
        
        self.penance_tier_3 = [ # Brutal (For chronic failures)
            "Cold Shower (2 minutes).",
            "100 Burpees.",
            "Donate $10 to a charity you hate.",
            "Call your mother and tell her you love her (but don't explain why)."
        ]

    def consult_oracle(self, streak=0):
        """
        Selects a punishment based on the user's current failure state.
        If they have a low streak, we go easy? NO. 
        Actually, let's invert it.
        If they JUST failed (streak 0), they get Tier 1 to get back on track?
        """
        
        # simple logic: Random choice for now. 
        # You can expand this to check previous failures later.
        
        roll = random.random()
        
        # Veterans get brutalized. New failures get eased back in.

        if streak > 14:
            weights = (0.05, 0.45, 0.50)
        elif streak > 7:
            weights = (0.10, 0.65, 0.25)
        else:
            weights = (0.20, 0.60, 0.20)
    
        if roll < weights[0]:
            tier, severity = self.penance_tier_1, "MILD"
        elif roll < weights[0] + weights[1]:
            tier, severity = self.penance_tier_2, "STANDARD"
        else:
            tier, severity = self.penance_tier_3, "BRUTAL"
    
        return f"[{severity}] {random.choice(tier)}"

if __name__ == "__main__":
    p0 = ProtocolZero("Tester")
    print(p0.consult_oracle())
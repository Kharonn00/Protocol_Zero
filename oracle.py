import random      # Gives us random.choice() to pick random items from a list
import datetime    # Gives us tools to work with dates and times

class ProtocolZero:
    """
    A class that acts as an "Oracle" to randomly assign punishments/tasks.
    
    Think of a class as a blueprint for creating objects. This class defines
    what data (attributes) and behaviors (methods) our Oracle will have.
    """
    
    def __init__(self, user_name, target_date):
        """
        The __init__ method is called a "constructor" - it runs automatically
        when you create a new ProtocolZero object. It sets up the initial state.
        
        Parameters:
            user_name (str): The name of the person using the oracle
            target_date (datetime.date): A future date you're working toward
        """
        # self.user_name stores the user's name for this specific oracle instance
        self.user_name = user_name
        
        # self.target_date stores the goal date for this specific oracle instance
        self.target_date = target_date
        
        # NOTE: This version doesn't connect to a database
        # Database connections were removed because a separate "Bot" handles data storage

    def consult_oracle(self):
        """
        This method is the main function of the Oracle. When called, it:
        1. Defines a list of possible punishments/tasks
        2. Calculates how many days until the target date
        3. Randomly selects one punishment to return
        
        Returns:
            str: A randomly chosen punishment/task from the list
        """
        
        # ==============================================================
        # STEP 1: Define the List of Punishments
        # ==============================================================
        # This is a Python list containing strings. Each string is a possible
        # punishment or task that could be assigned.
        punishments = [
            "20 Push-ups",
            "20 Squats",
            "1 Minute Plank",
            "50 Jumping Jacks",
            "30 Lunges",
            "Wall Sit (45 seconds)",
            "Burpees (10 reps)",
            "Cold Shower (30 seconds)",
            "No Music for 1 Hour",
            "Clean your room/desk immediately",
            "Write 'I am in control' 20 times",
            "Drink 1 full glass of water",
            "Code 10 lines of Python",
            "Read 5 pages of a book"
        ]
        
        # ==============================================================
        # STEP 2: The Singularity Check (Calculate Days Remaining)
        # ==============================================================
        # This calculates how many days are left until the target date.
        # datetime.date.today() gives us today's date
        # We subtract it from target_date to get a timedelta object
        # .days gives us the number of days as an integer
        days_remaining = (self.target_date - datetime.date.today()).days
        
        # NOTE: Currently, days_remaining is calculated but not used in the logic.
        # You could enhance this by using days_remaining to add motivational messages
        # or adjust punishment difficulty based on how close you are to the goal.
        
        # ==============================================================
        # STEP 3: The Selection (Pick a Random Punishment)
        # ==============================================================
        # random.choice() picks one item randomly from the punishments list
        # Each item has an equal chance of being selected
        verdict = random.choice(punishments)
        
        # Return the selected punishment back to whoever called this method
        return verdict

# ==============================================================
# Test Code Section
# ==============================================================
# This section only runs if you execute this file directly (not when importing it)
# The condition checks if __name__ == "__main__"
if __name__ == "__main__":
    # Create a test instance of ProtocolZero
    # "Tester" is the user_name
    # datetime.date(2027, 1, 1) creates a date object for January 1st, 2027
    p0 = ProtocolZero("Tester", datetime.date(2027, 1, 1))
    
    # Call the consult_oracle method and print the result
    # The f-string lets us embed the result directly in the printed text
    print(f"Verdict: {p0.consult_oracle()}")
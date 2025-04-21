import secrets
import string
from models.models import Rooms  # Import your db instance from the app

def generate_room_code(length=6):
    #THis function is being used to generate a random code that does not exist already for another room 
    # Define the characters for the code to have A-Z and 0-9
    characters = string.ascii_uppercase + string.digits

    while True:
        # Generate a random room code using secrets for better randomness
        room_code = ''.join(secrets.choice(characters) for _ in range(length))

        # Use SQLAlchemy to check if the room code already exists in the Rooms table
        if not Rooms.query.filter_by(room_code=room_code).first():
            # If the room code does not exist, return the generated code
            return room_code
        # If the room code exists, the loop will continue and generate a new code
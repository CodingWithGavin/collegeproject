from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    def __init__  (self, name):
        self.name = name
        
    def __repr__(self):
        return f'<User {self.name}>'
    
class Rooms(db.Model):
    __tablename__ = "rooms"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) #sets the primary key as id to be used by the system, set to auto increment so we dont have to
    room_code = db.Column(db.String(255), unique=True, nullable=False) # sets the room code which we will use for players to join specific rooms
    round_count = db.Column(db.Integer, default=1) # the round count can be used the calculate how many rounds of combat have happened
    current_turn = db.Column(db.Integer, default=1) # current turn can be used to calcualte both the whos turn it is but also setting up our round count too
    session_start_time = db.Column(db.DateTime, default=datetime.utcnow) # session start dates could be used to help in future databse commands clearing out sessions from the databse that have gone on too long
    room_status = db.Column(db.Enum('active', 'paused', 'completed'), default='active') # helps tell what the current status is and could help with clearing off sessions too

    # One Room to many players relationship, backref adds a helpful .room property to each player instance , lazy=true tells sqlalchemy to not load in the player objects until we need to 
    players = db.relationship('Player', backref='room', lazy=True)
    
class Player(db.Model):
    __tablename__ = 'player'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True) #primary key for the players
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False) # foriegn key used to match the user to the right rooms
    player_type = db.Column(db.Enum('dm', 'player', 'enemy','npc'), nullable=False) # if the user is a player or dm
    initiative_count = db.Column(db.Integer) #used to track turn order at the beginning
    hit_point_count = db.Column(db.Integer) # Tracking users health
    player_name = db.Column(db.String(255), nullable=False) 
    AC = db.Column(db.Integer)  # Armor Class used to track if an attack hit or missed 
    
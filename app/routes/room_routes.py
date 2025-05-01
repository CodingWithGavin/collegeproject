from flask import json, render_template, request, redirect, url_for, flash, Response, stream_with_context, session
from functions.room_functions import generate_room_code
from app import app
from models.models import db, Rooms, Player
from queue import Queue, Empty
from datetime import datetime
from time import sleep
import time # imported this way due to issues with time being seen as the module rather than the function if we using 'from time import sleep, time'

sse_clients = {}

#Client listener for the sse update event 
@app.route('/room/<room_code>/events')
def sse(room_code):
    def event_stream(queue):
        try:
            while True:
                data = queue.get(timeout=10)  # Wait for up to 10 seconds
                yield f"event: roomUpdate\ndata: {data}\n\n"
        except Empty:
            pass
        finally:
            sse_clients[room_code].remove(queue)  # Cleanup the queue when the client disconnects

    queue = Queue()
    sse_clients.setdefault(room_code, []).append(queue)
    return Response(stream_with_context(event_stream(queue)), content_type='text/event-stream')




@app.route('/room/create_room', methods=['GET', 'POST']) 
def create_room():
    if request.method == 'POST':
        # Generate a unique room code using the updated function
        room_code = generate_room_code()

        # Create a new room with the generated code
        room = Rooms(room_code=room_code, session_start_time=datetime.now(), room_status='active', current_turn=1, round_count=1 )
        db.session.add(room)
        db.session.commit()
        
        # Get the player name from the form
        player_name = request.form.get('player_name')
        
        # Create the player (DM) and assign them to the room
        player = Player(player_name=player_name, room_id=room.id, player_type='dm', initiative_count='', hit_point_count='', AC='')
        db.session.add(player)
        db.session.commit()
        
        # Create the session data to help track dms information information 
        session['player_id'] = player.id
        session['player_name'] = player_name
        session['room_code'] = room_code
        session['role'] = 'dm'
        
        # Redirect to the room's own page (use room_code as part of the URL)
        return redirect(url_for('room_page', room_code=room_code))

    return render_template('rooms/room_page.html', room_code=room_code)

@app.route('/room/<room_code>')
def room_page(room_code):
    # Fetch the room from the database using the room code
    room = Rooms.query.filter_by(room_code=room_code).first()
    if not room:
        # If the room doesn't exist, return a 404 error
        return "Room not found", 404
    
    # Optionally, you can fetch players or other room details here
    players = Player.query.filter_by(room_id=room.id).all()
    
    return render_template('rooms/room_page.html', room=room, players=players)

@app.route('/room/join_room', methods=['POST'])
def join_room():
    # Retrieve form data
    room_code = request.form.get('room_code')
    player_name = request.form.get('player_name')
    initiative_count = request.form.get('initiative_count')
    hit_points = request.form.get('hit_points')
    ac = request.form.get('ac')

    # Check if the room exists
    room = Rooms.query.filter_by(room_code=room_code).first()
    if not room:
        flash("Room not found", "danger")
        return redirect(url_for('home'))  # Or redirect to a page where you handle errors

    # Create the player and assign them to the room
    player = Player(
        player_name=player_name,
        room_id=room.id,
        player_type='player',  # Assuming they are a player, not the DM
        initiative_count=initiative_count,
        hit_point_count=hit_points,
        AC=ac
    )
    
    # Add the player to the database
    db.session.add(player)
    db.session.commit()
    time.sleep(0.5) # using this to see if this helps possible tace condition of adding new user and updating user table
    # Send an update to all connected clients (SSE clients)
    players = Player.query.filter_by(room_id=room.id).all()
    game_state = {
        'current_turn': room.current_turn,
        'round_count': room.round_count,
        'players': [{
            'id': p.id,
            'name': p.player_name,
            'initiative': p.initiative_count,
            'hitpoints': p.hit_point_count,
            'ac': p.AC
        } for p in players]
    }

    for client in sse_clients.get(room_code, []):
        client.put(json.dumps(game_state)) # Send updated players list
    
    #Create the session data to help track player information 
    session['player_id'] = player.id
    session['player_name'] = player_name
    session['room_code'] = room_code
    session['role'] = 'player'
    
    
    flash("Successfully joined the room!", "success")
    return redirect(url_for('room_page', room_code=room_code))

@app.route('/room/<room_code>/sorted_players')
def sorted_players(room_code):
    start_time = time.time()
    
    room = Rooms.query.filter_by(room_code=room_code).first_or_404()
    players = Player.query.filter_by(room_id=room.id).order_by(Player.initiative_count.desc()).all()
    # Log how long this query takes for debugging purposes
    print(f"Query took {time.time() - start_time} seconds")
        # Debugging: Print the sorted players and their initiative counts
    players_data = [{
        'id': p.id,
        'name': p.player_name,
        'initiative': p.initiative_count,
        'hitpoints': p.hit_point_count,
        'ac': p.AC
    } for p in players]
    
    
    for player in players:
        print(f"Player: {player.player_name}, Initiative: {player.initiative_count}")

    
    return render_template('rooms/partials/player_list.html', players=players, room=room)

@app.route('/room/<room_code>/end_turn', methods=['POST'])
def end_turn(room_code):
    room = Rooms.query.filter_by(room_code=room_code).first_or_404()
    players = Player.query.filter_by(room_id=room.id).order_by(Player.initiative_count.desc()).all()

    # Save the old state before the change
    old_turn = room.current_turn
    old_round_count = room.round_count

    # Increment the current turn
    room.current_turn += 1

    # Check if we've passed the last player and reset current_turn if needed
    if room.current_turn > len(players):
        room.current_turn = 1
        room.round_count += 1

    db.session.commit()
    
    # Prepare the updated game state data
    game_state = {
        'current_turn': room.current_turn,
        'round_count': room.round_count,
        'players': [{
            'id': p.id,
            'name': p.player_name,
            'initiative': p.initiative_count,
            'hitpoints': p.hit_point_count,
            'ac': p.AC
        } for p in players]
    }
    
    # Only send updates if the turn or round count has changed
    if old_turn != room.current_turn or old_round_count != room.round_count:
        # Send update to all clients listening on SSE 
        for client in sse_clients.get(room_code, []):
            client.put(json.dumps(game_state))

    return '', 204
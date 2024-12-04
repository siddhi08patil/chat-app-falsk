from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
from string import ascii_uppercase

# Dictionary to store rooms and their info
rooms = {}

# Function to generate a unique room code
def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        if code not in rooms:
            break
    return code

# Initialize Flask app and SocketIO
app = Flask(__name__)
app.config["SECRET_KEY"] = "dhsiuchudsc"
socketio = SocketIO(app)

# Home page route (handle room creation and joining)
@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join")
        create = request.form.get("create")

        # Validation for name input
        if not name:
            return render_template("home.html", error="Please enter a name", code=code, name=name)
        
        # If trying to join a room but no room code is provided
        if join and not code:
            return render_template("home.html", error="Please enter a code to join the room", code=code, name=name)

        room = code
        if create:  # Check if 'create' button was clicked
            room = generate_unique_code(4)  # Generate unique room code
            rooms[room] = {"members": [name], "messages": []}  # Initialize room with 1 member (the creator)
        elif code not in rooms:  # If trying to join an existing room
            return render_template("home.html", error="Room does not exist", code=code, name=name)

        session["room"] = room  # Store room code in session
        session["name"] = name  # Store user name in session
        return redirect(url_for("room"))

    return render_template("home.html")

# Room page route (after room creation or joining)
@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))  # Redirect to home if no valid room found

    return render_template("room.html", room=room)

# Socket.IO event for message handling
@socketio.on('join')
def on_join(data):
    room = data['room']
    username = data['username']
    join_room(room)
    emit('message', {'username': 'System', 'message': f'{username} has entered the room.'}, room=room)

@socketio.on('message')
def handle_message(data):
    room = session.get("room")
    message = data['message']
    username = session.get("name")
    
    if room and username:
        rooms[room]['messages'].append({'username': username, 'message': message})
        emit('message', {'username': username, 'message': message}, room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    username = data['username']
    leave_room(room)
    emit('message', {'username': 'System', 'message': f'{username} has left the room.'}, room=room)

if __name__ == "__main__":
    socketio.run(app, debug=True)

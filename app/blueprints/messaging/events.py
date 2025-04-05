from app.extensions import socketio
from flask_socketio import emit
from flask import request 

@socketio.on('connect')
def handle_connect():
    print('Client connected'+ f'{request.sid}')
    
    emit('server_response', {'data': 'Connected to server'})


@socketio.on('client_message')
def handle_message(message,socketid):  # Changed parameter name to 'message'
    print(f'Received: {message} and {socketid}')
    sid = request.sid
    # Broadcast the raw message directly
    
    emit('server_response', {'data': message}, room=[sid, socketid])
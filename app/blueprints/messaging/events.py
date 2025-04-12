from app.extensions import socketio, mongo
from bson import ObjectId
from flask_socketio import emit
from flask_jwt_extended import jwt_required
from flask import request 
from datetime import datetime
import hashlib


    
class socke_handles():

    # function for generating chatid for tracking chats between users
    def get_or_create_chat(sender_id, receiver_id):
        ids = sorted([sender_id, receiver_id])
        # Generate a unique chatid using a hashing function
        chat_id = hashlib.sha256(f"{ids[0]}-{ids[1]}".encode()).hexdigest()
        return chat_id
    
    def connect(id):
            @socketio.on('connect')
            def handle_connect():
                user_id = id
                if user_id:
                    user = mongo.db.user.find_one({"_id": ObjectId(user_id)})
                    if user:
                        usernam = user['username']
                        print(f'{usernam}: connected {request.sid}')
                        mongo.db.user.update_one(
                            {"_id": ObjectId(user_id)},
                            {"$set": {"status": "online", "socket_id": str(request.sid)}}
                        )
                        emit("user_status", {"user_id": user_id, "status": "online"}, broadcast=True)
                    else:
                        print(f"User with ID {user_id} not found")
                else:
                    print("Connect event without user_id")
                    
    def disconnect():
            @socketio.on('disconnect')
            def handle_disconnect():
                print(f'Client disconnected: {request.sid}')
                # You'll need to retrieve the user_id associated with this socket_id
                user = mongo.db.user.find_one({"socket_id": str(request.sid)})
                if user:
                    user_id = str(user['_id'])
                    mongo.db.user.update_one(
                        {"_id": ObjectId(user_id)},
                        {"$set": {"status": "offline", "last_seen": datetime.utcnow().isoformat()},
                        "$unset": {'socket_id': ''}}
                    )
                    emit("user_status", {"user_id": user_id, "status": "offline"}, broadcast=True)
    
    def message(id):
            @socketio.on('client_message')
            def handle_message(message,rec_username): # Expecting message and rec_username in the data
                user_id = id
                sid = request.sid
                
                print(f'Received from {user_id} ({sid}): {message} to {rec_username}')

                if user_id and rec_username and message:
                    try:
                        sender = mongo.db.user.find_one({"_id": ObjectId(user_id)})
                        
                        if not sender:
                            print(f"Sender with ID {user_id} not found")
                            return

                        reciever = mongo.db.user.find_one({"username": rec_username})
                        if not reciever or 'socket_id' not in reciever or '_id' not in reciever:
                            print(f"Receiver with username {rec_username} not found or not connected")
                            emit('server_response', {'error': 'Receiver not found or not online'}, room=sid)
                            return

                        reciever_socketid = reciever['socket_id']
                        reciever_id = str(reciever['_id'])
                        print(f'{user_id} / {reciever_id}')
                        chat_id = socke_handles.get_or_create_chat(user_id, reciever_id)

                        message_sent = {
                            "chat_id": chat_id,
                            "sender_id": user_id,
                            "receiver_id": reciever_id,
                            "message_text": message,
                            "timestamp": datetime.utcnow().isoformat(),
                            "seen": False
                        }

                        result = mongo.db.message.insert_one(message_sent)
                        message_sent["_id"] = str(result.inserted_id)

                        emit('server_response', {'data': message, 'sender_id': user_id}, room=[sid, reciever_socketid])

                    except Exception as e:
                        print(f"Error handling message: {e}")
                        emit('server_response', {'error': 'Failed to send message'}, room=sid)
                else:
                    print("Incomplete message data received")

    
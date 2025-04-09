from app.extensions import socketio, mongo
from bson import ObjectId
from flask_socketio import emit
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
    
        def connect(user_id):
            @socketio.on('connect')
            def handle_connect():
                print('Client connected'+ f'{request.sid}')
                if user_id:
                    mongo.db.user.update_one(
                            {"_id": ObjectId(user_id)},
                            {"$set": {"status": "online"}}
                        )
                emit("user_status", {"user_id": user_id, "status": "online"}, broadcast=True)
                
                
        def disconnect(user_id):
            @socketio.on('disconnect')
            def handle_disconnect():
                print('client disconnect')
                if user_id:
                    mongo.db.user.update_one(
                        {"_id": ObjectId(user_id)},
                        {"$set": {"status": "offline",
                        "last_seen": datetime.utcnow().isoformat()
                        }}
                    )
                emit("user_status",{"user_id": user_id, "status": "offline"}, broadcast=True)

        def message(user_id):
            @socketio.on('client_message')
            def handle_message(message,rec_username):  # Changed parameter name to 'message'
                print(f'Received: {message} and {rec_username}')
                
                # user socket id
                sid = request.sid
                # adding current socket id to database
                if user_id:
                    mongo.db.user.update_one(
                        {"_id": ObjectId(user_id)},
                        { "$set": {"socket_id": sid} }
                    )
                # fetching reciever socket id by username
                try:
                    reciever = mongo.db.user.find_one(
                        {"username": rec_username }
                    )    
                    reciever_socketid = reciever['socket_id']
                    reciever_id = reciever['_id']
                    print(reciever_socketid)
                    print(str(reciever_id))
                except KeyError:
                    print("not socket id found")
                
                # adding message details in message collection of database
                if reciever:
                   chat_id = socke_handles.get_or_create_chat(user_id,str(reciever_id))
                else: chat_id = 0
                
                message_sent = {
                            "chat_id": chat_id,
                            "sender_id": user_id,
                            "receiver_id": str(reciever_id),
                            "message_text": message,
                            "timestamp": datetime.utcnow().isoformat(),
                            "seen": False
                        }
                
                result = mongo.db.message.insert_one(message_sent)
                message_sent["_id"] = str(result.inserted_id) 
                
                
                emit('server_response', {'data': message}, room=[sid, reciever_socketid])
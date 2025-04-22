from app.extensions import socketio, mongo
from bson import ObjectId
from flask_socketio import emit
from flask import request , flash
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
                user_id = request.args.get('user_id')
                
                if user_id != id:
                    print("wrong user_id provided. Disconnecting.")
                    return False 
                
                user = mongo.db.user.find_one({"_id": ObjectId(id)})
                if user:
                    current_username = user['username']
                    print(f'{current_username}: connected {request.sid}')
                    
                    mongo.db.user.update_one(
                        {"_id": ObjectId(id)},
                        {"$set": {
                            "socket_id": str(request.sid),
                            "status": True
                                  }}
                        )
                    
                    # getting active list from db
                    try:
                        actives=mongo.db.chatActive.find_one({"username": current_username})
                        active_list = actives["active"]
                    except:
                        active_list=[] # if active list not exist keep active list empty to avoid unneccosory conditional checks
                        print("actives not found")
                     
                    # emit event to active list users if exist    
                    if len(active_list)>0:
                        for username in active_list: # geting username one by one from list
                            
                            user_ = mongo.db.user.find_one({"username":username}) # getting user 
                            
                            try:
                               socket_id = user_["socket_id"] # gettin user socket id
                               socketio.emit("status_online",{"data":current_username},to=socket_id) 
                            except:
                                None
                    
                else:
                    print(f"User with ID {id} not found")
                
                    
    def disconnect():
            @socketio.on('disconnect')
            def handle_disconnect():
                # You'll need to retrieve the user_id associated with this socket_id
                user = mongo.db.user.find_one({"socket_id": request.sid})
                
                if user:
                    current_username = user["username"]
                    print(f'Client disconnected: {current_username}')
                    try:
                        actives=mongo.db.chatActive.find_one({"username": current_username})
                        active_list = actives["active"]
                    except:
                        active_list=[] # if active list not exist keep active list empty to avoid unneccosory conditional checks
                        print("actives not found")
                     
                    # emit event to active list users if exist    
                    if len(active_list)>0:
                        for username in active_list: # geting username one by one from list
                            print(username)
                            user_ = mongo.db.user.find_one({"username":username}) # getting user 
                            
                            try:
                               socket_id = user_["socket_id"] # getting user socket id 
                               socketio.emit("status_offline",{"data":current_username}, to=socket_id) 
                            except:
                                None
                    
                    user_id = str(user['_id'])
                    mongo.db.user.update_one(
                        {"_id": ObjectId(user_id)},
                        {"$set": {"status": False, "last_seen": datetime.utcnow().isoformat()},
                        "$unset": {'socket_id': ''}})
                    
    def active_chat():
        
            
            
            @socketio.on('chat_selected')
            def handle_active_chat(data):
                my_id = data["my_id"]
                selected_username = data["selected_username"]
                user = mongo.db.user.find_one({"_id": ObjectId(my_id)})
                username = user['username']
                user_1 = mongo.db.user.find_one({"username":selected_username})
                
                if user_1:
                    try:    
                        
                        mongo.db.chatActive.update_one(
                                                {"username": selected_username}, 
                                                {
                                                    "$setOnInsert": {"username": selected_username}, 
                                                    "$addToSet": {"active": username}
                                                }, 
                                                upsert=True)
                    except:
                        print("active not added")
                
            @socketio.on('chat_deselected')
            def handle_deactive_chat(data):
                
                my_id = data["my_id"]
                deselected_username = data["deselected_username"]
                user = mongo.db.user.find_one({"_id": ObjectId(my_id)})
                username = user['username']
                user_1 = mongo.db.user.find_one({"username":deselected_username})
                
                if user_1:
                    try:
                        update_result = mongo.db.chatActive.update_one(
                            {"username": deselected_username},
                            {"$pull": {"active": username}}
                            )
                        
                        if update_result.modified_count > 0:
                            mongo.db.chatActive.delete_one(
                                {"username": deselected_username, "active": {"$size": 0}}
                            )
                        
                    except:
                        print("deselect query not excueted")
            

            
            
                    
    
    def message():
            @socketio.on('client_message')
            def handle_message(message,rec_username): # Expecting message and rec_username in the data
               
                sid = request.sid

                if rec_username and message:
                    try:
                        sender = mongo.db.user.find_one({"socket_id": sid})
                        user_id = str(sender['_id'])
                        if not sender:
                            print(f"Sender with not found")
                            flash("contact not found")
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
                    
                
    def typing():
        @socketio.on('typing')
        def handle_typing(rec_username):
            try:
                reciever = mongo.db.user.find_one({'username':rec_username})
                reciever_id = reciever['socket_id']
                if reciever_id:
                   emit('typin_indicator',room=reciever_id )
            except TypeError:
                None
    
    
    
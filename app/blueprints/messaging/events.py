from app.extensions import socketio, mongo
from bson import ObjectId
from flask_socketio import emit
from flask import request , flash

import time
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
                
                user = mongo.db.user.find_one({"_id": ObjectId(user_id)})
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
                        {"$set": {"status": False, "last_seen": int(time.time() * 1000)},
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
                        
                not_saved_contact = mongo.db.contacts.find_one({
                                                "username": deselected_username,
                                                "contacts.username": username
                                            }) is None
                if not not_saved_contact:
                    mongo.db.contacts.update_one(
                                        { "username":  deselected_username},
                                        { "$set": { "contacts.$[elem].seen": data["cct"] } },
                                        array_filters=[{"elem.username": username}]
                                    )
            

            
            
                    
    
    def message():
            @socketio.on('client_message')
            def handle_message(data): # Expecting message and rec_username in the data
                print(f"message emited: {data}")
                message = data['message']
                rec_username = data['rec_username']
                sid = request.sid
                uuid = data["uuid"]

                if rec_username and message:
                    try:
                        sender = mongo.db.user.find_one({"socket_id": sid})
                        user_id = str(sender['_id'])
                        if not sender:
                            print(f"Sender with not found")
                            flash("contact not found")
                            return

                        reciever = mongo.db.user.find_one({"username": rec_username})
                        if not reciever:
                            return

                        
                        reciever_id = str(reciever['_id'])
                        chat_id = socke_handles.get_or_create_chat(user_id, reciever_id)
                        timestamp =  int(time.time() * 1000)

                        message_sent = {
                            "chat_id": chat_id,
                            "sender_id": user_id,
                            "receiver_id": reciever_id,
                            "message_text": message,
                            "timestamp": timestamp,
                            "seen": False
                        }

                        result = mongo.db.message.insert_one(message_sent)
                        message_sent["_id"] = str(result.inserted_id)
                        emit("msg_reached",{"uuid":uuid,"ru":rec_username},to=sid)
                        print(f"uuid:{uuid}")
                        try:
                            checkIfUserActive = mongo.db.chatActive.find_one({"username":str(sender["username"])})
                            actives = checkIfUserActive["active"]
                        except:
                            actives = []
                        
                        if rec_username in actives and ( rec_username != sender["username"]):
                            reciever_socketid = reciever['socket_id']
                            emit('server_response', {'data': message, 'sender_id': user_id, "timestamp":timestamp,"su":str(sender["username"]), "uuid":uuid }, room=[reciever_socketid])

                        not_saved_contact = mongo.db.contacts.find_one({
                                                "username": rec_username,
                                                "contacts.username": sender["username"]
                                            }) is None
                        
                        if not_saved_contact:
                            mongo.db.contacts.update_one(
                                    { "username":  rec_username },
                                    { "$push": { "contacts": { "username": sender["username"], "name": "Not Saved" } } }
                                )
                            # adc = add_contacts, cu = contact_username
                            emit("adc",{"cu":sender["username"]},to=reciever['socket_id'])

                    except Exception as e:
                        print(f"Error handling message: {e}")
                        flash("there is issue with connection, please refresh page")
                        emit('server_response', {'error': 'Failed to send message'}, room=sid)
                    
                else:
                    print("Incomplete message data received")
                    
    def msg_seen():
        @socketio.on('msg_seen')
        def handle_msgseen(data):
            reciever = mongo.db.user.find_one({"_id":ObjectId(data["ri"])})
            rec_username = reciever["username"]
            try:
                actives = mongo.db.chatActive.find_one({"username":rec_username})
                active = actives["active"]
            except:
                active = ['']
                
            sender_username = data["su"]
            if sender_username in active:
                uuid = data["uuid"] 
                sender = mongo.db.user.find_one({"username":sender_username})
                socket_id = sender["socket_id"]
                emit("msr",{"uuid":uuid, "ru":rec_username}, to=socket_id)
                
    def respone_msgseen():
        @socketio.on("msf")
        def handle_msgseen(data):
            id = data["id"]
            sender_username = data["su"]
            reciever = mongo.db.user.find_one({"_id": ObjectId(id)})
            rec_username = reciever["username"]
            try:
                 actives = mongo.db.chatActive.find_one({"username":rec_username})
                 active = actives["active"]
            except:
                active = ['']
                
            if sender_username in active:
                sender = mongo.db.user.find_one({"username":sender_username})
                socket_id = sender["socket_id"]
                #sending ack in realtime for msg seen by reciever 
                emit("ams",{"ru":rec_username},to=socket_id)
                    
                
    def typing():
        @socketio.on('typing')
        def handle_typing(data):
            rec_username = data["username"]
            user_id = data["user_id"]
            user=mongo.db.user.find_one({"_id": ObjectId(user_id)})
            username = user["username"]
            actives=mongo.db.chatActive.find_one({"username":username})
            
            
            if actives and (rec_username in actives["active"]) and ( rec_username != username):
                try:
                    reciever = mongo.db.user.find_one({'username':rec_username})
                    reciever_id = reciever['socket_id']
                    if reciever_id:
                       emit('typin_indicator',{"data":username},room=reciever_id )
                except:
                    None
    
    
    
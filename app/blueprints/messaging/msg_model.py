from flask import render_template, make_response, request, jsonify
from datetime import datetime
from app.extensions import mongo
from flask_jwt_extended import jwt_required, get_jwt_identity
from .forms import MessageForm
from .events import socke_handles
from bson import ObjectId


socket = socke_handles()

class Msg_model():
    
    def get_contacts(self,user_id):
        try:
            user = mongo.db.user.find_one({ "_id" : ObjectId(user_id) })
            username = user['username']
            contact = mongo.db.contacts.find_one({'username':username})
            contacts = contact['contacts']
        except:
            contacts = ["Add contacts"]
        return contacts
    
    def format_last_seen(self, last_seen):
        # Format the last seen timestamp
        last_seen_dt = datetime.strptime(last_seen[:19], "%Y-%m-%dT%H:%M:%S")
        now = datetime.utcnow()
        diff = now - last_seen_dt
        if diff.days == 0:
            if diff.seconds < 60:
                return "Last seen few seconds ago"
            elif diff.seconds < 3600:
                return f"Last seen {diff.seconds // 60} minutes ago"
            else:
                return f"Last seen {diff.seconds // 3600} hours ago"
        else:
            return f"Last seen on {last_seen_dt.strftime('%Y-%m-%d')}"
    
    def msg(self,user_id):
        forms = MessageForm()
        socke_handles.connect(user_id)
        socke_handles.active_chat()
        socke_handles.disconnect()
        socke_handles.message()
        socke_handles.typing()
        socke_handles.msg_seen()
        socke_handles.respone_msgseen()
        
        try:
            contacts = self.get_contacts(user_id)
        except:
            contacts = {"contacts":[{
                "name":"Add contact",
                "username":""
            }]}
        
        return render_template("chat_area.html",forms=forms,contacts=contacts,user_id=user_id)
    
    def getChat(self,user_id,usernmae):
        
        try:
            reciever=mongo.db.user.find_one({"username":usernmae})
            #print(reciever)
            reciever_id = reciever['_id']
        
            chat_id = socke_handles.get_or_create_chat(user_id,str(reciever_id))
            message_detail = mongo.db.message.find({"chat_id": chat_id}, {
                        "sender_id": 1,
                        "message_text": 1,
                        "timestamp": 1,
                        "seen": 1,
                        "_id": 0  
                    })
            # getting seen epoch time from contacts
            result = mongo.db.contacts.find_one(
                            { "_id":ObjectId(user_id), "contacts.username": usernmae },
                            { "contacts.$": 1 }
                        )
            
            if result and "contacts" in result and len(result["contacts"]) > 0:
                    seen_value = result["contacts"][0].get("seen")
            else: seen_value = 0
            
            return make_response({"ep_ti":seen_value,"message_data":message_detail},200)
        except:
            None
        
    
    def handle_chat_deselected(self):
            data = request.get_json()
            my_id = data.get("my_id")
            deselected_username = data.get("deselected_username")

            user = mongo.db.user.find_one({"_id": ObjectId(my_id)})
            if not user:
                return jsonify({"success": False, "error": "User not found"}), 400

            username = user["username"]
            user_1 = mongo.db.user.find_one({"username": deselected_username})
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
                except Exception as e:
                    print("Deselect error:", e)
                    return jsonify({"success": False}), 500

            return jsonify({"success": True}), 200
        
    def get_lastseen(self,username):
            user_lastseen= None
            status = None
            try:
                user = mongo.db.user.find_one({"username": username})
                user_lastseen = user["last_seen"]
                status = user["status"]
            except:
                if user_lastseen == None:
                   user_lastseen = 0
                if status == None:
                   status = False
            
            return make_response({"lastseen":user_lastseen, "status":status},200)

    
        
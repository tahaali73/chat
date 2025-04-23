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
        except TypeError:
            contacts = ["Add contacts"]
        return contacts
    
    def format_last_seen(self, last_seen):
        # Format the last seen timestamp
        last_seen_dt = datetime.strptime(last_seen[:19], "%Y-%m-%dT%H:%M:%S")
        now = datetime.utcnow()
        diff = now - last_seen_dt
        if diff.days == 0:
            if diff.seconds < 60:
                return "Online"
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
        contacts = self.get_contacts(user_id)
        
        return render_template("chat_area.html",forms=forms,contacts=contacts,user_id=user_id)
    
    def getChat(self,user_id,usernmae):
        
        try:
            reciever=mongo.db.user.find_one({"username":usernmae})
            #print(reciever)
            reciever_id = reciever['_id']
            try:
              status=reciever['status']
            except TypeError:
                status="offline"
            try:
                last_seen=reciever['last_seen']
                last_seen = self.format_last_seen(last_seen)
            except (TypeError, KeyError):
                last_seen="offline"
                
            print(reciever_id)
        except:
            None
        
        try:
            contacts = self.get_contacts(user_id)
        except TypeError:
            contacts = {"contacts":[{
                "name":"Add contact",
                "username":""
            }]}
       
        chat_id = socke_handles.get_or_create_chat(user_id,str(reciever_id))
        message_detail = mongo.db.message.find({"chat_id":chat_id})
        
        
        #if len(message_detail)==:
         #   return make_response({"msg":"no message found"},202)
        
        return make_response({"contact_name":contacts,"status":status,"last_seen":last_seen,"message_data":message_detail},200)
        
    
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

    
        
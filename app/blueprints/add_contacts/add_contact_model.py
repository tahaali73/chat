from bson import ObjectId
from app.extensions import mongo
from flask import render_template, flash
from app.blueprints.add_contacts.forms import ContactForm

class AddContact_Model():
    
    # helper function for add contact
    def insertContact(self,name,username,username_):
        user = mongo.db.user.find_one({"username": username})
        
        if user:
            already_available = mongo.db.contacts.find_one({
                                        "username": username_,
                                        "$or": [
                                            {"contacts": {"$elemMatch": {"name": name}}},
                                            {"contacts": {"$elemMatch": {"username": username}}}
                                        ]
                                    })
            if already_available:
                flash("user already in your contact list")
            
            else:
                mongo.db.contacts.update_one(
                            { "username": username_ },
                            { "$push": { "contacts": { "name": name, "username": username } } },
                            upsert=True
                        )
        else:
            flash("user not available")
    
    def add_contacts(self,user_id):
        
        user=mongo.db.user.find_one({"_id": ObjectId(user_id)}) 
        username_=user["username"]
        
        form=ContactForm()
        if form.validate_on_submit():
                name=form.name.data
                username=form.username.data
                try:
                    self.insertContact(name,username,username_)
                except TypeError:
                    None
                
        return render_template("add_contact.html",form=form)
        
    
    def del_contacts(self,user_id):
        
        None
    
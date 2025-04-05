from flask import render_template, flash, jsonify
from app.blueprints.auth.form import RegistrationForm, LoginForm
from app.extensions import mongo 
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies, decode_token
)
from bson import ObjectId

class Auth_Model():
    
    def pass_hash_generator(self,password):
        pass_hash = generate_password_hash(password)
        return pass_hash
    
    def pass_hash_check(self,password_hash,password):
        return check_password_hash(password_hash, password)
    
    def register_user(self):
        form= RegistrationForm()
        if form.validate_on_submit():
            
            # genrating password hash from password
            pass_hash=self.pass_hash_generator(form.password.data)
            
            # fetching user data from form
            username = form.username.data
            email = form.email.data
            
            # see if email or username already exist
            username_exist = mongo.db.user.find_one({"username": username })
            email_exist = mongo.db.user.find_one({"email": email })
            
            if (username_exist and email_exist) == None:
                # inserting user data in mongodb
                user_data = {
                    "username": username,
                    "email":email,
                    "password_hash":pass_hash
                }
                mongo.db.user.insert_one(user_data)
            else:
                flash("Username or email address already taken", "failure")
            
            
        return render_template("register.html",title="Registration", form=form)
    
    def login_user(self):
        
        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            
            user = mongo.db.user.find_one({"username":username})
            
            if user and self.pass_hash_check(user['password_hash'],password):
                user_id = str(user["_id"])
                access_token = create_access_token(identity=user_id, fresh=True)
                refresh_token = create_refresh_token(identity=user_id)
                
                # storing refresh token hash in database
                user_filter = {"username":user['username']}
                user_update = {"$set":{"refresh_token": refresh_token}}
                mongo.db.user.update_one(user_filter, user_update)
                
                response = jsonify(msg="Login successful")
                set_access_cookies(response, access_token)
                set_refresh_cookies(response, refresh_token)
                
            
            else:
                flash("invalid credentials","failure")    
                     
        return render_template('login.html',form=form,title='Login')
    
    
    def token_refresh(self, refresh_token):
        id = get_jwt_identity()
        #decode=decode_token(refresh_token)
        #inc_id=decode['jti']
        user = mongo.db.user.find_one({"_id": ObjectId(id)})
        #decode_stored = decode_token(user['refresh_token'])
        #str_id = decode_stored['jti']
        #print(f"inc: {inc_id}")
        #print(f"str_id: {str_id}")
        if user is None or "refresh_token" not in user:
            return jsonify(msg="User not found or token missing"), 401

        stored_token_hash = user["refresh_token"]

        # Compare hash of the refresh token
        if not (stored_token_hash == refresh_token):
            #print(f"stored_token: {user['refresh_token']}")
            #print(f"incomming_token: {refresh_token}")
            return jsonify(msg="Invalid refresh token from auth model"), 401

        new_access_token = create_access_token(identity=id, fresh=False)
        response = jsonify(msg="Token refreshed")
        set_access_cookies(response, new_access_token)
        return response

    
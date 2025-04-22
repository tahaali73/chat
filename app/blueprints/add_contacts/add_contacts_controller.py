from flask import Blueprint, request
from app.blueprints.add_contacts.add_contact_model import AddContact_Model
from flask_jwt_extended import jwt_required, get_jwt_identity

add_contact_bp = Blueprint("add_contacts", __name__, template_folder="templates")

model = AddContact_Model()

@add_contact_bp.route('/contacts/add-contacts',methods=['GET','POST'],endpoint='add_contacts')
@jwt_required()
def add_contacts(): 
    user_id = get_jwt_identity()
    return model.add_contacts(user_id)

@add_contact_bp.route('/contacts/del-contacts',methods=['POST'],endpoint='del_contacts')
@jwt_required()
def del_contacts(): 
    user_id = get_jwt_identity()
    return model.del_contacts(user_id)

@add_contact_bp.route('/contacts/update-contacts',methods=['PATCH'],endpoint='update_contacts')
@jwt_required()
def update_contacts(): 
    user_id = get_jwt_identity()
    return model.update_contacts(user_id)
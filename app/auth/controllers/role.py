'''
  holds the blueprint routes for roles
'''
from typing import List
from flask import Blueprint, jsonify, request
from firebase_admin import auth as fb_auth, exceptions
from . import Role

# role bp wip
role_bp = Blueprint('role', __name__)

@role_bp.route('/', methods=['GET', 'POST'])
def role():
  if request.method == 'GET':
    # get all roles
    roles: List[Role] = Role.query.all()
    return jsonify({'roles': [role.to_dict() for role in roles]})
  elif request.method == 'POST':
    body = request.get_json()
    print(body)
    new_role_name = body.get('role', None)
    new_role_description = body.get('description', None)
    
    if not new_role_name:
      return jsonify({'message': 'No role name provided'}), 400
    
    # verufy role does not exist
    exist_role = Role.query.filter_by(name=new_role_name).first()
    
    if exist_role:
      return jsonify({'message': 'Role already exists'}), 400
    
    # create role
    try:
      new_role = Role(name=new_role_name, description=new_role_description, level=0).save_instance()
    except Exception as e:
      print(e)
      return jsonify({'message': 'Failed to create role'}), 400
    return jsonify(new_role)


@role_bp.route('/add_role', methods=['GET'])
def add_role():
  # update firebase claims
  try:
    # auth.set_custom_user_claims('Lzm5MyCVMddIp9XAejqwnSBJvPk2', {'Roles': ["Admin", "Verified"]})
    fb_auth.update_user('Lzm5MyCVMddIp9XAejqwnSBJvPk2', custom_claims={'Roles': ["User"]})
  except ValueError:
    return jsonify({'message': 'Invalid User ID'})
  except exceptions.FirebaseError:
    return jsonify({'message': 'User not found'})
  
  user = fb_auth.get_user('Lzm5MyCVMddIp9XAejqwnSBJvPk2')
  print(user.custom_claims)
  print(user.__dict__)
  return jsonify({'message': 'Role added'})


@role_bp.route('/<role_name>', methods=['DELETE'])
def delete_role(role_name: str):
  # body = request.get_json()
  # # vars
  # role_name = body.get('role', None)
  print(role_name)
  
  # checks
  if not role_name:
    return jsonify({'message': 'No Role name provided'}), 400
  
  role: Role|None = Role.query.filter_by(name=role_name).delete()
  
  print(role)
  
  return jsonify({'message': 'The provided role does not exist'})
'''
  holds the blueprint routes for users
'''
from flask import Blueprint, jsonify, request
from firebase_admin import auth
from . import User, Role

# user bp wip
user_bp = Blueprint('user', __name__)
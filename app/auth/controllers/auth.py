from operator import itemgetter
from flask import Blueprint, request, jsonify, make_response
from firebase_admin import auth
from . import require_authorization, validate_token_or_raise, get_user_by_filter_or_raise, \
verify_session_or_raise, set_session_cookie_response_or_raise, create_user_or_raise,\
is_payload_authtime_less, RequestException, UnauthorizedException,\
get_session_cookie

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/verify_session', methods=['GET'])
def verify_session():
  session_cookie = get_session_cookie()
  user_payload = verify_session_or_raise(session_cookie)
  return jsonify(user_payload)
  

@auth_bp.route('/sessionLogin', methods=['POST'])
def signin():
  body = request.get_json()
  token, is_new_user = (body.get(key, None) for key in ["token", "is_new_user"])

  if not token:
    return jsonify({'message': 'No token provided'}), 400
  # verify claims
  user_payload = validate_token_or_raise(token)
  
  # token valid
  user_id, email, email_verified, = \
    itemgetter('user_id', 'email', 'email_verified')(user_payload)
  
  # try getting user to check if new user
  user = get_user_by_filter_or_raise(user_id=user_id)
  
  if user:
    # get session cookie and return
    response = set_session_cookie_response_or_raise(user_payload, token)
    return response
  
  # new user, get vars, create
  user = create_user_or_raise(user_id, email, email_verified, [])
  
  # get session cookie and return
  print("user: ", user.to_dict())
  response = set_session_cookie_response_or_raise(user_payload, token)
  return response


@auth_bp.route('/sessionLogout', methods=['POST'])
def signout():
  session_cookie = request.cookies.get('session-mb')
  if not session_cookie:
    # assume session is out?
    return jsonify({'message': 'No session_cookie provided'}), 200
  # delete session cookie
  response = make_response(jsonify({'status': 'Logged Out'}), 200)
  response.set_cookie(
    'session-mb', expires=0, httponly=True, secure=True, samesite='None')
  return response


@auth_bp.route('/register', methods=['POST'])
def register():
  token = request.get_json()['token']
  #  check token
  if not token:
    raise RequestException(description="No token provided")
  # verify claims
  user_payload = validate_token_or_raise(token)
  # verify auth time
  if not is_payload_authtime_less(user_payload, 5):
    raise UnauthorizedException(description="Recent sign in required")

  # create user
  user = create_user_or_raise(user_payload['user_id'], user_payload['email'], user_payload['email_verified'], [])
  print("user: ", user.to_dict())
  response = set_session_cookie_response_or_raise(user_payload, token)
  return response
  

@auth_bp.route('/verify_token', methods=['POST'])
def verify_token():
  body = request.get_json()
  token = body.get('token', None)
  if not token:
    return jsonify({'message': 'No token provided'}), 400  
  # verify token
  try:
    valid = auth.verify_id_token(token)
  except auth.ExpiredIdTokenError:
    return jsonify({'message': 'Expired Token'})
  except auth.RevokedIdTokenError:
    return jsonify({'message': 'Revoked Token'})
  except auth.InvalidIdTokenError:
    return jsonify({'message': 'Invalid Token'})
  return jsonify({'message': 'token is valid'})


@auth_bp.route('/profile', methods=['GET', 'POST'])
@require_authorization(["Admin"])
def access_restricted_content():
  return jsonify({'message': 'You have access to this content'})
  
  
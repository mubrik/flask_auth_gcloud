'''
  Contains user authentication/authorization code for app
'''
import time, datetime
from typing import Any, Dict, List
from functools import wraps
from flask import request, jsonify, make_response, Response, current_app as app
from firebase_admin import auth as fb_auth, exceptions
from google.auth.exceptions import TransportError
from dotenv import load_dotenv
from ..models import User, Role
from ...error_handlers import RequestException, UnauthorizedException

# load env
load_dotenv()


def is_payload_authtime_less(payload: Dict[str, Any], minutes: int) -> bool:
  """Check if the payload auth_time is less than supllied minutes
  Args:
    token (str): firebase auth id token
  Returns:
    bool: True if the token is valid and the auth_time is less than supllied minutes
  """
  return time.time() - payload['auth_time'] < minutes * 60


def get_session_cookie() -> str|None:
  '''This way i can change session cookie name from sngle location'''
  return request.cookies.get('_session_mb')


def set_session_cookie(response: Response, cookie: str, expires: datetime) -> Response:
  response.set_cookie(
    '_session_mb', cookie, expires=expires, httponly=True, secure=True, samesite='None')
  return response
  

def verify_session_or_raise(session_cookie: str) -> Dict[str, Any]:
  """Verify firebase auth session cookie or raise UnauthorizedException
  Args:
    session_cookie (str): firebase auth session cookie
  Raises:
    UnauthorizedException: Authentication error
  Returns:
    Dict[str, Any]: The user client claims
  """
  try:
    decoded_token = fb_auth.verify_session_cookie(session_cookie)
  except ValueError:
    raise UnauthorizedException(description='Invalid token')
  except fb_auth.ExpiredSessionCookieError:
    # change this to a redirect to login page
    raise UnauthorizedException(description='Session cookie expired. Please login again.')
  except fb_auth.RevokedSessionCookieError:
    raise UnauthorizedException(description='Session cookie revoked. Please login again.')
  except fb_auth.InvalidSessionCookieError:
    raise UnauthorizedException(description='Invalid session cookie. Please login again.')
  except TransportError:
    # most likely a network error, log this?
    app.logger.error('Failed to fetch certificate', exc_info=True)
    raise UnauthorizedException(description='Failed to fetch certificate, try again later')
  return decoded_token


def check_permission(cookie: str, role: str|List):
  try:
    decoded_token: Dict[str, Any] = verify_session_or_raise(cookie)
    roles = decoded_token['Roles']
  except ValueError:
    raise UnauthorizedException(description='Invalid token')
  except fb_auth.ExpiredSessionCookieError:
    raise UnauthorizedException(description='Session cookie expired. Please login again.')
  except fb_auth.RevokedSessionCookieError:
    raise UnauthorizedException(description='Session cookie revoked. Please login again.')
  except fb_auth.InvalidSessionCookieError:
    raise UnauthorizedException(description='Invalid session cookie. Please login again.')
  if not isinstance(role, list):
    role = [role]
  for r in role:
    if r in roles:
      return True
  raise UnauthorizedException(403, 'Forbidden', 'You are not authorized to perform this action.')


def set_session_cookie_response_or_raise(payload: dict, id_token: str) -> Response:
  try:
    # To ensure that cookies are set only on recently signed in users, check auth_time in
    # Only process if the user signed in within the last 5 minutes.
    if is_payload_authtime_less(payload, 5):
      #  Set session expiration to 5 days.
      expires_in = datetime.timedelta(days=5)
      expires = datetime.datetime.now() + expires_in
      session_cookie = fb_auth.create_session_cookie(id_token, expires_in=expires_in)
      response = make_response(jsonify({'status': 'success'}), 200)
      # same site="None" is required for the session cookie to work in all browsers and localhost
      # response.set_cookie(
      #   'session-mb', session_cookie, expires=expires, httponly=True, secure=True, samesite='None')
      return set_session_cookie(response, session_cookie, expires)
    # User did not sign in recently. To guard against ID token theft, require
    # re-authentication.
    raise UnauthorizedException(description='Recent sign in required')
  except (ValueError, fb_auth.InvalidIdTokenError):
    raise UnauthorizedException(description='Invalid ID token')
  except exceptions.FirebaseError:
    raise UnauthorizedException(description='Failed to create a session cookie')
  
  
def validate_token_or_raise(token: str) -> Dict[str, Any]:
  """Validate firebase auth token or raise UnauthorizedException
  Args:
    token (str): firebase auth id token
  Raises:
    UnauthorizedException: Authentication error
  Returns:
    Dict[str, Any]: The user client claims
  """
  try:
    decoded_token = fb_auth.verify_id_token(token)
  except ValueError:
    raise UnauthorizedException(description='Invalid token')
  except fb_auth.ExpiredIdTokenError:
    raise UnauthorizedException(description='Token expired. Please login again.')
  except fb_auth.RevokedIdTokenError:
    raise UnauthorizedException(description='Token revoked. Please login again.')
  except fb_auth.InvalidIdTokenError:
    raise UnauthorizedException(description='Invalid Token. Please login again.')
  return decoded_token


def require_authentication(func):
  def wrapper(*args, **kwargs):
    session_cookie = request.cookies.get('session-mb')
    if not session_cookie:
      # Session cookie is unavailable. Force user to login. can be a redirect
      raise UnauthorizedException(description='Session cookie unavailable. Please login.')
    try:
      verify_session_or_raise(session_cookie)
    except ValueError:
      raise UnauthorizedException(description='Invalid token')
    return func(*args, **kwargs)
  return wrapper


def require_authorization(role: str|List):
  def wrapper(func):
    @wraps(func)
    def inner(*args, **kwargs):
      session_cookie = request.cookies.get('session-mb')
      if not session_cookie:
        # Session cookie is unavailable. Force user to login. can be a redirect
        print("No session cookie")
        raise UnauthorizedException(description='Session cookie unavailable. Please login.')
      check_permission(session_cookie, role)
      return func(*args, **kwargs)
    return inner
  return wrapper
  

def create_user_or_raise(user_id: str, email: str, email_verified: bool, roles: List[Role]):
  # create user
  try:
    new_user = User(user_id=user_id, email=email, email_verified=email_verified)\
                .save_instance()
    return new_user
  except Exception:
    app.logger.error('Failed to create user', exc_info=True)
    raise RequestException(400, description='Failed to create user')


def get_user_by_filter_or_raise(user_id: str|int) -> User|None:
  try:
    user: User|None = User.query.filter_by(user_id=user_id).first()
    return user
  except Exception:
    app.logger.error('Failed to get user', exc_info=True)
    raise RequestException(400, description='Failed to get user') 

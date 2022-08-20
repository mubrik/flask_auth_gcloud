"""_summary_
App wide flask error handlers
"""
from flask import jsonify
from dataclasses import dataclass, field
from typing import ClassVar

# error classes
@dataclass(frozen=True)
class BaseAuthException(Exception):
  info: ClassVar[str] = "flsk"

@dataclass(frozen=True)
class UnauthorizedException(BaseAuthException):
  code: int = 401
  error: str = field(default="unauthorized")
  description: str = field(default="Unauthorized, Unable to authenticate.")
  
@dataclass(frozen=True)
class RequestException(BaseAuthException):
  code: int = 400
  error: str = field(default="bad request")
  description: str = field(default="Unable to process your request.")


# handlers
def handle_known_error(exception: BaseAuthException):
  return jsonify({
    'success': False,
    'code': exception.code,
    'error': exception.error,
    'message': exception.description
  }), exception.code

def handle_422(error):
  # bad syntax
  return jsonify({
    "success": False,
    "message": error.description if error.description is not None else "Error in Query/Data",
    "error": 422
  }), 422

def handle_404(error):
  # Not Found
  return jsonify({
    "success": False,
    "message": error.description if error.description is not None else "Resource not Found",
    "error": 404
  }), 404
  
def handle_400(error):
  # Not Found
  return jsonify({
    "success": False,
    "message": error.description if error.description is not None else "Bad Syntax",
    "error": 400
  }), 400

def handle_405(error):
  # Method Not Allowed
  return jsonify({
    "success": False,
    "message": error.description if error.description is not None else "Method not allowed",
    "error": 405
  }), 405

def handle_503(error):
  # Server cannot process the request
  return jsonify({
    "success": False,
    "message": error.description if error.description is not None else "System Busy",
    "error": 503
  }), 503
from os import environ as env
from dotenv import load_dotenv

# loadenv variable
load_dotenv()

# Statement for enabling the development environment
DEBUG = False

# Define the database - we are working with
DB_NAME = env.get('DB_NAME', None)
DB_USER = env.get('DB_USER', None)
DB_PASS = env.get('DB_PASS', None)
DB_HOST = env.get('DB_HOST', None)
DB_PORT = env.get('DB_PORT', None)
DB_ADAPTER = env.get('DB_ADAPTER', None)

# CHECK if all the variables are set
if not DB_NAME or not DB_PASS or not DB_HOST or not DB_PORT:
  raise ValueError('DB_NAME, DB_PASS, DB_HOST, DB_PORT are required')

# unix style socket path for gcloud app engine
SQLALCHEMY_DATABASE_URI = '{}://{}:{}@/{}?host={}'.format(DB_ADAPTER, DB_USER, DB_PASS, DB_NAME, DB_HOST)
# SQLALCHEMY_DATABASE_URI = f'{DB_ADAPTER}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# print queries if debug
SQLALCHEMY_ECHO = False
# over head
SQLALCHEMY_TRACK_MODIFICATIONS = False

DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data. 
SECRET_KEY = env.get('SECRET_KEY')

# flask-jwt, not in use atm
JWT_SECRET_KEY = env.get('JWT_SECRET_KEY')
JWT_TOKEN_LOCATION = ["headers", "cookies"]
JWT_COOKIE_SECURE = False if DEBUG else True # only send cookies over https, true for production

# bcrypt
BCRYPT_HANDLE_LONG_PASSWORDS = True
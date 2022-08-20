'''
  init file, set up the app
'''
import os, json, logging
from os import environ as env
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, init, migrate, upgrade
from flask_cors import CORS
# from flask_jwt_extended import JWTManager
# from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

# load env
load_dotenv()

# get env vars
APP_ENV = env.get('GAE_ENV', '')
CORS_ORIGINS_LIST = env.get('CORS_ORIGINS_LIST', '').split(',')

# middlewares
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()

# configure logging
def setup_logging():
  """
  setup for logging, should move to a separate file or .conf file
  """
  # dir for logs
  if APP_ENV.startswith('standard'):
    # gcloud production environment, use google cloud logging
    import google.cloud.logging
    from google.cloud.logging.handlers import CloudLoggingHandler, setup_logging
    
    client = google.cloud.logging.Client()
    handler = CloudLoggingHandler(client)
    logging.getLogger().setLevel(logging.INFO) # python root logger
    setup_logging(handler)
  else:
    # dev env, log to file
    root = os.path.dirname(os.path.abspath(__file__))
    logdir = os.path.join(root, env.get('LOG_DIR', 'logs'))
    if not os.path.exists(logdir):
      os.mkdir(logdir)
    log_file = os.path.join(logdir, env.get('LOG_FILE', 'app.log'))
  
    # configure formatters
    detailed_format = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s')
    simple_format = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s')
    
    # configure handlers
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(detailed_format)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(simple_format)
    
    # configure logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
  

# configure firebase
def setup_firebase():
  """_summary_
    configure firebase with credential from env
  Returns:
      _type_: firebase app
  """
  import firebase_admin
  from firebase_admin import credentials
  
  gcred = env.get('GCLOUD_APP_CRED', None)
  if gcred is not None:
    cred = credentials.Certificate(json.loads(gcred))
  default_fb_app = firebase_admin.initialize_app(cred if gcred is not None else None)
  return default_fb_app


# configure db migrations
def migrate_db():
  """_summary_
    migrate db
  """
  init(directory='/tmp/migrations')
  migrate(directory='/tmp/migrations')
  upgrade(directory='/tmp/migrations')


# flask function factory
def create_app(config_name: str|None = None) -> Flask:
  # configure logging
  setup_logging()
  # firebase
  setup_firebase()
  # create app
  app = Flask(__name__)
  # get config
  if APP_ENV.startswith('standard'):
    # gcloud production environment
    app.config.from_object('configs.production')
    # configure werzeug proxy fix
    from werkzeug.middleware.proxy_fix import ProxyFix

    app.wsgi_app = ProxyFix(
      app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )
  elif config_name is not None:
    # custom env
    app.config.from_object(config_name)
  else:
    # dev env
    app.config.from_object('configs.development')
  
  # initialize middlewares
  db.init_app(app)
  migrate.init_app(app, db)
  cors.init_app(app, resources={r"/api/*": {
    "origins": CORS_ORIGINS_LIST,
    "supports_credentials": True,
  }})
  
  # initialize blueprints
  from .auth.controllers.role import role_bp
  from .auth.controllers.auth import auth_bp
  
  app.register_blueprint(role_bp, url_prefix='/api/role')
  app.register_blueprint(auth_bp, url_prefix='/api/auth')
  
  # register error handlers
  from .error_handlers import BaseAuthException, handle_known_error, handle_422, handle_503, handle_400,\
    handle_404, handle_405
  
  app.register_error_handler(BaseAuthException, handle_known_error)
  app.register_error_handler(422, handle_422)
  app.register_error_handler(503, handle_503)
  app.register_error_handler(400, handle_400)
  app.register_error_handler(404, handle_404)
  app.register_error_handler(405, handle_405)
  
  # register cli functons
  # from .utils import app_cli
  
  # app.cli.add_command(app_cli)
  
  # testing
  # db.create_all(app=app)
  
  return app


if __name__ == "__main__":
  mainapp = create_app()
  mainapp.run(debug=True)

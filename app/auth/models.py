'''
  Models for user
'''
from app import db
from sqlalchemy.ext.hybrid import hybrid_property, Comparator
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CaseInsensitiveComparator(Comparator):
  def __eq__(self, other):
    return func.lower(self.__clause_element__()) == func.lower(other)

# table for many to many relationship
user_role = db.Table('user_role',
  db.Column('user_id', db.String, db.ForeignKey('users.user_id'), primary_key=True),
  db.Column('role_id', db.Integer, db.ForeignKey('roles.role_id'), primary_key=True)
)

class User(db.Model):
  '''
    User Model
    Lean, to be used for Authentication/Authorization
  '''
  __tablename__ = 'users'

  user_id = db.Column(db.String, primary_key=True)
  email = db.Column(db.String(128), nullable=False, unique=True)
  username = db.Column(db.String(128), nullable=False, default="Anonymous")
  email_verified = db.Column(db.Boolean, nullable=False, default=False)
  roles = db.relationship('Role', secondary='user_role', backref=db.backref('users', lazy='dynamic'))

  def __init__(self, user_id: str, email: str, email_verified: bool):
    self.user_id = user_id
    self.email = email
    self.email_verified = email_verified
  
  def save_instance(self):
    db.session.add(self)
    db.session.commit()
    return self
    
  def commit_instance(self):
    db.session.commit()
    return self.to_dict()
  
  def get_roles(self):
    return [role for role in self.roles]

  def to_dict(self):
    return {
      "user_id": self.user_id,
      "username": self.username,
      "email": self.email,
      "email_verified": self.email_verified,
    }
  
  def __repr__(self):
    return f'<User id:{self.user_id} username:{self.username}>'
  

class Role(db.Model):
  '''
    Role Model
  '''
  __tablename__ = 'roles'

  role_id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128), nullable=False, unique=True)
  description = db.Column(db.String, nullable=False)
  level = db.Column(db.Integer, nullable=False, default=0)

  def __init__(self, name: str, description: str, level: int):
    self.name = name
    self.description = description if description else "base"
    self.level = level
    
  def save_instance(self):
    db.session.add(self)
    db.session.commit()
    return self.to_dict()

  def to_dict(self):
    return {
      "role_id": self.role_id,
      "name": self.name,
      "description": self.description
    }
    
  @hybrid_property
  def i_name(self):
    return self.name.lower()

  @i_name.comparator
  def i_name(cls):
    return CaseInsensitiveComparator(cls.name)
  
  def __repr__(self):
    return f'<Role id:{self.role_id} name:{self.name}>'
  
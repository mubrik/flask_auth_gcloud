import click
from flask.cli import AppGroup
from app import db


# create a cli group
app_cli = AppGroup('app')

@app_cli.command('dbtables')
@click.argument('action')
def db_tables(action='create'):
  if action == 'create':
    db.create_all()
  elif action == 'drop':
    db.drop_all()
    

@app_cli.command('dbrows')
@click.argument('action')
def db_rows(action='create'):
  # run action
  pass

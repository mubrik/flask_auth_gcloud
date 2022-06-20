# Flask Modular app base

## Description

- This contains the base folder structure to be used for flask backend deployment
- Folder structure is modularized to allow plug and play of new modules/functions
- Follows Test Driven Development with unittest cases

## Installation

- make a clone of repository
- python>=3.5 app uses typing feature so this is an important requirement

### Install Dependencies

- Create a virtual environment

```bash
pip install virtualenv
virtualenv <environment_name>
```

- Activate the environment

linux/Git Bash:

```bash
source <environment_name>/bin/activate
```

Windows:

```bash
'<environment_name>\Scripts\activate'
```

- Install dependencies

```bash
pip install -r requirements.txt
```

## Set up the Database

This isnt a requirement, the default DB type used is SQLLite which is created

With Postgres running, create a database:

```bash
createdb dbname
```

## Set up your Enviroment Variables

- create a .env file in the root folder with the following variables, example:

```bash
DEBUG=True
DB_URI='postgresql://<postgresusername>:<postgrespassword>@localhost:5432/<dbname>'
TEST_DB_URI='postgresql://<postgresusername>:<postgrespassword>@localhost:5432/<dbname>'
DB_NAME='base.db' # if not set db will be test.db
TEST_DB_NAME='base_test.db'
FLASK_RUN_MODE=development # or testing
DB_TYPE=sqlite # or postgres
```

Please make sure the database name matches which you created above

## Run App

- using flask

```bash
flask run
```

- top module package

```bash
python run.py
```

## Run Test

- To run tests you need to set the `FLASK_RUN_MODE` environment variable to testing
- You also need to set the DB_TYPE to match the DB in use

```bash
TEST_DB_URI='postgresql://<postgresusername>:<postgrespassword>@localhost:5432/<dbname>'
TEST_DB_NAME='dbname
FLASK_RUN_MODE=testing
DB_TYPE=sqlite # or postgres
```

- To start tests, run:

```bash
flask run
```

## Database Creation/Drop

- In another terminal(activated) you have commands available to manipulate the db
  to drop db tables:

```bash
flask app dbtables drop
```

to add db tables:

```bash
flask app dbtables create
```

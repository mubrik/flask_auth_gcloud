# Flask Modular app base

## Description

- This contains the base folder structure to be used for flask backend deployment
- Folder structure is modularized to allow plug and play of new modules/blueprints
- Google firebase for authorization

## Installation

- make a clone of repository
- python=3.10 app uses typing feature so this is an important requirement

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

### local development

## Set up the Database

With Postgres running, create a database:

```bash
createdb <dbname>
```

## Set up your Enviroment Variables

- create a .env file in the root folder with the following variables, example:

```bash
DB_URI='postgresql://<username>:<password>@<host>:<port>/<dbname>'
CORS_ORIGINS_LIST="http://127.0.0.1:3000,http://localhost:3000"
SECRET_KEY='some-secret-string'
JWT_SECRET_KEY='some-secret-string'
# GCLOUD_APP_CRED is from firebase service account, not necessary when deploying to GCLOUD but necessary for other providers
GCLOUD_APP_CRED='{
  "type": "service_account",
  "project_id": "project_id",
  "private_key_id": "private_key_id",
  "private_key": "private_key",
  "client_email": "client_email",
  "client_id": "client_id",
  "auth_uri": "auth_uri",
  "token_uri": "token_uri",
  "auth_provider_x509_cert_url": "auth_provider_x509_cert_url",
  "client_x509_cert_url": "client_x509_cert_url"}'
}' 

```

Please make sure the database name matches which you created above

## Run App

- using flask

```bash
flask run
```

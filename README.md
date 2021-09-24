<img src="https://cdn3.iconfinder.com/data/icons/logos-and-brands-adobe/512/267_Python-512.png"
     alt="Markdown Python icon"
     height="30px"
/>&nbsp;&nbsp;&nbsp;
<img src="https://cdn.onlinewebfonts.com/svg/img_437027.png"
     alt="Markdown Flask icon"
     height="30px"
/>&nbsp;&nbsp;
<img src="https://wiki.postgresql.org/images/a/a4/PostgreSQL_logo.3colors.svg"
     alt="Markdown Postgre icon"
     height="30px"
/>&nbsp;&nbsp;&nbsp;

# Food App

Backend server for a creating and searching recipes.

## Usage

The app requires an `.env` file with the following variables:

```
DB_URI=postgresql://<username>:<password>@<database_url>:<port>/<database_name>
DB_TEST_URI=postgresql://<username>:<password>@database_url:<port>/<test_database_name>
HUNTER_KEY=<api key provided by Hunter.io>
CLEARBIT_KEY=<api key provided by Clearbit>
SECRET_KEY=<flask_secret_key>
```

Before running the app, please create test database and aquire api keys from
[Hunter.io](https://hunter.io/) and [Clearbit](https://clearbit.com/).

### Requirements

Python3 installed (3.2 or higher) -\*\* [Python](https://www.python.org/)


It is advised to work in a virtual environment. Create one using the following command:

```
python -m venv venv
```

Activating **venv**:

- Windows OS:

```
./venv/Scripts/activate
```

- Windows OS (GitBash):

```
source ./venv/Scripts/activate
```

Install the required packages into the newly created venv:

```
pip install -r requirements.txt
```

Run the following commands to setup the tables in your database:

```
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```

To start the server run:

```
flask run
```

To test requests you can use workspace in Postman:
[Postman](https://www.getpostman.com/collections/7bd9bfd0fe830ef2e82e)

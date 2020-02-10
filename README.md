# YABA (Yet Another Blogging App)

----
## What is YABA?
YABA is just another blogging app made for trying new technologies. It's rather simple but still more complex than the average TODO app and it was inspired by the Real World example app [Conduit](https://github.com/gothinkster/realworld).

----
## Stack
This backend REST API was made using the Python framework Flask and PostgreSQL for the database. Python version used is 3.8.0.

----
## Installation and usage
*Note: It's recommended that you use a Virtual Environment library to manage Python dependencies such as **venv** or **virtualenv**. Also, it's strictly necessary that you use PostgreSQL as your database too, because the app make use of its special data type **ARRAY** to simplify the management of user defined tags.*

1. Clone project.
2. cd into project folder.
3. Install dependencies.

        pip install -r requirements.txt

4. Copy *.env.example* file and overwrite it accordingly.

        cp .env.example .env

5. Run migrations

        python manage.py upgrade

6. Run development server

        python run.py

----
## Libraries used
* Flask
* Flask-JWT-Extended
* bcrypt
* SQLAlchemy
* psycopg2
* marshmallow
* pytest
* flake8

----
## Tests
Run tests using

    python -m pytest -s

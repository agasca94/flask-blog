import os
from dotenv import load_dotenv, find_dotenv
from src.app import create_app


load_dotenv(find_dotenv())

env_name = os.getenv('FLASK_ENV')

if __name__ == '__main__':
    app = create_app(env_name)
    app.run()

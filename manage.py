import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from src.app import create_app, db
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

env_name = os.getenv('FLASK_ENV')
app = create_app(env_name)

migrate = Migrate(app=app, db=db)
manager = Manager(app=app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

# Avoid circular references
from src.utils import identity_loader, user_loader # noqa

jwt.user_identity_loader(identity_loader)
jwt.user_loader_callback_loader(user_loader)

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from src.exceptions import missing_token_handler, invalid_token_handler


db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
cors = CORS()

# Avoid circular references
from src.utils import identity_loader, user_loader # noqa

jwt.user_identity_loader(identity_loader)
jwt.user_loader_callback_loader(user_loader)
jwt.unauthorized_loader(missing_token_handler)
jwt.invalid_token_loader(invalid_token_handler)

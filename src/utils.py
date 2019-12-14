from src.models import User


def user_loader(_id):
    return User.get_one(_id)


def identity_loader(user):
    return user.id

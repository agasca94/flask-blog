from src.models import User
import os
import uuid


def user_loader(_id):
    return User.get_one(_id)


def identity_loader(user):
    return user.id


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}


def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_file(file, path, allowed_extensions=ALLOWED_EXTENSIONS):
    if allowed_file(file.filename, allowed_extensions):
        extension = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{extension}"

        file.save(os.path.join(path, filename))

        return filename

    return None


def delete_file(path, filename):
    os.remove(os.path.join(path, filename))

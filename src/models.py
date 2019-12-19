import datetime
from src.extensions import db, bcrypt


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.created_at = datetime.datetime.now()
        self.modified_at = datetime.datetime.now()
        self.set_password(password)

    def save(self):
        self.modified_at = datetime.datetime.now()
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        for attr, value in kwargs.items():
            if attr == 'password':
                self.set_password(value)
            else:
                setattr(self, attr, value)
        self.save()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return User.query.all()

    @staticmethod
    def get_one(_id):
        return User.query.get(_id)

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(
            password,
            rounds=10
        ).decode('utf-8')

    def check_hash(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def __repr__(self):
        return f"<id {self.id}>"


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    contents = db.Column(db.Text, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, title, contents, owner_id):
        self.title = title
        self.contents = contents
        self.owner_id = owner_id
        self.created_at = datetime.datetime.now()
        self.modified_at = datetime.datetime.now()

    def save(self):
        self.modified_at = datetime.datetime.now()
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        self.save()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Post.query.all()

    @staticmethod
    def get_one(_id):
        return Post.query.get(_id)

    def __repr__(self):
        return f"<id {self.id}>"

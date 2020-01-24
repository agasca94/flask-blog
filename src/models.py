import datetime as dt
from sqlalchemy import select, func, bindparam
from sqlalchemy.orm import column_property, aliased
from sqlalchemy.ext.hybrid import hybrid_property
from flask_jwt_extended import current_user
from src.extensions import db, bcrypt


favorites_assoc = db.Table(
    'favorites_assoc',
    db.Column(
        'user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True
    ),
    db.Column(
        'post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True
    )
)
favaliased = aliased(favorites_assoc)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    bio = db.Column(db.String(300), nullable=True)
    username = db.Column(db.String(128), nullable=False, unique=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=True)
    posts = db.relationship(
        'Post',
        # Eager load the author of each post using an INNER JOIN
        # NOTE: joined loading is more commonly used to load
        # many-to-one not null relationships, not collections
        backref=db.backref('author', lazy='joined', innerjoin=True),
        lazy='dynamic'
    )
    comments = db.relationship(
        'Comment',
        # Eager load the author of each comment using an INNER JOIN
        backref=db.backref('author', lazy='joined', innerjoin=True),
        lazy=True
    )
    created_at = db.Column(
        db.DateTime, nullable=False, default=dt.datetime.now
    )
    modified_at = db.Column(
        db.DateTime, nullable=False, default=dt.datetime.now
    )

    def __init__(self, name, username, email, password, bio=''):
        self.name = name
        self.email = email
        self.username = username
        self.bio = bio
        self.set_password(password)

    def save(self):
        self.modified_at = dt.datetime.now()
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

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

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
    description = db.Column(db.Text, nullable=False)
    contents = db.Column(db.Text, nullable=False)
    comments = db.relationship(
        'Comment',
        backref='post',
        lazy='dynamic',
        cascade='save-update, merge, delete, delete-orphan'
    )
    owner_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False
    )
    favorited_by = db.relationship(
        'User',
        secondary=favorites_assoc,
        backref=db.backref('favorites', lazy='dynamic'),
        # Eager load the users who favorited this post using an
        # additional SELECT IN query
        lazy='selectin'
    )
    created_at = db.Column(
        db.DateTime, nullable=False, default=dt.datetime.now
    )
    modified_at = db.Column(
        db.DateTime, nullable=False, default=dt.datetime.now
    )

    def __init__(self, title, description, contents, owner_id):
        self.title = title
        self.description = description
        self.contents = contents
        self.owner_id = owner_id

    def save(self):
        self.modified_at = dt.datetime.now()
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        self.save()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def favorite(self, user):
        self.favorited_by.append(user)
        self.save()

    def unfavorite(self, user):
        try:
            self.favorited_by.remove(user)
            self.save()
        except ValueError:
            pass

    @staticmethod
    def get_all():
        return Post.query.all()

    @staticmethod
    def get_one(_id):
        return Post.query.get(_id)

    @hybrid_property
    def favorites_count(self):
        return len(self.favorited_by)

    def __repr__(self):
        return f"<id {self.id}>"


Post.is_favorited = column_property(
    select(
        [func.count(favaliased.c.post_id) == 1]
    ).where(
        favaliased.c.post_id == Post.id
    ).where(
        favaliased.c.user_id == bindparam(
            'current_user_id',
            callable_=lambda: current_user.id if current_user else None
        )
    )
)


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    contents = db.Column(db.Text, nullable=False)
    post_id = db.Column(
        db.Integer, db.ForeignKey('posts.id'), nullable=False
    )
    author_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False
    )
    created_at = db.Column(
        db.DateTime, nullable=False, default=dt.datetime.now
    )
    modified_at = db.Column(
        db.DateTime, nullable=False, default=dt.datetime.now
    )

    def __init__(self, post_id, contents, author_id):
        self.post_id = post_id
        self.contents = contents
        self.author_id = author_id

    def save(self):
        self.modified_at = dt.datetime.now()
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        self.save()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

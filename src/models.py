import datetime
from src.extensions import db, bcrypt
import datetime as dt
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import query_expression, with_expression
from flask_jwt_extended import current_user


favorites_assoc = db.Table(
    'favorites_assoc',
    db.Column(
        'user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True
    ),
    db.Column(
        'post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True
    )
)


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
        lazy=True
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
        lazy='dynamic'
    )
    owner_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False
    )
    favorited_by = db.relationship(
        'User',
        secondary=favorites_assoc,
        backref=db.backref('favorites', lazy=True),
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
    is_favorited = query_expression()

    def __init__(self, title, description, contents, owner_id):
        self.title = title
        self.description = description
        self.contents = contents
        self.owner_id = owner_id

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
    def with_favorites():
        query = Post.query
        if current_user:
            # Query the posts which have been favorited by the current user
            # Uses the association table favorites_assoc
            subquery = db.session.query(
                Post.id,
                Post.favorited_by.any(
                    User.id == current_user.id
                ).label('is_favorited')
            ).subquery()

            # Outer join the previous subquery with the base query and
            # retrieve the boolean value
            query = Post.query.options(
                with_expression(Post.is_favorited, subquery.c.is_favorited)
            ).outerjoin(
                subquery, Post.id == subquery.c.id
            )

        return query

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

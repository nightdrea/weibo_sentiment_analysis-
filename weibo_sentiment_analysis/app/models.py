from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(60), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class WeiboPost(db.Model):
    __tablename__ = 'weibo_posts'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False, index=True)
    publish_time = db.Column(db.DateTime, nullable=False, index=True)
    likes = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    reposts = db.Column(db.Integer, default=0)
    ip_location = db.Column(db.String(100), index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comments = db.relationship('WeiboComment', backref='post', lazy=True)

    def __repr__(self):
        return f"WeiboPost('{self.author}', '{self.publish_time}')"

class WeiboComment(db.Model):
    __tablename__ = 'weibo_comments'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('weibo_posts.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    commenter = db.Column(db.String(100), nullable=False, index=True)
    comment_time = db.Column(db.DateTime, nullable=False, index=True)
    likes = db.Column(db.Integer, default=0)
    ip_location = db.Column(db.String(100), index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"WeiboComment('{self.commenter}', '{self.comment_time}')"

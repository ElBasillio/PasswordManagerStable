from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    accounts = db.relationship('Account', backref='owner', lazy='dynamic')
    vaults = db.relationship('Vault', backref='owner', lazy='dynamic')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    theme_preference = db.Column(db.String(20), default='light')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Vault(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    accounts = db.relationship('Account', backref='vault', lazy='dynamic')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    icon = db.Column(db.String(128))
    accounts = db.relationship('Account', backref='category', lazy='dynamic')

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

account_tags = db.Table('account_tags',
    db.Column('account_id', db.Integer, db.ForeignKey('account.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(64))
    encrypted_password = db.Column(db.String(256), nullable=False)
    url = db.Column(db.String(256))
    notes = db.Column(db.Text)
    icon = db.Column(db.String(128))
    is_favorite = db.Column(db.Boolean, default=False)
    password_expires_at = db.Column(db.DateTime)
    strength_score = db.Column(db.Integer)
    custom_fields = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vault_id = db.Column(db.Integer, db.ForeignKey('vault.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    tags = db.relationship('Tag', secondary=account_tags, lazy='subquery',
        backref=db.backref('accounts', lazy=True))

class AccountHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    field_name = db.Column(db.String(64), nullable=False)
    old_value = db.Column(db.String(256))
    new_value = db.Column(db.String(256))

class AccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    access_time = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(256))
    action = db.Column(db.String(64))
    status = db.Column(db.String(64))

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) 
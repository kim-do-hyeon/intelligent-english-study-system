# -*- encoding: utf-8 -*-
from flask_login import UserMixin
from apps import db, login_manager
from apps.authentication.util import hash_pass
class Users(db.Model, UserMixin):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value = value[0]
            if property == 'password':
                value = hash_pass(value)
            setattr(self, property, value)
    def __repr__(self):
        return str(self.username)

class Excel_Data(db.Model, UserMixin) :
    __tablename__ = 'excel_data'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.Text)
    active = db.Column(db.Integer)

class word_data(db.Model, UserMixin) :
    __tablename__ = 'word_data'
    id = db.Column(db.Integer, primary_key = True)
    chapter = db.Column(db.Text)
    number = db.Column(db.Integer)
    word = db.Column(db.Text)
    priority = db.Column(db.Integer)
    parts = db.Column(db.Text)
    mean = db.Column(db.Text)
    example = db.Column(db.Text)
    example_mean = db.Column(db.Text)

class gpt_data(db.Model, UserMixin) :
    __tablename__ = 'gpt_data'
    id = db.Column(db.Integer, primary_key = True)
    word1 = db.Column(db.Text)
    word2 = db.Column(db.Text)
    example = db.Column(db.Text)
    example_mean = db.Column(db.Text)
    pass_count = db.Column(db.Integer, default = 0)
    fail_count = db.Column(db.Integer, default = 0)
    rate = db.Column(db.Float, default = 0.0)
    bug_count = db.Column(db.Integer, default = 0)

class user_word_data(db.Model, UserMixin) :
    __tablename__ = 'user_word_data'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.Text)
    index = db.Column(db.Integer)

@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None

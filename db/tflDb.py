# -*- coding: utf-8 -*-
import sys
sys.path.append(".")
sys.path.append("..")
from config import (HELPER_PATH, LOG_PATH, LOG_FORMAT, PG_CONNECTION_STRING)
sys.path.append(HELPER_PATH)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = PG_CONNECTION_STRING
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(256), unique=False)
    role = db.Column(db.String(128), unique=False)

    def __init__(self, username, email, password, role):
        self.username = username
        self.email = email
        self.password = password
        self.role = role

    def __repr__(self):
        return '<User %r (%r)>' % (self.username, self.role)


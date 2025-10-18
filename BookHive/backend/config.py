from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "super_secret_key"

# MySQL Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/library_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

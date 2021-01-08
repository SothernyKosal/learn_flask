import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = '17549fef4cab2eb94950475d0de332ba'
#specify database location
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:sotherny@localhost:5432/flaskblog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#db is the instance of Sqlalchemy
db = SQLAlchemy(app)
migrate = Migrate(app,db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

#config Mail server (Gmail)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_USERNAME'] = 'sotherny@gmail.com'
# app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD')  
app.config['MAIL_PASSWORD'] = 'rzriehrnlbtssgih'
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER')
mail = Mail(app)

from flaskblog import routes
from flask import Flask, render_template, url_for, redirect, flash
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '17549fef4cab2eb94950475d0de332ba'
#specify database location
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:sotherny@localhost:5432/flaskblog'
#db is the instance of Sqlalchemy
db = SQLAlchemy(app)
migrate = Migrate(app,db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg') 
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"





posts=[
    {
        'author': 'Sotherny Kosal',
        'title': 'blog post 1',
        'content': 'first post content',
        'date_posted': 'December 15th 2020',
    },
    {
        'author': 'Sothaknia Kosal',
        'title': 'blog post 2',
        'content': 'second post content',
        'date_posted': 'December 16th 2020',       
    }
]

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html', title="About")

@app.route('/register', methods=['GET','POST'])    
def register():
    #instance of the form
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        #flash(message, category) 
        #category is a bootrap class
        return redirect(url_for('home'))
    return render_template('register.html', title="Register", form = form)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == "admin@blog.com" and form.password.data == "password":
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form = form)


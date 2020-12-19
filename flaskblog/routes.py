import os
import secrets
from PIL import Image
from flask import render_template, url_for, redirect, flash, request, jsonify, make_response, session
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flaskblog.models import User, Post
import uuid
from flask_login import login_user, current_user, logout_user, login_required
from functools import wraps
import jwt
from datetime import datetime,timedelta



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
# start jwt
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        
        if not token:
            # flash('Token is missing!!', 'danger')
            return jsonify({'message':'Token is missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            
        except :
            # flash('Token is invalid', 'danger')
            return jsonify({'message':'Token is invalid'}), 401
        
        return f(*args, **kwargs)
        
    return decorated

@app.route('/all_users', methods=['GET'])
@token_required
def all_users():
    users = User.query.all()
    output = []
    for user in users:
        output.append({
            'public_id': user.public_id,
            'username': user.username,
            'email': user.email            
        })
        
    # return render_template('all_user.html', title = 'All Users', all_users = output)
    return jsonify({'users':output})
#end jwt

@app.route('/')
@app.route('/home')
def home():
    token = request.args.get('token')
    return render_template('home.html', posts=posts, token=token)

@app.route('/about')
# @token_required
def about():
    return render_template('about.html', title="About")

@app.route('/register', methods=['GET','POST'])    
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    #instance of the form
    form = RegistrationForm()
    if form.validate_on_submit():
        public_id = str(uuid.uuid4())
        username = form.username.data
        email = form.email.data
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        user = User(public_id = public_id, username=username, email=email, password=hash_password)
        db.session.add(user)
        db.session.commit()

        flash('Your account have been created! You are now able to log in.', 'success')
        #flash(message, category) 
        #category is a bootrap class        
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form = form)

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):

            #jwt: generate token
            token = jwt.encode({
                'public_id': user.public_id,
                'exp': datetime.utcnow() + timedelta(seconds=60)
            }, app.config['SECRET_KEY'])
            
            decoded_token = token.decode('UTF-8')
            # flash(f"'token': {decoded_token}", 'info')
            #end
            
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')            

            return redirect(next_page) if next_page else redirect(url_for('home', token=decoded_token))
            
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext #fn = filename
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    #resize the image before save
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()    
    if form.validate_on_submit():  
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file                        

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account have been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    image_file = url_for('static', filename = 'profile_pics/'+ current_user.image_file)
    return render_template('account.html', title='Account', 
                            image_file = image_file, form = form)
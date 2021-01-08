import os
import secrets
from PIL import Image
from flask import render_template, url_for, redirect, flash, request, jsonify, make_response, session, abort
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
                            PostForm, RequestResetForm, ResetPasswordForm, CreateProjectForm)
from flaskblog.models import User, Post, Role
import uuid
from flask_login import login_user, current_user, logout_user, login_required
from functools import wraps
import jwt
from datetime import datetime,timedelta
from flask_mail import Message


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

    # Set the pagination configuration
    page = request.args.get('page', 1, type=int)
    #request.args.get('page', default_page, type)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page = page, per_page=5)
    #post is the paginate object, which contain attr and method
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

@app.route('/account/<int:id>', methods=['GET','POST'])
@login_required
def account(id):
    total_user = User.query.all()

    if id>len(total_user):
        if current_user.role_id == 1:                    
            return render_template('404.html', title="404 Not Found")
        else:
            return render_template('403.html', title="403 Access Denied")

    user = User.query.filter_by(id=id).first()

    #the value passed in () is default value to display in selectfield
    form = UpdateAccountForm(role=user.role_id)
    #take the role from database and add to the selectfield in form
    form.role.choices = [(role.id, role.name) for role in Role.query.all()]
    
    if current_user.id == id or current_user.role_id==1:
        if request.method == 'POST':             
            if form.validate_on_submit():                         
                if form.picture.data:
                    picture_file = save_picture(form.picture.data)
                    user.image_file = picture_file                        

                user.username = form.username.data
                user.email = form.email.data

                if form.role.data:
                    user.role_id = form.role.data
                    
                db.session.commit()                
                flash('Your account have been updated!', 'success')

                return redirect(url_for('account',id=user.id))

        elif request.method == 'GET':
            form.username.data = user.username
            form.email.data = user.email
 
    else:
        return render_template('403.html', title="403 Access Denied")
        
    image_file = url_for('static', filename = 'profile_pics/'+ user.image_file)

    return render_template('account.html', title='Account', 
                            image_file = image_file, form = form, user=user)


#Post
@app.route('/post/new', methods=['GET', 'Post'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title = 'New Post', form = form, legend = "New Post")

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post have been updated', 'success')
        return redirect(url_for('post', post_id= post.id))
    elif request.method == 'GET':        
        form.title.data = post.title
        form.content.data = post.content  

    return render_template('create_post.html', title="Update Post", form=form, legend = "Update Post")

@app.route('/post/<int:post_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post have been deleted!', 'success')

    return redirect(url_for('home'))


@app.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
            .order_by(Post.date_posted.desc())\
            .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


#reset password
def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', 
                    sender=app.config['MAIL_USERNAME'], 
                    recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instruction to reset your password', 'success')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()    
    if form.validate_on_submit:
        if form.password.data:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = hashed_password 
            db.session.commit()
            flash('Your password has been updated! You are now able to log in', 'success')
            return redirect(url_for('login'))

    return render_template('reset_token.html', title="Reset Password", form=form)

#admin
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    all_users = User.query.all()

    if current_user.role_id != 1:
        return render_template('403.html', title="403 Access Denied")
    
    return render_template('admin.html', title="Admin Page", all_users=all_users)


# form not yet work and function not yet implement(need to validate form on submit and save data to db)
@app.route('/create_project', methods=['GET','POST'])    
def create_project():
    # if current_user.is_authenticated:
    #     return redirect(url_for('home'))
    #instance of the form
    form = CreateProjectForm()

    return render_template('create_project.html', title="Create Project", form=form)
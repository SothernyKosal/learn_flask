from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User, Skill


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])

    #assign role, admin only
    # role = SelectField('Role', choices=[(1, 'Admin'), (2, 'Stakeholder'), (3, 'Student')])
    role = SelectField('Role', choices=[])
    submit = SubmitField('Update')
    
    def validate_username(self, username):
        if current_user.role_id != 1:
            #
            current_user_id = current_user.id
            present_user = User.query.filter_by(id=current_user_id).first()                        
            if username.data != present_user.username:
            #
                user = User.query.filter_by(username=username.data).first()
                if user:
                    raise ValidationError('That username is taken. Please choose a different one.')
        else:
            pass

    def validate_email(self, email):
        if current_user.role_id != 1:
            #
            current_user_id = current_user.id
            present_user = User.query.filter_by(id=current_user_id).first()
            #
            # if email.data != current_user.email:
            if email.data != present_user.email:
                user = User.query.filter_by(email=email.data).first()
                if user:
                    raise ValidationError('That email is taken. Please choose a different one.')
        # else:
        #     pass


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Passsword Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with this email. You must register first.')
        
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

# class AssignRoleForm(FlaskForm):
#     role = SelectField('Role', choices=[(1, 'Admin'), (2, 'Stakeholder'), (3, 'Student')])
#     submit = SubmitField('Assign Role')

def get_users():
    return User.query.all()
    

def get_skills():
    return Skill.query.all()

class CreateProjectForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    code = StringField('Code', validators=[DataRequired()])
    member = QuerySelectField('Members', query_factory=get_users, allow_blank=False, validators=[DataRequired()], get_label='username', id="member")
    skill = QuerySelectField('Skills', query_factory=get_skills, allow_blank=False, validators=[DataRequired()], id="skill")
    submit = SubmitField('Submit')


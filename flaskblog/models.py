from flaskblog import db, login_manager, app
import jwt
from datetime import datetime, timedelta
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

ProjectMembers = db.Table('project_member',
                    db.Column('id',db.Integer, primary_key=True),
                    db.Column('project_id',db.Integer,db.ForeignKey('project.id', ondelete='CASCADE')),
                    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')))

ProjectSkills = db.Table('project_skill',
                    db.Column('id', db.Integer, primary_key=True),
                    db.Column('project_id', db.Integer, db.ForeignKey('project.id', ondelete='CASCADE')),
                    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id', ondelete='CASCADE')))                

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(20),unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg') 
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    role_id = db.Column(db.Integer,db.ForeignKey('role.id'), default=3)
    
    def get_reset_token(self):
        token = jwt.encode({
            'public_id': self.public_id,
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, app.config['SECRET_KEY'])

        return token.decode('UTF-8')

    @staticmethod
    def verify_reset_token(token):
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            user = User.query\
                .filter_by(public_id=data['public_id'])\
                .first()
        except :            
            return None        
        return user


    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')" 

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    users = db.relationship('User', backref='role')


class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    code = db.Column(db.String(20),unique=True)
    members = db.relationship('User',
                            secondary=ProjectMembers,
                            lazy="subquery",
                            backref=db.backref('projects', lazy=True))
    skills = db.relationship('Skill',
                            secondary=ProjectSkills,
                            lazy='subquery',
                            backref=db.backref('projects', lazy=True))                            
    
    def __repr__(self):
        return self.name


class Skill(db.Model):
    __tablename__ = 'skill'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.Integer,unique=True, nullable=False)

    def __repr__(self):
        return self.name

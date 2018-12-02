from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from jinja2 import Environment, select_autoescape
env = Environment(autoescape=select_autoescape(
    enabled_extensions=('html'),
    default_for_string=True,
))

# TODO implement auto escaping

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '%9VK@b2Bt^gu'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    time_stamp = db.Column(db.DateTime)

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
        self.time_stamp = datetime.utcnow()

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        valid_user = True
        valid_password = True
        valid_retyped_password = True
        # TODO - validate users data
        if len(username) < 3 or not username:
            valid_user = False
            flash('That is an invalid username', 'error')
        if not password:
            valid_password = False
            flash('Password cannot be blank', 'error')
        if not verify or password != verify:
            valid_retyped_password = False
            flash('Please retype the password exactly', 'error')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('User already exists', 'error')
        if not existing_user and valid_user and valid_password and valid_retyped_password:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/login')
                
    return render_template('signup.html')

@app.before_request
def require_login():
    allowed_routes = ['index', 'login', 'signup', 'main_blog', 'static']
    if request.endpoint == 'new_post' and 'username' not in session:
        return redirect('/login')
    elif request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/blog')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Logged in', 'login')
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/newpost', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        blog_owner = User.query.filter_by(username=session['username']).first()
        blog_title = request.form['title']
        blog_body = request.form['body']

        # Checking for blanks and rerenders with error messages.
        if not blog_title:
            title_error = "A title is required."
            if not blog_body:
                body_error = "Some text is required."
                return render_template('newpost.html', title_error=title_error, body_error=body_error, blog_title=blog_title, blog_body=blog_body)
            return render_template('newpost.html', title_error=title_error, blog_title=blog_title)
        elif not blog_body:
                body_error = "Some text is required."
                return render_template('newpost.html', body_error=body_error, blog_title=blog_title)

        new_post = Blog(blog_title, blog_body, blog_owner)

        db.session.add(new_post)
        db.session.commit()

        return redirect('/blog?id={0}'.format(str(new_post.id)))
        
    return render_template('newpost.html')

@app.route('/blog')
def main_blog():
    if "user" in request.args:
        user_id = request.args.get("user")
        user = User.query.get(user_id)
        user_blogs = Blog.query.filter_by(owner=user).all()
        return render_template('singleUser.html', user_blogs=user_blogs)

    blog_id = request.args.get('id')
    if blog_id == None:
        blog_posts = Blog.query.all()
        return render_template('posts.html', blog_posts=blog_posts)
    else:
        blog_post = Blog.query.get(blog_id)
        return render_template('display_post.html', blog_post=blog_post)

    return render_template('posts.html', blog_posts=blog_posts)
    
@app.route('/', methods=['POST', 'GET'])
def index():
    user_list = User.query.all()
    return render_template('index.html', user_list=user_list)


if __name__ == '__main__':
    app.run()
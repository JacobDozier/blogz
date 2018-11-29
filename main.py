from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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

    def __init__(self, title, body, owner_id):
        self.title = title
        self.body = body
        self.owner_id = owner_id

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password, blogs):
        self.email = email
        self.password = password

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')

@app.before_request
def require_login():
    allowed_routes = ['index', 'login', 'signup', 'main_blog', 'static']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/newpost', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        blog_owner = User.query.filter_by(username=session['username']).first()

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
    blog_posts = Blog.query.all()

    if request.args:
        blog_id = request.args.get('id')
        blog_post = Blog.query.get(blog_id)
        return render_template('display_post.html', blog_post=blog_post)

    return render_template('posts.html', blog_posts=blog_posts)
    
@app.route('/', methods=['POST', 'GET'])
def index():

    blog_posts = Blog.query.all()
    return render_template('posts.html', blog_posts=blog_posts)


if __name__ == '__main__':
    app.run()
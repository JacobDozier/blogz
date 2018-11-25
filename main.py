from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '%9VK@b2Bt^gu'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(255))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/newpost', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
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

        new_post = Blog(blog_title, blog_body)
        db.session.add(new_post)
        db.session.commit()
        id = new_post.id
        return redirect('/blog?id={0}'.format(id))
        
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
    return render_template('posts.html', page_title="Build a Blog", blog_posts=blog_posts)


if __name__ == '__main__':
    app.run()
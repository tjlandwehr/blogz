from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:root@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(280))
    body = db.Column(db.String(10000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pub_date = db.Column(db.DateTime)

    def __init__(self, title, body, owner, pub_date=None):
        self.title = title
        self.body = body
        self.owner = owner
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

    def __repr__(self):
        return ('<Title: %r, Body: %s>' % (self.title, self.body))

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def __repr__(self):
        return ('<Username: %r>') % (self.username)

def get_current_blogs():
    # List of Blog instances
    return Blog.query.order_by(Blog.pub_date.desc()).all()

@app.before_request
def require_login():
    allowed_routes = ['login', 'list_blogs', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/blog')
def list_blogs():
    blog_post_value = request.args.get('id')
    if blog_post_value:
        blog = Blog.query.get(blog_post_value)
        if not blog:
            error = "{0} is not a valid blog post ID.".format(blog_post_value)
            flash(error, "id_error")
            return render_template('blog.html', title="Build A Blog", heading="Build a Blog", blogs=get_current_blogs())
        else:
            return render_template('post.html', title=blog.title, heading=blog.title, body=blog.body)

    return render_template('blog.html', title="Build A Blog", heading="Build a Blog", blogs=get_current_blogs())

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    blog_title = ""
    blog_body = ""
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        blog_title += request.form['title']
        blog_body += request.form['body']
        if blog_title == "" or blog_body == "":
            if blog_title == "":
                flash("Please fill in the title", "title_error")
            if blog_body == "":
                flash("Please fill in the body", "body_error")
            return render_template('newpost.html', title="Add Blog Entry", heading="Add a Blog Entry", 
                blog_title=blog_title, blog_body=blog_body)
        else:
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id=' + str(new_blog.id))

    return render_template('newpost.html', title="Add Blog Entry", heading="Add a Blog Entry", 
        blog_title=blog_title, blog_body=blog_body)

@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            print(session)
            return redirect('/newpost')
        elif user and user.password != password:
            error = "Incorrect password"
            flash(error, "id_error")
            return redirect('/login')
        elif not user:
            error = "The username '{0}' does not exist".format(username)
            flash(error, "id_error")
            return redirect('/login')
    else:
        return render_template('login.html', title="Login to Blogz", heading="Login to Blogz")

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        user = User.query.filter_by(username=username).first()

        username_error = ""
        password_error = ""
        verify_error = ""

        if (not username) or (username.strip() == ""):
            username_error += "Username cannot be left blank."
        elif " " in username:
            username_error += "Username cannot contain a space character."
        elif len(username) < 3 or len(username) > 20:
            username_error += "Username must contain between 3-20 characters."
        elif user:
            username_error += "The username '{0}' already exists.".format(username)
        
        if (not password) or (password.strip() == ""):
            password_error += "Password cannot be left blank."
        elif " " in password:
            password_error = "Password cannot contain a space character."
        elif len(password) < 3 or len(password) > 20:
            password_error += "Password must contain between 3-20 characters."

        if (not verify) or (verify.strip() == ""):
            verify_error += "Password verification cannot be left blank."
        elif password != verify:
            verify_error += "Passwords do not match."

        if len(username_error) != 0:
            username = ""
        
        if len(username_error) != 0 or len(password_error) != 0 or len(verify_error) != 0:
            return render_template("signup.html", title="User Signup | Blogz", heading="Signup to Blogz", 
                username_error=username_error and cgi.escape(username_error, quote=True),
                password_error=password_error and cgi.escape(password_error, quote=True), 
                verify_error=verify_error and cgi.escape(verify_error, quote=True), 
                username=username and cgi.escape(username, quote=True))
        
        if not user and password == verify:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash("Signup successful!", "id_error")
            print(session)
            return redirect('/newpost')
    else:
        return render_template('signup.html', title="User Signup | Blogz", heading="Signup to Blogz")

if __name__ == '__main__':
    app.run()
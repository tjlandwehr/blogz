from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:root@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(280))
    body = db.Column(db.String(10000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

    def __repr__(self):
        return ('<Title: %r, Body: %s>' % (self.title, self.body))

def get_current_blogs():
    # List of Blog instances
    return Blog.query.all()

@app.route('/blog')
def show_blogs():
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
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id=' + str(new_blog.id))

    return render_template('newpost.html', title="Add Blog Entry", heading="Add a Blog Entry", 
        blog_title=blog_title, blog_body=blog_body)

if __name__ == '__main__':
    app.run()
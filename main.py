from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:hJr3`krm*tEt-E6@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1500))
    

    def __init__(self, title, body):
        self.title = title
        self.body = body



@app.route('/blog')
def index():
    blog_id = request.args.get('id')
    if (blog_id):
        post = Blog.query.get(blog_id)
        return render_template('post.html', title = "Blog Entry",
        post = post)
    posts = Blog.query.order_by(Blog.id.desc()).all()

    return render_template('blog.html',title="Build-a-Blog", 
        posts=posts)


@app.route('/newpost', methods = ['POST','GET'])

def new_post():
    if request.method == 'POST':


        title = request.form['blog_title']
        body = request.form['blog_body']
        title_error = ""
        body_error = ""

        #Error Validation
        if title == "":
            title_error = "Blog title is required."
        if body == "":
            body_error = "Blog body is required."
        if not title_error and not body_error:
            blog_post = Blog(title, body)
            db.session.add(blog_post)
            db.session.flush()
            db.session.commit()
            return redirect('/blog?id={0}'.format(blog_post.id))

        else:

            return render_template("new_blog_entry.html",
            blog_title = title,
            blog_body = body,
            title_error = title_error,
            body_error = body_error)
    else:
        return render_template('new_blog_entry.html')


if __name__ == '__main__':
    app.run()

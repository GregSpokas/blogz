from flask import Flask, redirect, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:gTG#49GBf*dUi#n@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'Xd3*k2%Pu!3h72NcI8L1J'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(800))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login','blog','index','signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/blog')
def blog():
    blog_id = request.args.get('id')
    user_id = request.args.get('user')
    if (blog_id):
        post = Blog.query.get(blog_id)
        return render_template('post.html', title = "Blog Entry",
        post = post)
    if (user_id):
        user_posts = Blog.query.filter_by(owner_id = user_id).order_by(Blog.id.desc()).all()

        return render_template('user_posts.html', posts = user_posts )
    
    posts = Blog.query.order_by(Blog.id.desc()).all()

    return render_template('blog.html',title="Blog Heaven", 
        posts=posts)


@app.route('/newpost', methods = ['POST','GET'])

def new_post():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':


        title = request.form['blog_title']
        body = request.form['blog_body']

        #Error Validation
        if title == "" or body == "":
            flash('Blog title is required or blog body is required.','error')
            return redirect('/newpost')

        if not title == "" and not body == "":
            blog_post = Blog(title, body, owner)
            db.session.add(blog_post)
            db.session.flush()
            db.session.commit()
            return redirect('/blog?id={0}'.format(blog_post.id))

        else:

            return render_template("new_blog_entry.html",
            blog_title = title,
            blog_body = body)
    else:
        return render_template('new_blog_entry.html')

@app.route('/login', methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash("Logged In")
            return redirect('/newpost')
        elif user and user.password != password:
            flash('User password incorrect', 'error')
            return redirect('/login')
        elif not user:
            flash('This username does not exist','error')

    return render_template("login.html")

@app.route('/signup',methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username == "" or password == "" or verify =="":
            flash('One or more fields are invalid', 'error')
            return redirect('/signup')

        if len(username) > 0:
            if len(username) < 3 or re.search(r"\s",username):
                if len(password) > 0:
                    if len(password) < 3 or re.search(r"\s",password):
                        flash('Please enter a username atleast 3 characters or username contains spaces.', 'error')
                        flash('Please enter a password atleast 3 characters or password contains spaces.', 'error')
                        password = ""
                        return redirect('/signup')
                    else:
                        flash('Please enter a username atleast 3 characters or username contains spaces.', 'error')
                        return redirect('/signup')

        if len(password) > 0:
            if len(password) < 3 or re.search(r"\s",password):
                if len(username) > 0:
                    if len(username) < 3 or re.search(r"\s",username):
                        flash('Please enter a username atleast 3 characters or username contains spaces.', 'error')
                        flash('Please enter a password atleast 3 characters or password contains spaces.', 'error')
                        password = ""
                        return redirect('/signup')
                    else:
                        flash('Please enter a password atleast 3 characters or password contains spaces.', 'error')
                        password = ""
                        return redirect('/signup')



                flash('Please enter a username atleast 3 characters or username contains spaces.', 'error')
                return redirect('/signup')
            
        if len(password) > 0:
            if len(password) < 3 or re.search(r"\s",password):
                flash('Please enter a password atleast 3 characters or password contains spaces.', 'error')
                password = ""
                return redirect('/signup')

        if password != verify:
            flash('Password and verify password do not match', 'error')
            return redirect('/signup')
        
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.flush()
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash('That username is already in use', 'error')
            return redirect('/signup')

    return render_template('signup.html')

@app.route('/')
def index():
    
    user_id = request.args.get('id')
    if (user_id):
        user = User.query.get(user_id)
        return render_template('user_posts.html', title = "User's Posts",
        user = user)
    users = User.query.all()

    return render_template('index.html',title="User List",
    users=users)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')



if __name__ == '__main__':
    app.run()

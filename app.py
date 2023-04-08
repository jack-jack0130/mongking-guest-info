from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import psycopg2



app = Flask(__name__)
app.secret_key = 'your_secret_key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database01.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://syxwskkdhrleum:eee65fcc76485977633e78db6288242869b7fad6688a39324773849795a28005@ec2-3-234-204-26.compute-1.amazonaws.com:5432/d2meslrrdssfgt'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://syxwskkdhrleum:eee65fcc76485977633e78db6288242869b7fad6688a39324773849795a28005@ec2-3-234-204-26.compute-1.amazonaws.com:5432/d2meslrrdssfgt'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    image = db.Column(db.String(100), nullable=True)



    def __repr__(self):
        return '<Post %r>' % self.title


@app.route('/welcome')
def welcome():
    posts = Post.query.all()
    return render_template('welcome.html' )


@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('client.html', posts=posts )

@app.route('/post/<int:id>')
def post(id):
    post = Post.query.filter_by(id=id).first()
    return render_template('post.html', post=post)

@app.route('/admin')
def admin():
    if 'username' in session:
        return render_template('admin.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('username', None)

        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['username'] = request.form['username']
            return redirect(url_for('admin'))

        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/addpost', methods=['GET', 'POST'])
def addpost():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        ifile = request.files['image']
        vfile = request.files['video']

        if ifile:
            filename = secure_filename(ifile.filename)
            ifile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        elif vfile:
            vfilename = secure_filename(vfile.filename)
            vfile.save(os.path.join(app.config['UPLOAD_FOLDER'], vfilename))
        else:
            filename="none.jpg"



        post = Post(title=title, description=description, image=filename)
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('admin'))

    return render_template('admin.html')


@app.route('/display')
def display():
    posts = Post.query.all()
    return render_template('display.html', posts=posts )

@app.route('/edit', methods=['POST','GET'])
def edit_post():
    if request.form.get('delete') == 'del':
        post_title = request.form['title']
        post = Post.query.filter_by(title=post_title).first()
        db.session.delete(post)
        db.session.commit()

    if request.form.get('up') == 'up':
        title = request.form['title']
        posts = Post.query.all()
        if posts:
            row1 = Post.query.filter_by(title=title).first()
            index = posts.index(row1)

        row2 = Post.query.offset(index-1).limit(1).first()

        temp1= row1.title
        temp2= row1.description
        temp3= row1.image
        row1.title=row2.title
        row1.description=row2.description
        row1.image=row2.image
        row2.title=temp1
        row2.description=temp2
        row2.image=temp3
        db.session.commit()

    if request.form.get('down') == 'down':
        title = request.form['title']
        posts = Post.query.all()
        if posts:
            row1 = Post.query.filter_by(title=title).first()
            index = posts.index(row1)

        row2 = Post.query.offset(index+1).limit(1).first()

        temp1= row1.title
        temp2= row1.description
        temp3= row1.image
        row1.title=row2.title
        row1.description=row2.description
        row1.image=row2.image
        row2.title=temp1
        row2.description=temp2
        row2.image=temp3

        db.session.commit()

    if request.form.get('edit') == 'edit':
        title = request.form['title']
        posts = Post.query.all()
        if posts:
            row1 = Post.query.filter_by(title=title).first()
            return render_template('edit.html', row1=row1 )

    """
        if request.form.get('undo') == 'undo':
        db.session.rollback()
    """


    return redirect(url_for('display'))

@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        id=request.form['id']

        row1 = Post.query.filter_by(id=id).first()
        row1.title=title
        row1.description=description

        db.session.commit()

        return redirect(url_for('display'))

    return render_template('display.html')






if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

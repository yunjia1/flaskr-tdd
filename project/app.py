from functools import wraps
from pathlib import Path
import os 

from flask import Flask, render_template, request, session, \
                  flash, redirect, url_for, abort, jsonify
from flask_sqlalchemy import SQLAlchemy


basedir = Path(__file__).resolve().parent

# created a configuration section for config variables 
DATABASE = "flaskr.db"
USERNAME = "admin"
PASSWORD = "admin"
SECRET_KEY = "change_me"
# SQLALCHEMY_DATABASE_URI configuration is set to point to a local SQLite database file (flaskr.db) 
url = os.getenv('DATABASE_URL', f'sqlite:///{Path(basedir).joinpath(DATABASE)}')

if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URI = url
SQLALCHEMY_TRACK_MODIFICATIONS = False # to avoid overhead

# Once app.py connects to the database, it assumes the tables have already been created (which happened when you ran create_db.py).
# app.py can now query and manipulate the data in those tables via SQLAlchemy.


# create and initialize a new Flask app
app = Flask(__name__)
# loaded the config after app initialization
app.config.from_object(__name__)
# init sqlalchemy
db = SQLAlchemy(app)

from project import models


@app.route('/')
def index():
    """Searches the database for entries, then displays them."""
    entries = db.session.query(models.Post)
    return render_template('index.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    """Adds new post to the database."""
    if not session.get('logged_in'):
        abort(401)
    new_entry = models.Post(request.form['title'], request.form['text'])
    db.session.add(new_entry)
    db.session.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('index'))

# GET is used for accessing a webpage, while POST is used when information is sent to the server
# When a user accesses the /login URL, they are using a GET request, but when they attempt to log in, a POST request is used.
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login/authentication/session management."""
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """User logout/authentication/session management."""
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))

# Ensures that only authenticated users (those with 'logged_in' set to True in the session) can access certain routes.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in.')
            return jsonify({'status': 0, 'message': 'Please log in.'}), 401
        # logged_in' is True, the decorator calls the original function (f(*args, **kwargs)), passing along any arguments and keyword arguments.
        return f(*args, **kwargs)
    return decorated_function

# Checks if the user is logged in, and if not, it returns an error message and prevents further execution of the protected route.
@app.route('/delete/<int:post_id>', methods=['GET'])
@login_required
def delete_entry(post_id):
    """Deletes post from database."""
    result = {'status': 0, 'message': 'Error'}
    try:
        new_id = post_id
        db.session.query(models.Post).filter_by(id=new_id).delete()
        db.session.commit()
        result = {'status': 1, 'message': "Post Deleted"}
        flash('The entry was deleted.')
    except Exception as e:
        result = {'status': 0, 'message': repr(e)}
    return jsonify(result)

@app.route('/search/', methods=['GET'])
def search():
    query = request.args.get("query") # gets input field
    entries = db.session.query(models.Post)
    if query:
        return render_template('search.html', entries=entries, query=query) # passes into template so that entry can be shown
    return render_template('search.html')

if __name__ == "__main__":
    app.run()
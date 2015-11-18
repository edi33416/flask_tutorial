# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
        render_template, flash

# add support to initialize the database for the application
from contextlib import closing

# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

# working with the database

# initialize the database
def init_db():
    # keep the connection open for the duration of the with block with the 
    # help of the `closing()` helper function
    with closing(connect_db()) as db:
        # open the file from the resource location and read from it
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

# end of database related functions

# view functions

# show all the entries stored in the database in descending order, from the
# most recent one to the oldest one
@app.route('/')
def show_entries():
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title = row[0], text = row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries = entries)

# allow a logged in user to add a new entry to the database
@app.route('/add', methods = ['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)

    # Security Note
    # use question marks when building SQL statements in order to prevent
    # SQL injection when using string formatting
    g.db.execute('insert into entries (title, text) values (?, ?)',
                [request.form['title'], request.form['text']])
    # do not forget to commit the changes
    g.db.commit()

    flash('New entry was successfully posted')

    return redirect(url_for('show_entries'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were successfully logged in')
            return redirect(url_for('show_entries'))

    return render_template('login.html', error = error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were successfully logged out')
    return redirect(url_for('show_entries'))

# end of view functions

if __name__ == '__main__':
    init_db()
    app.run()

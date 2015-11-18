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

if __name__ == '__main__':
    #init_db()
    app.run()

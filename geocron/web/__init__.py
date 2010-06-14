from flask import Flask, render_template, session
from geocron import settings
from geocron.location import Latitude
from geocron.web.auth import auth
from pymongo import Connection

application = Flask(__name__)
application.register_module(auth)

conn = Connection(settings.MONGODB_HOST, settings.MONGODB_PORT)

# request lifecycle

@app.before_request
def before_request():
    g.db = conn.geocron
    
@app.after_request
def after_request(response):
    return response

# application

@application.route("/")
def hello():
    
    if 'access_token' in session and 'access_secret' in session:
        l = Latitude(session['access_token'], session['access_secret'])
        content = l.current_location()
    else:
        content = "asdfasdf"
    
    return render_template('base.html', content=content)

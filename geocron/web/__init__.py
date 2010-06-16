from flask import Flask, g, redirect, render_template, request, session, url_for
from geocron import settings
from geocron.location import Latitude
from geocron.rules import rules
from geocron.web.auth import auth
from geocron.rules import rules
from pymongo import Connection
import time


application = Flask(__name__)
application.register_module(auth)

conn = Connection(settings.MONGODB_HOST, settings.MONGODB_PORT)

# request lifecycle

@application.before_request
def before_request():
    g.db = conn.geocron
    if 'identity' in session:
        g.user = g.db.users.find_one({'_id': session['identity']})
    else:
        g.user = None
    
@application.after_request
def after_request(response):
    return response

# application

@application.route("/")
def hello():
    
    if 'access_token' in session and 'access_secret' in session:
        l = Latitude(session['access_token'], session['access_secret'])
        content = l.current_location()
    else:
        content = ""
    
    if g.user == None:
        return render_template('hello.html', content=content)
    else:
        return render_template('rules.html')

@application.route("/users")
def user_list():
    users = g.db.users.find()
    return render_template('user_list.html', users=users)

@application.route("/users/<identity>")
def user_detail(identity):
    user = g.db.users.find_one({'_id': identity})
    return render_template('user_detail.html', user=user)

@application.route("/checkin", methods=['GET', 'POST'])
def checkin():
    if request.method == 'POST':
        identity = request.form['identity']
        location = {
            'kind': 'latitude#location',
            'latitude': float(request.form['latitude']),
            'longitude': float(request.form['longitude']),
            'accuracy': int(request.form['accuracy']),
            'timestampMs': int(time.time() * 1000),
        }
        user = g.db.users.find_one({'_id': identity})
        user['locations'].insert(0, location)
        g.db.users.save(user)
        rules.check(identity, (location['latitude'], location['longitude']))
        return redirect(url_for('user_detail', identity=user['_id']))
    else:
        return render_template('checkin.html')

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
        user = rules.get_user(g.user['_id'])
        return render_template('rules.html',user=user)

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
        if 'locations' not in user:
            user['locations'] = []
        user['locations'].insert(0, location)
        g.db.users.save(user)
        rules.check(identity, (location['latitude'], location['longitude']))
        return redirect(url_for('user_detail', identity=user['_id']))
    else:
        return render_template('checkin.html')

@application.route("/save_rule", methods=['POST'])
def save_rule():
    
    rule = {
        'name': request.form['name'],
        'location': [request.form['latitude'], request.form['longitude']],
        'action_type': request.form['action_type'],
        'days': request.form['days'],
        'times': request.form['times'],
        'address': request.form['location'],
        'recipient': request.form['recipient']
    }
    
    if request.form['action_type'] == 'email':
        rule['email_address'] = request.form['recipient']
        rule['email_text'] = request.form['message']
    elif request.form['action_type'] == 'webhook':
        rule['method'] = 'POST'
        rule['callback_url'] = request.form['recipient']
    elif request.form['action_type'] == 'sms':
        rule['phone_number'] = request.form['recipient']
        rule['phone_carrier'] = request.form['carrier']
        rule['sms'] = request.form['message']

    if request.form['days'] == 'everyday':
        rule['valid_days'] = [0,1,2,3,4,5,6]
    elif request.form['days'] == 'weekdays':
        rule['valid_days'] = [1,2,3,4,5]
    elif request.form['days'] == 'weekends':
        rule['valid_days'] = [0,6]

    if request.form['times'] == 'anytime':
        rule['valid_start_time'] = '00:00'
        rule['valid_end_time'] = '00:00'
    elif request.form['times'] == 'day':
        rule['valid_start_time'] = '07:00'
        rule['valid_end_time'] = '07:00'
    elif request.form['times'] == 'morning':
        rule['valid_start_time'] = '06:00'
        rule['valid_end_time'] = '12:00'
    elif request.form['times'] == 'afternoon':
        rule['valid_start_time'] = '12:00'
        rule['valid_end_time'] = '00:00'
    elif request.form['times'] == 'evening':
        rule['valid_start_time'] = '04:00'
        rule['valid_end_time'] = '00:00'
    elif request.form['times'] == 'overnight':
        rule['valid_start_time'] = '19:00'
        rule['valid_end_time'] = '07:00'
    
    rules.set_rule(g.user['_id'], **rule)
    return redirect(url_for('hello'))

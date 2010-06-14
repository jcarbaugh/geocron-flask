
from settings import *
from pymongo import Connection
from datetime import datetime
from actions import *
connection = Connection(HOST, PORT)
db = connection[DATABASE_NAME]

#Python has a bug(gasp!) that doesn't allow unicode characters in keys of dicts that are expanded using the **kwargs notation. 
#I guess the keys get converted in the pymongo wrapper, so we use this function to convert back
def convert_from_unicode(data):
    if isinstance(data, unicode):
        return str(data)
    elif isinstance(data, dict):
        return dict(map(convert_from_unicode, data.iteritems()))
    elif isinstance(data, (list, tuple, set, frozenset)):
        return type(data)(map(convert_from_unicode, data))
    else:
        return data


# Function to add a rule to a user document
# the kwargs is a dict containing the attributes of the rule
# expected format: (email message)
# { 'name': 'Honey I'm Home!',
#   'location': [23.42342, -25.5234], 
#   'action_type': 'email'  
#   'email_address': 'receiver@mail.net',
#   'email_text': 'come pick me up!',
#   'valid_days': [1, 2, 3, 4, 5],
#   'valid_start_time': '06:00',
#   'valid_end_time': '13:00',
# }
#
# expected format: (webhook)
# { 'name': 'Honey I'm Home!',
#   'location': [23.2343, -25.2343],
#   'action_type': 'callback',
#   'method': 'POST',
#   'callback_url': 'http://kaitlin.com/callback?action=iamhome',
#   'valid_days': [1, 2, 3, 4, 5],
#   'valid_start_time': '06:00',
#   'valid_end_time': '13:00',
# }

def debug(user):
    print user

def get_user(email):
    
    users = db.users
    user = users.find_one({"email": email})
    if not user:
        user = users.find_one({"_id": users.insert({"email":email})})
    
    return user

def save_user(user):
    users = db.users
    users.save(user)

def set_rule(email, **kwargs):

    user = get_user(email)

    #treat kwargs as the dict for another rule
    if kwargs.has_key('name'):
        if not user.has_key('rules'):
            user['rules'] = []
        rules = user['rules']
        for r in rules:
            if r['name'] == kwargs['name']:
                return 'Rule with this name already exists'
        user['rules'].append(kwargs)
    
    else:
        return 'Rule must have a unique name'

    save_user(user)
    debug(user)
    return 'success!'

def update_rule(email, rule_name, **kwargs):
    
    user = get_user(email)
    for r in user['rules']:
        if r['name'] == rule_name:
            user['rules'].remove(r)
            user['rules'].append(kwargs)
            
            save_user(user)
            debug(user)
            return 'success!'

def delete_rule(email, name):
    
    user = get_user(email)
    for r in user['rules']:
        if r['name'] == name:
            user['rules'].remove(r)
            save_user(user)
            debug(user)
            return 'success!'
           
def test_time(**rule):
    
    now = datetime.today()
    if rule.has_key('valid_days'):
        if now.weekday() not in rule['valid_days']:
            return 'day of the week condition failed'

    if rule.has_key('valid_start_time'):
        time = rule['valid_start_time']
        if now.time.hour < int(time.split(':')[0]) and now.time.minute < int(time.split(':')[1]):
            return 'start time condition failed'

    if rule.has_key('valid_end_time'):
        time = rule['valid_end_time']
        if now.time.hour > int(time.split(':')[0]) and now.time.minute > int(time.split(':')[1]):
            return 'end time condition failed'
    
    return True


def test_location(current_location, **rule):

    if rule['location'][0] == current_location[0] and rule['location'][1] == current_location[1]:
        return True  

    else: return False            
                
def check(email, current_location):
    
    user = get_user(email)
    if user.has_key('rules'):
        for r in user['rules']:
            if test_location(current_location, **convert_from_unicode(r)) and test_time(**convert_from_unicode(r)):
                #do action
                execute_action(email, **convert_from_unicode(r))
                print 'execute action!'

    else:
        return "This user has no rules"
              
                 
if __name__ == "__main__":

    #msg = delete_rule('katycorp@gmail.com', 'send an email')

    msg = update_rule("katycorp@gmail.com", 'time conditions', name="time conditions", action_type="email", email_text="hi", email_address="klee@sunlightfoundation.com", location=[2, 2], valid_days=[1,2,3,4,5], valid_start_time='12:00', valid_end_time='20:00')
    #print msg

    check('katycorp@gmail.com', [2, 2])


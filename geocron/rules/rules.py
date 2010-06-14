
from settings import *
from pymongo import Connection
from datetime import datetime

connection = Connection(HOST, PORT)
db = connection[DATABASE_NAME]

# Function to add a rule to a user document
# the kwargs is a dict containing the attributes of the rule
# expected format: (email message)
# { 'name': 'Honey I'm Home!',
#   'location': [23.42342, -25.5234], 
#   'action_type': 'email'  
#   'email_address': 'receiver@mail.net',
#   'email_text': 'come pick me up!',
#   'valid_days': [1, 2, 3, 4, 5],
#   'valid_start_time': 06:00,
#   'valid_end_time': 13:00,
# }
#
# expected format: (webhook)
# { 'name': 'Honey I'm Home!',
#   'location': [23.2343, -25.2343],
#   'action_type': 'callback',
#   'method': 'POST',
#   'callback_url': 'http://kaitlin.com/callback?action=iamhome',
#   'valid_days': [1, 2, 3, 4, 5],
#   'valid_start_time': 06:00,
#   'valid_end_time': 13:00,
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

def test_location(location, **rule):

    if r['location'][0] == location[0] and r['location'][1] == location[1]:
        return True  

    else: return False            
                
def check(email, location):
    
    user = get_user(email)
    if user.has_key(rules):
        for r in user['rules']:
            if test_location(location, r) and test_time(r):
                #do action
                pass

    else:
        return "This user has no rules"
              
                 
if __name__ == "__main__":

    msg = delete_rule('katycorp@gmail.com', 'send an email')

    msg = update_rule("katycorp@gmail.com", "send one email", location=[2, 2], name="send one email", action_type="email", email_address="someone@bla.net")
    print msg


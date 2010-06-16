
from geocron import settings
from pymongo import Connection
from datetime import datetime
import math
from geocron.rules.actions import DataError, execute_action


connection = Connection(settings.MONGODB_HOST, settings.MONGODB_PORT)
db = connection[settings.MONGODB_DB]

class ValidationError(DataError):
    pass

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
#   'action_type': 'webhook',
#   'method': 'POST',
#   'callback_url': 'http://kaitlin.com/callback?action=iamhome',
#   'valid_days': [1, 2, 3, 4, 5],
#   'valid_start_time': '06:00',
#   'valid_end_time': '13:00',
# }
#
# For SMS, make sure 'phone_number', 'phone_carrier' and 
# 'sms' are present

def debug(user):
    print user

def get_user(email):
    
    users = db.users
    user = users.find_one({"email": email})
    if not user:
        print "no user found with email: %s" % email
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
                raise ValidationError('Rule with this name already exists')
        user['rules'].append(kwargs)
    
    else:
        raise ValidationError('Rule must have a unique name')

    save_user(user)

def update_rule(email, rule_name, **kwargs):
    
    user = get_user(email)
    for r in user['rules']:
        if r['name'] == rule_name:
            user['rules'].remove(r)
            user['rules'].append(kwargs)
            save_user(user)
            return
    raise ValidationError('No rule with that name')

def delete_rule(email, name):
    
    user = get_user(email)
    for r in user['rules']:
        if r['name'] == name:
            user['rules'].remove(r)
            save_user(user)
            return
    raise ValidationError('no rule with that name')
     
def test_time(**rule):
    
    current_time = datetime.now()
    if rule.has_key('valid_days'):
        if current_time.weekday() not in rule['valid_days']:
            return False

    if rule.has_key('valid_start_time'):
        time = rule['valid_start_time']
        if current_time.hour < int(time.split(':')[0]) and current_time.minute < int(time.split(':')[1]):
            return False

    if rule.has_key('valid_end_time'):
        time = rule['valid_end_time']
        if current_time.hour > int(time.split(':')[0]) and current_time.minute > int(time.split(':')[1]):
            return False
    
    return True


def test_location(current_location, **rule):
    #Haversine Formula - Calculate distance between two points based on longitude, latitude, and the average radius of the earth
    lat1 = math.radians(current_location[0])
    lon1 = math.radians(current_location[1])
    lat2 = math.radians(float(rule['location'][0]))
    lon2 = math.radians(float(rule['location'][1]))

    earth_radius = 6371000 #meters

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    
    a = ((math.sin(delta_lat / 2.0))**2) + (math.cos(lat1) * math.cos(lat2) * ((math.sin(delta_lon / 2.0))**2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = earth_radius * c

    print "distance: %s" % distance
    if distance <= 300:
        return True
    else:
        return False
                
def check(email, current_location):
    
    user = get_user(email)
    if user.has_key('rules'):
        for r in user['rules']:
            if test_location(current_location, **convert_from_unicode(r)) and test_time(**convert_from_unicode(r)):
                #do action
                execute_action(email, **convert_from_unicode(r))
                print 'execute action!'

    else:
        pass
        #raise DataError("This user has no rules")
              
                 
if __name__ == "__main__":

    #delete_rule('katycorp@gmail.com', 'send one email')

    msg = update_rule("katycorp@gmail.com", "url test",  name="ama test", phone_number=8605935117, phone_carrier='att', sms='HEEEYYY', action_type="sms", location=[38.993496, -77.032399], valid_days=[1,2,3,4,5], valid_start_time='12:00', valid_end_time='20:00')
    #print msg

    check('katycorp@gmail.com', [38.991929, -77.032228])


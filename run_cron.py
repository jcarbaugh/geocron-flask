#!/usr/bin/env python
from geocron import settings
from geocron.location import Latitude
from geocron.rules import rules
from pymongo import Connection
import time

"""
{u'latitude': 38.895111800000002, u'kind': u'latitude#location', u'longitude': -77.036365799999999, u'timestampMs': u'1276541860634'}
"""

if __name__ == "__main__":
    
    conn = Connection(settings.MONGODB_HOST, settings.MONGODB_PORT)
    users = conn.geocron.users
    
    for user in users.find():
        
        if 'locations' not in user:
            user['locations'] = []
        
        oauth = user.get('oauth', None)
        if oauth:
            
            timestamps = [l['timestampMs'] for l in user['locations']]
            
            latitude = Latitude(oauth['token'], oauth['secret'])
            for location in latitude.locations(granularity='best')['data']['items']:
                
                if location['timestampMs'] not in timestamps:
                    user['locations'].append(location)
                    print "!!!", location
                    rules.check(None, location)
        
        users.save(user)
        
        time.sleep(1)
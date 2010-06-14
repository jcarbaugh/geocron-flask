#!/usr/bin/env python
from geocron import settings
from geocron.location import Latitude
from geocron.rules import rules
from pymongo import Connection
import time

if __name__ == "__main__":
    
    conn = Connection(settings.MONGODB_HOST, settings.MONGODB_PORT)
    users = conn.geocron.users
    
    for user in users.find():
        
        oauth = user.get('oauth', None)
        if oauth:
            
            latitude = Latitude(oauth['token'], oauth['secret'])
            for location in latitude.locations(granularity='best'):
                
                user['locations'].append(location)
                
                rules.check(None, location)
        
        time.sleep(100)
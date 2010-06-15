from geocron import settings
import httplib
import oauth2 as oauth
import urllib

try:
    import json
except ImportError:
    import simplejson as json

RESOURCE_DOMAIN = "www.googleapis.com"

class Latitude(object):
    
    def __init__(self, token, secret):
        self._token = token
        self._secret = secret
        self._conn = httplib.HTTPSConnection(RESOURCE_DOMAIN)
    
    def _invoke(self, path, params=None):
        
        resource_url = "http://%s/%s" % (RESOURCE_DOMAIN, path.lstrip('/'))
        
        token = oauth.Token(self._token, self._secret)
        consumer = oauth.Consumer(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
        oauth_request = oauth.Request.from_consumer_and_token(consumer, token, 'GET', resource_url, params)
        oauth_request.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, token)

        headers = oauth_request.to_header(realm='http://*.geocron.us')

        if params:
            resource_url = "%s?%s" % (resource_url, urllib.urlencode(params))

        self._conn.request('GET', resource_url, headers=headers)
        response = self._conn.getresponse()
        return json.loads(response.read())
    
    def current_location(self):    
        return self._invoke("/latitude/v1/currentLocation")
    
    def locations(self, granularity=None, max_results=100):
        if not granularity:
            granularity = 'city'
        return self._invoke("/latitude/v1/location", {
            'granularity': granularity,
            'max-results': 100,
        })

        
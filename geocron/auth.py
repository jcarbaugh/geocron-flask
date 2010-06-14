import httplib
import oauth2 as oauth
import settings
import time
import urllib
import urlparse
import webbrowser

LATITUDE_AUTH_SCOPE = "https://www.googleapis.com/auth/latitude"

REQUEST_URL = "https://www.google.com/accounts/OAuthGetRequestToken"
AUTH_URL = "https://www.google.com/latitude/apps/OAuthAuthorizeToken"
ACCESS_URL = "https://www.google.com/accounts/OAuthGetAccessToken"

# Create your consumer with the proper key/secret.
consumer = oauth.Consumer(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
# optionally set oauth_callback
request_token_url = "%s?oauth_callback=oob&scope=%s" % (REQUEST_URL, LATITUDE_AUTH_SCOPE)
client = oauth.Client(consumer)
resp, content = client.request(request_token_url, "POST")

request_token = dict(urlparse.parse_qsl(content))
oauth_token = request_token['oauth_token']
oauth_token_secret = request_token['oauth_token_secret']

print oauth_token, oauth_token_secret

print "%s?domain=geocron.us&location=all&granularity=best&hd=default&oauth_token=%s" % (LATITUDE_AUTH_URL, oauth_token)

oauth_verifier = raw_input('What is the PIN? ')

token = oauth.Token(oauth_token, oauth_token_secret)
token.set_verifier(oauth_verifier)

client = oauth.Client(consumer, token)
resp, content = client.request(ACCESS_URL, "POST")
access_token = dict(urlparse.parse_qsl(content))

access_token = {'oauth_token_secret': 'BWTG5qDfM08EAxHlR7/Hjw73', 'oauth_token': '1/IuNr5HSNUhvUR5viNT3sQLMc31NdyonwaDPYk2Fv0UU'}

oauth_access = access_token['oauth_token']
oauth_access_secret = access_token['oauth_token_secret']

#print "Access token:", access_token

###################

RESOURCE_DOMAIN = "www.googleapis.com"
RESOURCE_PATH = "/latitude/v1/currentLocation"
RESOURCE_URL = "http://%s%s" % (RESOURCE_DOMAIN, RESOURCE_PATH)

parameters = {
    'granularity': 'city',
    'max-results': 100,
}

token = oauth.Token(oauth_access, oauth_access_secret)
consumer = oauth.Consumer(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
oauth_request = oauth.Request.from_consumer_and_token(consumer, token, 'GET', RESOURCE_URL, parameters)
oauth_request.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, token)

headers = oauth_request.to_header(realm='http://*.geocron.us')
headers['Accept-Encoding'] = 'compress, gzip'

conn = httplib.HTTPSConnection(RESOURCE_DOMAIN)
#conn.set_debuglevel(10)
conn.request('GET', "%s?%s" % (RESOURCE_URL, urllib.urlencode(parameters)), headers=headers)
response = conn.getresponse()
print response.read()

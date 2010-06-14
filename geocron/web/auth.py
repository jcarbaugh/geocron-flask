from flask import Module, redirect, request, session
from geocron import settings
import oauth2 as oauth
import urllib
import urlparse

LATITUDE_SCOPE = "https://www.googleapis.com/auth/latitude"

REQUEST_URL = "https://www.google.com/accounts/OAuthGetRequestToken"
AUTH_URL = "https://www.google.com/latitude/apps/OAuthAuthorizeToken"
ACCESS_URL = "https://www.google.com/accounts/OAuthGetAccessToken"

if settings.DEBUG:
    CALLBACK_URL = "http://localhost:5000/login/auth"
else:
    CALLBACK_URL = "http://geocron.us/login/auth"

auth = Module(__name__)

@auth.route('/login')
def login():
    
    consumer = oauth.Consumer(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
    request_token_url = "%s?oauth_callback=%s&scope=%s" % (REQUEST_URL, CALLBACK_URL, LATITUDE_SCOPE)
    resp, content = oauth.Client(consumer).request(request_token_url, "POST")

    request_token = dict(urlparse.parse_qsl(content))
    session['request_token'] = request_token['oauth_token']
    session['request_secret'] = request_token['oauth_token_secret']

    params = {
        'domain': 'geocron.us',
        'location': 'all',
        'granularity': 'best',
        'hd': 'default',
        'oauth_token': request_token['oauth_token'],
    }

    url = "%s?%s" % (AUTH_URL, urllib.urlencode(params))
    return redirect(url)

@auth.route('/login/auth')
def login_auth():
    
    request_token = session.pop('request_token')
    request_secret = session.pop('request_secret')
    
    verifier = request.args.get('oauth_verifier', '')
    
    token = oauth.Token(request_token, request_secret)
    token.set_verifier(verifier)

    consumer = oauth.Consumer(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
    resp, content = oauth.Client(consumer, token).request(ACCESS_URL, "POST")
    access_token = dict(urlparse.parse_qsl(content))

    session['access_token'] = access_token['oauth_token']
    session['access_secret'] = access_token['oauth_token_secret']
    
    return redirect("/")
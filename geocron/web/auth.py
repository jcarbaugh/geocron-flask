from flask import Module, g, redirect, render_template, request, session
from geocron import settings
from openid.consumer.consumer import Consumer
from openid.store.filestore import FileOpenIDStore
from openid.yadis.discover import DiscoveryFailure
import oauth2 as oauth
import urllib
import urlparse

LATITUDE_SCOPE = "https://www.googleapis.com/auth/latitude"

OPENID_ENDPOINT = "https://www.google.com/accounts/o8/id"
REQUEST_URL = "https://www.google.com/accounts/OAuthGetRequestToken"
AUTH_URL = "https://www.google.com/latitude/apps/OAuthAuthorizeToken"
ACCESS_URL = "https://www.google.com/accounts/OAuthGetAccessToken"

if settings.DEBUG:
    REALM = "http://localhost:5000/"
else:    
    REALM = "http://geocron.us/"
    
OPENID_CALLBACK_URL = REALM + "login/auth"
OAUTH_CALLBACK_URL = REALM + "login/complete"

auth = Module(__name__)

@auth.route('/login')
def login():
    """
    Authenticate a user with Google OpenID.
    """

    # create new session state. should be deleted in login_complete.
    session['openid_session'] = {}
    
    # create consumer and make create request
    openid_consumer = Consumer(session['openid_session'], FileOpenIDStore('/tmp/'))
    try:
        auth_request = openid_consumer.begin(OPENID_ENDPOINT)
    except DiscoveryFailure, df:
        return render_template("500.html", error=df)
    
    # this is where attribute exchange stuff should be added
    extras = {
        "openid.ns.ax": "http://openid.net/srv/ax/1.0",
        "openid.ax.mode": "fetch_request",
        "openid.ax.required": "email",
        "openid.ax.type.email": "http://axschema.org/contact/email",
        #"openid.ax.type.firstname": "http://axschema.org/namePerson/first",
        #"openid.ax.type.lastname": "http://axschema.org/namePerson/last",
    }
    
    # generate OpenID request redirect URL
    url = auth_request.redirectURL(REALM, return_to=OPENID_CALLBACK_URL)
    
    return redirect("%s&%s" % (url, urllib.urlencode(extras)))

@auth.route('/login/auth')
def login_auth():
    """
    Once an OpenID has been verified, check to see if we have an OAuth token.
    If not, pass the user over to Google OAuth to get a Latitude token.
    """

    # get users collection from mongo
    users = g.db.users
    
    # get identity from request params and store in session
    # delete from session on logout
    identity = request.args.get('openid.ext1.value.email', '')
    session['identity'] = identity
    
    # check to see if user exists in mongo
    user = users.find_one({'_id': identity}) or {}
    
    if user and 'oauth' in user:
        # user exists and we have oauth tokens, redirect to home
        return redirect("/")
    
    if '_id' not in user:
        # user is brand new, save new user to mongo
        user['_id'] = identity
        user['email'] = identity
        user['firstname'] = request.args.get('openid.ext1.value.firstname', '')
        user['lastname'] = request.args.get('openid.ext1.value.lastname', '')
        users.save(user)
    
    # create oauth consumer
    consumer = oauth.Consumer(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
    request_token_url = "%s?oauth_callback=%s&scope=%s" % (REQUEST_URL, OAUTH_CALLBACK_URL, LATITUDE_SCOPE)
    resp, content = oauth.Client(consumer).request(request_token_url, "POST")

    # get request token from response
    request_token = dict(urlparse.parse_qsl(content))
    
    # set request token in session variables, remove in login_complete
    session['request_token'] = request_token['oauth_token']
    session['request_secret'] = request_token['oauth_token_secret']

    # parameters for obtaining access token
    params = {
        'domain': 'geocron.us',
        'location': 'all',
        'granularity': 'best',
        'hd': 'default',
        'oauth_token': request_token['oauth_token'],
    }

    # generate URL and redirect
    url = "%s?%s" % (AUTH_URL, urllib.urlencode(params))
    return redirect(url)

@auth.route('/login/complete')
def login_complete():
    """
    We've come back from OAuth so save everything and let's get going!
    """

    # get user from mongo
    users = g.db.users
    user = users.find_one({'_id': session['identity']})
    
    # pull request tokens from session
    request_token = session.pop('request_token')
    request_secret = session.pop('request_secret')
    
    # get verifier from GET variable
    verifier = request.args.get('oauth_verifier', '')
    
    # create new token using request tokens and verifier
    token = oauth.Token(request_token, request_secret)
    token.set_verifier(verifier)

    # create consumer and client to get access token
    consumer = oauth.Consumer(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
    resp, content = oauth.Client(consumer, token).request(ACCESS_URL, "POST")
    
    # parse access token from client response
    access_token = dict(urlparse.parse_qsl(content))
    
    # save oauth access tokens to mongo
    user['oauth'] = {
        'token': access_token['oauth_token'],
        'secret': access_token['oauth_token_secret'],
    }
    users.save(user)
    
    # remove openid_session dict from session
    if 'openid_session' in session:
        session.pop('openid_session')
    
    return redirect("/")

@auth.route('/logout')
def logout():
    if 'identity' in session:
        session.pop('identity')
    return redirect("/")
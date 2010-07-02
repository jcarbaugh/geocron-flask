DEBUG = True

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_DB = 'geocron'

# These should go in local_settings
# CONSUMER_KEY = ''
# CONSUMER_SECRET = ''
# SECRET_KEY = ''
# VALID_USERS = ('',)
# ADMINS = ('',)

try:
    from local_settings import *
except ImportError:
    pass
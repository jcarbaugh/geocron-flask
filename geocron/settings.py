DEBUG = True

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

try:
    from local_settings import *
except ImportError:
    pass
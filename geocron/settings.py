DEBUG = True

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_DB = 'geocron'

try:
    from local_settings import *
except ImportError:
    pass
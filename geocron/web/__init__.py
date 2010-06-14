from flask import Flask
from geocron.web.auth import auth

application = Flask(__name__)
application.register_module(auth)

@application.route("/")
def hello():
    return "Hello World!"

#!/usr/bin/env python
from geocron import settings
from geocron.web import application

if __name__ == "__main__":

    application.secret_key = settings.SECRET_KEY
    application.run(port=8000, debug=settings.DEBUG)
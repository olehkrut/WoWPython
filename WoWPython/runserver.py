"""
This script runs the WoWPython application using a development server.
"""

from os import environ
from WoWPython import app

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '4442'))
    except ValueError:
        PORT = 4442
    app.run(HOST, PORT)

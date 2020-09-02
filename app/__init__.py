from flask import Flask
from flask import request, jsonify

from app.controllers import default

app = Flask(__name__)

app.config.from_object('config')

# default.app_define(app)

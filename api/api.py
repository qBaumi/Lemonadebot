import json

import flask
from flask import Flask
import sys

# appending the parent directory path
sys.path.append('../')
import dbutils

app = Flask(__name__)


@app.route('/commands')
def commands():
    with open("../json/commands.json", "r") as f:
        commands = json.load(f)
    response = flask.jsonify(commands)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/emotes')
def emotes():
    emotestats = dbutils.sql_select(f"SELECT * FROM emote_tracker")
    response = flask.jsonify(emotestats)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

app.run()
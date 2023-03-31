import datetime
import json

import flask
from flask import Flask
import sys
from flask_cors import CORS

# appending the parent directory path
sys.path.append('../')
import dbutils, utils

app = Flask(__name__)
CORS(app) # This will enable CORS for all routes


@app.route('/commands')
def commands():
    with open("../json/commands.json", "r") as f:
        commands = json.load(f)
    response = flask.jsonify(commands)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/emotes')
def emotes():
    emotestats = dbutils.sql_select(f"SELECT name, SUM(count) FROM emote_tracker GROUP BY name ORDER BY SUM(count) DESC")
    response = flask.jsonify(emotestats)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/emotes/daily')
def emotesdaily():
    date = utils.getDate()
    emotestats = dbutils.sql_select(f"SELECT name, SUM(count) FROM emote_tracker WHERE date = '{date}' GROUP BY name ORDER BY SUM(count) DESC")
    response = flask.jsonify(emotestats)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/emotes/monthly')
def emotesmonthly():
    date = datetime.datetime.fromtimestamp((datetime.datetime.now().timestamp() - 2630000)).strftime("%Y-%m-%d")
    emotestats = dbutils.sql_select(f"SELECT name, SUM(count) FROM emote_tracker WHERE CONCAT(SUBSTRING(date, 7, 10), '-', SUBSTRING(date, 4, 2), '-', SUBSTRING(date, 1, 2)) >= '{date}' GROUP BY name ORDER BY SUM(count) DESC")
    response = flask.jsonify(emotestats)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/emotes/weekly')
def emotesweekly():
    date = datetime.datetime.fromtimestamp((datetime.datetime.now().timestamp() - 604800)).strftime("%Y-%m-%d")
    emotestats = dbutils.sql_select(f"SELECT name, SUM(count) FROM emote_tracker WHERE CONCAT(SUBSTRING(date, 7, 10), '-', SUBSTRING(date, 4, 2), '-', SUBSTRING(date, 1, 2)) >= '{date}' GROUP BY name ORDER BY SUM(count) DESC")
    response = flask.jsonify(emotestats)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
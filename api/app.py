import datetime
import json

import flask
from flask import Flask, request
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


@app.route('/saveZeit', methods=['POST'])
def saveZeit():
    if request.method == 'POST':
        data = request.get_json()  # Assuming the request body contains JSON data
        # Process the data as needed
        print(data)
        dbutils.sql_exec(f"INSERT INTO stoppuhr(timestamp, millilseconds) VALUES ({data['zeit']}, '{data['timestamp']}')")
        return 'Data received successfully'
    else:
        return 'Invalid request method'


if __name__ == '__main__':
    app.run(port=5695, host="0.0.0.0")

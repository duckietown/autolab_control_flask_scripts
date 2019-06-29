#!flask/bin/python
import os, subprocess
from ping_all import ping_all_main, ping_all_with_list
from logging_checks import logging_checks_main, logging_checks_with_list
from space_checks import space_checks_main
from start_logging import start_logging_main
from stop_logging import stop_logging_main
from clear_memory import clear_memory_main

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/lights_off', methods=['GET'])
@cross_origin()
def lights_off():
    return jsonify({'success': True})

@app.route('/lights_on', methods=['GET'])
@cross_origin()
def lights_on():
    return jsonify({'success': True})

@app.route('/ping', methods=['GET','POST'])
@cross_origin()
def ping_hosts():
    if request.method == 'GET':
        host, ping = ping_all_main()
        return jsonify({'hostname': host, 'ping': ping})
    else:
        data=request.get_json()["list"]
        host, ping = ping_all_with_list(data)
        return jsonify({'hostname': host, 'ping': ping})

@app.route('/logging_checks', methods=['GET','POST'])
@cross_origin()
def logging_checker():
    if request.method == 'GET':
        host, check = logging_checks_main()
        return jsonify({'hostname': host, 'logging_check': check})
    else:
        data=request.get_json()["list"]
        host, check = logging_checks_with_list(data)
        return jsonify({'hostname': host, 'logging_check': check})

@app.route('/storage_space_checks', methods=['GET'])
@cross_origin()
def space_checker():
    host, check = space_checks_main()
    return jsonify({'hostname': host, 'space_check': check})

@app.route('/start_logging', methods=['GET'])
@cross_origin()
def logging_starter():
    host, check = start_logging_main()
    return jsonify({'hostname': host, 'logging_start': check})

@app.route('/stop_logging', methods=['GET'])
@cross_origin()
def logging_stopper():
    host, check = stop_logging_main()
    return jsonify({'hostname': host, 'logging_stop': check})

@app.route('/clear_memory', methods=['GET'])
@cross_origin()
def memory_clearer():
    host, check = clear_memory_main()
    return jsonify({'hostname': host, 'clear_memory': check})

@app.route('/test', methods=['POST'])
@cross_origin()
def post_test():
    data=request.get_json()["test"]
    for entry in data:
        print(entry)
    return jsonify({"hello":"world"})

if __name__ == '__main__':
    app.run(host= '0.0.0.0')

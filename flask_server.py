#!flask/bin/python
import os, subprocess
from ping_all import ping_all_main, ping_all_with_list
from logging_checks import logging_checks_main, logging_checks_with_list
from space_checks import space_checks_main, space_checks_with_list
from start_logging import start_logging_main, start_logging_with_list
from stop_logging import stop_logging_main, stop_logging_with_list
from clear_memory import clear_memory_main, clear_memory_with_list
from start_active_bots import start_active_bots_with_list
from start_passive_bots import start_passive_bots_with_list

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import requests, json

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

@app.route('/storage_space_checks', methods=['GET','POST'])
@cross_origin()
def space_checker():
    if request.method == 'GET':
        host, check = space_checks_main()
        return jsonify({'hostname': host, 'space_check': check})
    else:
        data=request.get_json()["list"]
        host, check = space_checks_with_list(data)
        return jsonify({'hostname': host, 'space_check': check})

@app.route('/start_logging', methods=['GET','POST'])
@cross_origin()
def logging_starter():
    if request.method == 'GET':
        host, check = start_logging_main()
        return jsonify({'hostname': host, 'logging_start': check})
    else:
        data=request.get_json()["list"]
        host, check = start_logging_with_list(data)
        return jsonify({'hostname': host, 'logging_start': check})

@app.route('/stop_logging', methods=['GET','POST'])
@cross_origin()
def logging_stopper():
    if request.method == 'GET':
        host, check = stop_logging_main()
        return jsonify({'hostname': host, 'logging_stop': check})
    else:
        data=request.get_json()["list"]
        host, check = stop_logging_with_list(data)
        return jsonify({'hostname': host, 'logging_stop': check})

@app.route('/clear_memory', methods=['GET','POST'])
@cross_origin()
def memory_clearer():
    if request.method == 'GET':
        host, check = clear_memory_main()
        return jsonify({'hostname': host, 'clear_memory': check})
    else:
        data=request.get_json()["list"]
        host, check = clear_memory_with_list(data)
        return jsonify({'hostname': host, 'clear_memory': check})

@app.route('/start_active_bots', methods=['POST'])
@cross_origin()
def start_active():
    list=request.get_json()["list"]
    container=request.get_json()["container"]
    duration=request.get_json()["duration"]
    host, check = start_active_bots_with_list(list, container, duration)
    return jsonify({'hostname': host, 'container': check})

@app.route('/start_passive_bots', methods=['POST'])
@cross_origin()
def start_passive():
    list=request.get_json()["list"]
    container=request.get_json()["container"]
    host, check = start_passive_bots_with_list(list, container)
    return jsonify({'hostname': host, 'container': check})

@app.route('/toggle_switch', methods=['GET'])
@cross_origin()
def toggle_switch():
    url = 'http://172.31.168.15/report'
    response = requests.request('GET', url)
    response = response.json()
    print(response)
    return jsonify(response)

if __name__ == '__main__':
    app.run(host= '0.0.0.0', port=5050)

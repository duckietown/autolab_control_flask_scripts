#!flask/bin/python
import os, subprocess
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import requests, json

from ping_all import ping_all_main, ping_all_with_list
from logging_checks import logging_checks_main, logging_checks_with_list
from space_checks import space_checks_main, space_checks_with_list
from start_logging import start_logging_main, start_logging_with_list
from stop_logging import stop_logging_main, stop_logging_with_list
from clear_memory import clear_memory_main, clear_memory_with_list
from start_active_bots import start_active_bots_with_list
from start_passive_bots import start_passive_bots_with_list
from submission_server import request_job, upload_job
from reset_duckiebot import reset_duckiebot_with_list

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
    bot_list=request.get_json()["list"]
    container=request.get_json()["container"]
    duration=int(request.get_json()["duration"])
    host, check = start_active_bots_with_list(bot_list, container, duration)
    return jsonify({'hostname': host, 'container': check})

@app.route('/start_passive_bots', methods=['POST'])
@cross_origin()
def start_passive():
    bot_list=request.get_json()["list"]
    demo=request.get_json()["demo"]
    host, check = start_passive_bots_with_list(bot_list, demo)
    return jsonify({'hostname': host, 'container': check})

@app.route('/toggle_switch', methods=['GET'])
@cross_origin()
def toggle_switch():
    url = 'http://172.31.168.15/report'
    response = requests.request('GET', url)
    response = response.json()
    return jsonify(response)

@app.route('/request_submission', methods=['POST'])
@cross_origin()
def submission_request():
    token = request.get_json()["token"]
    endpoint = request.get_json()["endpoint"]
    url = request.get_json()["url"]
    response = request_job(token, endpoint, url)
    return jsonify(response)

@app.route('/upload_data', methods=['POST'])
@cross_origin()
def data_upload():
    token = request.get_json()["token"]
    endpoint = request.get_json()["endpoint"]
    url = request.get_json()["url"]
    response = upload_job(token, endpoint, url)
    return jsonify(response)

@app.route('/reset_duckiebot', methods=['POST'])
@cross_origin()
def duckiebot_reset():
    bot_list=request.get_json()["list"]
    host, outcome = reset_duckiebot_with_list(bot_list)
    return jsonify({'hostname': host, 'outcome': outcome})

if __name__ == '__main__':
    app.run(host= '0.0.0.0', port=5050)

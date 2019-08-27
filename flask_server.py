#!flask/bin/python
import os
import subprocess
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import requests
import json

from ping_all import ping_all_main, ping_all_with_list
from start_active_bots import start_active_bots_with_list
from start_passive_bots import start_passive_bots_with_list
from submission_server import request_job, upload_job
from reset_duckiebot import reset_duckiebot_with_list
from create_log import generate_log_file
from logging_utils import start_logging, stop_logging
from bag_processing import start_bag_processing, check_bag_processing
from space_check import check_space_for_logging
from docker_maintenance import docker_maintenance_with_list
from localization import run_localization, check_localization
from stop_passive_bots import stop_passive_bots_with_list
from copy_autolab_roster import copy_roster_with_list

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# API call to ping the devices on the network. GET call will call all devices in the device_list.txt file, POST will call the hosts given in the 'list' argument
@app.route('/ping', methods=['GET', 'POST'])
@cross_origin()
def ping_hosts():
    if request.method == 'GET':
        host, ping = ping_all_main()
        return jsonify({'hostname': host, 'ping': ping})
    else:
        data = request.get_json()["list"]
        host, ping = ping_all_with_list(data)
        return jsonify({'hostname': host, 'ping': ping})

# API call to start submission containers received from the submissions server on the duckiebots (active bots)
@app.route('/start_active_bots', methods=['POST'])
@cross_origin()
def start_active():
    bot_list = request.get_json()["list"]
    container = request.get_json()["container"]
    duration = int(request.get_json()["duration"])
    host, check = start_active_bots_with_list(bot_list, container, duration)
    return jsonify({'hostname': host, 'container': check})

# API call to start demos on the duckiebots (passive bots)
@app.route('/start_passive_bots', methods=['POST'])
@cross_origin()
def start_passive():
    bot_list = request.get_json()["list"]
    demo = request.get_json()["demo"]
    host, check = start_passive_bots_with_list(bot_list, demo)
    return jsonify({'hostname': host, 'container': check})

# API call to handle the smart switches (due to CORS exceptions this needs to be done via the Flask server and not directly via the webinterface)
@app.route('/toggle_switch', methods=['GET'])
@cross_origin()
def toggle_switch():
    url = request.get_json()["url"]
    response = requests.request('GET', url)
    response = response.json()
    return jsonify(response)

# API call to request a new submission from the server, needs to be called multiple times before the server answers
@app.route('/request_submission', methods=['POST'])
@cross_origin()
def submission_request():
    token = request.get_json()["token"]
    endpoint = request.get_json()["endpoint"]
    url = request.get_json()["url"]
    response = request_job(token, endpoint, url)
    return jsonify(response)

# API call to upload a finished submission to the server
@app.route('/upload_data', methods=['POST'])
@cross_origin()
def data_upload():
    token = request.get_json()["token"]
    endpoint = request.get_json()["endpoint"]
    url = request.get_json()["url"]
    response = upload_job(token, endpoint, url)
    return jsonify(response)

# API call to reset the duckiebot-inteface and acquisition-bridge on a duckiebot
@app.route('/reset_duckiebot', methods=['POST'])
@cross_origin()
def duckiebot_reset():
    bot_list = request.get_json()["list"]
    host, outcome = reset_duckiebot_with_list(bot_list)
    return jsonify({'hostname': host, 'outcome': outcome})

# API call to create a .yaml file containing a log of a submission
@app.route('/create_log', methods=['POST'])
@cross_origin()
def log_creator():
    content = request.get_json()["content"]
    filename = request.get_json()["filename"]
    mount = request.get_json()["mount"]
    outcome = generate_log_file(content, filename, mount)
    return jsonify({'outcome': outcome})

# API call to check the available space on the server for logging
@app.route('/space_check', methods=['POST'])
@cross_origin()
def space_checker():
    outcome = check_space_for_logging()
    return jsonify({'outcome': outcome})

# API call to start the logging container (Rosbag) and log all necessary frames
@app.route('/start_logging', methods=['POST'])
@cross_origin()
def logging_starter():
    computer = request.get_json()["computer"]
    filename = request.get_json()["filename"]
    device_list = request.get_json()["device_list"]
    mount_folder = request.get_json()["mount_folder"]
    outcome = start_logging(computer, filename, device_list, mount_folder)
    return jsonify({'outcome': outcome})

# API call to stop logging after the submission terminated
@app.route('/stop_logging', methods=['POST'])
@cross_origin()
def logging_stopper():
    computer = request.get_json()["computer"]
    outcome = stop_logging(computer)
    return jsonify({'outcome': outcome})

# API call to start the apriltag posprocessing from the gathered Rosbag/images
@app.route('/start_bag_processing', methods=['POST'])
@cross_origin()
def apriltag_processor():
    input_bag_name = request.get_json()["input_bag_name"]
    output_bag_name = request.get_json()["output_bag_name"]
    mount_computer_side = request.get_json()["mount_computer_side"]
    mount_container_side = request.get_json()["mount_container_side"]
    outcome = start_bag_processing(
        input_bag_name, output_bag_name, mount_computer_side, mount_container_side)
    return jsonify({'outcome': outcome})

# API call to check the apriltag posprocessing from the gathered Rosbag/images
@app.route('/check_bag_processing', methods=['POST'])
@cross_origin()
def check_apriltag_processor():
    outcome = check_bag_processing()
    return jsonify({'outcome': outcome})

# API call to perform docker maintenance on multiple agents, i.e. restarting, stopping, ... containers
@app.route('/docker_maintenance', methods=['POST'])
@cross_origin()
def docker_maintainer():
    command = request.get_json()["command"]
    device_list = request.get_json()["device_list"]
    host, outcome = docker_maintenance_with_list(command, device_list)
    return jsonify({'hostname': host, 'outcome': outcome})

# API call to process localization
@app.route('/process_localization', methods=['POST'])
@cross_origin()
def process_localization():
    input_bag_name = request.get_json()["input_bag_name"]
    output_dir = request.get_json()["output_dir"]
    mount_computer_side = request.get_json()["mount_computer_side"]
    mount_container_side = request.get_json()["mount_container_side"]
    outcome = run_localization(
        input_bag_name, output_dir, mount_computer_side, mount_container_side)
    return jsonify({'outcome': outcome})

# API call to check localization progress
@app.route('/check_localization', methods=['POST'])
@cross_origin()
def localization_checker():
    outcome = check_localization()
    return jsonify({'outcome': outcome})

# API call to stop demos on the duckiebots (passive bots)
@app.route('/stop_passive_bots', methods=['POST'])
@cross_origin()
def stop_passive():
    bot_list = request.get_json()["list"]
    demo = request.get_json()["demo"]
    host, check = stop_passive_bots_with_list(bot_list, demo)
    return jsonify({'hostname': host, 'container': check})

# API call to stop demos on the duckiebots (passive bots)
@app.route('/copy_roster', methods=['POST'])
@cross_origin()
def copy_roster():
    bot_list = request.get_json()["list"]
    mount = request.get_json()["mount"]
    roster_location = request.get_json()["roster_location"]
    outcome = copy_roster_with_list(bot_list, mount, roster_location)
    return jsonify({'outcome': outcome})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)

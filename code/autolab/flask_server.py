#!flask/bin/python
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import requests

from .ping_all import ping_all_main, ping_all_with_list
from .start_active_bots import start_active_bots_with_list
from .start_passive_bots import start_passive_bots_with_list
from .submission_server import request_job, upload_job, create_hashes, upload_s3
from .reset_duckiebot import reset_duckiebot_with_list
from .create_log import generate_log_file
from .logging_utils import start_logging, stop_logging
from .bag_processing import start_bag_processing, check_bag_processing
from .space_check import check_space_for_logging
from .docker_maintenance import docker_maintenance_with_list
from .localization import run_localization, check_localization
from .stop_passive_bots import stop_passive_bots_with_list
from .copy_autolab_roster import copy_roster_with_list
from .get_trajectory import request_yaml
from .submission_map import get_map, copy_map


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


# API call to ping the devices on the network.
# GET call will call all devices in the device_list.txt file,
# POST will call the hosts given in the 'list' argument
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


# API call to start submission containers received from the submissions server on the duckiebots
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


# API call to handle the smart switches
# (due to CORS, this needs to be done via the Flask server and not directly via the webinterface)
@app.route('/toggle_switch', methods=['GET'])
@cross_origin()
def toggle_switch():
    url = request.get_json()["url"]
    response = requests.request('GET', url)
    response = response.json()
    return jsonify(response)


# API call to request a new submission from the server,
# needs to be called multiple times before the server answers
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
    job_id = request.get_json()["job_id"]
    result = request.get_json()["result"]
    ipfs_hashes = request.get_json()["ipfs_hashes"]
    scores = request.get_json()["scores"]
    uploaded = request.get_json()["uploaded"]
    response = upload_job(token, endpoint, url, job_id,
                          result, ipfs_hashes, scores, uploaded)
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
    # computer = request.get_json()["computer"]
    device_list = request.get_json()["device_list"]
    filename = request.get_json()["filename"]
    mount_folder = request.get_json()["mount_folder"]
    outcome = start_logging(filename, device_list, mount_folder)
    return jsonify({'outcome': outcome})


# API call to stop logging after the submission terminated
@app.route('/stop_logging', methods=['POST'])
@cross_origin()
def logging_stopper():
    # computer = request.get_json()["computer"]
    # outcome = stop_logging(computer)
    outcome = stop_logging()
    return jsonify({'outcome': outcome})


# API call to start the apriltag posprocessing from the gathered Rosbag/images
@app.route('/start_bag_processing', methods=['POST'])
@cross_origin()
def apriltag_processor():
    input_bag_name = request.get_json()["input_bag_name"]
    output_bag_name = request.get_json()["output_bag_name"]
    mount_computer_side = request.get_json()["mount_computer_side"]
    mount_container_side = request.get_json()["mount_container_side"]
    device_list = request.get_json()["device_list"]
    ros_master_ip = request.get_json()["ros_master_ip"]
    outcome = start_bag_processing(
        ros_master_ip,
        input_bag_name,
        output_bag_name,
        mount_computer_side,
        device_list,
        mount_container_side
    )
    return jsonify({'outcome': outcome})


# API call to check the apriltag posprocessing from the gathered Rosbag/images
@app.route('/check_bag_processing', methods=['POST'])
@cross_origin()
def check_apriltag_processor():
    output_bag_name = request.get_json()["output_bag_name"]
    mount_computer_origin = request.get_json()["mount_computer_origin"]
    mount_computer_destination = request.get_json()[
        "mount_computer_destination"]
    outcome = check_bag_processing(
        output_bag_name, mount_computer_origin, mount_computer_destination)
    return jsonify({'outcome': outcome})


# API call to perform docker maintenance on multiple agents,
# i.e. restarting, stopping, ... containers
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
    ros_master_ip = request.get_json()["ros_master_ip"]
    input_bag_name = request.get_json()["input_bag_name"]
    output_dir = request.get_json()["output_dir"]
    mount_computer_side = request.get_json()["mount_computer_side"]
    mount_container_side = request.get_json()["mount_container_side"]
    outcome = run_localization(
        ros_master_ip, input_bag_name, output_dir, mount_computer_side, mount_container_side)
    return jsonify({'outcome': outcome})


# API call to check localization progress
@app.route('/check_localization', methods=['POST'])
@cross_origin()
def localization_checker():
    active_bot = request.get_json()["active_bot"]
    passive_bots = request.get_json()["passive_bots"]
    mount_computer_side = request.get_json()["mount_computer_side"]
    outcome = check_localization(active_bot, passive_bots, mount_computer_side)
    return jsonify({'outcome': outcome})


# API call to stop demos on the duckiebots (passive bots)
@app.route('/stop_passive_bots', methods=['POST'])
@cross_origin()
def stop_passive():
    bot_list = request.get_json()["list"]
    demo = request.get_json()["demo"]
    host, check = stop_passive_bots_with_list(bot_list, demo)
    return jsonify({'hostname': host, 'container': check})


# API call to copy the required roster files to the submission
@app.route('/copy_roster', methods=['POST'])
@cross_origin()
def copy_roster():
    bot_list = request.get_json()["list"]
    mount = request.get_json()["mount"]
    roster_location = request.get_json()["roster_location"]
    outcome = copy_roster_with_list(bot_list, mount)
    return jsonify({'outcome': outcome})


# API call request submission csv
@app.route('/request_yaml', methods=['POST'])
@cross_origin()
def yaml_requester():
    mount = request.get_json()["mount"]
    duckiebot = request.get_json()["duckiebot"]
    data = request_yaml(mount, duckiebot)
    return jsonify({'data': data})


# API call to get subission map with starting positions
@app.route('/get_map', methods=['POST'])
@cross_origin()
def map_fetcher():
    container = request.get_json()["container"]
    name = request.get_json()["name"]
    step = request.get_json()["step"]
    data = get_map(container, name, step)
    return jsonify({'data': data})


# API call to copy yaml map to logging folder
@app.route('/copy_map', methods=['POST'])
@cross_origin()
def map_copy():
    mount = request.get_json()["mount"]
    map_location = request.get_json()["map_location"]
    path = request.get_json()["path"]
    outcome = copy_map(mount, map_location, path)
    return jsonify({'outcome': outcome})


# API call to create ipfs hashes
@app.route('/ipfs_add', methods=['POST'])
@cross_origin()
def ipfs_add():
    mount = request.get_json()["mount"]
    data = create_hashes(mount)
    return jsonify({'data': data})


# API call to upload to S3
@app.route('/upload_s3', methods=['POST'])
@cross_origin()
def s3_uploader():
    aws_config = request.get_json()["aws_config"]
    path = request.get_json()["path"]
    ignore_pattern = request.get_json()["ignore_pattern"]
    data = upload_s3(aws_config, path, ignore_pattern)
    print(data)
    return jsonify({'data': data})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)

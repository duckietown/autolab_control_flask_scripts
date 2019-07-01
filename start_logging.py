import multiprocessing
import subprocess
from typing import List

from aido_utils import get_device_list, show_status


def log_device(device):
    if "watchtower" in device:
        cmd = "docker -H %s.local restart ros_picam" % device
        try:
            subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            print("Error trying to launch ros-picam on %s" % device)

    cmd = 'docker -H %s.local stop logger; \
           docker -H %s.local rm logger; \
           docker -H %s.local run --rm -d --net host \
           --name logger -v /data/logs:/logs duckietown/rpi-duckiebot-base:master19 \
           make log-minimal-docker' \
           % (device, device, device)

    try:
        subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)

        cmd = 'docker -H %s.local inspect -f \'{{.State.Running}}\' logger' % device
        res = subprocess.check_output(cmd, shell=True)
        res = res.rstrip().decode("utf-8")

        if res == "true":
            return "Started container"
        else:
            return "Couldn't start"

    except subprocess.CalledProcessError as e:
        return "Error %s" % e.output.decode("utf-8")


def log_all_devices(device_list):
    pool = multiprocessing.Pool(processes=20)
    results = pool.map(log_device, device_list)
    pool.close()
    pool.join()
    show_status(device_list, results)
    return results

def start_logging_main():
    device_list = get_device_list('device_list.txt')
    return device_list, log_all_devices(device_list)

def start_logging_with_list(device_list):
    return device_list, log_all_devices(device_list)

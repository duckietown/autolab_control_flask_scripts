import multiprocessing
import subprocess
from typing import List
import time

from aido_utils import get_device_list, show_status

container = ""
duration = 0

def start_device(device):
    global container
    global duration
    try:
        cmd = "docker -H %s.local restart duckiebot-interface" % device
        subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        print(device+ ": Restarting the duckiebot-interface")
        time.sleep(10)
        print(device+ ": Starting the submission: "+container)
        cmd = "dts duckiebot evaluate --duckiebot_name %s --image %s --duration %s" % (device, container, duration)
        res = subprocess.Popen(cmd, shell=True, executable="/bin/bash")
        time.sleep(10)
        cmd = 'docker inspect -f \'{{.State.Running}}\' agent'
        res = subprocess.check_output(cmd, shell=True)
        print("here 2")
        res = res.rstrip().decode("utf-8")
        print(res)

        if res == "true":
            return "Started evaluation"
        else:
            return "Couldn't start"

    except subprocess.CalledProcessError:
        return "Error"


def start_all_devices(device_list):
    pool = multiprocessing.Pool(processes=20)
    results = pool.map(start_device, device_list)
    pool.close()
    pool.join()
    show_status(device_list, results)
    return results

def start_active_bots_with_list(device_list, submission_container, submission_duration):
    global container
    global duration
    container = submission_container
    duration = submission_duration
    return device_list, start_all_devices(device_list)

print(start_active_bots_with_list({"autobot03"}, "localhost:5000/webbe035/aido-submissions:2019_07_23_15_41_34", 20))
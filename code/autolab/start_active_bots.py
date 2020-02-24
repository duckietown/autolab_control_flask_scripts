import subprocess
import multiprocessing
from typing import List
import time

from .aido_utils import get_device_list, show_status

container = ""
duration = 0


def start_device(device):
    global container
    global duration
    try:
        print(device + ": Starting the submission: "+container)
        cmd = "dts duckiebot evaluate --duckiebot_name %s --image %s --duration %s" % (
            device, container, duration
        )
        subprocess.Popen(cmd, shell=True, executable="/bin/bash")
        return "Started evaluation"

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
    outcome = start_all_devices(device_list)
    return device_list, outcome

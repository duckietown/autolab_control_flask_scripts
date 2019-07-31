import subprocess,multiprocessing
from typing import List
import time

from aido_utils import get_device_list, show_status

def start_device(device):
    try:
        print(device+ ": Restarting the duckiebot-interface")
        cmd = "docker -H %s.local restart duckiebot-interface" % device
        subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        time.sleep(10)
        print(device+ ": Restarting the acquisition-bridge")
        cmd = "docker -H %s.local restart acquisition-bridge" % device
        subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return "Duckiebot reset"

    except subprocess.CalledProcessError:
        return "Error"


def start_all_devices(device_list):
    pool = multiprocessing.Pool(processes=20)
    results = pool.map(start_device, device_list)
    pool.close()
    pool.join()
    show_status(device_list, results)
    return results

def reset_duckiebot_with_list(device_list):
    outcome = start_all_devices(device_list)
    return device_list, outcome
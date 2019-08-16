import subprocess
import multiprocessing
from typing import List
from aido_utils import get_device_list, show_status

operation = ""


def docker_maintenance(device):
    global operation
    cmd = 'docker -H %s.local %s' % (device, operation)
    try:
        out = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT)
        return out
    except subprocess.CalledProcessError:
        return 0


def docker_maintenance_all_devices(device_list):
    pool = multiprocessing.Pool(processes=20)
    results = pool.map(docker_maintenance, device_list)
    pool.close()
    pool.join()
    show_status(device_list, results)
    return results

def docker_maintenance_with_list(cmd, device_list):
    global operation
    operation = cmd
    return device_list, docker_maintenance_all_devices(device_list)

print(docker_maintenance_with_list("restart acquisition-bridge",["watchtower01"]))
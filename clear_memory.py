import multiprocessing
import subprocess
from typing import *

from aido_utils import get_device_list, show_status


def free_space_device(device):
    cmd = 'ssh -q %s "sudo rm -rf /data/logs/*"' % (device)

    try:
        subprocess.check_output(cmd, shell=True)
        return "Success"
    except subprocess.CalledProcessError as e:
        return "Error"


def free_space_all_devices(device_list):
    pool = multiprocessing.Pool(processes=20)
    results = pool.map(free_space_device, device_list)
    pool.close()
    pool.join()
    show_status(device_list, results)
    return results

def clear_memory_main():
    device_list = get_device_list('device_list.txt')
    return device_list, free_space_all_devices(device_list)

import multiprocessing
import subprocess
from typing import List

from aido_utils import get_device_list, show_status

container = ""

def start_device(device):
    return container


def start_all_devices(device_list):
    pool = multiprocessing.Pool(processes=20)
    results = pool.map(start_device, device_list)
    pool.close()
    pool.join()
    show_status(device_list, results)
    return results

def start_passive_bots_with_list(device_list, passive_container):
    container = passive_container
    return device_list, start_all_devices(device_list)

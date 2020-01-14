import os
import re
import subprocess
import multiprocessing
from typing import List

from .aido_utils import get_device_list, show_status
from .constants import STATIC_DIR


def ping_device(device):
    cmd = f'ping -c 3 -W 5 -i 0.2 {device}.local'
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        stats = out.decode('utf-8').split('\n')
        if len(stats) < 2:
            return 0
        m = re.search('^rtt min/avg/max/mdev = [^\/]+/([^\/]+)/.*$', stats[-2])
        return m.group(1) if m else 0
    except subprocess.CalledProcessError:
        return 0


def ping_all_devices(device_list):
    pool = multiprocessing.Pool(processes=20)
    results = pool.map(ping_device, device_list)
    pool.close()
    pool.join()
    show_status(device_list, results)
    return results


def ping_all_main():
    device_list_filepath = os.path.join(STATIC_DIR, 'device_list.txt')
    device_list = get_device_list(device_list_filepath)
    return device_list, ping_all_devices(device_list)


def ping_all_with_list(device_list):
    return device_list, ping_all_devices(device_list)

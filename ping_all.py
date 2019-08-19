import subprocess
import multiprocessing
from typing import List
from aido_utils import get_device_list, show_status


def ping_device(device):
    cmd = 'ping -c 3 %s.local' % device
    try:
        out = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT)
        tmp = out[out.find('mdev'):]
        tmp2 = tmp[tmp.find('/')+1:]
        tmp3 = tmp2[:tmp2.find('/')]
        return tmp3
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
    device_list = get_device_list('device_list.txt')
    return device_list, ping_all_devices(device_list)


def ping_all_with_list(device_list):
    return device_list, ping_all_devices(device_list)

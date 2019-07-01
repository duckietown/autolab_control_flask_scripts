import multiprocessing
import subprocess
from typing import List

from aido_utils import get_device_list, show_status


def check_space_device(device):

    cmd1 = 'ssh -q %s "df -h | grep /dev/root; exit 0;"' % (device)
    cmd2 = 'ssh -q %s "df -h | grep /dev/sda1; exit 0;"' % (device)

    try:
        res1 = subprocess.check_output(cmd1, shell=True)
        res1 = res1.rstrip().decode("utf-8")

        if res1 == "":
            return "Error"
        else:
            res1 = res1.split()[3]

        res2 = subprocess.check_output(cmd2, shell=True)
        res2 = res2.rstrip().decode("utf-8")

        if res2 == "":
            res2 = "0G"
        else:
            res2 = res2.split()[3]

        return "Root:%s, USB: %s"%(res1,res2)

    except subprocess.CalledProcessError:
        return "Error"


def check_space_all_devices(device_list):
    pool = multiprocessing.Pool(processes=20)
    results = pool.map(check_space_device, device_list)
    pool.close()
    pool.join()
    show_status(device_list, results)
    return results


def space_checks_main():
    device_list = get_device_list('device_list.txt')
    return device_list, check_space_all_devices(device_list)

def space_checks_with_list(device_list):
    return device_list, check_space_all_devices(device_list)

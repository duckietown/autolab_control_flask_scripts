import multiprocessing
import subprocess
from typing import List
import time
from aido_utils import get_device_list, show_status


def stop_logging_device(device):

    # Check if already stopped
    try:
        cmd = 'docker -H %s.local inspect -f \'{{.State.Running}}\' logger' % device
        res = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        res = e.output.decode("utf-8")
        if "No such object" in res:
            return "Already stopped"
        return "Error"

    # Otherwise stop
    cmd = 'docker -H %s.local stop logger' % (device)
    try:
        subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)

        while True:
            print("Waiting for %s.." % device)
            cmd = 'docker -H %s.local inspect -f \'{{.State.Running}}\' logger' % device
            res = subprocess.check_output(
                cmd, shell=True, stderr=subprocess.STDOUT)
            if res.decode("utf-8") == "false\n":
                cmd = 'docker -H %s.local rm -f  logger' % device
                try:
                    res = subprocess.check_output(
                        cmd, shell=True, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as e:
                    res = e.output.decode("utf-8")
                    if "No such object" in res:
                        return "Stopped"

            time.sleep(0.5)

    except subprocess.CalledProcessError as e:
        res = e.output.decode("utf-8")
        if "No such object" in res:
            return "Stopped"
        return "Error"


def stop_logging_all_devices(device_list):
    pool = multiprocessing.Pool(processes=20)
    results = pool.map(stop_logging_device, device_list)
    pool.close()
    pool.join()
    show_status(device_list, results)
    return results


def stop_logging_main():
    device_list = get_device_list('device_list.txt')
    return device_list, stop_logging_all_devices(device_list)

def stop_logging_with_list(device_list):
    return device_list, stop_logging_all_devices(device_list)

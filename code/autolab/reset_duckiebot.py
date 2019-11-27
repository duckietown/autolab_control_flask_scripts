import subprocess
import multiprocessing
from typing import List
import time
from docker import DockerClient
from docker.errors import NotFound

from .aido_utils import get_device_list, show_status

def start_device(device):
    docker = DockerClient(f'{device}.local:2375')

    try:
        if "bot" in device:
            print(device+ ": Stopping the car-interface")
            docker.containers.get('car-interface').stop()
            # cmd = "docker -H %s.local stop car-interface" % device
            # subprocess.check_call(cmd, shell=True, stderr=subprocess.STDOUT)
        else:
            print(device+ ": Stopping the light-sensor")
            try:
                docker.containers.get('dt-light-sensor').stop()
            except NotFound:
                pass
            # cmd = "docker -H %s.local stop dt-light-sensor" % device
            # subprocess.check_call(cmd, shell=True, stderr=subprocess.STDOUT)
        # time.sleep(5)

        print(device+ ": Stopping the acquisition-bridge")
        docker.containers.get('acquisition-bridge').stop()
        # cmd = "docker -H %s.local stop acquisition-bridge" % device
        # subprocess.check_call(cmd, shell=True, stderr=subprocess.STDOUT)
        # time.sleep(5)

        print(device+ ": Restarting the duckiebot-interface")
        docker.containers.get('duckiebot-interface').restart()
        # cmd = "docker -H %s.local restart duckiebot-interface" % device
        # subprocess.check_call(cmd, shell=True, stderr=subprocess.STDOUT)
        # time.sleep(5)

        if "bot" in device:
            print(device+ ": Restarting the car-interface")
            docker.containers.get('car-interface').start()
            # cmd = "docker -H %s.local start car-interface" % device
            # subprocess.check_call(cmd, shell=True, stderr=subprocess.STDOUT)
        else:
            print(device+ ": Restarting the light-sensor")
            try:
                docker.containers.get('dt-light-sensor').start()
            except NotFound:
                pass
            # cmd = "docker -H %s.local start dt-light-sensor" % device
            # subprocess.check_call(cmd, shell=True, stderr=subprocess.STDOUT)
        # time.sleep(5)

        print(device+ ": Restarting the acquisition-bridge")
        docker.containers.get('acquisition-bridge').start()
        # cmd = "docker -H %s.local start acquisition-bridge" % device
        # subprocess.check_call(cmd, shell=True, stderr=subprocess.STDOUT)

        time.sleep(10)

        return "Duckiebot reset"

    except subprocess.CalledProcessError as e:
        print(e)
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

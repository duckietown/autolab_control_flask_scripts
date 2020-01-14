import subprocess
import multiprocessing
from typing import List
import time
from docker import DockerClient
from docker.errors import NotFound

from .aido_utils import get_device_list, show_status

def start_device(device):
    # TODO: right now this process takes forever, we should implement everything using `dt_exec` which speeds up the stop (does not escalate to kill)
    docker = DockerClient(f'{device}.local:2375')

    try:
        if "bot" in device:
            print(device+ ": Stopping the car-interface")
            if docker.containers.get('car-interface').status == 'running':
                docker.containers.get('car-interface').kill()
        else:
            print(device+ ": Stopping the light-sensor")
            try:
                docker.containers.get('dt-light-sensor').kill()
            except NotFound:
                pass

        print(device+ ": Stopping the acquisition-bridge")
        if docker.containers.get('acquisition-bridge').status == 'running':
            docker.containers.get('acquisition-bridge').kill()

        print(device+ ": Stopping the duckiebot-interface")
        if docker.containers.get('duckiebot-interface').status == 'running':
            docker.containers.get('duckiebot-interface').kill()

        print(device+ ": Starting the duckiebot-interface")
        docker.containers.get('duckiebot-interface').start()

        if "bot" in device:
            print(device+ ": Starting the car-interface")
            docker.containers.get('car-interface').start()
        else:
            print(device+ ": Starting the light-sensor")
            try:
                docker.containers.get('dt-light-sensor').start()
            except NotFound:
                pass

        print(device+ ": Starting the acquisition-bridge")
        docker.containers.get('acquisition-bridge').start()

        return "Duckiebot reset"

    except subprocess.CalledProcessError as e:
        print(e)
        return "Error"


def start_all_devices(device_list):
    pool = multiprocessing.Pool(processes=20)
    results = pool.map(start_device, device_list)
    pool.close()
    pool.join()

    # TODO: what is this for? Maybe wait for duckiebot-interface to be ready to get the E-Stop signal?
    time.sleep(10)
    # TODO: what is this for?

    show_status(device_list, results)
    return results

def reset_duckiebot_with_list(device_list):

    # TODO: remove
    # return device_list, ["Duckiebot reset"] * len(device_list)
    # TODO: remove


    outcome = start_all_devices(device_list)
    return device_list, outcome

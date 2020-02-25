import time
import multiprocessing
from docker import DockerClient

from .docker_utils import kill_if_running, blocking_start
from .aido_utils import show_status


def start_device(device):
    # TODO: right now this process takes forever, we should implement everything using `dt_exec` which speeds up the stop (does not escalate to kill)
    docker = DockerClient(f'{device}.local:2375')

    # Stopping all containers
    if "bot" in device:
        # print(device + ": Killing the car-interface")
        kill_if_running(docker, "car-interface")

        kill_if_running(docker, "files-api")

    # else:
        # print(device + ": Killing the light-sensor")
        # kill_if_running(docker, "dt-light-sensor")

    # print(device + ": Stopping the acquisition-bridge")
    kill_if_running(docker, "acquisition-bridge")

    # print(device + ": Stopping the duckiebot-interface")
    kill_if_running(docker, "duckiebot-interface")

    # Restarting all containers
    # print(device + ": Starting the duckiebot-interface")
    if blocking_start(client=docker, container_name="duckiebot-interface"):
        # Waiting for the roscore to be on
        time.sleep(5)

        if "bot" in device:
            # print(device + ": Starting the car-interface")
            if not blocking_start(client=docker, container_name="car-interface"):
                print("Could not start car-interface")
                return "Error"
            if not blocking_start(client=docker, container_name="files-api"):
                print("Could not start files-api")
                return "Error"
        # else:
        #     # print(device + ": Starting the light-sensor")
        #     if not blocking_start(client=docker, container_name="dt-light-sensor"):
        #         print("Could not start dt-light-sensor")
        #         return "Error"

        # print(device + ": Starting the acquisition-bridge")
        if blocking_start(client=docker, container_name="acquisition-bridge"):
            return "Duckiebot reset"
        else:
            print("Could not start acquisition-bridge")
            return "Error"

    else:
        print("Could not start duckiebot-interface")
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

import subprocess
import multiprocessing
from typing import List
from docker import DockerClient
from docker.errors import NotFound, APIError
from .aido_utils import get_device_list, show_status

demo_name = ""


def stop_device(device):
    global demo_name
    docker = DockerClient(f'{device}.local:2375')

    try:
        demo_container = docker.containers().get("demo_%s" % demo_name)
        cmd = '/bin/bash environment.sh rostopic pub -1 /%s/joy_mapper_node/joystick_override duckietown_msgs/BoolStamped\
                         "{header: {seq: 0, stamp: {secs: 0, nsecs: 0}, frame_id: \'\'}, data: true}"' % device
        demo_container.exec_run(cmd)
        demo_container.exec_run(cmd)

        demo_container.stop(timeout=2)

        return "Success"

    except docker.errors.APIError as e:
        return "Error : %s" % str(e)


def stop_all_devices(device_list):
    pool = multiprocessing.Pool(processes=20)
    results = pool.map(stop_device, device_list)
    pool.close()
    pool.join()
    show_status(device_list, results)
    return results


def stop_passive_bots_with_list(device_list, passive_demo):
    global demo_name
    demo_name = passive_demo
    return device_list, stop_all_devices(device_list)

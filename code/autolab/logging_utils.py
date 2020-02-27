import subprocess
import time
from docker import from_env
import os
from docker import from_env
from docker.errors import NotFound


BAG_RECORDER = 'bag_recorder'


def start_logging(filename, device_list, mount_folder):
    docker = from_env()

    # try to remove another finish bag_recorder container
    try:
        docker.containers.get(BAG_RECORDER).remove(force=True)
    except:
        pass

    # Create the log folder
    os.makedirs(mount_folder, exist_ok=True)

    # attach workspace
    volumes = {
        mount_folder: {
            'bind': '/data',
            'mode': 'rw'
        }
    }

    # The logging command for the container
    cmd = "/bin/bash -c 'rosbag record -O /data/%s __name:=bag_recorder_node" % filename
    for device in device_list:
        cmd += " /"+device+"/imageSparse/compressed /"+device+"/camera_node/camera_info"
        if "bot" in device:
            cmd += " /"+device+"/wheels_driver_node/wheels_cmd_decalibrated"
    cmd += "'"

    # Launching the container
    try:
        docker.containers.run(
            command=cmd,
            image="duckietown/dt-ros-commons:daffy-amd64",
            detach=True,
            volumes=volumes,
            name=BAG_RECORDER,
            network_mode="host")
        return "Success"
    except Exception as e:
        print(e)
        return "Error: %s" % e


def stop_logging():
    # TODO: implement this in `dt-ros-commons` with `dt_exec` and graceful stop using `docker stop`

    docker = from_env()

    # try to stop a bag_recorder container
    try:
        container = docker.containers.get(BAG_RECORDER)
    except NotFound:
        print("Could not stop the logging")
        return "Error"
    # stop recorder and container (if running)
    if container.status == 'running':
        print("Stopping bag recorder")
        cmd = "/bin/bash -c 'source /code/catkin_ws/devel/setup.bash; rosnode kill bag_recorder_node'"
        container.exec_run(cmd)
        while container.status != "exited":
            time.sleep(0.1)
            container.reload()

    return "Success"

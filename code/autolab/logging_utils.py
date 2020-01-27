import subprocess
import time
from docker import from_env
import os


def start_logging(filename, device_list, mount_folder):
    docker = from_env()
    name = "bag_recorder"

    # try to remove another finish bag_recorder container
    try:
        docker.containers.get(name).remove(force=True)
    except:
        pass

    # Create the log folder
    os.mkdir(mount_folder)

    # attach workspace
    volumes = {
        "data": {
            'bind': mount_folder,
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
        container = docker.containers.run(
            command=cmd
            image="duckietown/dt-ros-commons:master19-amd64",
            detach=True,
            volumes=volumes,
            name=name,
            network_mode="host")
        return("Success")
    except Exception as e:
        return ("Error: %s" % e)


def stop_logging():
    # TODO: implement this in `dt-ros-commons` with `dt_exec` and graceful stop using `docker stop`
    cmd = "/bin/bash -c 'rosnode kill bag_recorder_node'"

    docker = from_env()
    name = "bag_recorder"

    # try to remove another finish bag_recorder container
    try:
        container = docker.containers.get(name)
        container.exec_run(cmd)
        container.remove(force=True)
    except:
        print("Could not stop the logging")
        return "Error"

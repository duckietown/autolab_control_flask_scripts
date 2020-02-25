import subprocess
import time
from docker import from_env
import os
from .docker_utils import kill_if_running, blocking_start


def start_logging(filename, device_list, mount_folder):
    docker = from_env()
    name = "bag_recorder"

    # try to remove another finish bag_recorder container
    try:
        docker.containers.get(name).remove(force=True)
    except:
        pass

    # Create the log folder
    print(mount_folder)
    os.makedirs(mount_folder, exist_ok=True)

    # attach workspace
    volumes = {
        mount_folder: {
            'bind': "/data",
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
    # cmd = "/bin/bash -c 'while true; do echo hey; done'"
    # Launching the container
    try:
        container = docker.containers.run(
            command=cmd,
            image="duckietown/dt-ros-commons:daffy-amd64",
            detach=True,
            volumes=volumes,
            name=name,
            network_mode="host")
        return("Success")
    except Exception as e:
        print(e)
        return ("Error : %s" % str(e))


def stop_logging():
    # TODO: implement this in `dt-ros-commons` with `dt_exec` and graceful stop using `docker stop`
    cmd = "/bin/bash -c 'source /code/catkin_ws/devel/setup.bash; rosnode kill bag_recorder_node'"

    docker = from_env()
    name = "bag_recorder"

    # try to remove another finish bag_recorder container
    try:
        container = docker.containers.get(name)
        (exit_code, output) = container.exec_run(cmd, detach=False)
        # print(output)
        kill_if_running(docker, name)
        return "Success"
    except Exception as e:
        print("Could not stop the logging : %s" % e)
        return "Error"


# if __name__ == "__main__":
#     start_logging("test", ["autobot02"], "/home/amaury")
#     time.sleep(5)
#     stop_logging()

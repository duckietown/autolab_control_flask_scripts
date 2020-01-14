import subprocess
import time


# def start_logging(computer, filename, device_list, mount_folder):
def start_logging(filename, device_list, mount_folder):
    # TODO: implement this using docker API
    cmd = "docker rm -f bag_recorder || echo not bag_recorder before;  mkdir -p %s; docker run --name bag_recorder --rm -v %s:/data --net=host -dit duckietown/dt-ros-commons:master19-amd64 /bin/bash -c 'rosbag record -O /data/%s __name:=bag_recorder_node" % (
         mount_folder, mount_folder, filename)
    for device in device_list:
        cmd += " /"+device+"/imageSparse/compressed /"+device+"/camera_node/camera_info"
        if "bot" in device:
            cmd += " /"+device+"/wheels_driver_node/wheels_cmd_decalibrated"
    cmd += "'"
    try:
        subprocess.check_output(cmd, shell=True)
        return "Success"
    except subprocess.CalledProcessError:
        return "Error"


# def stop_logging(computer):
def stop_logging():
    # TODO: implement this in `dt-ros-commons` with `dt_exec` and graceful stop using `docker stop`
    cmd = "docker exec bag_recorder /bin/bash -c 'source /opt/ros/kinetic/setup.bash; rosnode kill bag_recorder_node'"

    try:
        subprocess.check_output(cmd, shell=True)
        return "Success"
    except subprocess.CalledProcessError:
        return "Error"

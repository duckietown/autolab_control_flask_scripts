import subprocess,time

def start_logging(computer, filename, device_list, mount_folder):
    cmd = "docker -H %s rm -f bag_recorder || echo not bag_recorder before;  mkdir -p %s; docker -H %s run --name bag_recorder --rm -v %s:/data --net=host -dit duckietown/dt-ros-commons:master19-amd64 /bin/bash -c 'rosbag record -O /data/%s __name:=bag_recorder_node" %(computer, mount_folder, computer, mount_folder, filename)
    for device in device_list:
        cmd += " /"+device+"/imageSparse/compressed /"+device+"/camera_node/camera_info"
    cmd+="'"
    try:
        subprocess.check_output(cmd, shell=True)
        return "Success"
    except subprocess.CalledProcessError:
        return "Error"

def stop_logging(computer):
    cmd = "docker -H %s exec bag_recorder /bin/bash -c 'source /opt/ros/kinetic/setup.bash; rosnode kill bag_recorder_node'" % (computer)

    try:
        subprocess.check_output(cmd, shell=True)
        return "Success"
    except subprocess.CalledProcessError:
        return "Error"
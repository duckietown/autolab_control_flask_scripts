import subprocess
# import rosbag
import docker
import time
from docker import DockerClient


name = "localization-graphoptimizer"


def run_localization(ros_master_ip, input_bag_path, output_dir, mount_computer_side, mount_container_side="/data"):
    docker = DockerClient()
    # try to remove another existing graph optimizer processor container
    try:
        docker.containers.get(name).remove(force=True)
    except:
        pass
    # define environment
    env = {
        "ROS_MASTER_IP": ros_master_ip,
        "ROS_MASTER": ros_master_ip,
        "ATMSGS_BAG": f"{mount_container_side}/logs_processed/{input_bag_path}.bag",
        "OUTPUT_DIR": output_dir
    }
    # mount workspace
    volumes = {
        mount_computer_side: {
            'bind': mount_container_side,
            'mode': 'rw'
        }
    }
    # run graph optimizer
    docker.containers.run(
        name=name,
        image="duckietown/cslam-graphoptimizer:daffy-amd64",
        volumes=volumes,
        environment=env,
        detach=True,
        network_mode="host"
    )
    return ("Success")


def check_localization(active_bots, passive_bots, mount_computer_side):
    destination_path = f"{mount_computer_side}/trajectories"
    client = docker.from_env()
    # TODO: change this to client.containers.get(<XYZ>).status
    container_list = client.containers.list()
    for container in container_list:
        if container.name == name:
            status = container.status
            if status == "running" or status == "created":
                return("Running")
            else:
                continue
    try:
        cmd = "mkdir -p %s" % destination_path
        subprocess.check_output(cmd, shell=True)

        for i in range(len(passive_bots)):
            cmd = "mv %s/%s.yaml %s/passive%s.yaml" % (
                mount_computer_side, passive_bots[i], destination_path, i+1)
            subprocess.check_output(cmd, shell=True)
        for i in range(len(active_bots)):
            cmd = "mv %s/%s.yaml %s/active%s.yaml" % (
                mount_computer_side, active_bots[i], destination_path, i+1)
            subprocess.check_output(cmd, shell=True)
        return("Success")
    except subprocess.CalledProcessError as e:
        return ("Error: %s" % e)

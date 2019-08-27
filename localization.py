import subprocess
import rosbag
import docker

name = "localization-graphoptimizer"


def run_localization(input_bag_path, output_dir, mount_computer_side, mount_container_side="/data"):
    cmd = "docker-compose -f processor_compose.yaml run --rm -v %s:%s -e  ATMSGS_BAG=%s/%s.bag -e OUTPUT_DIR=%s --name %s localization" % (
        mount_computer_side, mount_container_side, mount_container_side, input_bag_path, output_dir, name)
    print(cmd)
    try:
        res = subprocess.Popen(cmd, shell=True)
        print(res)
        return ("Success")
    except subprocess.CalledProcessError as e:
        return ("Error: %s" % e)
    pass


def check_localization():
    client = docker.from_env()
    container_list = client.containers.list()
    for container in container_list:
        if container.name == name:
            status = container.status
            if status == "running" or status == "created":
                return("Running")
            if status == "exited":
                return("Success")
    return("Success")

import subprocess
import rosbag
import docker
import time

name = "localization-graphoptimizer"


def run_localization(input_bag_path, output_dir, mount_computer_side, mount_container_side="/data"):
    cmd = "docker-compose -f processor_compose.yaml run --rm -v %s:%s -e  ATMSGS_BAG=%s/%s.bag -e OUTPUT_DIR=%s --name %s localization" % (
        mount_computer_side, mount_container_side, mount_container_side, input_bag_path, output_dir, name)
    print(cmd)
    try:
        res = subprocess.Popen(cmd, shell=True)
        print(res)
        time.sleep(5)
        return ("Success")
    except subprocess.CalledProcessError as e:
        return ("Error: %s" % e)
    pass


def check_localization(active_bot, passive_bots, origin_path, destination_path):
    client = docker.from_env()
    container_list = client.containers.list()
    for container in container_list:
        if container.name == name:
            status = container.status
            if status == "running" or status == "created":
                return("Running")
            if status == "exited":
                try:
                    cmd = "mkdir -p %s" % destination_path
                    subprocess.check_output(cmd, shell=True)

                    for i in range(len(passive_bots)):
                        cmd = "mv %s/%s.yaml %s/passive%s.yaml" % (origin_path,passive_bots[i],destination_path,i+1)
                        subprocess.check_output(cmd, shell=True)
                    cmd = "mv %s/%s.yaml %s/active.yaml" % (origin_path,active_bot,destination_path)   
                    subprocess.check_output(cmd, shell=True)
                    return("Success")
                except subprocess.CalledProcessError as e:
                    return ("Error: %s" % e)
    return("Success")

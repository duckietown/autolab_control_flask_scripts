import os
import subprocess
import time
from docker import from_env
from .docker_utils import remove_if_running

# def merge_bags(bags_name, output_bag_path):
#     output_bag = rosbag.Bag(output_bag_path, 'w')
#     for bag_name in bags_name:
#         print("trying to do %s" % bag_name)
#         bag = rosbag.Bag(bag_name)
#         for topic, message, timestamp in bag.read_messages():
#             # print(topic)
#             output_bag.write(topic, message, timestamp)
#         output_bag.flush()
#         bag.close()
#     output_bag.close()
#     print("finished with merging the bags")
#     return ("Success")

name = "postprocessor"


def split_bags(input_bag_name, device_list, mount_folder):

    docker = from_env()
    name = "bag_splitter"

    # try to remove another finish bag_recorder container
    try:
        docker.containers.get(name).remove(force=True)
    except:
        pass

    # Create the log folder
    mount_folder += "/logs_raw"
    print(mount_folder)
    os.makedirs(mount_folder, exist_ok=True)

    # attach workspace
    volumes = {
        mount_folder: {
            'bind': "/data",
            'mode': 'rw'
        }
    }

    # The splitting command for the container
    container_side_input = "/data/%s.bag" % input_bag_name
    bigcmd = ["/bin/bash", "-c"]
    bagcomd = ""

    reindexCmd = "if [ -s %s.active ]; then rosbag reindex %s.active; mv %s.active %s; rm %s.orig.active; fi;" % (
        container_side_input, container_side_input, container_side_input, container_side_input, container_side_input)
    bagcomd += reindexCmd
    for device in device_list:
        new_bag_name = "/data/%s.bag" % device
        cmd = "rosbag filter %s %s \" '%s' in topic \";" % (
            container_side_input, new_bag_name, device)
        bagcomd += cmd
    bigcmd.append(bagcomd)

    # bigcmd += "\""
    # Launching the container
    try:
        container = docker.containers.run(
            command=bigcmd,
            image="duckietown/dt-ros-commons:daffy-amd64",
            detach=False,
            volumes=volumes,
            name=name,
            network_mode="host")
    except Exception as e:
        print(e)
        return (False)

    return True


def start_bag_processing(ros_master_ip, input_bag_name, output_bag_name, mount_computer_side, device_list, mount_container_side="/data"):
    cmd = f"mkdir -p {mount_computer_side}/logs_processed"
    subprocess.check_output(cmd, shell=True)

    if not split_bags(input_bag_name, device_list, mount_computer_side):
        print("Could not split the bags!!")

    for agent in device_list:
        input_bag_name = "%s" % agent
        container = start_bag_processing_one_agent(ros_master_ip, input_bag_name, output_bag_name,
                                                   mount_computer_side, mount_container_side="/data")
        if isinstance(container, str):
            return container
        else:
            while container.status != "exited":
                time.sleep(0.1)
                container.reload()
    return "Success"


def start_bag_processing_one_agent(ros_master_ip, input_bag_name, output_bag_name, mount_computer_side, mount_container_side="/data"):
    # create output dir
    # open docker client
    docker = from_env()
    # define path to input (inside the container)
    container_side_input = os.path.join(
        mount_container_side, 'logs_raw', input_bag_name)
    # split bag

    # define path to output (inside the container)
    container_side_output = os.path.join(
        mount_container_side, 'logs_processed', output_bag_name)
    # define environment
    env = {
        "INPUT_BAG_PATH": container_side_input,
        "OUTPUT_BAG_PATH": f"{container_side_output}.bag",
        "ROS_MASTER_URI": f"http://{ros_master_ip}:11311"
    }
    # attach workspace
    volumes = {
        mount_computer_side: {
            'bind': mount_container_side,
            'mode': 'rw'
        }
    }
    # try to remove another existing postprocessor container
    try:
        docker.containers.get(name).remove(force=True)
    except:
        pass
    # spin a new post-processor
    try:
        container = docker.containers.run(
            image="duckietown/post-processor:daffy-amd64",
            detach=True,
            environment=env,
            volumes=volumes,
            name=name,
        )
        return container
    except Exception as e:
        return ("Error: %s" % e)


def check_bag_processing(output_bag_name, mount_computer_origin, mount_computer_destination):
    docker = from_env()
    container_list = docker.containers.list()
    # TODO: change this into docker.containers.get(<XYZ>).status == ??
    for container in container_list:
        if container.name == name:
            status = container.status
            if status == "running" or status == "created":
                return("Running")
            if status == "exited":
                print(
                    f"move_file({output_bag_name}, {mount_computer_origin}, {mount_computer_destination})")
                # try to cleanup
                try:
                    docker.containers.get(name).remove(force=True)
                except:
                    pass
                # stop waiting
                break
    return "Success"

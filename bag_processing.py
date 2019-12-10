import subprocess
import rosbag
import time
import docker
import os

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


def split_bags(input_bag_name, mount_computer_side, device_list):

    container_side_input = "/%s/%s.bag" % (mount_computer_side, input_bag_name)
    for device in device_list:
        new_bag_name = "/%s/%s.bag" % (mount_computer_side, device)
        cmd = "rosbag filter %s %s \" '%s' in topic \" " % (
            container_side_input, new_bag_name, device)
        try:
            out = subprocess.check_output(
                cmd, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print("Error splitting for %s : %s" % (device, e))
            return False
    return True


def cut_bag_beginning(input_bag_name, mount_computer_side, start_time):
    container_side_input = "/%s/%s.bag" % (mount_computer_side, input_bag_name)
    new_bag_name = "/%s/%s_cut.bag" % (mount_computer_side, input_bag_name)
    cmd = "rosbag filter %s %s \" t.secs >= %f \" " % (
        container_side_input, new_bag_name, start_time/1000.0 - 1.0)
    try:
        out = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print("Error cutting bag : %s" % e)
        return False
    
    if(os.path.getsize(new_bag_name) > 10000):
        os.remove(container_side_input)
        os.rename(new_bag_name, container_side_input)
    else:
        print("cut bag was too small")
    return True


def start_bag_processing(input_bag_name, output_bag_name, mount_computer_side, device_list, start_time, mount_container_side="/data"):
    client = docker.from_env()
    bags_name = []
    container_side_input = "/%s/%s" % (mount_container_side, input_bag_name)

    if not cut_bag_beginning(input_bag_name, mount_computer_side, start_time):
        print("Could not cut bag beginning")

    if not split_bags(input_bag_name, mount_computer_side, device_list):
        print("Could not split the bags!!")
    processed_bag_name = "%s.bag" % (output_bag_name)
    output_container = "/%s/%s" % (
        mount_container_side, processed_bag_name)
    output_computer = "%s/%s" % (mount_computer_side, processed_bag_name)
    bags_name.append(output_computer)

    env = []
    env.append("INPUT_BAG_PATH=%s" % container_side_input)
    env.append("OUTPUT_BAG_PATH=%s" % output_container)
    env.append("ROS_MASTER_URI=http://172.31.168.112:11311")
    volume = {mount_computer_side: {
        'bind': mount_container_side, 'mode': 'rw'}}
    try:
        client.containers.prune()
        container = client.containers.run(
            image="duckietown/post-processor:daffy-amd64", detach=True, environment=env, volumes=volume, name=name)
        print("Success: ")
        # print(container)
        # print(container.status)
        # logs = None
        # try:
        #     while container.status == "running" or container.status == "created":
        #         logs = container.logs()
        #         time.sleep(0.1)
        # except:
        #     pass
        # print logs
        return("Success")

    except subprocess.CalledProcessError as e:
        return ("Error: %s" % e)

    print("finished with all apriltags")

    # for autobot in autobots:
    #     print("processing %s" % autobot)
    #     processed_bag_name = "processed_%s.bag" % autobot
    #     output_container = "%s/%s" % (
    #         mount_container_side, processed_bag_name)
    #     output_computer = "%s/%s" % (mount_computer_side, processed_bag_name)
    #     bags_name.append(output_computer)
    #     container_side_input = "%s/%s" % (mount_container_side, input_bag_name)

    #     # cmd = "docker rm -f wheelodometryprocessor%s; docker-compose -f processor_compose.yaml run -v %s:%s -e ACQ_DEVICE_NAME=%s -e INPUT_BAG_PATH=%s -e OUTPUT_BAG_PATH=%s --rm --name wheelodometryprocessor%s odometry-processor" % (
    #     #     autobot, mount_computer_side, mount_container_side, autobot, container_side_input, output_container, autobot)
    #     # cmd = "docker rm -f apriltagprocessor%s || echo 'blabla'; docker run hello-world " % autobot

    #     env = []
    #     env.append("ACQ_DEVICE_NAME=%s" % autobot)
    #     env.append("INPUT_BAG_PATH=%s" % container_side_input)
    #     env.append("OUTPUT_BAG_PATH=%s" % output_container)
    #     env.append("ROS_MASTER_URI=http://172.31.168.2:11311")
    #     volume = {mount_computer_side: {
    #         'bind': mount_container_side, 'mode': 'rw'}}
    #     name = "odometryprocessor%s" % autobot
    #     try:
    #         client.containers.prune()
    #         container = client.containers.run(
    #             image="duckietown/wheel-odometry-processor:master19-amd64", auto_remove=True, detach=True, environment=env, volumes=volume, name=name)
    #         print("Success: ")
    #         print(container.status)
    #         while container.status == "running" or container.status == "created":
    #             try:
    #                 container.reload()
    #                 time.sleep(1)
    #             except:
    #                 break
    #     except subprocess.CalledProcessError as e:
    #         print("Error: %s" % e)
    #         return ("Error: %s" % e)


def check_bag_processing(output_bag_name, mount_computer_origin, mount_computer_destination):
    client = docker.from_env()
    container_list = client.containers.list()
    for container in container_list:
        if container.name == name:
            status = container.status
            if status == "running" or status == "created":
                return("Running")
            if status == "exited":
                return(move_file(output_bag_name, mount_computer_origin, mount_computer_destination))
    return(move_file(output_bag_name, mount_computer_origin, mount_computer_destination))


def move_file(name, origin, destination):
    try:
        cmd = "mkdir -p %s; mv %s/%s.bag %s" % (
            destination, origin, name, destination)
        subprocess.check_output(cmd, shell=True, executable="/bin/bash")
        return "Success"

    except subprocess.CalledProcessError:
        return "Error"

import subprocess
import rosbag
import time
import docker


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


def start_bag_processing(input_bag_name, output_bag_name, mount_computer_side, mount_container_side="/data"):
    client = docker.from_env()
    bags_name = []
    container_side_input = "%s/%s" % (mount_container_side, input_bag_name)

    processed_bag_name = "%s.bag" % (output_bag_name)
    output_container = "%s/%s" % (
        mount_container_side, processed_bag_name)
    output_computer = "%s/%s" % (mount_computer_side, processed_bag_name)
    bags_name.append(output_computer)

    env = []
    env.append("INPUT_BAG_PATH=%s" % container_side_input)
    env.append("OUTPUT_BAG_PATH=%s" % output_container)
    env.append("ROS_MASTER_URI=http://172.31.168.115:11311")
    volume = {mount_computer_side: {
        'bind': mount_container_side, 'mode': 'rw'}}
    try:
        client.containers.prune()
        container = client.containers.run(
            image="duckietown/post-processor:master19-amd64", detach=True, environment=env, volumes=volume, name=name)
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
    #     env.append("ROS_MASTER_URI=http://172.31.168.115:11311")
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
        cmd = "mkdir -p %s; mv %s/%s.bag %s" % (destination, origin, name, destination)
        subprocess.check_output(cmd, shell=True, executable="/bin/bash")
        return "Success"

    except subprocess.CalledProcessError:
        return "Error"

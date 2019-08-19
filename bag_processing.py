import subprocess
import rosbag


def start_bag_processing(input_bag_name, output_bag_name, mount_computer_side, mount_container_side="/data"):
    bag = rosbag.Bag(mount_computer_side +"/"+ input_bag_name + ".bag")
    watchtowers = []
    autobots = []
    for topic, _, _ in bag.read_messages():
        topic_parts = topic.split("/")
        for part in topic_parts:
            if "watchtower" in part:
                if part not in watchtowers:
                    watchtowers.append(part)
            if "autobot" in part or "duckiebot" in part:
                if part not in autobots:
                    autobots.append(part)

    bags_name = []
    container_side_input = "%s/%s" % (mount_container_side, input_bag_name)
    print(watchtowers)
    print(autobots)
    for watchtower_id in watchtowers:
        processed_bag_name = "processed_%s.bag" % watchtower_id
        output_container = "%s/%s" % (
            mount_container_side, processed_bag_name)
        output_computer = "%s/%s" % (mount_computer_side, processed_bag_name)
        bags_name.append(output_computer)
        cmd = "docker-compose -f processor_compose.yaml run -v %s:%s -e ACQ_DEVICE_NAME=%s -e INPUT_BAG_PATH=%s -e OUTPUT_BAG_PATH=%s --name apriltagprocessor%s apriltag-processor" % (
            mount_computer_side, mount_container_side, watchtower_id, container_side_input, output_container, watchtower_id)
        try:
            res = subprocess.check_output(cmd, shell=True)
            return ("Success: %s" % res)
        except subprocess.CalledProcessError as e:
            return ("Error: %s" % e)

    for autobot in autobots:
        processed_bag_name = "processed_%s.bag" % autobot
        output_container = "%s/%s" % (
            mount_container_side, processed_bag_name)
        output_computer = "%s/%s" % (mount_computer_side, processed_bag_name)
        bags_name.append(output_computer)
        cmd = "docker-compose -f processor_compose.yaml run -v %s:%s -e ACQ_DEVICE_NAME=%s -e INPUT_BAG_PATH=%s -e OUTPUT_BAG_PATH=%s --name wheelodometryprocessor%s odometry-processor" % (
            mount_computer_side, mount_container_side, autobot, container_side_input, output_container, autobot)
        try:
            res = subprocess.check_output(cmd, shell=True)
            return ("Success: %s" % res)
        except subprocess.CalledProcessError as e:
            return ("Error: %s" % e)

    merge_bags(bags_name, mount_computer_side +"/"+ output_bag_name + ".bag")

    def merge_bags(bags_name, output_bag_path):
        output_bag = rosbag.Bag(output_bag_path, 'w')
        for bag_name in bags_name:
            bag = rosbag.Bag(bag_name)
            for topic, message, timestamp in bag.read_messages():
                output_bag.write(topic, message, timestamp)
            bag.close()
        output_bag.close()

import subprocess
import rosbag


def start_apriltag_processing(input_bag_path, output_bag_path, mount_computer_side, mount_container_side="/data"):
    bag = rosbag.Bag(input_bag_path)
    watchtowers = []
    for topic, _, _ in bag.read_messages():
        topic_parts = topic.split("/")
        for part in topic_parts:
            if "watchtower" in part:
                if part not in watchtowers:
                    watchtowers.append(part)

    bags_name = []
    for watchtower_id in watchtowers:
        processed_bag_name = "processed_%s.bag" % watchtower_id
        output_container = "%s/%s" % (
            mount_container_side, processed_bag_name)
        output_computer = "%s/%s" % (mount_computer_side, processed_bag_name)
        bags_name.append(output_computer)
        cmd = "docker-compose -f apriltag_processor_compose.yaml run -v %s:%s -e ACQ_DEVICE_NAME=%s -e INPUT_BAG_PATH=%s -e OUTPUT_BAG_PATH=%s --name apriltagprocessor%s apriltag-processor" % (
            mount_computer_side, mount_container_side, watchtower_id, input_bag_path, output_container, watchtower_id)
        try:
            res = subprocess.check_output(cmd, shell=True)
            return ("Success: %s" % res)
        except subprocess.CalledProcessError as e:
            return ("Error: %s" % e)

    merge_bags(bags_name, output_bag_path)

    def merge_bags(bags_name, output_bag_path):
        output_bag = rosbag.Bag(output_bag_path, 'w')
        for bag_name in bags_name:
            bag = rosbag.Bag(bag_name)
            for topic, message, timestamp in bag.read_messages():
                output_bag.write(topic, message, timestamp)
            bag.close()
        output_bag.close()

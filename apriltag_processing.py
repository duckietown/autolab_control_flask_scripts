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
    for watchtower_id in watchtowers:
        cmd = "docker-compose -f apriltag_processor_compose.yaml run -d -v %s:%s -e ACQ_DEVICE_NAME=%s -e INPUT_BAG_PATH=%s -e OUTPUT_BAG_PATH=%s --name apriltagprocessor%s apriltag-processor" % (
            mount_computer_side, mount_container_side, watchtower_id, input_bag_path, output_bag_path, watchtower_id)
        try:
            res = subprocess.check_output(cmd, shell=True)
            return ("Success: %s" % res)
        except subprocess.CalledProcessError as e:
            return ("Error: %s" % e)

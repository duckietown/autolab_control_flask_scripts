import subprocess
import rosbag


def run_localization(input_bag_path, output_dir, mount_computer_side, mount_container_side="/data"):

    cmd = "docker-compose -f processor_compose.yaml run -v %s:%s -e  -e ATMSGS_BAG=%s -e OUTPUT_DIR=%s --name localization-graphoptimizer localization" % (
        mount_computer_side, mount_container_side, input_bag_path, output_dir)
       try:
            res = subprocess.check_output(cmd, shell=True)
            return ("Success: %s" % res)
        except subprocess.CalledProcessError as e:
            return ("Error: %s" % e)
    pass

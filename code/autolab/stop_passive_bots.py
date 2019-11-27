import subprocess
import multiprocessing
from typing import List

from .aido_utils import get_device_list, show_status

demo_name = ""


def stop_device(device):
    global demo_name
    try:
        cmd = 'docker -H %s.local exec -it demo_%s\
                         /bin/bash environment.sh rostopic pub -1 /%s/joy_mapper_node/joystick_override duckietown_msgs/BoolStamped\
                         "{header: {seq: 0, stamp: {secs: 0, nsecs: 0}, frame_id: \'\'}, data: true}"' % (device, demo_name, device)
        subprocess.Popen(cmd, shell=True, executable="/bin/bash")
        print(device + ": Engaged joystick override")

        print(device + ": Stopping the demo: "+demo_name)
        cmd = "docker -H %s.local stop demo_%s" % (device, demo_name)
        subprocess.Popen(cmd, shell=True, executable="/bin/bash")
        return "Success"

    except subprocess.CalledProcessError:
        return "Error"


def stop_all_devices(device_list):
    pool = multiprocessing.Pool(processes=20)
    results = pool.map(stop_device, device_list)
    pool.close()
    pool.join()
    show_status(device_list, results)
    return results


def stop_passive_bots_with_list(device_list, passive_demo):
    global demo_name
    demo_name = passive_demo
    return device_list, stop_all_devices(device_list)

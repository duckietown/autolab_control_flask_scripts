import subprocess
import multiprocessing
from typing import List
import time
from docker import DockerClient
from .aido_utils import get_device_list, show_status

demo_name = "indefinite_navigation"


def start_device(device):
    global demo_name

    try:
        print(device + ": Starting the demo: "+demo_name)
        cmd = "dts duckiebot demo --demo_name %s --duckiebot %s --package_name duckietown_demos --image duckietown/dt-core:daffy" % (
            demo_name, device)
        res = subprocess.Popen(cmd, shell=True, executable="/bin/bash")
        time.sleep(10)
        count = 0
        while True and count < 60:
            try:

                cmd = 'docker -H %s.local inspect -f \'{{.State.Running}}\' demo_%s' % (
                    device, demo_name)
                res = subprocess.check_output(cmd, shell=True)
                res = res.rstrip().decode("utf-8")
                if res == "true":
                    print(device + ": Try number "+str(count) +
                          " was successfull, the demo is running")
                    time.sleep(30)
                    cmd = "docker -H %s.local exec -it demo_%s\
                         /bin/bash -c \"source ../../devel/setup.bash; rostopic pub /%s/joy_mapper_node/joystick_override duckietown_msgs/BoolStamped\
                         \'{header: {seq: 0, stamp: {secs: 0, nsecs: 0}}, data: false}\'\"" % (device, demo_name, device)
                    print(cmd)
                    res = subprocess.Popen(
                        cmd, shell=True, executable="/bin/bash")
                    print(device + ": Released joystick override")
                    return "Started demo"
            except:
                print(device + "Try Number :"+str(count) +
                      ", the demo is not running yet")
                count += 1
                time.sleep(1)
        return "Couldn't start"

    except subprocess.CalledProcessError:
        return "Error"


def start_all_devices(device_list):
    pool = multiprocessing.Pool(processes=20)
    results = pool.map(start_device, device_list)
    pool.close()
    pool.join()
    show_status(device_list, results)
    return results


def start_passive_bots_with_list(device_list, passive_demo):
    global demo_name
    demo_name = passive_demo
    return device_list, start_all_devices(device_list)

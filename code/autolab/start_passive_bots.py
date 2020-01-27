import subprocess
import multiprocessing
from typing import List
import time
from docker import DockerClient
from .aido_utils import get_device_list, show_status
from utils.docker_utils import bind_duckiebot_data_dir, default_env, remove_if_running, pull_if_not_exist
from utils.networking_utils import get_duckiebot_ip

demo_name = "indefinite_navigation"


def start_device(device):
    global demo_name
    docker = DockerClient(f'{device}.local:2375')

    try:
        print(device + ": Starting the demo: "+demo_name)

        image_base = "duckietown/dt-core:daffy"
        package_name = "duckietown_demos"

        cmd = "roslaunch %s %s.launch veh:=%s" % (
            package_name,
            demo_name,
            device,
        )

        container_name = "demo_%s" % demo_name
        duckiebot_ip = get_duckiebot_ip(device)

        remove_if_running(docker, container_name)

        env_vars = default_env(device, duckiebot_ip)
        env_vars.update({
            "VEHICLE_NAME": device,
            "VEHICLE_IP": duckiebot_ip
        })

        demo_container = docker.containers.run(
            image=image_base,
            command=cmd,
            network_mode="host",
            volumes=bind_duckiebot_data_dir(),
            privileged=True,
            name=container_name,
            mem_limit="800m",
            memswap_limit="2800m",
            stdin_open=True,
            tty=True,
            detach=True,
            environment=env_vars,
        )

        count = 0
        while True and count < 5:
            try:
                # demo_container = docker.containers.get("demo_%s" % demo_name)
                while demo_container.status != "running":
                    time.sleep(1)
                    demo_container.reload()

                cmd = '/bin/bash environment.sh rostopic pub -1 /%s/joy_mapper_node/joystick_override duckietown_msgs/BoolStamped\

                    "{header: {seq: 0, stamp: {secs: 0, nsecs: 0}, frame_id: \'\'}, data: false}"' % device

                demo_container.exec_run(cmd)

                print(device + ": Released joystick override")
                return "Started demo"
            except NotFound:
                print("Container not found in start_passive_bot")
                count += 1
            except:
                count += 1

        return "Error"

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

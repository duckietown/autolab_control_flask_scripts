import os
import time
import subprocess
from docker import DockerClient
from docker.errors import NotFound

def get_map(image, name, step):
    docker = DockerClient()
    container_name = 'map_container'
    map_filepath = os.path.join(os.getcwd(), 'static', 'map.svg')
    
    try:
        cmd = f"mkdir -p {os.path.dirname(map_filepath)}"
        subprocess.check_call(cmd, shell=True, executable="/bin/bash")

        docker.images.pull(image)
        # cmd = f"docker pull {image}"
        # subprocess.check_call(cmd, shell=True, executable="/bin/bash")

        try:
            container = docker.containers.get(container_name)
            container.remove(force=True)
        except NotFound:
            pass
        # cmd = "docker rm -f map_container || exit 0"
        # subprocess.check_call(cmd, shell=True, executable="/bin/bash")

        container = docker.containers.run(image, name=container_name, detach=True)
        # cmd = f"docker run --name map_container -i --rm {image}"
        # subprocess.Popen(cmd, shell=True, executable="/bin/bash")

        time.sleep(2)

        container_path = f"/project/robotarium_scenario_maker/compiled/{name}/{step}/drawing.svg"
        bits, stat = container.get_archive(container_path)
        with open(map_filepath, 'wb') as fout:
            for chunk in bits:
                fout.write(chunk)
        # cmd = f"docker cp map_container:{container_path} {map_filepath}"
        # subprocess.check_call(cmd, shell=True, executable="/bin/bash")

        container.remove(force=True)
        # cmd = "docker rm -f map_container"
        # subprocess.check_call(cmd, shell=True, executable="/bin/bash")

        return '/' + os.path.relpath(map_filepath)

    except Exception as e:
        print(e)
        return "Error"


def copy_map(mount, map_location, path):

    try:
        cmd = "cd %s; git pull" %(map_location)
        subprocess.check_output(cmd, shell=True, executable="/bin/bash")

        cmd = "mkdir -p %s; cp %s/%s %s/map.yaml" %(mount, map_location, path, mount)
        subprocess.Popen(cmd, shell=True, executable="/bin/bash")

        return "Success"

    except subprocess.CalledProcessError:
        return "Error"

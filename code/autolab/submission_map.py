import os
import io
import time
import tarfile
import subprocess
from docker import DockerClient
from docker.errors import NotFound

def get_map(image, name, step):
    docker = DockerClient()
    container_name = 'map_container'
    map_filepath = os.path.join(os.getcwd(), 'autolab', 'static')
    container_path = f"/project/robotarium_scenario_maker/compiled/{name}/{step}/drawing.svg"

    try:
        # create directory for map
        cmd = f"mkdir -p {os.path.dirname(map_filepath)}"
        subprocess.check_call(cmd, shell=True, executable="/bin/bash")

        # pull image
        docker.images.pull(image)

        # (optional) try to remove a pre-existing container
        try:
            docker.containers.get(container_name).remove(force=True)
        except NotFound:
            pass

        # run the container (wait for it to be ready)
        container = docker.containers.run(image, name=container_name, detach=True, remove=True)
        time.sleep(2)

        # get tar of image
        bits, stat = container.get_archive(container_path)

        # write bytes to buffer
        b = io.BytesIO()
        for c in bits:
            b.write(c)
        b.seek(0)

        # read the buffer as tar
        t = tarfile.open(fileobj=b, mode='r')

        # extract map
        t.extract('drawing.svg', path=map_filepath)
        # ---
        return '/static/drawing.svg'

    except Exception as e:
        print('Error: ', str(e))
    finally:
        try:
            docker.containers.get(container_name).stop()
        except:
            pass
    # ---
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

import subprocess
import time

def get_map(container, name, step):

    try:
        print("Starting the map container: "+container)
        cmd = "docker run --name map_container -it --rm %s" % (container)
        subprocess.Popen(cmd, shell=True, executable="/bin/bash")

        time.sleep(1.5)

        cmd = "docker cp map_container:/project/robotarium_scenario_maker/compiled/%s/%s/drawing.svg static/map.svg" % (name, step)
        subprocess.check_output(cmd, shell=True, executable="/bin/bash")

        cmd = "docker rm -f map_container"
        subprocess.Popen(cmd, shell=True, executable="/bin/bash")

        return "/static/map.svg"

    except subprocess.CalledProcessError:
        return "Error"

    
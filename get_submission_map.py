import subprocess

def get_map(container):

    try:
        print("Starting the map container: "+container)
        cmd = "docker run --name map_container -it --rm %s" %(container)
        subprocess.Popen(cmd, shell=True, executable="/bin/bash")

        cmd = "docker cp map_container:/project/robotarium_scenario_maker/compiled/aido2-LFVI-real-validation/eval0/drawing.svg static/map.svg"
        subprocess.check_output(cmd, shell=True, executable="/bin/bash")

        cmd = "docker rm -f map_container"
        subprocess.Popen(cmd, shell=True, executable="/bin/bash")

        return "/static/map.svg"

    except subprocess.CalledProcessError:
        return "Error"

    
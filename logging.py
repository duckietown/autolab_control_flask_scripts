import subprocess,time

def start_logging(account, computer, filename):
    cmd = "docker -H %s rm -f bag_recorder || echo not bag_recorder before; docker -H %s run --name bag_recorder --rm -v /home/amaury/AIDO3_experiment_data:/data --net=host -dit duckietown/dt-ros-commons:master19-amd64 /bin/bash -c 'rosbag record -o /data/%s -a __name:=bag_recorder_node'" %(computer,computer, filename)

    try:
        subprocess.check_output(cmd, shell=True)
        return "Success"
    except subprocess.CalledProcessError as e:
        return "Error"

def stop_logging(account, computer):
    cmd = "docker -H %s exec bag_recorder /bin/bash -c 'source /opt/ros/kinetic/setup.bash; rosnode kill bag_recorder_node'" % (computer)

    try:
        subprocess.check_output(cmd, shell=True)
        return "Success"
    except subprocess.CalledProcessError as e:
        return "Error"
    # cmd = "docker -H %s stop bag_recorder" % (computer)
    # print cmd

    # try:
    #     subprocess.Popen(cmd, shell=True)
    #     print "Done"
    #     return "Success"
    # except subprocess.CalledProcessError as e:
    #     return "Error stopping docker container"
    


def clip_bag(account, computer, filename, start_time, end_time):
    command = "source /opt/ros/melodic/setup.bash; rosbag filter ~/AIDO3_experiment_data/%s ~/AIDO3_experiment_data/clipped_%s \' %f <= t.to_sec() <= %f \'" %(filename, filename, start_time, end_time)
    cmd = 'ssh -q %s@%s "%s"' % (account, computer,command)

    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        return "Error at clipping"

    command = "sudo rm ~/AIDO3_experiment_data/%s" %(filename)
    cmd = 'ssh -q %s@%s "%s"' % (account, computer,command)

    try:
        subprocess.check_output(cmd, shell=True)
        return "Success"  
    except subprocess.CalledProcessError as e:
        return "Error at removing"




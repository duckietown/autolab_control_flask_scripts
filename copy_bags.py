#!/usr/bin/env python
import multiprocessing
import os
import subprocess
from typing import List
import sys
import time
from aido_utils import get_device_list, show_status

OUTPUT_DIR = ""
starting_time = 0
ending_time = 0


def copy_bags_device(device):
    global OUTPUT_DIR
    global starting_time
    global ending_time

    print (device+": Starting clipping")
    print(starting_time)
    print(ending_time)
    cmd = "docker -H %s.local rm -f clipper || echo bla && docker -H %s.local run --rm -dit --net host \
            --name clipper -v /data/logs:/data/logs duckietown/rpi-duckiebot-base:master19 \
            /bin/bash -c \"cd /data/logs; \
            source /home/software/catkin_ws/devel/setup.bash; \
            for file in *; do if [[ \$file != *\"clipped\"* && \$file != *\".orig.\"* ]]; then \
            if [ ! -f clipped_\$file ]; then rosbag reindex \$file; fi; fi; done; \
            for file in *; do if [[ \$file != *\"clipped\"* && \$file != *\".orig.\"* ]]; then \
            rosbag info \$file ||  sudo unlink *.orig.* || echo bla && rosbag info \$file || rosbag reindex \$file ; fi; done; \
            for file in *; do if [[ \$file != *\"clipped\"* && \$file != *\".orig.\"* ]]; then \
            rosbag info \$file ||  sudo unlink *.orig.* || echo bla && rosbag info \$file || rosbag reindex \$file ; fi; done; \
            for file in *; do if [[ \$file != *\"clipped\"* && \$file != *\".orig.\"* ]]; then \
            sudo mv \$file \${file%%.active} || echo bla && sudo unlink *.orig.* || echo blabla; fi; done; \
            for file in *; do if [[ \$file != *\"clipped\"* && \$file != *\".orig.\"* ]]; then \
            rosbag info \$file && rosbag filter \$file clipped_\$file \' %f <= t.to_sec() <= %f \' && sudo rm -f \$file; fi; done \" " % (device, device, starting_time, ending_time)

    try:
        error = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        return "Error while attempting to clip bags: %s" % error.output.decode("utf-8")

    time.sleep(2)

    try:
        print (device+": Inspecting clipping status")
        while True:
            cmd = 'docker -H %s.local inspect -f \'{{.State.Running}}\' clipper' % device
            res = subprocess.check_output(
                cmd, shell=True, stderr=subprocess.STDOUT)
            if res.decode("utf-8") == "false\n":
                break
            time.sleep(0.5)
    except Exception as e:
        res = e.output.decode("utf-8")
        if "No such object" in res:
            pass
        else:
            print(res)

    print (device+": Starting copying")
    cmd = 'rsync -avz --block-size=131072 --protocol=29 --partial-dir=.rsync-partial %s:/data/logs/ %s/' % (
        device, OUTPUT_DIR)
    print (cmd)
    try:
        subprocess.check_output(cmd, shell=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        return "Copy failed : %s" % e.output.decode("utf-8")

    return "Success"


def list_files():
    global OUTPUT_DIR

    OUTPUTDIR = os.path.abspath(OUTPUT_DIR)
    while True:
        files = os.listdir(OUTPUTDIR)
        string = "-------------------------------------------------------\n"
        for f in sorted(files):
            if (os.path.isfile(os.path.join(OUTPUTDIR, f))):
                f_size = os.path.getsize(os.path.join(OUTPUTDIR, f))
                string += "%s : %9.3f MBs\n" % (f,
                                                float(f_size)/(1024.0*1024.0))
        sys.stdout.write(string)
        sys.stdout.flush()
        time.sleep(1)


def copy_bags_all_devices(device_list):
    global OUTPUT_DIR
    global starting_time
    global ending_time

    p = multiprocessing.Process(target=list_files)
    p.start()

    pool = multiprocessing.Pool(processes=20)
    results = pool.map(copy_bags_device, device_list)

    pool.close()
    pool.join()
    time.sleep(5)
    p.terminate()
    p.join()

    print()
    show_status(device_list, results)
    return results


def copy_bags_main_with_list(device_list, outputdir, starting_time_in, ending_time_in):
    global OUTPUT_DIR
    global starting_time
    global ending_time

    OUTPUT_DIR = outputdir
    starting_time = starting_time_in
    ending_time = ending_time_in

    if OUTPUT_DIR == None:
        OUTPUT_DIR = '/data/bags'

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print('Copying bags:')
    return device_list, copy_bags_all_devices(device_list)



test1, test2 = copy_bags_main_with_list({"watchtower22"}, None, 1564749866240, 1564749885589)
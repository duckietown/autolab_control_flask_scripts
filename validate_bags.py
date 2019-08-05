#!/usr/bin/env python
import multiprocessing
import os
import subprocess
import yaml

from typing import List
from aido_utils import get_device_list, show_status


OUTPUT_DIR = ""
bagfiles = None

def find_bag(device, bag_files):
    bag_name = "Not found"
    for bag in bag_files:
        if device in bag:
            bag_name = bag
            break

    return bag_name


def check_bag(device):
    global bag_files
    bag = find_bag(device, bag_files)

    if bag == "Not found":
        return "Missing"

    cmd = "rosbag info %s" % bag
    try:
        subprocess.check_output(cmd, shell=True)
    except:
        cmd = 'rosbag reindex %s' % bag
        try:
            subprocess.check_output(cmd, shell=True)
            bag_root = os.path.splitext(bag)[0]
            if ("active" in bag):
                os.rename(bag, bag_root)
            try:
                os.unlink('%s.orig.active' % bag_root)
            except:
                os.unlink('%s.orig.bag' % bag_root)
        except subprocess.CalledProcessError:
            return "Reindex error"

    info_dict = yaml.load(subprocess.check_output(
        ['rosbag', 'info', '--yaml', bag]
    ).rstrip().decode("utf-8"),
        Loader=yaml.FullLoader)
    try:
        duration = info_dict['duration']
        bag_topics = info_dict['topics']

        count = 0

        for topic in bag_topics:
            if "compressed" in topic['topic']:
                count = topic['messages']
                break

        return "T:%.1f, R:%.1f" % (duration, count/duration)
    except KeyError:
        return "Empty"


def check_all_bags(device_list):

    global OUTPUT_DIR
    global bag_files
    bag_files = [os.path.join(OUTPUT_DIR, f)
                 for f in os.listdir(OUTPUT_DIR)
                 if os.path.isfile(os.path.join(OUTPUT_DIR, f))]
    print(bag_files)
    pool = multiprocessing.Pool(processes=20)
    results = pool.map(check_bag, device_list)
    pool.close()
    pool.join()

    show_status(device_list, results)


def copy_bags_main(device_list, outputdir):

    global OUTPUT_DIR

    OUTPUT_DIR = outputdir

    if OUTPUT_DIR == None:
        OUTPUT_DIR = '/data/bags'

    print('Validating bags:')
    check_all_bags(device_list)

print(copy_bags_main({"watchtower22"}, None))
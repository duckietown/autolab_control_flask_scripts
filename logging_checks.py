import multiprocessing
import subprocess
from typing import List

from aido_utils import get_device_list, show_status

def check_device(device):

    cmd = 'ssh -q  %s \'bash -c "\
                            if [ -e /dev/sda1 ]; \
                            then \
                                if [ $(mount | grep -c /data/logs) != 1 ]; \
                                then \
                                    sudo mkdir /data/logs > /dev/null 2>&1; \
                                    sudo mount /dev/sda1 /data/logs > /dev/null 2>&1;\
                                fi; \
                                echo Again; \
                            else \
                                echo No USB Device; \
                            fi; \
                            "\'' % (device)
    try:
        res = subprocess.check_output(cmd, shell=True)
        res = res.rstrip().decode("utf-8")

        if res == 'Again':
            cmd = 'ssh -q %s \'bash -c "\
                                    if [ $(mount | grep -c /data/logs) != 1 ]; \
                                    then \
                                        echo Mount failed; \
                                    else \
                                        if sudo -s test -w /dev/sda1 ; \
                                        then \
                                            echo Writable USB;\
                                        else \
                                            echo Unwritable USB; \
                                        fi; \
                                    fi; \
                                    "\'' % (device)

            res = subprocess.check_output(cmd, shell=True)
            res = res.rstrip().decode("utf-8")
        return res

    except subprocess.CalledProcessError as e:
        return "Error"


def check_all_devices(device_list):
    pool = multiprocessing.Pool(processes=20)
    results = pool.map(check_device, device_list)
    pool.close()
    pool.join()
    show_status(device_list, results)
    return results

def logging_checks_main():
    device_list = get_device_list('device_list.txt')
    return device_list, check_all_devices(device_list)

def logging_checks_with_list(device_list):
    return device_list, check_all_devices(device_list)

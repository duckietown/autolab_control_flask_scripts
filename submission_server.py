import json
import subprocess

import requests

from upload_s3 import upload_files


def request_job(token, endpoint, url):
    features = {
        'disk_available_mb': 100000,
        'disk_total_mb': 256000,
        'processor_free_percent': 95,
        'nduckiebots': 6,
        'x86_64': 1,
        'processor_frequency_mhz': 3500,
        'map_aido2_LF_pub': 1,
        'map_aido2_LFV_pub': 1,
        'map_aido2_LFVI_pub': 1,
        'gpu': 0,
        'mac': 0,
        'armv7l': 0,
        'ram_total_mb': 16000,
        'ram_available_mb': 10000,
        'nprocessors': 12,
        'p1': 1,
        'picamera': 0,
        'ipfs': 1

    }
    data_get = {
        'submission_id': None,
        'machine_id': 'autolab_server',
        'process_id': 'autolab_server-1',
        'evaluator_version': 1,
        'features': features,
        'reset': False
    }

    tmp = requests.get(url + endpoint, data=json.dumps(data_get), headers={'X-Messaging-Token': token})
    return tmp.content


def upload_s3(aws_config, path, ignore_pattern):
    uploaded = upload_files(path, aws_config, ignore_pattern)
    return uploaded


def create_hashes(path):
    try:
        cmd = f"ipfs add -r {path}"
        out = subprocess.check_output(cmd, shell=True, executable="/bin/bash")
        out = out.decode()
        tmp = out.split('\n')
        if tmp[-1] == "":
            tmp = tmp[:-1]
        result = {}
        for line in tmp:
            line = line.split(' ')
            result[line[2]] = line[1]
        return result

    except subprocess.CalledProcessError:
        return "Error"


def upload_job(token, endpoint, url, job_id, result, ipfs_hashes, scores, uploaded):
    stats = {
        'msg': 'Scores from the evaluation of job: ' + str(job_id),
        'scores': scores
    }

    data_post = {
        'job_id': job_id,
        'machine_id': 'autolab_server',
        'process_id': 'autolab_server-1',
        'result': result,
        'stats': stats,
        'uploaded': uploaded,
        'ipfs_hashes': ipfs_hashes,
        'evaluator_version': 1
    }

    tmp = requests.post(url + endpoint, data=json.dumps(data_post), headers={'X-Messaging-Token': token})
    return tmp.content

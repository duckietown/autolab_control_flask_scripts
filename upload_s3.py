#Taken from https://github.com/duckietown/duckietown-challenges-runner/blob/v3/src/duckietown_challenges_runner/runner.py
import os
import subprocess
import mimetypes
from collections import OrderedDict
import boto3
from botocore.exceptions import ClientError

def get_files_to_upload(path, ignore_patterns=()):
    def to_ignore(x):
        for p in ignore_patterns:
            if os.path.basename(x) == p:
                return True
        return False

    toupload = OrderedDict()
    for dirpath, _ , filenames in os.walk(path):
        for f in filenames:
            if to_ignore(f):
                continue
            rpath = os.path.join(os.path.relpath(dirpath, path), f)
            if rpath.startswith('./'):
                rpath = rpath[2:]

            toupload[rpath] = os.path.join(dirpath, f)
    print(toupload)
    return toupload

def compute_sha256hex(filename):
    cmd = ['shasum', '-a', '256', filename]
    res = subprocess.check_output(cmd)
    tokens = res.split()
    h = tokens[0]
    assert len(h) == len('08c1fe03d3a6ef7dbfaccc04613ca561b11b5fd7e9d66b643436eb611dfba348')
    return h

def guess_mime_type(filename):
    mime_type, _encoding = mimetypes.guess_type(filename)

    if mime_type is None:
        if filename.endswith('.yaml'):
            mime_type = 'text/yaml'
        else:
            mime_type = 'binary/octet-stream'
    return mime_type

def upload(aws_config, toupload):

    bucket_name = aws_config['bucket_name']
    aws_access_key_id = aws_config['aws_access_key_id']
    aws_secret_access_key = aws_config['aws_secret_access_key']
    # aws_root_path = aws_config['path']
    aws_path_by_value = aws_config['path_by_value']
    

    s3 = boto3.resource("s3",
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key)

    uploaded = []
    for rpath, realfile in toupload.items():

        sha256hex = compute_sha256hex(realfile)

        # path_by_value
        object_key = os.path.join(aws_path_by_value, 'sha256', sha256hex)

        size = os.stat(realfile).st_size
        mime_type = guess_mime_type(realfile)

        aws_object = s3.Object(bucket_name, object_key)
        try:
            aws_object.load()
            status = 'known'
            print('%15s %8s  %s' % (status, size, rpath))

        except ClientError as e:
            not_found = e.response['Error']['Code'] == '404'
            if not_found:
                status = 'uploading'
                print('%15s %8s  %s' % (status, size, rpath))
                aws_object.upload_file(realfile, ExtraArgs={'ContentType': mime_type})

            else:
                raise
        url = 'http://%s.s3.amazonaws.com/%s' % (bucket_name, object_key)
        storage = dict(s3=dict(object_key=object_key, bucket_name=bucket_name, url=url))
        uploaded.append(dict(size=size, mime_type=mime_type, rpath=rpath, sha256hex=sha256hex, storage=storage))
    return uploaded

def upload_files(wd, aws_config, ignore_patterns=('.DS_Store',)):
    toupload = get_files_to_upload(wd, ignore_patterns=ignore_patterns)

    if not aws_config:
        print('Not uploading artifacts because AWS config not passed.')
        return "Error"
    else:
        return upload(aws_config, toupload)
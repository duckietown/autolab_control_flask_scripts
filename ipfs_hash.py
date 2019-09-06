import subprocess

def create_hashes(path):
    
    try:
        cmd = "ipfs add -r -q %s" % (path)
        out = subprocess.check_output(cmd, shell=True, executable="/bin/bash")

        return out

    except subprocess.CalledProcessError:
        return "Error"
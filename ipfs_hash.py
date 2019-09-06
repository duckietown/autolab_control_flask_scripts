import subprocess

def create_hashes(path):
    
    try:
        cmd = "ipfs add -r -q %s" % (path)
        out = subprocess.check_output(cmd, shell=True, executable="/bin/bash")

        return out

    except subprocess.CalledProcessError:
        return "Error"


pwd = "~/AIDO3_experiment_data/submission_20/eval0/20190905_195810"
out = create_hashes(pwd)
print(out)
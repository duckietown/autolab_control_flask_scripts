import subprocess

def create_hashes(path):

    try:
        cmd = "ipfs add -r %s" % (path)
        out = subprocess.check_output(cmd, shell=True, executable="/bin/bash")
        tmp = out.split('\n')
        if (tmp[-1]==""):
            tmp = tmp[:-1]
        result = {}
        for line in tmp:
            line=line.split(' ')
            result[line[2]]=line[1]
        return result

    except subprocess.CalledProcessError:
        return "Error"

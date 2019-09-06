import subprocess

def create_hashes(path):

    try:
        cmd = "ipfs add -r %s" % (path)
        out = subprocess.check_output(cmd, shell=True, executable="/bin/bash")
        tmp = out.split('\n')
	if (tmp[-1]==""):
		tmp = tmp[:-1]
	result = []
	for i, line in enumerate(tmp):
		line=line.split(' ')
		result.append([])
		result[i].append(line[1])
		result[i].append(line[2])
        return result

    except subprocess.CalledProcessError:
        return "Error"

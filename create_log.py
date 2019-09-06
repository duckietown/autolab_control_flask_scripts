import yaml
import subprocess

def generate_log_file(content, filename, mount):
    try:
        cmd = "mkdir -p %s" % (mount)
        subprocess.check_output(cmd, shell=True, executable="/bin/bash")
        f = open(mount+"/"+filename,"w")
        yaml.safe_dump(content,f,default_flow_style=False, encoding='utf-8', allow_unicode=True)
        f.close
        return "Success"

    except subprocess.CalledProcessError:
        return "Error"

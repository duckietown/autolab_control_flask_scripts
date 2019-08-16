import subprocess

def check_space_for_logging(account, computer):
    cmd = 'ssh -q %s@%s "df | grep /dev/nvme0n1p2; exit 0;"' % (account, computer)

    try:
        res = subprocess.check_output(cmd, shell=True)
        res = res.rstrip().decode("utf-8")

        if res == "":
            return "Error"
        else:
            res = res.split()[3]

        return res

    except subprocess.CalledProcessError:
        return "Error"
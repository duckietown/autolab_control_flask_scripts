import os
import shutil
import subprocess


def copy_roster_with_list(bot_list, mount):
    roster_path = os.environ.get('ROSTER_PATH', '/roster')

    cmd = "cd %s; git pull; mkdir -p %s" % (roster_path, mount)

    try:
        subprocess.check_output(cmd, shell=True)
        for bot in bot_list:
            if "bot" in bot:
                cmd = "cp -r %s/autobots/%s %s" % (roster_path, bot, mount)
            else:
                cmd = "cp -r %s/watchtowers/%s %s" % (roster_path, bot, mount)
            try:
                subprocess.check_output(cmd, shell=True)
            except subprocess.CalledProcessError:
                return "Error"

    except subprocess.CalledProcessError:
        return "Error"
    return "Success"

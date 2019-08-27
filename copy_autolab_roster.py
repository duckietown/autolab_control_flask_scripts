import subprocess

def copy_roster_with_list(bot_list, mount, roster_location):
    cmd = "cd %s; git pull" %(roster_location)

    try:
        subprocess.check_output(cmd, shell=True)
        for bot in bot_list:
            if "bot" in bot:
                cmd = "cp autobots/%s %s" %(bot, mount)
            else:
                cmd = "cp watchtowers/%s %s" %(bot, mount)
            try:
                subprocess.check_output(cmd, shell=True)
            except subprocess.CalledProcessError:
                return "Error"

    except subprocess.CalledProcessError:
        return "Error"
    return "Success"

copy_roster_with_list(["autobot03"],"~/AIDO3_experiment_data","ETHZ-autolab-fleet-roster")
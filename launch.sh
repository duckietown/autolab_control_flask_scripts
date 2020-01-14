#!/bin/bash

source /environment.sh

# initialize launch file
dt_launchfile_init

# YOUR CODE BELOW THIS LINE
# ----------------------------------------------------------------------------


# NOTE: Use the variable CODE_DIR to know the absolute path to your code
# NOTE: Use `dt_exec COMMAND` to run the main process (blocking process)
service avahi-daemon start

# load external ssh keys if available
if [ -d /external_ssh ]; then
  echo "[INFO]: Received external SSH keys, loading them..."
  cp -r /external_ssh ~/.ssh
  chown -R `whoami` ~/.ssh
  echo "[INFO]: Done!"
fi

# check if the roster was mounted
if [ ! -d /roster ]; then
  echo "[FATAL]: No roster found in '/roster'. Please, mount your roster repository to '/roster'"
  exit 1
fi

# check if the IPFS was mounted
if [ ! -d /root/.ipfs ]; then
  echo "[FATAL]: No IPFS configuration found. Please, mount your IPFS directory ('~/.ipfs') to '/root/.ipfs'"
  exit 2
fi

# check if docker is shared
if [ ! -S /run/docker.sock ]; then
  echo "[FATAL]: No Docker socket found. Please, mount your Docker socket ('/var/run/docker.sock') to '/var/run/docker.sock'"
  exit 3
fi

# launching app
dt_exec python3 -m autolab.flask_server $@


# ----------------------------------------------------------------------------
# YOUR CODE ABOVE THIS LINE

# terminate launch file
dt_launchfile_terminate

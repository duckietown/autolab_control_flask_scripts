from os.path import expanduser


def default_env(duckiebot_name, duckiebot_ip):
    return {
        "ROS_MASTER": duckiebot_name,
        "DUCKIEBOT_NAME": duckiebot_name,
        "ROS_MASTER_URI": "http://%s:11311" % duckiebot_ip,
        "DUCKIEFLEET_ROOT": "/data/config",
        "DUCKIEBOT_IP": duckiebot_ip,
        "DUCKIETOWN_SERVER": duckiebot_ip,
        "QT_X11_NO_MITSHM": 1,
    }


def bind_local_data_dir():
    return {"%s/data" % expanduser("~"): {"bind": "/data"}}


def bind_duckiebot_data_dir():
    return {"/data": {"bind": "/data"}}


def stop_container(container):
    try:
        container.stop()
    except Exception as e:
        pass
        # dtslogger.warn("Container %s not found to stop! %s" % (container, e))


def remove_container(container):
    try:
        container.remove()
    except Exception as e:
        pass
        # dtslogger.warn("Container %s not found to remove! %s" % (container, e))


def check_if_running(client, container_name):
    try:
        _ = client.containers.get(container_name)
        # dtslogger.info("%s is running." % container_name)
        return True
    except Exception as e:
        # dtslogger.error("%s is NOT running - Aborting" % e)
        return False


def remove_if_running(client, container_name):
    try:
        container = client.containers.get(container_name)
        # dtslogger.info("%s already running - stopping it first.." %
        #                container_name)
        stop_container(container)
        # dtslogger.info("removing %s" % container_name)
        remove_container(container)
    except Exception as e:
        pass
        # dtslogger.warn("couldn't remove existing container: %s" % e)


def pull_if_not_exist(client, image_name):
    from docker.errors import ImageNotFound

    try:
        client.images.get(image_name)
    except ImageNotFound:
        # dtslogger.info(
        #     "Image %s not found. Pulling from registry." % (image_name))

        repository = image_name.split(':')[0]
        try:
            tag = image_name.split(':')[1]
        except IndexError:
            tag = 'latest'

        loader = 'Downloading .'
        for _ in client.api.pull(repository, tag, stream=True, decode=True):
            loader += '.'
            if len(loader) > 40:
                print(' '*60, end='\r', flush=True)
                loader = 'Downloading .'
            print(loader, end='\r', flush=True)

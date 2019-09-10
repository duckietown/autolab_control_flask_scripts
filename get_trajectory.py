def request_yaml(mount, duckiebot):
    f = open(mount+"/"+duckiebot+".yaml","r")
    data = f.read()
    f.close
    return data

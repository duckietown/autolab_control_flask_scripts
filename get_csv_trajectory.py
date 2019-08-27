def request_csv(mount, duckiebot):
    f = open(mount+"/duckiebot_"+duckiebot+".csv","r")
    data = f.read()
    f.close
    data=data.replace('\t', ',')
    return data

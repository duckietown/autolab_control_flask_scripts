def request_csv(mount, duckiebot):
    f = open(mount+"/autobot"+duckiebot+".csv","r")
    data = f.read()
    f.close
    data=data.replace('\t', ',')
    return data

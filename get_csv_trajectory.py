def request_csv(mount, duckiebot):
    f = open(mount+"/duckiebot_"+duckiebot+".csv","r")
    data = f.read()
    f.close
    return data

print(request_csv("~/AIDO3_experiment_data/submission_8/eval0/20190827_124740","403"))
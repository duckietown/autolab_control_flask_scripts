import yaml

def generate_log_file(content, filename, mount):
    f = open(mount+"/"+filename,"w")
    yaml.safe_dump(content,f,default_flow_style=False, encoding='utf-8', allow_unicode=True)
    f.close
    return 0

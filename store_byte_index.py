import json
import re

def write_byte_index():
    map = {}

    with open("stored_index.json", 'rb') as f:
        for line in f:
            # if line in json file starts with a quote a.k.a. it is a token
            if line[0:1].decode('utf-8') == "\"":
                map[re.sub(r'\W+', '', line.decode('utf-8'))] = f.tell() - len(line)
    
    print("RUN2")
    with open("stored_byte_index.json", "w") as f:
        json.dump(map, f, indent=0, separators=(", ", ": "))

    return map

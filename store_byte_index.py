import json
import re

def write_byte_index():
    map = {}

    for i in range(1,4):
        with open(f"partial_index{i}.json", 'rb') as f:
            for line in f:
                if line[0:1].decode('utf-8') == "\"":
                    map[re.sub(r'\W+', '', line.decode('utf-8'))] = [i, f.tell() - len(line)]
    
    with open("stored_byte_index.json", "w") as f:
        json.dump(map, f, indent=0, separators=(", ", ": "))

    return map

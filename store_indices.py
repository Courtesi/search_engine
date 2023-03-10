import json

def store(indicies: list):
    indexNum = 0
    for index in indicies:
        indexNum += 1
        with open(f"partial_index{indexNum}.json", "w") as f:
            json.dump(index, f, indent=0, separators=(", ", ": "))
            f.write("\n")

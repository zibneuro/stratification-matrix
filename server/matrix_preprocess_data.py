import json 
import os 

def convert(item):
    foo = {
        "presynaptic" : {},
        "postsynaptic" : {}
    }
    foo["presynaptic"]["cell_type"] = item["prT"]
    foo["postsynaptic"]["cell_type"] = item["poT"]
    foo["value"] = item["con"][1]
    return foo

with open("/home/philipp/cis/cortexinsilico3d/public/connectivity/connectome.json") as f:
    data = json.load(f)["data"]

rules = []
for item in data:
    if(item["prR"] == "C2" and item["poR"] == "C2"):
        rules.append(convert(item))
    
outData = {
    "rules" : rules
}

with open("/home/philipp/cis/src/data/matrix/default/DSC_null_model.json", "w+") as f:
    json.dump(outData, f)
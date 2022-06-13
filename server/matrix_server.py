import os
import json
import sys
import flask
from flask import request
from flask_cors import cross_origin

app = flask.Flask(__name__)


def loadJson(filename):
    with open(filename) as f:
        return json.load(f)


@app.route("/matrixServer/getProfiles", methods=["GET", "POST"])
@cross_origin()
def getProfiles():
    global props
    if request.method == "POST":
        if request.data:
            data = request.get_json(force=True)
            print("getProfiles request:", data)
            return json.dumps(props)


@app.route("/matrixServer/test", methods=["GET", "POST"])
@cross_origin()
def test():
    return "matrix server"


def printUsageAndExit():
    print("Usage:")
    print("python matrix_server.py data-dir")
    exit()


if __name__ == "__main__":
    if(len(sys.argv) != 2):
        printUsageAndExit()

    dataDir = sys.argv[1]

    props = {}
    profilesJson = loadJson(os.path.join(dataDir, "profiles.json"))
    profiles = profilesJson["profiles"]
    props["default_profile"] = profilesJson["default_profile"]
    
    for profile in profiles:
        profileName = profile["name"]        
        props[profileName] = loadJson(os.path.join(dataDir, "{}.json".format(profileName)))
    
    app.run(host="localhost", port=5000)
    


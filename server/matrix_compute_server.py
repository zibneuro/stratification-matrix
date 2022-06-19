import os
import json
import profile
import sys
import flask
from flask import request, jsonify
from flask_cors import CORS, cross_origin

import util
from query_processor import QueryProcessor

app = flask.Flask(__name__)


@app.route("/matrixComputeServer/getTiles", methods=["GET", "POST"])
@cross_origin()
def getTiles():
    global processors
    if request.method == "POST":
        if request.data:
            data = request.get_json(force=True)
            #print(">> request Raw", data)
            profileName = data["profile"]            
            tiles = processors[profileName].computeTileData(data)            
            return json.dumps(tiles)            


@app.route("/matrixComputeServer/test", methods=["GET", "POST"])
@cross_origin()
def test():
    return "matrix compute server"


def printUsageAndExit():
    print("Usage:")
    print("python matrix_comptute_server.py <data-folder>")
    exit()


if __name__ == "__main__":
    if(len(sys.argv) != 2):
        printUsageAndExit()

    dataFolder = sys.argv[1]

    processors = {}

    profiles = util.loadJson(os.path.join(dataFolder, "profiles.json"))["profiles"]
    for profile in profiles:
        profileName = profile["name"]
        processors[profileName] = QueryProcessor(dataFolder, profileName)
        processors[profileName].loadMasks()

    app.run(host="localhost", port=5001)

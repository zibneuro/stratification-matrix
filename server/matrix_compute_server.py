import os
import json
import profile
import sys
import flask
from flask import request, jsonify
from flask_cors import CORS, cross_origin

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



"""
@app.route("/matrixComputeServer/getTiles", methods=["GET", "POST"])
@cross_origin()
def getTiles():
    global props
    if request.method == "POST":
        print("getTiles")
        if request.data:
            data = request.get_json(force=True)
            #print(">> request Raw", data)
            tiles = calculator.computeTileData(props, data)
            response_data = tiles
            return json.dumps(response_data)


@app.route("/matrixComputeServer/getDistribution", methods=["GET", "POST"])
@cross_origin()
def getDistribution():
    global props
    if request.method == "POST":
        print("getDistribution")
        if request.data:
            data = request.get_json(force=True)
            #print(">> request Raw", data)
            tiles = calculator.getDistribution(props, data)
            response_data = tiles
            return json.dumps(response_data)


@app.route("/matrixComputeServer/cluster", methods=["GET", "POST"])
@cross_origin()
def cluster():
    global props
    if request.method == "POST":
        print("cluster")
        if request.data:
            data = request.get_json(force=True)
            #print(">> request Raw", data)
            tiles = calculator.cluster(props, data)
            response_data = tiles
            return json.dumps(response_data)


@app.route("/matrixComputeServer/edit", methods=["GET", "POST"])
@cross_origin()
def edit():
    global props
    if request.method == "POST":
        print("edit")
        if request.data:
            data = request.get_json(force=True)
            print(">> request Raw", data)
            calculator.edit(props, data)
            return json.dumps({"message": "OK"})


@app.route("/matrixComputeServer/resetEdits", methods=["GET", "POST"])
@cross_origin()
def resetEdits():
    global props
    if request.method == "POST":
        print("edit")
        calculator.resetEdits(props)
        return json.dumps({"message": "OK"})

"""


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
    #processors["RBC"] = QueryProcessor(dataFolder, "RBC")
    #processors["RBC"].loadMasks()
    #processors["VIS"] = QueryProcessor(dataFolder, "VIS")
    #processors["VIS"].loadMasks()
    processors["H01"] = QueryProcessor(dataFolder, "H01")
    processors["H01"].loadMasks()

    """
    testRequest = {
        "profile" : "RBC",
        "rowSelectionStack" : [[["cell_type", "L2PY"],["subregion","septum"]],[["cell_type", "VPM"]],[["cell_type", "L4PY"]],[["cell_type", "L5PT"]]],
        "colSelectionStack" : [[["cortical_column", "A1"]],[["cortical_column", "C2"]],[["cortical_column", "A3"]],[["cortical_column", "A4"]]]
    }
    print(processors["RBC"].computeTileData(testRequest))
    """

    app.run(host="localhost", port=5001)

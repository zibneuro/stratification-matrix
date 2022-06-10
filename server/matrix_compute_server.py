import flask
import io
import os
import json
import sys

from flask import request, jsonify
from flask_cors import CORS, cross_origin

import matrix_server_worker
import matrix_server_tiling
import matrix_server_calculator as calculator

app = flask.Flask(__name__)


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


@app.route("/matrixComputeServer/runInference", methods=["GET", "POST"])
@cross_origin()
def runInference():
    global props
    if request.method == "POST":
        print("runInference")
        #calculator.resetEdits(props)
        return json.dumps({"message": "OK"})


@app.route("/matrixComputeServer/test", methods=["GET", "POST"])
@cross_origin()
def test():
    return "matrix compute server"


def printUsageAndExit():
    print("Usage:")
    print("python matrix_comptute_server.py RBC_DATA_DIR")
    exit()


if __name__ == "__main__":
    if(len(sys.argv) != 2):
        printUsageAndExit()

    dataDir = sys.argv[1]
    props = {}
    calculator.init(props, dataDir)
    app.run(host="localhost", port=5001)

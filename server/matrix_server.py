import flask
import io
import os
import json
import sys

from flask import request, jsonify
from flask_cors import CORS, cross_origin

import matrix_server_worker
import matrix_server_tiling

app = flask.Flask(__name__)


@app.route("/matrixServer/getMeta", methods=["GET", "POST"])
@cross_origin()
def getMeta():
    global props
    if request.method == "POST":
        if request.data:
            data = request.get_json(force=True)
            print("getMeta request:", data)
            response_data = props["meta"]
            return json.dumps(response_data)


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
    matrix_server_worker.init(props, dataDir)    
    app.run(host="localhost", port=5000)
    


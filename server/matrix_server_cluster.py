import sys
import os
import json

import util
import util_stats
import util_time
import matrix_server_calculator
import matrix_server_filter


def drawSamples(props, n, categorySelection):
    samples = {}
    for i in range(0, 11):
        for j in range(0,10):
            tileKey = ((-1, i, -1, -1), (-1, j, -1), (-1, -1, -1, -1))
            #tileKey = matrix_server_filter.getRandomTileKey(props, categorySelection)        
            print(tileKey)
            tileData = matrix_server_calculator.initTile(props, None, tileKey, None)
            util_time.startTimer("compute single tile")
            while(len(tileData["computeState"]["cp_null_model"]) != len(tileData["computeState"]["uniquePre"])):           
                matrix_server_calculator.computeConnectivityNull(props, tileData, tileKey)
            util_time.writeTimer("compute single tile")
            hist = util_stats.evalHistogramNormed(tileData["computeState"]["cp_null_model_distribution"])
            if(hist[0] < 0.9):
                samples[matrix_server_filter.getKeyAsString(tileKey)] = hist[1:]        
            #print(samples)
    return samples


def printUsageAndExit():
    print("python matrix_server_cluster.py data-dir")
    exit()


if __name__ == "__main__":
    if(len(sys.argv) != 2):
        printUsageAndExit()
    dataDir = sys.argv[1]
    outputDir = os.path.join(dataDir, "cluster")  
    util.makeCleanDir(outputDir)
    props = {}
    matrix_server_calculator.init(props, dataDir)
    categorySelection = {
        "presynaptic" : ["cell_type"],
        "postsynaptic" : ["cell_type"],
        "subcellular" : []
    }
    samples = drawSamples(props, 50, categorySelection)
    with open(os.path.join(outputDir, "samples.json"), "w+") as f:
        json.dump(samples, f)


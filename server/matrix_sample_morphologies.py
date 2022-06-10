import os
import sys
import time
import datetime
import numpy as np
import copy
import shutil
import json
import util_amira as amira
import util_selection as selection
import convert_nx_asc
import convert_nx_swc


def printUsageAndExit():
    print("Usage:")
    print("matrix_sample_morphologies.py <specification>")
    print("")
    sys.exit()


def readIds(filename):
    NIDs = []
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            line = line.rstrip()
            if(" " in line):
                line = line.split(" ")[0]
            NIDs.append(int(line))
    return NIDs


def readPreIdsMap(filename):
    NIDs = {}
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            line = line.rstrip()
            NIDs[int(line.split(" ")[0])] = int(line.split(" ")[1])
    return NIDs


def initFolder(folder):
    outputFolder = os.path.join(folder)
    if(os.path.exists(outputFolder)):
        shutil.rmtree(outputFolder)
    os.makedirs(outputFolder)
    return outputFolder

def getDefinedSample(ids, k, seed):    
    ids.sort()
    if(len(ids) < k):
        return ids
    np.random.seed(seed)
    np.random.shuffle(ids)    
    return ids[0:k]

def getUniqueNIDs(props):
    foo = {}
    for NID, prop in props.items():
        if(prop["file"] not in foo.keys()):
            foo[prop["file"]] = NID
    return list(foo.values())

def sampleNIDs(props, specs):
    if(specs["side"] == "pre"):
        uniqueNIDs = getUniqueNIDs(props)
        return getDefinedSample(uniqueNIDs, specs["n"], specs["randomSeed"])
    else:
        return getDefinedSample(list(props.keys()), specs["n"], specs["randomSeed"])   


if __name__ == "__main__":
    if(len(sys.argv) != 2):
        printUsageAndExit()

    modelDataFolder = "/vis/data/projects/buildingbrains/input_mapping/morphologies/ascii"
    outputFolderBase = "/vis/scratchN/bzfharth/matrixMorphologies"
    specsFile = sys.argv[1]
    specsName = os.path.basename(specsFile).split(".")[0].replace("specification","batch")

    outputFolder = initFolder(os.path.join(outputFolderBase, specsName))
    shutil.copy2(specsFile, outputFolder)
    mergedFolder = initFolder(os.path.join(outputFolder, "merged"))
    clustersMeta = []

    with open(specsFile) as f:
        specs = json.load(f)

    for i in range(0,len(specs)):
        clusterSpecs = specs[i]
        clusterInfo = {
            "index" : i + 1,
            "cluster" : clusterSpecs["name"],
            "values" : []
        }        

        clusterOutputFolder = initFolder(os.path.join(outputFolder, clusterSpecs["name"]))
        idsFile = os.path.join(outputFolderBase, "NIDs", clusterSpecs["NIDs"])
        samplingRate = clusterSpecs["samplingRate"]
        NIDs = readIds(idsFile)
        props = {}

        spatialGrahpSet = amira.readSpatialGraphSet(
            os.path.join(modelDataFolder, "MorphologiesWithNeuronIDs.am"))

        for NID in NIDs:
            if(clusterSpecs["side"] == "pre"):
                props[NID] = spatialGrahpSet[NID][-1]
            else:
                props[NID] = spatialGrahpSet[NID][0]
        
        NIDsSampled = sampleNIDs(props, clusterSpecs)

        for NID in NIDsSampled:
            # 2 LOAD TRANSFORMED MORPHOLOGY IN NX FROM AM
            fileName = props[NID]["file"]
            transformation = props[NID]["transformation"]        
            g = amira.readSpatialGraph(fileName, transformation)
            try:
                convert_nx_asc.postprocessGraph(g, separateSoma=False, relabel=False)
                swcFile = os.path.join(clusterOutputFolder, "{}-{}-{}.swc".format(NID, clusterSpecs["side"], samplingRate))
                clusterInfo["values"].append(os.path.basename(swcFile))
                convert_nx_swc.save_SWC(g, swcFile, samplingRate = samplingRate)
                shutil.copy2(swcFile, mergedFolder)

            except Exception as e:
                print("Error: {} {} {}".format(NID, clusterSpecs["name"], fileName))
                print(str(e))

        clustersMeta.append(clusterInfo)

    with open(os.path.join(outputFolder, "clusters.json"), "w+") as f:
        json.dump(clustersMeta, f)


   
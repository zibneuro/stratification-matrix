import os
import sys
import json
import numpy as np

#import umap
#import hdbscan

import util_time
import util_stats
import matrix_server_rules
import matrix_server_filter
import matrix_server_test


def loadJson(filename):
    with open(filename) as f:
        return json.load(f)


def init(props, dataDir):
    print("init")
    props["dataDir"] = dataDir
    props["increment"] = 0
    props["constants"] = {}
    props["featuresFloat"] = {}
    props["featuresInt"] = {}
    props["meta"] = {}
    props["rows"] = {}
    props["cols"] = {}
    props["attributeInfoRows"] = {}
    props["attributeInfoCols"] = {}
    props["attributeInfoSubcellular"] = {}
    props["attributeInfoOrder"] = {}
    props["tileCache"] = {}
    props["dscCacheNull"] = {}
    loadRowsColumns(props)
    loadFeatures(props)
    setAttributeInfo(props)
    printAttributeInfo(props)
    loadConstants(props)


def loadConstants(props):
    props["constants"]["CP_empirical"] = matrix_server_rules.parseRules(props, loadJson(
        os.path.join(props["dataDir"], "default", "CP_empirical.json")))
    props["constants"]["bouton_weight_modified_model"] = matrix_server_rules.parseRules(props, loadJson(
        os.path.join(props["dataDir"], "default", "bouton_weight_modified_model.json")))


def loadRowsColumns(props):
    dataDir = props["dataDir"]
    props["meta"] = loadJson(os.path.join(dataDir, "meta.json"))
    props["rows"] = np.loadtxt(os.path.join(dataDir, "rows.tsv"), dtype=int)
    props["cols"] = np.loadtxt(os.path.join(dataDir, "cols.tsv"), dtype=int)
    props["attributeInfoOrder"]["rows"] = getMaskColumns(
        os.path.join(dataDir, "rows.tsv"))
    props["attributeInfoOrder"]["cols"] = getMaskColumns(
        os.path.join(dataDir, "cols.tsv"))


def getMaskColumns(filename):
    with open(filename) as f:
        lines = f.readlines()
        labels = lines[0].rstrip().replace("# ", "").split("\t")
        return labels


def loadFeatures(props):
    dataDir = props["dataDir"]
    uniquePreIds = np.unique(props["rows"][:, 3])
    for i in range(0, len(uniquePreIds),4):
    #for i in range(0, 5, 1):
        preId = uniquePreIds[i]
        print("load features ({}) {}".format(i, preId))
        props["featuresFloat"][preId] = np.loadtxt(os.path.join(
            dataDir, "features", "{}_float.tsv".format(preId)), dtype=float)
        filenameInt = os.path.join(
            dataDir, "features", "{}_int.tsv".format(preId))
        props["featuresInt"][preId] = np.loadtxt(filenameInt, dtype=int)
        if(i == 0):
            props["attributeInfoOrder"]["subcellular"] = getMaskColumns(
                filenameInt)


def setAttributeInfo(props):
    meta = props["meta"]
    for attribute in meta["rows"]["attributes"]:
        if(attribute["category"] == "subcellular"):
            props["attributeInfoSubcellular"][attribute["name"]
                                              ] = getAttributeInfo(attribute)
        else:
            props["attributeInfoRows"][attribute["name"]
                                       ] = getAttributeInfo(attribute)
    for attribute in meta["cols"]["attributes"]:
        if(attribute["category"] == "subcellular"):
            props["attributeInfoSubcellular"][attribute["name"]
                                              ] = getAttributeInfo(attribute)
        else:
            props["attributeInfoCols"][attribute["name"]
                                       ] = getAttributeInfo(attribute)
    getMaskColumns(
        os.path.join(props["dataDir"], "rows.tsv"))


def getAttributeInfo(attribute):
    valueIndex = {}
    for i in range(0, len(attribute["values"])):
        value = attribute["values"][i]
        index = attribute["indices"][i]
        valueIndex[value] = index
    return valueIndex


def printAttributeInfo(props):
    print("attribute info rows", props["attributeInfoRows"])
    print("attribute info cols", props["attributeInfoCols"])
    print("attribute info subcellular", props["attributeInfoSubcellular"])
    print("attribute info order", props["attributeInfoOrder"])


def computeDSCPerPost(featuresInt, dsc):
    if(not featuresInt.shape[0]):
        return np.array([]), np.array([])
    postIds, idx = np.unique(featuresInt[:, 0], return_index=True)
    valuesSplit = np.split(dsc, idx[1:])
    dscPerPost = []
    for values in valuesSplit:
        dscPerPost.append(np.sum(values))
    return np.array(postIds), np.array(dscPerPost)


def computeTileData(props, request):
    util_time.startTimer("computeTileData")
    #configuration = request["configuration"]
    attributeParameters = request["attributeParameters"]
    tiles = request["tiles"]
    #print("config", configuration)
    #print("attributeParameters", attributeParameters)
    # print("")
    tileData = []
    print("num tiles", len(tiles))
    for tileName, tileProps in tiles.items():
        selectionString = tileProps["selectionString"]
        tileResponse = computeSingleTile(
            props, tileName, tileProps, attributeParameters)
        tileResponse["selectionString"] = selectionString
        tileData.append(tileResponse)
    util_time.writeTimer("computeTileData")
    return {
        "tiles": tileData
    }

def normEmbedding(a):
    minx = np.min(a[:,0])
    maxx = np.max(a[:,0])
    a[:,0] = (a[:,0] - minx) / (maxx - minx)
    miny = np.min(a[:,1])
    maxy = np.max(a[:,1])
    a[:,1] = (a[:,1] - miny) / (maxy - miny)


def cluster(props, request):
    return None
    """
    util_time.startTimer("cluster")    
    attributeParameters = request["attributeParameters"]
    tiles = request["tiles"]
    
    tileData = {}
    print("num tiles cluster", len(tiles))

    clusterData = []
    selectionStrings = []

    for tileName, tileProps in tiles.items():
        selectionString = tileProps["selectionString"]
        
        tileKey = matrix_server_filter.getTileKey(props, tileProps)
        if(tileKey in props["tileCache"]):
            channel1 = util_stats.evalHistogramMaxNonempty(props["tileCache"][tileKey]["computeState"]["cp_null_model_distribution"])
            channel2 = util_stats.evalHistogramMaxNonempty(props["tileCache"][tileKey]["computeState"]["cp_modified_model_distribution"])

            if(channel1 is not None):
                clusterData.append(channel1)        
                selectionStrings.append(selectionString)                
    
    clusterDataNp = np.array(clusterData)
    print("cluster data shape", clusterDataNp.shape)
    canCluster = clusterDataNp.shape[0] > 8
    if(canCluster):
        reducer = umap.UMAP(n_neighbors=5, min_dist=0.1)
        print("start embedding")
        embedding = reducer.fit_transform(clusterDataNp)
        print("finish embedding")
        labels = hdbscan.HDBSCAN(min_samples=1, min_cluster_size=5).fit_predict(embedding)
        normEmbedding(embedding)
        tileData["embedding"] = embedding.tolist()
        tileData["selectionStrings"] = selectionStrings
        tileData["labels"] = labels.tolist()

    tileData["canCluster"] = canCluster
    

    util_time.writeTimer("cluster")
    return {
        "tiles": tileData
    """



def edit(props, request):
    selection = request["selection"]
    tileProps = {
        "selection": selection
    }
    tileKey = matrix_server_filter.getTileKey(props, tileProps)
    channelName = request["channelName"]
    if(channelName not in props["constants"].keys()):
        return
    else:
        value = request["newValue"]
        props["constants"][channelName][tileKey] = value
        print("constants after edit", props["constants"][channelName])
        resetModifiedModel(props)


def resetModifiedModel(props):
    for tileData in props["tileCache"].values():
        tileData["computeState"]["resetAfterEdit"] = True


def resetEdits(props):
    loadConstants(props)
    resetModifiedModel(props)


def initTile(props, tileProps, tileKey, attributeParameters):
    #print("init tile")
    # print(tileProps)
    # print(tileKey)
    tileData = {}
    if(attributeParameters is not None):
        computeConstants(props, tileData, tileKey, attributeParameters)

    maskPre = matrix_server_filter.getFilterMask(props["rows"], tileKey[0])
    mappedIds, duplicities = np.unique(
        props["rows"][maskPre, 3], return_counts=True)
    tileData["computeState"] = {
        "uniquePre": mappedIds,
        "duplicities": duplicities,
        "dsc_null_model": [],
        "dsc_null_model_sum": 0,
        "cp_null_model": [],
        "cp_null_model_sum": 0,
        "cp_null_model_distribution" : util_stats.getEmptyFixedHistogram(25,1),
        "n_pairs_null": 0,
        "dsc_modified_model": [],
        "dsc_modified_model_sum": 0,
        "cp_modified_model": [],
        "cp_modified_model_sum": 0,
        "cp_modified_model_distribution" : util_stats.getEmptyFixedHistogram(25,1),
        "n_pairs_modified": 0,
        "resetAfterEdit": False
    }

    progress = 0
    if(not len(mappedIds)):
        progress = 1

    tileData["DSC_null_model"] = [0, progress]
    tileData["CP_null_model"] = [0, progress]
    tileData["DSC_modified_model"] = [0, progress]
    tileData["CP_modified_model"] = [0, progress]

    return tileData


def getResponseData(tileData):
    return {
        "CP_empirical": tileData["CP_empirical"],
        "bouton_weight_modified_model": tileData["bouton_weight_modified_model"],
        "DSC_null_model": tileData["DSC_null_model"],
        "CP_null_model": tileData["CP_null_model"],
        "DSC_modified_model": tileData["DSC_modified_model"],
        "CP_modified_model": tileData["CP_modified_model"]
    }


def computeSingleTile(props, tileName, tileProps, attributeParameters):
    tileResponse = {}
    tileResponse["name"] = tileName
    tileData = {}
    tileKey = matrix_server_filter.getTileKey(props, tileProps)
    if(tileKey not in props["tileCache"]):
        props["tileCache"][tileKey] = initTile(
            props, tileProps, tileKey, attributeParameters)
    tileData = props["tileCache"][tileKey]
    computeConnectivityNull(props, tileData, tileKey)
    computeConnectivityModified(props, tileData, tileKey)
    computeConstants(props, tileData, tileKey, attributeParameters)
    tileResponse["data"] = getResponseData(tileData)
    return tileResponse


def getDistribution(props, tileProps):
    tileKey = matrix_server_filter.getTileKey(props, tileProps)
    if(tileKey not in props["tileCache"]):
        return {
            "channel1" : [],
            "channel2" : [],
        }
    else:
        channel1 = util_stats.evalHistogramMax(props["tileCache"][tileKey]["computeState"]["cp_null_model_distribution"])
        channel2 = util_stats.evalHistogramMax(props["tileCache"][tileKey]["computeState"]["cp_modified_model_distribution"])
        return {
            "channel1" : channel1,
            "channel2" : channel2
        }

def getProbability(dsc):
    return 1-np.exp(-dsc)


def appendConnectivityNullModel(tileData, dsc, prob, nPre, nPost):
    tileData["computeState"]["dsc_null_model"].append(np.mean(dsc))
    tileData["computeState"]["cp_null_model"].append(np.mean(prob))
    tileData["computeState"]["n_pairs_null"] += nPre * nPost
    tileData["computeState"]["dsc_null_model_sum"] += np.sum(nPre * dsc)
    tileData["computeState"]["cp_null_model_sum"] += np.sum(nPre * prob)
    for p in prob:
        for k in range(0, nPre):
            util_stats.updateHistogram(tileData["computeState"]["cp_null_model_distribution"], p)



def setResponseDataNullModel(tileData):
    nUnique = len(tileData["computeState"]["uniquePre"])
    progress = len(tileData["computeState"]["dsc_null_model"]) / nUnique
    dsc = tileData["computeState"]["dsc_null_model_sum"]
    cp = tileData["computeState"]["cp_null_model_sum"]
    nPairs = tileData["computeState"]["n_pairs_null"]
    if(nPairs == 0):
        dscMean = 0
        cpMean = 0
    else:
        dscMean = dsc/nPairs
        cpMean = cp/nPairs
    tileData["DSC_null_model"] = [dscMean, progress]
    tileData["CP_null_model"] = [cpMean, progress]


def appendConnectivityModifiedModel(tileData, dsc, prob, nPre, nPost):
    tileData["computeState"]["dsc_modified_model"].append(np.mean(dsc))
    tileData["computeState"]["cp_modified_model"].append(np.mean(prob))
    tileData["computeState"]["n_pairs_modified"] += nPre * nPost
    tileData["computeState"]["dsc_modified_model_sum"] += np.sum(nPre * dsc)
    tileData["computeState"]["cp_modified_model_sum"] += np.sum(nPre * prob)
    for p in prob:
        for k in range(0, nPre):
            util_stats.updateHistogram(tileData["computeState"]["cp_modified_model_distribution"], p)


def setResponseDataModifiedModel(tileData):
    nUnique = len(tileData["computeState"]["uniquePre"])
    progress = len(tileData["computeState"]["dsc_modified_model"]) / nUnique
    dsc = tileData["computeState"]["dsc_modified_model_sum"]
    cp = tileData["computeState"]["cp_modified_model_sum"]
    nPairs = tileData["computeState"]["n_pairs_modified"]
    if(nPairs == 0):
        dscMean = 0
        cpMean = 0
    else:
        dscMean = dsc/nPairs
        cpMean = cp/nPairs
    tileData["DSC_modified_model"] = [dscMean, progress]
    tileData["CP_modified_model"] = [cpMean, progress]


def computeConnectivityNull(props, tileData, tileKey):
    k = len(tileData["computeState"]["dsc_null_model"])
    nUnique = len(tileData["computeState"]["uniquePre"])
    if(not nUnique):
        return
    if(k >= nUnique):
        return
    maskPost = matrix_server_filter.getFilterMask(props["cols"], tileKey[1])
    postIds = props["cols"][maskPost, 0]
    mappedId = tileData["computeState"]["uniquePre"][k]
    duplicity = tileData["computeState"]["duplicities"][k]
    if(mappedId not in props["featuresInt"].keys()):
        appendConnectivityNullModel(
            tileData, [0], [0], duplicity, len(postIds))
    else:
        featuresInt = props["featuresInt"][mappedId]
        featuresFloat = props["featuresFloat"][mappedId]
        maskSubcellular = matrix_server_filter.getFilterMask(
            featuresInt, tileKey[2])
        featuresIntPruned = featuresInt[maskSubcellular, :]
        featuresFloatPruned = featuresFloat[maskSubcellular]
        postIdsAll, dscAll = computeDSCPerPost(
            featuresIntPruned, featuresFloatPruned)
        if(not postIdsAll.shape[0]):
            appendConnectivityNullModel(
                tileData, [0], [0], duplicity, len(postIds))
        else:
            shared, idx1, idx2 = np.intersect1d(
                postIdsAll, postIds, assume_unique=True, return_indices=True)
            if(not shared.shape[0]):
                appendConnectivityNullModel(
                    tileData, [0], [0], duplicity, len(postIds))
            else:
                dsc = dscAll[idx1]
                probability = getProbability(dsc)
                appendConnectivityNullModel(
                    tileData, dsc, probability, duplicity, len(postIds))
    setResponseDataNullModel(tileData)


def copyNullModel(tileData):
    computeState = tileData["computeState"]
    computeState["dsc_modified_model"] = computeState["dsc_null_model"].copy()
    computeState["dsc_modified_model_sum"] = computeState["dsc_null_model_sum"]
    computeState["cp_modified_model"] = computeState["cp_null_model"].copy()
    computeState["cp_modified_model_sum"] = computeState["cp_null_model_sum"]
    computeState["cp_modified_model_distribution"] = computeState["cp_null_model_distribution"].copy()
    computeState["n_pairs_modified"] = computeState["n_pairs_null"]


def computeConnectivityModified(props, tileData, tileKey):
    if(tileData["computeState"]["resetAfterEdit"]):
        tileData["computeState"]["dsc_modified_model"] = []
        tileData["computeState"]["dsc_modified_model_sum"] = 0
        tileData["computeState"]["cp_modified_model"] = []
        tileData["computeState"]["cp_modified_model_sum"] = 0
        tileData["computeState"]["cp_modified_model_distribution"] = util_stats.getEmptyFixedHistogram(25,1)
        tileData["computeState"]["n_pairs_modified"] = 0
        tileData["computeState"]["resetAfterEdit"] = False
    k = len(tileData["computeState"]["dsc_modified_model"])
    nUnique = len(tileData["computeState"]["uniquePre"])
    if(not nUnique):
        return
    if(k >= nUnique):
        return
    maskPost = matrix_server_filter.getFilterMask(props["cols"], tileKey[1])
    postIds = props["cols"][maskPost, 0]
    mappedId = tileData["computeState"]["uniquePre"][k]
    duplicity = tileData["computeState"]["duplicities"][k]
    if(mappedId not in props["featuresInt"].keys()):
        appendConnectivityModifiedModel(
            tileData, [0], [0], duplicity, len(postIds))
    else:
        rules = matrix_server_rules.getRulesForConnectivity(props, tileKey)
        if(len(rules) > 1):
            print(tileKey, rules)
            featuresInt = props["featuresInt"][mappedId]
            featuresFloat = props["featuresFloat"][mappedId]
            maskSubcellular = matrix_server_filter.getFilterMask(
                featuresInt, tileKey[2])
            featuresIntPruned, featuresFloatModified = applyRulesToFeatures(
                featuresInt, featuresFloat, maskSubcellular, props, rules)
            postIdsAll, dscAll = computeDSCPerPost(
                featuresIntPruned, featuresFloatModified)
            if(not postIdsAll.shape[0]):
                appendConnectivityModifiedModel(
                    tileData, [0], [0], duplicity, len(postIds))
            else:
                shared, idx1, idx2 = np.intersect1d(
                    postIdsAll, postIds, assume_unique=True, return_indices=True)
                if(not shared.shape[0]):
                    appendConnectivityModifiedModel(
                        tileData, [0], [0], duplicity, len(postIds))
                else:
                    dsc = dscAll[idx1]
                    probability = getProbability(dsc)
                    appendConnectivityModifiedModel(
                        tileData, dsc, probability, duplicity, len(postIds))
        else:
            copyNullModel(tileData)
    setResponseDataModifiedModel(tileData)


def applyRulesToFeatures(featuresInt, featuresFloat, maskSubcellular, props, rules):
    featuresIntPruned = featuresInt[maskSubcellular, :]
    featuresFloatPruned = featuresFloat[maskSubcellular]
    featuresFloatModified = np.copy(featuresFloatPruned)
    for ruleKey in rules:
        mask = matrix_server_filter.getFilterMask(
            featuresIntPruned, ruleKey[2])
        value = props["constants"]["bouton_weight_modified_model"][ruleKey]
        if(value != 1):
            print("value >>", value)
            featuresFloatModified[mask] = value * featuresFloatPruned[mask]
    return featuresIntPruned, featuresFloatModified


def computeConstants(props, tileData, tileKey, attributeParameters):
    constants = props["constants"]
    tileData["CP_empirical"] = computeConstant(
        props, tileKey, constants["CP_empirical"], attributeParameters, True)
    tileData["bouton_weight_modified_model"] = computeConstant(
        props, tileKey, constants["bouton_weight_modified_model"], attributeParameters, False)


def computeConstant(props, tileKey, channel, attributeParameters, exactMatch):
    value = matrix_server_rules.getConstant(props,
                                            tileKey, channel, attributeParameters["rows"]["attributeNames"], attributeParameters["cols"]["attributeNames"], exactMatch)
    if(value is None):
        return [0, -1]
    else:
        return [value, 1]


def printUsageAndExit():
    print("python matrix_server_calculator.py data-dir request.json")
    exit()


if __name__ == "__main__":
    if(len(sys.argv) != 3):
        printUsageAndExit()
    dataDir = sys.argv[1]
    requestFile = sys.argv[2]
    props = {}
    init(props, dataDir)
    #request = loadJson(requestFile)
    request = matrix_server_test.getTestRequest()
    response = computeTileData(props, request)
    print(response)

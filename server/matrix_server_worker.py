import os
import json
import numpy as np

"""
import util
import util_selection
import util_meta
import util_filter
import util_time
import util_matrix
import matrix_server_constants
import matrix_server_annotations
"""

def loadJson(filename):
    with open(filename) as f:
        return json.load(f)


def init(props, dataDir):
    props["matrixDataDir"] = dataDir        
    props["profiles"] = loadJson(os.path.join(props["matrixDataDir"], metaFile))

"""
def filterNeurons(props, selection):
    util_time.startTimer("filter neurons")
    isSlice = False
    filtersPre = util_selection.getSelectionFilters(selection, "A", isSlice, props["selectionsDir"], presynaptic=True)
    print("filterPre", filtersPre)
    filtersPost = util_selection.getSelectionFilters(selection, "B", isSlice, props["selectionsDir"])
    preIds = util_filter.filterNeurons(props["neurons"], filtersPre, idsOnly=True)
    postIds = util_filter.filterNeurons(props["neurons"], filtersPost, idsOnly=True)
    util_time.writeTimer("filter neurons")
    return preIds, postIds


def sortAndFilter(props, preIds, postIds, orderRows, orderCols):
    props["orderRows"] = orderRows
    props["orderCols"] = orderCols
    util_time.startTimer("sort and filter rows/cols")
    rowsSorted = np.sort(props["rowsMeta"], order=orderRows, axis=0)
    colsSorted = np.sort(props["colsMeta"], order=orderCols, axis=0)
    props["rowsMetaSorted"] = rowsSorted
    props["colsMetaSorted"] = colsSorted
    props["rowsMetaSortedFiltered"] = getFilteredArray(rowsSorted, preIds)    
    props["colsMetaSortedFiltered"] = getFilteredArray(colsSorted, postIds)
    util_time.writeTimer("sort and filter rows/cols")


def getFilteredArray(sortedTuples, allowedIds):    
    filtered = []
    for t in sortedTuples:
        if(t[0]) in allowedIds:
            filtered.append(list(t))
    return np.asarray(filtered)


def fillIndexCache(cache, partitions):
    for i in range(0, len(partitions)):
        for k in range(0, partitions[i].shape[0]):
            row = partitions[i][k, :]
            cache[(row[0], row[1])] = i


def fillValues(S, synapses, cacheRows, cacheCols):
    rowKeys = set(cacheRows.keys())
    colKeys = set(cacheCols.keys())
    for k in range(0, synapses.shape[0]):
        rowKey = (synapses[k, 0], synapses[k, 2])
        colKey = (synapses[k, 1], synapses[k, 2])
        if(rowKey in rowKeys and colKey in colKeys):
            S[cacheRows[rowKey], cacheCols[colKey]] += synapses[k, 3]


def fillCubeCache(n, indexCache):
    C = {}
    for i in range(0,n):
        C[i] = set()
    for key, index in indexCache.items():
        cubeId = key[1]
        C[index].add(cubeId)
    return C

def getSelectedCubes(props, indices):
    if("cacheRowsCube" not in props.keys() or "cacheColsCube" not in props.keys()):
        print("a")
        return []
    i = indices[0]
    j = indices[1]
    if(i >= props["n"] or j >= props["n"]):
        print("b")
        return []
    return list(props["cacheRowsCube"][i] | props["cacheColsCube"][j])
    

def computeMatrix(props):
    n = props["n"]
    util_time.startTimer("compute matrix n={}".format(n))
    if("rowsMetaSortedFiltered" not in props.keys() or "colsMetaSortedFiltered" not in props.keys()):
        print("missing")
    rows = props["rowsMetaSortedFiltered"]
    cols = props["colsMetaSortedFiltered"]   
    if(rows.shape[0] < n or cols.shape[0] < n):
        print("n={} too large for rows ({}) or cols ({})".format(n, rows.shape[0], cols.shape[0]))
    rowsPart = np.array_split(rows, n)
    colsPart = np.array_split(cols, n)
    cacheRows = {}
    cacheCols = {}
    fillIndexCache(cacheRows, rowsPart)
    fillIndexCache(cacheCols, colsPart)
    
    props["cacheRowsCube"] = fillCubeCache(n, cacheRows)
    props["cacheColsCube"] = fillCubeCache(n, cacheCols)
    

    S1 = np.zeros(shape=(n, n), dtype=float)
    fillValues(S1, props["synapsesNull"], cacheRows, cacheCols)
   
    S2 = np.zeros(shape=(n, n), dtype=float)
    fillValues(S2, props["synapsesRule"], cacheRows, cacheCols)
    
    SD = S2-S1

    S1 = normalize(S1)        
    props["S1"] = S1
    S2 = normalize(S2)        
    props["S2"] = S2
    SD = normalizeSigned(SD)
    props["SD"] = SD

    print("delta norm", np.max(S2-S1))
    
    props["rowAnnotations"] = matrix_server_annotations.getAnnotationProps(props, rowsPart, props["orderRows"])    
    props["colAnnotations"] = matrix_server_annotations.getAnnotationProps(props, colsPart, props["orderCols"])
    print(props["rowAnnotations"])
    util_time.writeTimer("compute matrix n={}".format(n))    

def normalize(S):
    maxVal = S.max()
    if(maxVal > 0):
        S = 1/maxVal * S
    np.round(S, 2)
    return S

def normalizeSigned(S):
    np.round(S,2)
    minVal = S.min()
    if(minVal < 0):
        S[S<0] = -1/minVal*(S[S<0])
    maxVal = S.max()
    if(maxVal > 0):
        S[S>0] = 1/maxVal*(S[S>0])
    return S


def sampleMatrix(props):
    if("sortFilteredRowIds" not in props.keys()):
        return
    n = props["n"]
    numSamples = 1
    preIds = props["sortFilteredRowIds"]
    postIds = props["sortFilteredColIds"]
    preIdsPart = np.array_split(preIds, n)
    postIdsPart = np.array_split(postIds, n)
    postIdsSets = util_matrix.getPostIdsSet(postIdsPart)

    util_time.startTimer("sample")
    S = np.zeros(shape=(n, n), dtype=int)
    if("S" not in props.keys()):
        props["S"] = np.zeros(shape=(n, n), dtype=int)
    util_matrix.sample(props["matrixDataDir"], preIdsPart, postIdsSets, S, numSamples)
    util_time.writeTimer("sample")
    props["S"] = props["S"] + S


def resetMatrix(props):
    if("S1" in props.keys()):
        del props["S1"]
    if("S2" in props.keys()):
        del props["S2"]
    if("SD" in props.keys()):
        del props["SD"]


def getTiles(props):

    meta = {
        "rows": props["n"],
        "cols": props["n"],
        "rowAnnotations" : props["rowAnnotations"],
        "colAnnotations" : props["colAnnotations"]
    }

    if("S1" not in props.keys() or "S2" not in props.keys() or "SD" not in props.keys()):
        n = props["n"]
        S1 = np.zeros(shape=(n, n), dtype=int)
        S2 = np.zeros(shape=(n, n), dtype=int)
        SD = np.zeros(shape=(n, n), dtype=int)
        return S1.tolist(), S2.tolist, SD.tolist(), meta
    else:
        S1 = props["S1"].copy()        
        S2 = props["S2"].copy()
        SD = props["SD"].copy()        
        return S1.tolist(), S2.tolist(), SD.tolist(), meta



if __name__ == "__main__":
    props = {}
    init(props)

    with open("/tmp/filterSpec.json") as f:
        selection = json.load(f)

    preIds, postIds = filterNeurons(props, selection)
    print("filteredIds", len(preIds), len(postIds))
    orderRows = matrix_server_constants.getDefaultOrder("comparisonInference")
    orderCols = orderRows
    sortAndFilter(props, preIds, postIds, orderRows, orderCols)
    computeMatrix(props)
"""

import os
import shutil
import json
import numpy as np


def makeCleanDir(dirname):
    if(os.path.exists(dirname)):
        shutil.rmtree(dirname, ignore_errors=False, onerror=None)
    os.mkdir(dirname)


def makeDir(dirname):
    if(not os.path.exists(dirname)):
        os.mkdir(dirname)


def loadJson(filename):
    with open(filename) as f:
        return json.load(f)


def getHeaderCols(filename, delimiter=","):
    with open(filename) as f:
        headerLine = f.readline()
        return headerLine.rstrip().split(delimiter)


def printDataRange(name, dataColumn, invalidValue = None):
    if(invalidValue is None):
        filterMask = np.ones(dataColumn.size, dtype=bool)
    else:
        filterMask = dataColumn != invalidValue
    print(name, np.min(dataColumn[filterMask]), np.max(dataColumn[filterMask]))


def printQuantiles(name, dataVector):
    print(name,np.quantile(dataVector, [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]))


def printDataRangeCategorical(name, dataColumn):
    uniqueValues = np.unique(dataColumn)
    print(name, uniqueValues)


def assertMaskConsistency(bins, lenDataColumn):
    count = 0
    for bin in bins:
        count += np.count_nonzero(bin["mask"])
    assert count == lenDataColumn


def writeBins(baseFolder, propertyName, bins, displayName=None, selectionProperties = None):
    targetFolder = os.path.join(baseFolder, propertyName)
    makeCleanDir(targetFolder)
    values = []
    for bin in bins:
        filename = os.path.join(targetFolder, bin["value"])
        np.savetxt(filename, bin["mask"].astype(int), fmt="%d")
        values.append(bin["value"])
    meta = {
        "name" : propertyName,
        "values" : values,
        "property_type" : "categorical"
    }
    if(displayName is not None):
        meta["display_name"] = displayName
    metaFile = os.path.join(targetFolder, "meta.json")
    with open(metaFile, "w") as f:
        json.dump(meta, f)
    if(selectionProperties is not None):
        selectionProperties.append(meta)
    

def binCategoricalAttributes(dataColumn, values, valueId_value, isArrayData = False):
    value_mask = {}
    if(isArrayData):
        lenDataColumn = len(dataColumn)
    else:
        lenDataColumn = dataColumn.size

    for value in values:            
        value_mask[value] = np.zeros(lenDataColumn, dtype=bool)
    
    for i in range(0, lenDataColumn):
        valueId = dataColumn[i]
        value = valueId_value[valueId]
        value_mask[value][i] = True

    bins = []
    for value in values:
        bins.append({
            "value" : value,
            "mask" : value_mask[value]
        })

    assertMaskConsistency(bins, lenDataColumn)
    return bins


def binTags(data, values, id_value, na_id):
    n = len(data)
    value_mask = {}
    for value in values:
        value_mask[value] = np.zeros(n, dtype=bool)
    
    for i in range(0, n):
        tags = data[i]
        assigned = False
        for tag in tags:
            if(tag in id_value):
                value_mask[id_value[tag]][i] = True
                assigned = True
        if(not assigned):
            value_mask[id_value[na_id]][i] = True

    bins = []
    for value in values:
        bins.append({
            "value" : value,
            "mask" : value_mask[value]
        })
    return bins  

def binNumericAttributes(dataColumn, firstBinStartValue, lastBinStartValue, step):
    bins = [] 
    currentStartValue = firstBinStartValue
    mask_binned = np.zeros(dataColumn.size, dtype=bool)
    while(currentStartValue <= lastBinStartValue):        
        currentEndValue = currentStartValue + step
        mask_current = (dataColumn > currentStartValue) & (dataColumn <= currentEndValue)
        mask_binned |= mask_current        
        bins.append({
            "value" : "{}".format(currentEndValue),
            "mask" : mask_current            
        })
        currentStartValue = currentEndValue
    bins.append({
        "value" : "other",
        "mask" : ~mask_binned
    })

    assertMaskConsistency(bins, dataColumn.size)
    return bins


def getBinsFromQuantiles(dataVector, numQuantiles):
    bins = []
    for k in range(0,numQuantiles):
        a = np.quantile(dataVector, k / numQuantiles)
        if(k==0):
            a -=1 
        b = np.quantile(dataVector, (k+1) / numQuantiles)
        bins.append((a,b))
    return bins 


def getBinsFromFixedQuantiles(dataVector, quantiles):
    bins = []
    for k in range(0,len(quantiles)):        
        if(k==0):
            a =-1
        else:
            a = np.quantile(dataVector,quantiles[k-1])
        b = np.quantile(dataVector, quantiles[k])
        bins.append((a,b))
    return bins 


def getBinBounds(startValue, numBins, step):
    bounds = []
    for i in range(0,numBins):
        a = startValue + i * step
        b = a + step
        bounds.append((a,b))
    return bounds


def binNumericAttributesFixedBins(dataColumn, binBounds):
    # (a,b] start exclusive, end inclusive
    bins = []     
    mask_binned = np.zeros(dataColumn.size, dtype=bool)
    for binBound in binBounds:               
        mask_current = (dataColumn > binBound[0]) & (dataColumn <= binBound[1])
        mask_binned |= mask_current        
        bins.append({
            "value" : "{:.0f}".format(binBound[1]),
            "mask" : mask_current            
        })
    bins.append({
        "value" : "other",
        "mask" : ~mask_binned
    })

    assertMaskConsistency(bins, dataColumn.size)
    return bins


def getRandomSubset(itemSet, n, sortBeforeShuffle = False):
    if(n >= len(itemSet)):
        return itemSet

    array = list(itemSet)
    if(sortBeforeShuffle):
        array.sort()
    np.random.shuffle(array)
    return set(array[0:n]) 


def convertIntFormat(items):
    converted = []
    for item in items:
        converted.append(int(item))
    return converted


def writeMeta(filename, selectionProperties, channels, options = {}):
    meta = {
        "options" : options,
        "channels" : channels,
        "selection_properties" : selectionProperties
    }
    with open(filename,"w") as f:
        json.dump(meta, f)

def revertDict(dictIn):
    return dict((v,k) for k,v in dictIn.items())
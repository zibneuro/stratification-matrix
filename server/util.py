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


def getHeaderCols(filename):
    with open(filename) as f:
        headerLine = f.readline()
        return headerLine.rstrip().split(",")


def printDataRange(name, dataColumn, invalidValue = None):
    if(invalidValue is None):
        filterMask = np.ones(dataColumn.size, dtype=bool)
    else:
        filterMask = dataColumn != invalidValue
    print(name, np.min(dataColumn[filterMask]), np.max(dataColumn[filterMask]))


def printDataRangeCategorical(name, dataColumn):
    uniqueValues = np.unique(dataColumn)
    print(name, uniqueValues)


def assertMaskConsistency(dataColumn, bins):
    count = 0
    for bin in bins:
        count += np.count_nonzero(bin["mask"])
    assert count == dataColumn.size


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
    

def binCategoricalAttributes(dataColumn, values, valueId_value):
    value_mask = {}
    for value in values:
        value_mask[value] = np.zeros(dataColumn.size, dtype=bool)

    for i in range(0, dataColumn.size):
        valueId = dataColumn[i]
        value = valueId_value[valueId]
        value_mask[value][i] = True

    bins = []
    for value in values:
        bins.append({
            "value" : value,
            "mask" : value_mask[value]
        })

    assertMaskConsistency(dataColumn, bins)
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

    assertMaskConsistency(dataColumn, bins)
    return bins



    
import numpy as np
import random

def getTileKey(props, tileProps):
    orderInfo = props["attributeInfoOrder"]
    key = [[], [], []]
    rowSelection = tileProps["selection"]["presynaptic"]
    colSelection = tileProps["selection"]["postsynaptic"]
    for name in orderInfo["rows"]:
        if(name in rowSelection.keys()):
            key[0].append(props["attributeInfoRows"][name][rowSelection[name]])
        else:
            key[0].append(-1)
    for name in orderInfo["cols"]:
        if(name in colSelection.keys()):
            key[1].append(props["attributeInfoCols"][name][colSelection[name]])
        else:
            key[1].append(-1)
    for name in orderInfo["subcellular"]:
        if(name in rowSelection.keys()):
            key[2].append(props["attributeInfoSubcellular"]
                          [name][rowSelection[name]])
        elif(name in colSelection.keys()):
            key[2].append(props["attributeInfoSubcellular"]
                          [name][colSelection[name]])
        else:
            key[2].append(-1)
    return (tuple(key[0]), tuple(key[1]), tuple(key[2]))


def getRandomValue(nameValue):
    values = list(nameValue.values())
    return values[random.randrange(0,len(values))]


def getRandomTileKey(props, sampleCategories):
    orderInfo = props["attributeInfoOrder"]
    key = [[], [], []]
    rowSelection = sampleCategories["presynaptic"]
    colSelection = sampleCategories["postsynaptic"]
    subcellularSelection = sampleCategories["subcellular"]
    for name in orderInfo["rows"]:
        if(name in rowSelection):
            key[0].append(getRandomValue(props["attributeInfoRows"][name]))
        else:
            key[0].append(-1)
    for name in orderInfo["cols"]:
        if(name in colSelection):
            key[1].append(getRandomValue(props["attributeInfoCols"][name]))
        else:
            key[1].append(-1)
    for name in orderInfo["subcellular"]:
        if(name in subcellularSelection):
            key[2].append(getRandomValue(props["attributeInfoSubcellular"][name]))
        else:        
            key[2].append(-1)
    return (tuple(key[0]), tuple(key[1]), tuple(key[2]))


def getWildcardTileKey(props):
    selection = {
        "presynaptic": {},
        "postsynaptic": {}
    }
    tileProps = {
        "selection": selection
    }
    return getTileKey(props, tileProps)


def getFilterMask(data, key):
    m = np.ones(data.shape[0], dtype=bool)
    for k in range(0, len(key)):
        value = key[k]
        if(value != -1):
            m &= data[:, k] == value
    return m


def areCompatibleSingle(key1, key2):
    if(len(key1) != len(key2)):
        raise RuntimeError()
    for i in range(0, len(key1)):
        if(key1[i] != -1 and key2[i] != -1 and key1[i] != key2[i]):
            return False
    return True


def areCompatible(key1, key2):
    return areCompatibleSingle(key1[0], key2[0]) and areCompatibleSingle(key1[1], key2[1]) and areCompatibleSingle(key1[2], key2[2])


def getDistanceSingle(key1, key2):
    if(len(key1) != len(key2)):
        raise RuntimeError()
    d = 0
    for i in range(0, len(key1)):
        if(key1[i] == key2[i]):
            d += 1
    return d

def getDistance(key1, key2):
    return getDistanceSingle(key1[0], key2[0]) + getDistanceSingle(key1[1], key2[1]) + getDistanceSingle(key1[2], key2[2])

def getSingleKeyAsString(key):
    a = []
    for i in range(0, len(key)):
        a.append(str(key[i]))
    return ",".join(a)

def getKeyAsString(key):
    return "({},{},{})".format(getSingleKeyAsString(key[0]),getSingleKeyAsString(key[1]),getSingleKeyAsString(key[2]))
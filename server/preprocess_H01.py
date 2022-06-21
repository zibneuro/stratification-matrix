from re import L
import sys
import os
import json
from types import CellType
import numpy as np

import util 

def printUsageAndExit():
    print("python preprocess_H01.py data-folder")
    exit()
    

def getNeuronProperties(filename, propertyName):    
    propertiesFile = os.path.join(filename)
    with open(propertiesFile) as f:
        properties = json.load(f)
    propertyIdx = {}
    for i in range(0, len(properties["inline"]["properties"])):
        propName = properties["inline"]["properties"][i]["id"]
        #print(i, propName)
        propertyIdx[propName] = i

    tags_all = properties["inline"]["properties"][propertyIdx["tags"]]["tags"]    
    values_all = properties["inline"]["properties"][propertyIdx[propertyName]]["values"]    
    ids_all = properties["inline"]["ids"]
        
    return ids_all, tags_all, values_all


def splitTagDataColumns(dataColumn):
    n = len(dataColumn)    
    col1 = np.zeros(n, dtype=int)
    col2 = np.zeros(n, dtype=int)
    col3 = np.zeros(n, dtype=int)
    for i in range(0,n):
        col1[i] = dataColumn[i][0]
        col2[i] = dataColumn[i][1]
        #col3[i] = dataColumn[i][2]
    return col1, col2, col3


def relabelTagValues(values_tags):
    relabelled = []
    for value in values_tags:
        valueNew = value.replace("microglia/opc", "microglia-opc").replace("excitatory/spiny-with-atypical-tree","spiny-with-atypical-tree")
        relabelled.append(valueNew)
    return relabelled


def getTagIdValue(values_tags):
    id_value = {}
    for i in range(0, len(values_tags)):
        id_value[i] = values_tags[i]
    return id_value


def getLayer():
    """
    0 L1
    1 L2
    2 L3
    3 L4
    4 L5
    5 L6
    6 WM
    7 layer-unclassified
    """
    values = ["L1","L2","L3","L4","L5","L6","WM","na"]
    id_value = {
        0 : "L1",
        1 : "L2",
        2 : "L3",
        3 : "L4",
        4 : "L5",
        5 : "L6",
        6 : "WM",
        7 : "na",
    }
    return values, id_value, 7


def getCelltype():
    """
    8 unknown-type
    10 neuron
    14 glial
    18 blood-vessel-cell
    """
    values = ["neuron", "glial", "blood-vessel", "na"]
    id_value = {        
        8: "na",
        10: "neuron",
        14: "glial",
        18: "blood-vessel"
    }
    return values, id_value, 8


def getNeuronAnnotation():
    """
    9. pyramidal     
    11. interneuron
    12. unclassified-neuron
    19. spiny-stellate
    20. excitatory/spiny-with-atypical-tree
    21. thin-apical-dendrite
    22. bipolar
    23. inverted-apical-dendrite
    24. unusually-thin-dendrites
    25. sparsely-spiny
    26. lots-of-spines
    27. possible-interneuron
    28. web-like-interneuron
    29. lot-of-axon    
    """
    values = ["pyramidal", "interneuron", "spiny-stellate", "spiny-with-atypical-tree", "bipolar", 
        "sparsely-spiny", "lots-of-spines", "possible-interneuron", "web-like-interneuron", "lot-of-axon", "thin-apical-dendrite", 
        "inverted-apical-dendrite", "unusually-thin-dendrites", "na"]
    id_value = {
        9 : "pyramidal",
        11 : "interneuron",
        12: "na",
        19: "spiny-stellate",
        20: "spiny-with-atypical-tree",
        21: "thin-apical-dendrite",
        22: "bipolar",
        23: "inverted-apical-dendrite",
        24: "unusually-thin-dendrites",
        25: "sparsely-spiny",
        26: "lots-of-spines",
        27: "possible-interneuron",
        28: "web-like-interneuron",
        29: "lot-of-axon"
    }    
    return values, id_value, 12


def getGlialAnnotation():
    """
    13 astrocyte
    15 oligodendrocyte
    16 microglia/opc
    17 c-shaped
    30 dark
    31 grey
    """
    values = ["astrocyte", "oligodendrocyte", "microglia-opc", "c-shaped", "dark", "grey", "na"]
    id_value = {
        13: "astrocyte",
        15: "oligodendrocyte",
        16: "microglia-opc",
        17: "c-shaped",
        30: "dark",
        31: "grey",
        32: "na"
    }
    return values, id_value, 32


if __name__ == "__main__":
    if(len(sys.argv) != 2):
        printUsageAndExit()

    dataFolder = sys.argv[1]

    h01BaseFolder = os.path.join(dataFolder, "H01")
    outfolder_channel0 = os.path.join(h01BaseFolder, "channel0")
    util.makeCleanDir(outfolder_channel0)
    propertiesFile = os.path.join(h01BaseFolder, "info")
    samplesFile = os.path.join(h01BaseFolder, "samples0")
    
    ids, _, dataColumn = getNeuronProperties(propertiesFile, "tags")
    ids = util.convertIntFormat(ids)
        
    selection_properties = []

    layer_values, layer_id_value, layer_na = getLayer()
    bins = util.binTags(dataColumn, layer_values, layer_id_value, layer_na)
    util.writeBins(outfolder_channel0, "layer", bins, "layer", selection_properties)

    celltype_values, celltype_id_value, celltype_na = getCelltype()
    bins = util.binTags(dataColumn, celltype_values, celltype_id_value, celltype_na)
    util.writeBins(outfolder_channel0, "cell_type", bins, "cell type", selection_properties)

    neuronAnnotation_values, neuronAnnotation_id_value, neuronAnnotation_na = getNeuronAnnotation()
    bins = util.binTags(dataColumn, neuronAnnotation_values, neuronAnnotation_id_value, neuronAnnotation_na)
    util.writeBins(outfolder_channel0, "neuron_annotation", bins, "neuron annotation", selection_properties)

    otherAnnotation_values, otherAnnotation_id_value, otherAnnotation_na = getGlialAnnotation()
    bins = util.binTags(dataColumn, otherAnnotation_values, otherAnnotation_id_value, otherAnnotation_na)
    util.writeBins(outfolder_channel0, "other_annotation", bins, "misc. annotation", selection_properties)

    """
    1 NVx
    2 NSO
    3 NSI
    4 NSIe
    5 NSIi
    6 NDe
    7 NAx
    8 NSp
    9 NCi
    10 NAis
    11 NMy
    12 Sp
    """

    displayNames = {
        "NVx" : "volume (NVx)",
        "NAx" : "axon nodes (NAx)",
        "NDe" : "dendrite nodes (NDe)",
        "Sp" : "spinyness (Sp)",
        "NSO" : "synapses outgoing (NSO)",
        "NSI" : "synapses incoming (NSI)",
    }
    quantiles = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.91,0.92,0.93,0.94,0.95,0.96,0.97,0.98,0.99,0.992,0.994,0.996,0.998,0.999,1]

    for numericProperty in ["NVx", "NAx", "NDe", "NSO", "NSI"]:
        _, _, dataNumeric = getNeuronProperties(propertiesFile, numericProperty)        
        dataNumeric = np.array(dataNumeric)

        if(numericProperty == "Sp"):
            dataNumeric *=100

        np.savetxt("/tmp/{}".format(numericProperty), dataNumeric)
        bin_bounds = util.getBinsFromFixedQuantiles(dataNumeric, quantiles)
        bins = util.binNumericAttributesFixedBins(dataNumeric, bin_bounds)
        util.writeBins(outfolder_channel0, numericProperty, bins, displayNames[numericProperty], selection_properties)

    filenameMeta = os.path.join(dataFolder, "H01.json")
    channels = [
        {
            "display_name" : "cell count"
        }
    ],
    util.writeMeta(filenameMeta, selection_properties, channels)
    
    np.savetxt(samplesFile, ids, fmt="%d")
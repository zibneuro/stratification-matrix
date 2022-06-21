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
        print(i, propName)
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

    filenameMeta = os.path.join(dataFolder, "H01.json")
    channels = [
        {
            "display_name" : "cell count"
        }
    ],
    util.writeMeta(filenameMeta, selection_properties, channels)
    
    np.savetxt(samplesFile, ids, fmt="%d")

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



    """
    samples_channel0 = synapses_channel0[:,(getColIdx_channel0("pre_id"), getColIdx_channel0("post_id"))].reshape((-1,2))
    np.savetxt(os.path.join(h01BaseFolder, "samples0"), samples_channel0, fmt="%d")
    
    samples_channel1 = synapses_channel1[:,(getColIdx_channel1("pre_id"), getColIdx_channel1("post_id"))].reshape((-1,2))
    np.savetxt(os.path.join(h01BaseFolder, "samples1"), samples_channel1, fmt="%d")

    preIds_channel0 = synapses_channel0[:,getColIdx_channel0("pre_id")].astype(int)
    NAx_channel0 = getNeuronProperties(propertiesFile, preIds_channel0, "NAx")

    preIds_channel1 = synapses_channel1[:,getColIdx_channel1("pre_id")].astype(int)
    NAx_channel1 = getNeuronProperties(propertiesFile, preIds_channel1, "NAx")       
   
    print("ranges synapses empirical")
    util.printDataRangeCategorical("pre celltype", synapses_channel0[:,getColIdx_channel0("pre_celltype")]) 
    util.printDataRangeCategorical("post celltype", synapses_channel0[:,getColIdx_channel0("post_celltype")]) 
    util.printDataRangeCategorical("pre compartment", synapses_channel0[:,getColIdx_channel0("pre_compartment")]) 
    util.printDataRangeCategorical("post compartment", synapses_channel0[:,getColIdx_channel0("post_compartment")]) 
    util.printQuantiles("NAx", NAx_channel0)
    
    selection_properities = []    

    # first channel
    celltype_values, celltype_id_value = getCelltypes()    
    bins_cell_type_pre = util.binCategoricalAttributes(synapses_channel0[:,getColIdx_channel0("pre_celltype")], celltype_values, celltype_id_value)
    util.writeBins(outfolder_channel0, "pre_cell_type", bins_cell_type_pre, "pre cell type", selection_properities)
    bins_cell_type_post = util.binCategoricalAttributes(synapses_channel0[:,getColIdx_channel0("post_celltype")], celltype_values, celltype_id_value)
    util.writeBins(outfolder_channel0, "post_cell_type", bins_cell_type_post, "post cell type", selection_properities)

    layer_values, layer_id_value = getLayers()    
    bins_layer_pre = util.binCategoricalAttributes(synapses_channel0[:,getColIdx_channel0("pre_celltype")], layer_values, layer_id_value)
    util.writeBins(outfolder_channel0, "pre_layer", bins_layer_pre, "pre layer", selection_properities)
    bins_layer_post = util.binCategoricalAttributes(synapses_channel0[:,getColIdx_channel0("post_celltype")], layer_values, layer_id_value)
    util.writeBins(outfolder_channel0, "post_layer", bins_layer_post, "post layer", selection_properities)

    compartment_values, compartment_id_value = getCompartment()
    bins_compartment = util.binCategoricalAttributes(synapses_channel0[:,getColIdx_channel0("post_compartment")], compartment_values, compartment_id_value)
    util.writeBins(outfolder_channel0, "compartment", bins_compartment, "compartment", selection_properities)
    
    bin_bounds_NAx = util.getBinsFromQuantiles(NAx_channel0, 10)
    bins_NAx = util.binNumericAttributesFixedBins(NAx_channel0, bin_bounds_NAx)
    util.writeBins(outfolder_channel0, "NAx", bins_NAx, "axon size", selection_properities)
    
    # second channel        
    bins_cell_type_pre = util.binCategoricalAttributes(synapses_channel1[:,getColIdx_channel1("pre_celltype")], celltype_values, celltype_id_value)
    util.writeBins(outfolder_channel1, "pre_cell_type", bins_cell_type_pre, "pre cell type")
    bins_cell_type_post = util.binCategoricalAttributes(synapses_channel1[:,getColIdx_channel1("post_celltype")], celltype_values, celltype_id_value)
    util.writeBins(outfolder_channel1, "post_cell_type", bins_cell_type_post, "post cell type")

    bins_layer_pre = util.binCategoricalAttributes(synapses_channel1[:,getColIdx_channel1("pre_celltype")], layer_values, layer_id_value)
    util.writeBins(outfolder_channel1, "pre_layer", bins_layer_pre, "pre layer")
    bins_layer_post = util.binCategoricalAttributes(synapses_channel1[:,getColIdx_channel1("post_celltype")], layer_values, layer_id_value)
    util.writeBins(outfolder_channel1, "post_layer", bins_layer_post, "post layer")

    compartment_values, compartment_id_value = getCompartment()
    bins_compartment = util.binCategoricalAttributes(synapses_channel1[:,getColIdx_channel1("post_compartment")], compartment_values, compartment_id_value)
    util.writeBins(outfolder_channel1, "compartment", bins_compartment, "compartment")
        
    bins_NAx = util.binNumericAttributesFixedBins(NAx_channel1, bin_bounds_NAx)
    util.writeBins(outfolder_channel1, "NAx", bins_NAx, "axon size")

    # write meta
    meta = {
        "channels" : [
            {
                "display_name" : "synapse counts empirical"
            },
            {
                "display_name" : "synapse counts model"
            }
        ],
        "selection_properties" : selection_properities
    }
    with open(os.path.join(dataFolder, "H01-synapses.json"),"w") as f:
        json.dump(meta, f)
    """
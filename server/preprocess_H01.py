import sys
import os
import json
import numpy as np

import util 

def printUsageAndExit():
    print("python preprocess_H01.py <data-folder>")    
    exit()


def getCelltypes():
    values = ["PYR", "INTER", "OTHER"]
    id_value = {
        11 : "PYR",
        21 : "PYR",
        31 : "PYR",
        41 : "PYR",
        51 : "PYR",
        61 : "PYR",
        71 : "PYR",
        12 : "INTER",
        22 : "INTER",
        32 : "INTER",
        42 : "INTER",
        52 : "INTER",
        62 : "INTER",
        72 : "INTER",
        13 : "OTHER",
        23 : "OTHER",
        33 : "OTHER",
        43 : "OTHER",
        53 : "OTHER",
        63 : "OTHER",
        73 : "OTHER"
    }    
    return values, id_value


def getLayers():
    values = ["L1", "L2", "L3", "L4", "L5", "L6", "WM"]
    id_value = {
        11 : "L1",
        21 : "L2",
        31 : "L3",
        41 : "L4",
        51 : "L5",
        61 : "L6",
        71 : "WM",
        12 : "L1",
        22 : "L2",
        32 : "L3",
        42 : "L4",
        52 : "L5",
        62 : "L6",
        72 : "WM",
        13 : "L1",
        23 : "L2",
        33 : "L3",
        43 : "L4",
        53 : "L5",
        63 : "L6",
        73 : "WM",
    }    
    return values, id_value


def getCompartment():
    values = ["DENDRITE", "AIS", "SOMA"]
    id_value = {
        2 : "DENDRITE",
        3 : "AIS",
        4 : "SOMA",
    }
    return values, id_value


def getExcInh():
    values = ["exc", "inh"]
    id_value = {
        2 : "exc",
        1 : "inh"
    }
    return values, id_value
    


def getNeuronProperties(filename, neuronIds, propertyName):    
    propertiesFile = os.path.join(filename)
    with open(propertiesFile) as f:
        properties = json.load(f)
    propertyIdx = {}
    for i in range(0, len(properties["inline"]["properties"])):
        propName = properties["inline"]["properties"][i]["id"]
        print(i, propName)
        propertyIdx[propName] = i
    
    values_all = properties["inline"]["properties"][propertyIdx[propertyName]]["values"]    
    ids_all = properties["inline"]["ids"]
  
    id_value = {}
    for i in range(0, len(ids_all)):
        id_value[int(ids_all[i])] = values_all[i]

    values = []
    for neuronId in neuronIds:
        values.append(id_value[neuronId])
    
    return np.array(values)


if __name__ == "__main__":
    if(len(sys.argv) != 2):
        printUsageAndExit()

    dataFolder = sys.argv[1]
    h01Folder = os.path.join(dataFolder, "H01")
    #neuronsFile = os.path.join(visFolder, "somas.csv")
    propertiesFile =  os.path.join(h01Folder, "info")
    synapsesFile = os.path.join(h01Folder, "synapses-classified-neurons.csv")
    
    headerCols = util.getHeaderCols(synapsesFile)    
    print(headerCols)
    def getColIdx(name):
        return headerCols.index(name)

    synapses = np.loadtxt(synapsesFile, skiprows=1, delimiter=",")

    preIds = synapses[:,getColIdx("pre_id")].astype(int)
    NAx = getNeuronProperties(propertiesFile, preIds, "NAx")       
   
    # convert synapse position from nanometer to microns
    synapses[:,getColIdx("x")] *= 0.001
    synapses[:,getColIdx("y")] *= 0.001
    synapses[:,getColIdx("z")] *= 0.001

    print("ranges")
    util.printDataRangeCategorical("pre celltype", synapses[:,getColIdx("pre_celltype")]) 
    util.printDataRangeCategorical("post celltype", synapses[:,getColIdx("post_celltype")]) 
    util.printDataRangeCategorical("pre compartment", synapses[:,getColIdx("pre_compartment")]) 
    util.printDataRangeCategorical("post compartment", synapses[:,getColIdx("post_compartment")]) 
    util.printDataRangeCategorical("exc inh", synapses[:,getColIdx("exc_inh_classification")]) 
    util.printQuantiles("NAx", NAx)

    util.printDataRange("x", synapses[:,getColIdx("x")])
    util.printDataRange("y", synapses[:,getColIdx("y")])
    util.printDataRange("z", synapses[:,getColIdx("z")])
    
    selection_properities = []    

    celltype_values, celltype_id_value = getCelltypes()    
    bins_cell_type_pre = util.binCategoricalAttributes(synapses[:,getColIdx("pre_celltype")], celltype_values, celltype_id_value)
    util.writeBins(h01Folder, "pre_cell_type", bins_cell_type_pre, "pre cell type", selection_properities)
    bins_cell_type_post = util.binCategoricalAttributes(synapses[:,getColIdx("post_celltype")], celltype_values, celltype_id_value)
    util.writeBins(h01Folder, "post_cell_type", bins_cell_type_post, "post cell type", selection_properities)

    layer_values, layer_id_value = getLayers()    
    bins_layer_pre = util.binCategoricalAttributes(synapses[:,getColIdx("pre_celltype")], layer_values, layer_id_value)
    util.writeBins(h01Folder, "pre_layer", bins_layer_pre, "pre layer", selection_properities)
    bins_layer_post = util.binCategoricalAttributes(synapses[:,getColIdx("post_celltype")], layer_values, layer_id_value)
    util.writeBins(h01Folder, "post_layer", bins_layer_post, "post layer", selection_properities)

    compartment_values, compartment_id_value = getCompartment()
    bins_compartment = util.binCategoricalAttributes(synapses[:,getColIdx("post_compartment")], compartment_values, compartment_id_value)
    util.writeBins(h01Folder, "compartment", bins_compartment, "compartment", selection_properities)
    
    excInh_values, excInh_id_value = getExcInh()
    bins_excInh = util.binCategoricalAttributes(synapses[:,getColIdx("exc_inh_classification")], excInh_values, excInh_id_value)
    util.writeBins(h01Folder, "exc_inh", bins_excInh, "exc/inh", selection_properities)

    bins_x = util.binNumericAttributes(synapses[:,getColIdx("x")], 800, 3700, 100)
    util.writeBins(h01Folder, "synapse_x", bins_x, "synapse x-coord", selection_properities)
    bins_y = util.binNumericAttributes(synapses[:,getColIdx("y")], 300, 2200, 100)
    util.writeBins(h01Folder, "synapse_y", bins_y, "synapse y-coord", selection_properities)
    bins_z = util.binNumericAttributes(synapses[:,getColIdx("z")], 0, 170, 10)
    util.writeBins(h01Folder, "synapse_z", bins_z, "synapse z-coord", selection_properities)

    bin_bounds_NAx = util.getBinsFromQuantiles(NAx, 10)
    bins_NAx = util.binNumericAttributesFixedBins(NAx, bin_bounds_NAx)
    util.writeBins(h01Folder, "NAx", bins_NAx, "axon size", selection_properities)
    
    meta = {
        "selection_properties" : selection_properities
    }
    with open(os.path.join(dataFolder, "H01.json"),"w") as f:
        json.dump(meta, f)

    
import sys
import os
import json
import numpy as np

import util 

def printUsageAndExit():
    print("python preprocess_H01.py data-folder")
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

    h01BaseFolder = os.path.join(dataFolder, "H01-synapses")
    outfolder_channel0 = os.path.join(h01BaseFolder, "channel0")
    util.makeCleanDir(outfolder_channel0)
    outfolder_channel1 = os.path.join(h01BaseFolder, "channel1")
    util.makeCleanDir(outfolder_channel1)
    #neuronsFile = os.path.join(visFolder, "somas.csv")
    propertiesFile =  os.path.join(h01BaseFolder, "info")
    
    synapsesFile_channel0 = os.path.join(h01BaseFolder, "synapses-classified-neurons.csv")
    synapsesFile_channel1 = os.path.join(h01BaseFolder, "synapses-no-specificity.csv")
        
    headerCols_channel0 = util.getHeaderCols(synapsesFile_channel0)    
    print(headerCols_channel0)
    def getColIdx_channel0(name):
        return headerCols_channel0.index(name)
        
    headerCols_channel1 = util.getHeaderCols(synapsesFile_channel1)    
    print(headerCols_channel1)
    def getColIdx_channel1(name):
        return headerCols_channel1.index(name)
    
    synapses_channel0 = np.loadtxt(synapsesFile_channel0, skiprows=1, delimiter=",")
    synapses_channel1 = np.loadtxt(synapsesFile_channel1, skiprows=1, delimiter=",")

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
# convert synapse position from nanometer to microns
#synapses_channel0[:,getColIdx("x")] *= 0.001
#synapses_channel0[:,getColIdx("y")] *= 0.001
#synapses_channel0[:,getColIdx("z")] *= 0.001

#util.printDataRangeCategorical("exc inh", synapses_channel0[:,getColIdx("exc_inh_classification")]) 

#util.printDataRange("x", synapses_channel0[:,getColIdx("x")])
#util.printDataRange("y", synapses_channel0[:,getColIdx("y")])
#util.printDataRange("z", synapses_channel0[:,getColIdx("z")])

#bins_x = util.binNumericAttributes(synapses_channel0[:,getColIdx("x")], 800, 3700, 100)
#util.writeBins(outfolder, "synapse_x", bins_x, "synapse x-coord", selection_properities)
#bins_y = util.binNumericAttributes(synapses_channel0[:,getColIdx("y")], 300, 2200, 100)
#util.writeBins(outfolder, "synapse_y", bins_y, "synapse y-coord", selection_properities)
#bins_z = util.binNumericAttributes(synapses_channel0[:,getColIdx("z")], 0, 170, 10)
#util.writeBins(outfolder, "synapse_z", bins_z, "synapse z-coord", selection_properities)

excInh_values, excInh_id_value = getExcInh()
bins_excInh = util.binCategoricalAttributes(synapses_channel0[:,getColIdx_channel0("exc_inh_classification")], excInh_values, excInh_id_value)
util.writeBins(outfolder_channel0, "exc_inh", bins_excInh, "exc/inh", selection_properities)
"""
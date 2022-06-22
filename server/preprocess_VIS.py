import sys
import os
import json
import numpy as np

import util 

def printUsageAndExit():
    print("python preprocess_VIS.py <data-folder>")    
    exit()


def getCelltypes():
    values = ["EXC", "INH"]
    id_value = {
        1 : "EXC",
        2 : "INH",
    }
    return values, id_value


def getProofeditingStatus(): 
    values = ["non", "clean", "extended"]
    id_value = {
        0 : "non",
        1 : "clean",
        2 : "extended"
    }
    return values, id_value

if __name__ == "__main__":
    if(len(sys.argv) != 2):
        printUsageAndExit()

    dataFolder = sys.argv[1]
    visFolder = os.path.join(dataFolder, "VIS")
    neuronsFile = os.path.join(visFolder, "somas_extended.csv")
    channel0Folder = os.path.join(visFolder, "channel0")
    util.makeCleanDir(channel0Folder)
    samplesFile0 = os.path.join(visFolder, "samples0")

    headerCols = util.getHeaderCols(neuronsFile)    
    print(headerCols)
    def getColIdx(name):
        return headerCols.index(name)

    neurons = np.loadtxt(neuronsFile, skiprows=1, delimiter=",")

    # convert soma position from nanometer to microns
    neurons[:,getColIdx("soma_x")] *= 0.001
    neurons[:,getColIdx("soma_y")] *= 0.001
    neurons[:,getColIdx("soma_z")] *= 0.001

    print("ranges")
    util.printDataRangeCategorical("celltype", neurons[:,getColIdx("celltype")]) 
    util.printDataRangeCategorical("dendrite_proofediting", neurons[:,getColIdx("dendrite_proofediting")]) 
    util.printDataRangeCategorical("axon_proofediting", neurons[:,getColIdx("axon_proofediting")]) 
    util.printDataRange("soma_x", neurons[:,getColIdx("soma_x")])
    util.printDataRange("soma_y", neurons[:,getColIdx("soma_y")])
    util.printDataRange("soma_z", neurons[:,getColIdx("soma_z")])
    util.printDataRange("incoming_synapses_classified", neurons[:,getColIdx("incoming_synapses_classified")])
    util.printDataRange("outgoing_synapses_classified", neurons[:,getColIdx("outgoing_synapses_classified")])
    util.printDataRange("incoming_synapses_pre_or_post_classified", neurons[:,getColIdx("incoming_synapses_pre_or_post_classified")])
    util.printDataRange("outgoing_synapses_pre_or_post_classified", neurons[:,getColIdx("outgoing_synapses_pre_or_post_classified")])

    selection_properties = []    

    celltype_values, celltype_id_value = getCelltypes()    
    bins_cell_type = util.binCategoricalAttributes(neurons[:,getColIdx("celltype")], celltype_values, celltype_id_value)
    util.writeBins(channel0Folder, "cell_type", bins_cell_type, "cell type", selection_properties)

    proofediting_values, proofediting_id_value = getProofeditingStatus()    
    bins_proofediting_dendrite = util.binCategoricalAttributes(neurons[:,getColIdx("dendrite_proofediting")], proofediting_values, proofediting_id_value)
    util.writeBins(channel0Folder, "dendrite_proofediting", bins_proofediting_dendrite, "dendrite proofediting", selection_properties)
    bins_proofediting_axon = util.binCategoricalAttributes(neurons[:,getColIdx("axon_proofediting")], proofediting_values, proofediting_id_value)
    util.writeBins(channel0Folder, "axon_proofediting", bins_proofediting_axon, "axon proofediting", selection_properties)

    bins_soma_x = util.binNumericAttributes(neurons[:,getColIdx("soma_x")], 200, 1600, 100)
    util.writeBins(channel0Folder, "soma_x", bins_soma_x, "soma x-coord", selection_properties)
    bins_soma_y = util.binNumericAttributes(neurons[:,getColIdx("soma_y")], 200, 1100, 100)
    util.writeBins(channel0Folder, "soma_y", bins_soma_y, "soma y-coord", selection_properties)
    bins_soma_z = util.binNumericAttributes(neurons[:,getColIdx("soma_z")], 500, 1100, 100)
    util.writeBins(channel0Folder, "soma_z", bins_soma_z, "soma z-coord", selection_properties)

    bin_bounds = [(-1,0)] + util.getBinBounds(0,20,1) + [(20,100)]
    bins_incoming_classified = util.binNumericAttributesFixedBins(neurons[:,getColIdx("incoming_synapses_classified")], bin_bounds)        
    util.writeBins(channel0Folder, "incoming_classified", bins_incoming_classified, "incoming syn.", selection_properties)

    bin_bounds = [(-1,0)] + util.getBinBounds(0,20,1) + [(20,100)]
    bins_outgoing_classified = util.binNumericAttributesFixedBins(neurons[:,getColIdx("outgoing_synapses_classified")], bin_bounds)
    util.writeBins(channel0Folder, "outgoing_classified", bins_outgoing_classified, "outgoing syn.", selection_properties)

    bin_bounds = [(-1,0)] + util.getBinBounds(0,20,1) + [(20,50), (50,100), (100,200), (200,500), (500,1000), (1000,2000), (2000,5000), (5000,10000)] 
    bins_incoming_all = util.binNumericAttributesFixedBins(neurons[:,getColIdx("incoming_synapses_pre_or_post_classified")], bin_bounds)
    util.writeBins(channel0Folder, "incoming_all", bins_incoming_all, "incoming syn. (all)", selection_properties)

    bin_bounds = [(-1,0)] + util.getBinBounds(0,20,1) + [(20,50), (50,100), (100,200), (200,500), (500,1000), (1000,2000), (2000,5000), (5000,10000)] 
    bins_outgoing_all = util.binNumericAttributesFixedBins(neurons[:,getColIdx("outgoing_synapses_pre_or_post_classified")], bin_bounds)
    util.writeBins(channel0Folder, "outgoing_all", bins_outgoing_all, "outgoing syn. (all)", selection_properties)
    
    channels = [{
        "display_name" : "neuron count"
    }]
    metaFile = os.path.join(dataFolder, "VIS.json")
    util.writeMeta(metaFile, selection_properties, channels)

    samples = neurons[:,getColIdx("neuron_id")]
    np.savetxt(samplesFile0, samples, fmt="%d")
    

   
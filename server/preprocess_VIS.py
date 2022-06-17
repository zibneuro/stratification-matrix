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

    selection_properities = []    

    celltype_values, celltype_id_value = getCelltypes()    
    bins_cell_type = util.binCategoricalAttributes(neurons[:,getColIdx("celltype")], celltype_values, celltype_id_value)
    util.writeBins(visFolder, "cell_type", bins_cell_type, "cell type", selection_properities)

    proofediting_values, proofediting_id_value = getProofeditingStatus()    
    bins_proofediting_dendrite = util.binCategoricalAttributes(neurons[:,getColIdx("dendrite_proofediting")], proofediting_values, proofediting_id_value)
    util.writeBins(visFolder, "dendrite_proofediting", bins_proofediting_dendrite, "dendrite proofediting", selection_properities)
    bins_proofediting_axon = util.binCategoricalAttributes(neurons[:,getColIdx("axon_proofediting")], proofediting_values, proofediting_id_value)
    util.writeBins(visFolder, "axon_proofediting", bins_proofediting_axon, "axon proofediting", selection_properities)

    bins_soma_x = util.binNumericAttributes(neurons[:,getColIdx("soma_x")], 200, 1600, 100)
    util.writeBins(visFolder, "soma_x", bins_soma_x, "soma x-coord", selection_properities)
    bins_soma_y = util.binNumericAttributes(neurons[:,getColIdx("soma_y")], 200, 1100, 100)
    util.writeBins(visFolder, "soma_y", bins_soma_y, "soma y-coord", selection_properities)
    bins_soma_z = util.binNumericAttributes(neurons[:,getColIdx("soma_z")], 500, 1100, 100)
    util.writeBins(visFolder, "soma_z", bins_soma_z, "soma z-coord", selection_properities)

    bin_bounds = [(-1,0)] + util.getBinBounds(0,20,1) + [(20,100)]
    bins_incoming_classified = util.binNumericAttributesFixedBins(neurons[:,getColIdx("incoming_synapses_classified")], bin_bounds)        
    util.writeBins(visFolder, "incoming_classified", bins_incoming_classified, "incoming syn.", selection_properities)

    bin_bounds = [(-1,0)] + util.getBinBounds(0,20,1) + [(20,100)]
    bins_outgoing_classified = util.binNumericAttributesFixedBins(neurons[:,getColIdx("outgoing_synapses_classified")], bin_bounds)
    util.writeBins(visFolder, "outgoing_classified", bins_outgoing_classified, "outgoing syn.", selection_properities)

    bin_bounds = [(-1,0)] + util.getBinBounds(0,20,1) + [(20,50), (50,100), (100,200), (200,500), (500,1000), (1000,2000), (2000,5000), (5000,10000)] 
    bins_incoming_all = util.binNumericAttributesFixedBins(neurons[:,getColIdx("incoming_synapses_pre_or_post_classified")], bin_bounds)
    util.writeBins(visFolder, "incoming_all", bins_incoming_all, "incoming syn. (all)", selection_properities)

    bin_bounds = [(-1,0)] + util.getBinBounds(0,20,1) + [(20,50), (50,100), (100,200), (200,500), (500,1000), (1000,2000), (2000,5000), (5000,10000)] 
    bins_outgoing_all = util.binNumericAttributesFixedBins(neurons[:,getColIdx("outgoing_synapses_pre_or_post_classified")], bin_bounds)
    util.writeBins(visFolder, "outgoing_all", bins_outgoing_all, "outgoing syn. (all)", selection_properities)

    meta = {
        "selection_properties" : selection_properities
    }
    with open(os.path.join(dataFolder, "VIS.json"),"w") as f:
        json.dump(meta, f)
    

   
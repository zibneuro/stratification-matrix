import sys
import os
import numpy as np

import util 

def printUsageAndExit():
    print("python preprocess_RBC-L5PT.py <data-folder>")    
    exit()


def getCelltypes(filename):
    celltype_values = []
    celltype_id_value = {}
    excinh_values = ["exc", "inh"]
    excinh_id_value = {}
    with open(filename) as f:
        lines = f.readlines()
        for i in range(1, len(lines)):
            parts = lines[i].rstrip().split(",")                
            celltypeValue = parts[1]
            celltype_values.append(celltypeValue)
            celltype_id_value[celltypeValue] = celltypeValue
            isExc = int(parts[2]) 
            if(isExc):
                excinh_id_value[celltypeValue] = "exc"  
            else:
                excinh_id_value[celltypeValue] = "inh"  
    return celltype_values, celltype_id_value, excinh_values, excinh_id_value


def getColumns():
    values = ["A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "C1", "C2", "C3", "C4", "D1", "D2", "D3", "D4", "E1", "E2", "E3", "E4", "Alpha", "Beta", "Gamma", "Delta"]
    id_value = {}
    for value in values:
        id_value[value] = value
    return values, id_value


def getFilterMaskInside(dataCol, region_id_defaultName):
    mask = np.ones(dataCol.size, dtype=bool)
    for i in range(0, dataCol.size):
        regionName = region_id_defaultName[dataCol[i]]
        if("Surrounding" in regionName):
            mask[i] = False
    return mask


if __name__ == "__main__":
    if(len(sys.argv) != 2):
        printUsageAndExit()

    dataFolder = sys.argv[1]
    baseFolder = os.path.join(dataFolder, "RBC-L5PT")
    neuronsFile = os.path.join(baseFolder, "neurons.csv")
    neuronId = 400929

    channel0Folder = os.path.join(baseFolder, "channel0")
    util.makeCleanDir(channel0Folder)
    samplesFile = os.path.join(baseFolder, "samples0")

    column_values, column_id_value = getColumns()
    celltype_values, celltype_id_value, excinh_values, excinh_id_value  = getCelltypes(os.path.join(baseFolder, "realization_2021-06-16", "cell_types.csv"))

    dataCelltype = []
    dataColumn = []

    with open(os.path.join(baseFolder, "realization_2021-06-16", "post_neurons", "{}".format(neuronId), "{}.con".format(neuronId))) as f:
        lines = f.readlines()
        numSynapses = len(lines) - 4
        print("num synapses", numSynapses)

        for i in range(4,len(lines)):
            parts = lines[i].rstrip().split("\t")
            celltype, column = parts[0].split("_")
            dataCelltype.append(celltype)
            dataColumn.append(column)

    synapseFile3D = os.path.join(baseFolder, "realization_2021-06-16", "post_neurons", "{}".format(neuronId), "{}_synapses_3D.csv".format(neuronId))    
    headerColsSynapses = util.getHeaderCols(synapseFile3D, delimiter=" ")    
    def getColIdxSynapses(name):
        return headerColsSynapses.index(name)
    synapses3D = np.loadtxt(synapseFile3D, skiprows=1, delimiter=" ")
    print(synapses3D.shape)

    print("ranges")
    util.printDataRange("x", synapses3D[:,getColIdxSynapses("x")])
    util.printDataRange("y", synapses3D[:,getColIdxSynapses("y")])
    util.printDataRange("z", synapses3D[:,getColIdxSynapses("z")])    

    selectionProperties = []
        
    bins_celltype = util.binCategoricalAttributes(dataCelltype, celltype_values, celltype_id_value, True)
    util.writeBins(channel0Folder, "cell_type", bins_celltype, "cell type", selectionProperties)

    bins_column = util.binCategoricalAttributes(dataColumn, column_values, column_id_value, True)
    util.writeBins(channel0Folder, "cortical_column", bins_column, "cortical column", selectionProperties)

    bins_excinh = util.binCategoricalAttributes(dataCelltype, excinh_values, excinh_id_value, True)
    util.writeBins(channel0Folder, "exc_inh", bins_excinh, "exc/inh", selectionProperties)
        
    bins_synapses_x = util.binNumericAttributes(synapses3D[:,getColIdxSynapses("x")], -400, 150, 50)
    util.writeBins(channel0Folder, "synapse_x", bins_synapses_x, "synapse x-coord", selectionProperties)

    bins_synapses_y = util.binNumericAttributes(synapses3D[:,getColIdxSynapses("y")], 50, 650, 50)
    util.writeBins(channel0Folder, "synapse_y", bins_synapses_y, "synapse y-coord", selectionProperties)

    bins_synapses_z = util.binNumericAttributes(synapses3D[:,getColIdxSynapses("z")], -550, 700, 50)    
    util.writeBins(channel0Folder, "synapse_z", bins_synapses_z, "synapse z-coord", selectionProperties)

    metaFile = os.path.join(dataFolder, "RBC-L5PT.json")
    channels = [
            {
                "display_name" : "synapse counts"
            }
        ],
    util.writeMeta(metaFile, selectionProperties, channels)

    samples = synapses3D[:,getColIdxSynapses("pre_ID")]
    np.savetxt(samplesFile, samples, fmt="%d")
    

from fileinput import filename
import sys
import os
import json
import glob
import numpy as np

import util 

def printUsageAndExit():
    print("python preprocess_H01-synapses-ext.py data-folder")
    exit()


def getCelltypes():
    values = ["PYR", "INTER", "OTHER", "UNKNOWN"]
    id_valueIdx = {
        11 : values.index("PYR"),
        21 : values.index("PYR"),
        31 : values.index("PYR"),
        41 : values.index("PYR"),
        51 : values.index("PYR"),
        61 : values.index("PYR"),
        71 : values.index("PYR"),
        12 : values.index("INTER"),
        22 : values.index("INTER"),
        32 : values.index("INTER"),
        42 : values.index("INTER"),
        52 : values.index("INTER"),
        62 : values.index("INTER"),
        72 : values.index("INTER"),
        13 : values.index("OTHER"),
        23 : values.index("OTHER"),
        33 : values.index("OTHER"),
        43 : values.index("OTHER"),
        53 : values.index("OTHER"),
        63 : values.index("OTHER"),
        73 : values.index("OTHER"),
        -1 : values.index("UNKNOWN")
    }    
    return values, id_valueIdx


def getLayers():
    values = ["L1", "L2", "L3", "L4", "L5", "L6", "WM","UNKNOWN"]
    id_valueIdx = {
        11 : values.index("L1"),
        21 : values.index("L2"),
        31 : values.index("L3"),
        41 : values.index("L4"),
        51 : values.index("L5"),
        61 : values.index("L6"),
        71 : values.index("WM"),
        12 : values.index("L1"),
        22 : values.index("L2"),
        32 : values.index("L3"),
        42 : values.index("L4"),
        52 : values.index("L5"),
        62 : values.index("L6"),
        72 : values.index("WM"),
        13 : values.index("L1"),
        23 : values.index("L2"),
        33 : values.index("L3"),
        43 : values.index("L4"),
        53 : values.index("L5"),
        63 : values.index("L6"),
        73 : values.index("WM"),
        -1 : values.index("UNKNOWN")
    }    
    return values, id_valueIdx


def getCompartment():
    values = ["DENDRITE", "AIS", "SOMA"]
    id_valueIdx = {
        2 : values.index("DENDRITE"),
        3 : values.index("AIS"),
        4 : values.index("SOMA")
    }
    return values, id_valueIdx


def getExcInh():
    values = ["exc", "inh"]
    id_value = {
        2 : "exc",
        1 : "inh"
    }
    return values, id_value
    

if __name__ == "__main__":
    if(len(sys.argv) != 2):
        printUsageAndExit()

    dataFolder = sys.argv[1]
    baseFolder = os.path.join(dataFolder, "H01-synapses-ext")
    stackedDataFile = os.path.join(baseFolder, "synapseData")
    plotFolder = os.path.join(baseFolder, "plots")
    util.makeCleanDir(plotFolder)
    rawDataFolder = os.path.join(baseFolder, "postprocessed_ext")

    
    filenames = glob.glob(os.path.join(rawDataFolder, "*.csv"))
    headerCols_channel0 = util.getHeaderCols(filenames[0])    
    print(headerCols_channel0)
    def getColIdx(name):
        return headerCols_channel0.index(name)

    writeStackedData = False
    if(writeStackedData):    
        colIndices = (getColIdx("pre_celltype"),getColIdx("post_celltype"),getColIdx("post_compartment"),getColIdx("pre_size"),getColIdx("post_size"),getColIdx("radial_dist"))
        stackedData = []
        for i in range(0, len(filenames)):
            print(i)
            stackedData.append(np.loadtxt(filenames[i], skiprows=1, delimiter=",", usecols=colIndices).astype(int))
        stackedData = np.vstack(stackedData)
        np.savetxt(stackedDataFile,stackedData, fmt="%d")
    
    values_precelltype, data_valueIdx_precelltype = getCelltypes()
    data_precelltype = util.loadDataVector(stackedDataFile, 0)
    values_postcelltype, data_valueIdx_postcelltype = getCelltypes()
    data_postcelltype = util.loadDataVector(stackedDataFile, 1)
    values_postcompartment, data_valueIdx_postcompartment = getCompartment()
    data_postcompartment = util.loadDataVector(stackedDataFile, 2)

    datavector_presize = util.loadDataVector(stackedDataFile, 3)
    data_presize, values_presize, _ = util.getQuantilesForLargeDataVector(datavector_presize, "synapse-volume-pre", plotFolder, 0.1, useLog_x=True, useLog_y=True)

    datavector_postsize = util.loadDataVector(stackedDataFile, 4)
    data_postsize, values_postsize, _ = util.getQuantilesForLargeDataVector(datavector_postsize, "synapse-volume-post", plotFolder, 0.1, useLog_x=True, useLog_y=True)

    datavector_radialdist = util.loadDataVector(stackedDataFile, 5)
    data_radialdist, values_radialdist, _ = util.getQuantilesForLargeDataVector(datavector_radialdist, "radial-distance", plotFolder, 0.1, useLog_x=False, useLog_y=False)

    numProperties = 6
    keyCombinations = util.getPropertyCombinationKeys(numProperties)

    channel0 = util.getInitializedDict([
        len(values_precelltype),
        len(values_postcelltype),
        len(values_postcompartment),
        len(values_presize),
        len(values_postsize),        
        len(values_radialdist)        
    ])

    samplingFactor = 1
    for i in range(0, data_precelltype.size, samplingFactor):
        if(i % 1000 == 0):
            print(i)
        precelltypeIdx = data_valueIdx_precelltype[data_precelltype[i]]
        postcelltypeIdx = data_valueIdx_postcelltype[data_postcelltype[i]]
        postcompartmentIdx = data_valueIdx_postcompartment[data_postcompartment[i]]
        presizeIdx = data_presize[i]
        postsizeIdx = data_postsize[i]
        radialdistIdx = data_radialdist[i]
        
        propValues = [precelltypeIdx, postcelltypeIdx, postcompartmentIdx, presizeIdx, postsizeIdx, radialdistIdx]        
        indicesForIncrement = util.getIndicesForIncrement(keyCombinations, propValues)
        for k in range(0,indicesForIncrement.shape[0]):            
            channel0[tuple(indicesForIncrement[k,:])] += 1
        
    channel0File = os.path.join(baseFolder, "channel0.csv")
    with open(channel0File, "w") as f:
        f.write("celltype_pre,celltype_post,compartment_post,synapse_size_pre,synapse_size_post,radial_distance,aggregated_count\n")
        for valueKey, aggregatedCount in channel0.items():
            f.write("{},{},{},{},{},{},{}\n".format(*valueKey, aggregatedCount))

    filenameMeta = os.path.join(dataFolder, "H01-synapses-ext.json")
    channels = [
        {
            "display_name" : "synapse count"
        }
    ]
    selection_properties = [
        {
            "name" : "celltype_pre",
            "property_type" : "categorical", 
            "display_name" : "presynaptic cell type",
            "values" : values_precelltype
        },
        {
            "name" : "celltype_post",
            "property_type" : "categorical", 
            "display_name" : "postsynaptic cell type",
            "values" : values_postcelltype
        },
        {
            "name" : "compartment",
            "property_type" : "categorical", 
            "display_name" : "compartment",
            "values" : values_postcompartment
        },
        {
            "name" : "synapse_volume_pre",
            "property_type" : "categorical", 
            "display_name" : "presynaptic volume",
            "values" : values_presize
        },
        {
            "name" : "synapse_volume_post",
            "property_type" : "categorical", 
            "display_name" : "postsynaptic volume",
            "values" : values_postsize
        },
        {
            "name" : "radial_distance",
            "property_type" : "categorical", 
            "display_name" : "radial distance",
            "values" : values_radialdist
        }
    ]
    options = {
        "aggregated_by_property_values" : True
    }
    util.writeMeta(filenameMeta, selection_properties, channels, options)    
from fileinput import filename
import sys
import os
import json
import glob
import numpy as np

import util 

def printUsageAndExit():
    print("python preprocess_VIS-L23.py data-folder")
    exit()



def getCelltypes():
    values = ["PYR", "INTER-unknown", "INTER-bipolar", "INTER-basket", "INTER-chandelier", 
        "INTER-martinotti", "INTER-neurogliaform", "UNKNOWN"]
    id_valueIdx = {
        1 : values.index("PYR"),
        20 : values.index("INTER-unknown"),
        21 : values.index("INTER-bipolar"),
        22 : values.index("INTER-basket"),
        23 : values.index("INTER-chandelier"),
        24 : values.index("INTER-martinotti"),
        25 : values.index("INTER-neurogliaform"),
        -1 : values.index("UNKNOWN")        
    }    
    return values, id_valueIdx


def getCompartment():
    values = ["DENDRITE", "AIS", "SOMA", "UNKNOWN"]
    id_valueIdx = {
        2 : values.index("DENDRITE"),
        3 : values.index("AIS"),
        4 : values.index("SOMA"),
        -1 : values.index("UNKNOWN")
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
    baseFolder = os.path.join(dataFolder, "VIS-L23")
    synapseFile = os.path.join(baseFolder, "synapses_flat.csv")

    
    values_precelltype, data_valueIdx_precelltype = getCelltypes()
    data_precelltype = util.loadDataVector(synapseFile, 5, delimiter=",", skiprows=1)
    values_postcelltype, data_valueIdx_postcelltype = getCelltypes()
    data_postcelltype = util.loadDataVector(synapseFile, 6, delimiter=",", skiprows=1)
    values_postcompartment, data_valueIdx_postcompartment = getCompartment()
    data_postcompartment = util.loadDataVector(synapseFile, 7, delimiter=",", skiprows=1)
   
    numProperties = 3
    keyCombinations = util.getPropertyCombinationKeys(numProperties)

    channel0 = util.getInitializedDict([
        len(values_precelltype),
        len(values_postcelltype),
        len(values_postcompartment)
    ])

    samplingFactor = 1
    for i in range(0, data_precelltype.size, samplingFactor):
        if(i % 1000 == 0):
            print(i)        
        precelltypeIdx = data_valueIdx_precelltype[data_precelltype[i]]
        postcelltypeIdx = data_valueIdx_postcelltype[data_postcelltype[i]]
        postcompartmentIdx = data_valueIdx_postcompartment[data_postcompartment[i]]
        
        propValues = [precelltypeIdx, postcelltypeIdx, postcompartmentIdx]        
        indicesForIncrement = util.getIndicesForIncrement(keyCombinations, propValues)
        for k in range(0,indicesForIncrement.shape[0]):            
            channel0[tuple(indicesForIncrement[k,:])] += 1
        
    channel0File = os.path.join(baseFolder, "channel0.csv")
    with open(channel0File, "w") as f:
        f.write("celltype_pre,celltype_post,compartment_post\n")
        for valueKey, aggregatedCount in channel0.items():
            f.write("{},{},{},{}\n".format(*valueKey, aggregatedCount))

    filenameMeta = os.path.join(dataFolder, "VIS-L23.json")
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
        }
    ]
    options = {
        "aggregated_by_property_values" : True
    }
    util.writeMeta(filenameMeta, selection_properties, channels, options)    
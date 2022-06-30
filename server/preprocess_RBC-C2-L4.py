import os
import sys
import matplotlib.pyplot as plt
import numpy as np

import util


def printUsageAndExit():
    print("python preprocess_RBC-C2-L4.py <data-folder>")    
    exit()


def computeIntersomaticDistances(neurons, header, ids_celltype, outfile):
    id_position = {}
    a_b_distance = {}

    colIdx = (header.index("soma_x"), header.index("soma_y"), header.index("soma_z"))

    for i in range(0, neurons.shape[0]):
        neuronId = int(neurons[i,0])
        position = neurons[i,colIdx]
        id_position[neuronId] = position    

    for i in range(0,ids_celltype.shape[0]):        
        a = ids_celltype[i,0]
        celltype_a = ids_celltype[i,1]
        for j in range(0,ids_celltype.shape[0]):
            b = ids_celltype[j,0]
            celltype_b = ids_celltype[j,1]
            if(a < b):                
                if(celltype_a == 10 or celltype_b == 10):
                    a_b_distance[(a, b)] = -1
                else:
                    a_b_distance[(a, b)] = np.linalg.norm(id_position[a] - id_position[b])

    with open(outfile, "w") as f:
        f.write("neuron_id_a,neuron_id_b,intersomatic_distance\n")
        for a_b, distance in a_b_distance.items():
            f.write("{},{},{:.1f}\n".format(*a_b, distance))


def getQuantilesForDistanceDistribution(distancesFile, plotFile, distancesBinnedFile, quantilesFile):
    distancesAllCols = np.loadtxt(distancesFile, skiprows=1, delimiter=",")
    distanceIndices = distancesAllCols[:,0:2]
    distances = distancesAllCols[:,2]
    distancesValid = distances[distances > 0]
    
    quantiles = np.quantile(distancesValid, util.getQuantileSteps(0.05))
    print(quantiles)

    _ = plt.hist(distancesValid, bins=100)
    for quantile in quantiles:
        plt.axvline(x=quantile, color="black")
    
    plt.xlabel(r"intersomatic distance [$\mu m$]")
    plt.savefig(plotFile, dpi=300)

    quantileIndices = util.getQuantileIndicesForDataVector(distances, [-1,0], quantiles)
    np.savetxt(distancesBinnedFile, np.hstack([distanceIndices, quantileIndices.reshape(-1,1)]), fmt="%d")
    np.savetxt(quantilesFile, quantiles)



def loadIntersomaticDistances(filename):
    ab_distance = {}

    with open(filename) as f:
        lines = f.readlines()
        for i in range(1, len(lines)):
            parts = lines[i].rstrip().split(",")
            a = int(parts[0])
            b = int(parts[1])
            ab_distance[(a,b)] = parts[2]

    return ab_distance


def computeRealization(probabilitiesFile, realizationFile, eps = 0.00001):
    probabilities = np.loadtxt(probabilitiesFile, skiprows=1, delimiter=",", usecols=2)
    print(probabilities.shape)
    mask_high_prob = probabilities == 1
    probabilities[mask_high_prob] -= eps
    dsc = -np.log(1-probabilities)
    synapses = np.random.poisson(dsc)
    np.savetxt(realizationFile, synapses, fmt="%d")    


def getCelltypes(ids_celltype):   
    values_celltype = ["L3PY", "L4PY", "L4sp", "L4ss", "INH", "VPM"]
    celltypeIdsMapped = {
        1 : 0,
        2 : 1,
        3 : 2,
        4 : 3,
        11 : 4,
        10 : 5
    }
    neuronId_celltypeId = {}
    for i in range(0, ids_celltype.shape[0]):
        neuronId = ids_celltype[i,0]
        celltypeId = ids_celltype[i,1]
        neuronId_celltypeId[neuronId] = celltypeIdsMapped[celltypeId]
    return values_celltype, neuronId_celltypeId


def getValuesQuantiles(quantilesFile):
    quantiles = np.loadtxt(quantilesFile)    
    quantilesText = ["other"]
    for quantile in quantiles:
        quantilesText.append("{:.1f}".format(quantile))
    return quantilesText 


def getValuesSynapsesPerConnection(maxClusterSize):
    values_synapse_count = []
    for k in range(maxClusterSize + 1):
        if(k == maxClusterSize):
            values_synapse_count.append(">={}".format(k))    
        else:
            values_synapse_count.append(str(k))    
    return values_synapse_count


def loadIntersomaticDistanceDict(filename):
    distancesBinned  = np.loadtxt(filename)
    distanceDict = {}
    for i in range(0, distancesBinned.shape[0]):
        a = distancesBinned[i,0]
        b = distancesBinned[i,1]
        dist = distancesBinned[i,2]
        distanceDict[(a,b)] = dist
        distanceDict[(b,a)] = dist
    return distanceDict



if __name__ == "__main__":
    if(len(sys.argv) != 2):
        printUsageAndExit()

    dataFolder = sys.argv[1]
    baseFolder = os.path.join(dataFolder, "RBC-C2-L4")

    neuronsFile = os.path.join(baseFolder, "neurons.csv")
    header_cols = util.getHeaderCols(neuronsFile)      
    neurons = np.loadtxt(neuronsFile, skiprows=1, delimiter=",")    
    ids_celltype = np.loadtxt(os.path.join(baseFolder, "neurons_meta.csv"), skiprows=1, delimiter=",").astype(int)    
    
    # compute intersomatic distances    
    distancesFile = os.path.join(baseFolder, "intersomatic_distances.csv")    
    plotFile = os.path.join(baseFolder, "intersomatic_distance_distribution.png")    
    distancesBinnedFile = os.path.join(baseFolder, "intersomatic_distances_binned")
    quantilesFile = os.path.join(baseFolder, "intersomatic_distances_quanties")    
    """
    computeIntersomaticDistances(neurons, header_cols, ids_celltype, distancesFile)
    getQuantilesForDistanceDistribution(distancesFile, plotFile, distancesBinnedFile, quantilesFile)
    """

    # compute realization 
    probabilitiesFile = os.path.join(baseFolder, "connection_probabilities.csv")
    realizationFile = os.path.join(baseFolder, "realization")
    #computeRealization(probabilitiesFile, realizationFile)

    values_celltype, neuronId_celltypeId = getCelltypes(ids_celltype)    
    values_intersomatic = getValuesQuantiles(quantilesFile)
    maxSynapsesPerConnection = 10
    values_synapse_count = getValuesSynapsesPerConnection(maxSynapsesPerConnection)
    values_connected = ["connected", "unconnected"]

    channel0 = util.getInitializedDict([
        len(values_celltype),
        len(values_celltype),
        len(values_connected),
        len(values_synapse_count),
        len(values_intersomatic)
    ])

    # map realization to property values
    data_preId_postId = np.loadtxt(probabilitiesFile, skiprows=1, delimiter=",", usecols=(0,1)).astype(int)
    data_synapses = np.loadtxt(realizationFile).astype(int)

    assert data_preId_postId.shape[0] == data_synapses.size

    def getConnectedUnconnectedValue(synapseCount):
        if(synapseCount == 0):
            return 1
        else:
            return 0

    def getSynapseCountBin(synapseCount):
        if(synapseCount < maxSynapsesPerConnection):
            return synapseCount
        else:
            return maxSynapsesPerConnection

    distanceDict = loadIntersomaticDistanceDict(distancesBinnedFile)

    def getDistanceBin(preId, postId):
        if(preId == postId):
            return -1
        else:
            return distanceDict[(preId, postId)] 

    keyCombinations = util.getPropertyCombinationKeys(5)

    for i in range(0, data_preId_postId.shape[0]):
        if(i % 1000):
            print(i)
        preId = data_preId_postId[i,0]
        preCelltypeId = neuronId_celltypeId[preId]
        postId = data_preId_postId[i,1]
        postCelltypeId = neuronId_celltypeId[postId]
        synapseCount = data_synapses[i]
        connectedUconnected = getConnectedUnconnectedValue(synapseCount)
        synapseCountBin = getSynapseCountBin(synapseCount)
        distanceBin = getDistanceBin(preId, postId)

        propValues = [preCelltypeId, postCelltypeId, connectedUconnected, synapseCountBin, distanceBin]
        indicesForIncrement = util.getIndicesForIncrement(keyCombinations, propValues)
        for k in range(0,indicesForIncrement.shape[0]):            
            channel0[tuple(indicesForIncrement[k,:])] += 1
        
    channel0File = os.path.join(baseFolder, "channel0.csv")
    with open(channel0File, "w") as f:
        f.write("celltype_pre,celltype_post,connected_unconnected,synapse_count,intersomatic_distance,aggregated_count\n")
        for valueKey, aggregatedCount in channel0.items():
            f.write("{},{},{},{},{},{}\n".format(*valueKey, aggregatedCount))


    filenameMeta = os.path.join(dataFolder, "RBC-C2-L4.json")
    channels = [
        {
            "display_name" : "neuron pairs"
        }
    ]
    selection_properties = [
        {
            "name" : "celltype_pre",
            "property_type" : "categorical", 
            "display_name" : "presynaptic cell type",
            "values" : values_celltype
        },
        {
            "name" : "celltype_post",
            "property_type" : "categorical", 
            "display_name" : "postsynaptic cell type",
            "values" : values_celltype
        },
        {
            "name" : "connected_unconnected",
            "property_type" : "categorical", 
            "display_name" : "connected/unconnected",
            "values" : values_connected
        },
        {
            "name" : "synapse_count",
            "property_type" : "categorical", 
            "display_name" : "synapse count",
            "values" : values_synapse_count
        },
        {
            "name" : "intersomatic_distance",
            "property_type" : "categorical", 
            "display_name" : "intersomatic distance",
            "values" : values_intersomatic
        }
    ]
    options = {
        "aggregated_by_property_values" : True
    }
    util.writeMeta(filenameMeta, selection_properties, channels, options)    
    
    



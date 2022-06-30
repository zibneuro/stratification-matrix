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

    
    
    



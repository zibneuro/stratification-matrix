from email import header
import sys
import os
import numpy as np

import util 

def printUsageAndExit():
    print("python preprocess_RBC.py <data-folder>")    
    exit()


def getCelltypes(filename):
    celltype_values = []
    celltype_id_value = {}
    with open(filename) as f:
        lines = f.readlines()
        for i in range(1, len(lines)):
            parts = lines[i].rstrip().split(",")    
            celltypeId = int(parts[0])
            celltypeValue = parts[1]
            celltype_values.append(celltypeValue)
            celltype_id_value[celltypeId] = celltypeValue
    return celltype_values, celltype_id_value 


def getRegions(filename):
    region_id_defaultName = {}
    column_values = ["A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "C1", "C2", "C3", "C4", "D1", "D2", "D3", "D4", "E1", "E2", "E3", "E4", "Alpha", "Beta", "Gamma", "Delta"]
    region_id_column_value = {}
    subregion_values = ["inside", "septum", "other"]  
    region_id_subregion_value = {}
    ignoreList = ["Brain","Neocortex","Thalamus","S1","S1_Surrounding","S1_Septum"]

    def getColumnFromName(name):
        return name.replace("_Barreloid","").replace("S1_Surrounding_","").replace("S1_Septum_","")

    def getSubregionFromName(name):
        if("Septum" in name):
            return "septum"
        elif("_Barreloid" in name):
            return "other"
        elif("S1_Surrounding" in name):
            return "other"
        else:
            return "inside"        

    with open(filename) as f:
        lines = f.readlines()
        for i in range(1, len(lines)):
            parts = lines[i].rstrip().split(",")    
            regionId = int(parts[0])
            regionName = parts[1]
            region_id_defaultName[regionId] = regionName
            if(regionName not in ignoreList):
                region_id_column_value[regionId] = getColumnFromName(regionName)
                region_id_subregion_value[regionId] = getSubregionFromName(regionName)

    return region_id_defaultName, column_values, region_id_column_value, subregion_values, region_id_subregion_value


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
    rbcFolder = os.path.join(dataFolder, "RBC")
    neuronsFile = os.path.join(rbcFolder, "neurons.csv")

    celltype_values, celltype_id_value = getCelltypes(os.path.join(rbcFolder, "cell_types.csv"))
    region_id_defaultName, column_values, region_id_column_value, subregion_values, region_id_subregion_value = getRegions(os.path.join(rbcFolder, "regions.csv"))
    
    headerCols = util.getHeaderCols(neuronsFile)
    
    neurons = np.loadtxt(neuronsFile, skiprows=1, delimiter=",")
    mask_inside = getFilterMaskInside(neurons[:,headerCols.index("region")], region_id_defaultName)
    neurons = neurons[mask_inside, :]

    

    print("ranges")
    util.printDataRange("soma_x", neurons[:,headerCols.index("soma_x")])
    util.printDataRange("soma_y", neurons[:,headerCols.index("soma_y")])
    util.printDataRange("soma_z", neurons[:,headerCols.index("soma_z")], -4000)
    util.printDataRange("cortical_depth", neurons[:,headerCols.index("cortical_depth")], -1)

    bins_soma_x = util.binNumericAttributes(neurons[:,headerCols.index("soma_x")], -1100, 1300, 100)
    util.writeBins(rbcFolder, "soma_x", bins_soma_x)
    bins_soma_y = util.binNumericAttributes(neurons[:,headerCols.index("soma_y")], -800, 1400, 100)
    util.writeBins(rbcFolder, "soma_y", bins_soma_y)
    bins_soma_z = util.binNumericAttributes(neurons[:,headerCols.index("soma_z")], -1500, 600, 100)
    util.writeBins(rbcFolder, "soma_z", bins_soma_z)
    bins_cortical_depth = util.binNumericAttributes(neurons[:,headerCols.index("cortical_depth")], 0, 2100, 100)
    util.writeBins(rbcFolder, "cortical_depth", bins_cortical_depth)
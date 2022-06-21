import sys
import os
import json
import numpy as np

import util 

def printUsageAndExit():
    print("python preprocess_COVID.py data-folder")
    exit()
    

def getNeuronProperties(filename, propertyName):    
    propertiesFile = os.path.join(filename)
    with open(propertiesFile) as f:
        properties = json.load(f)
    propertyIdx = {}
    for i in range(0, len(properties["inline"]["properties"])):
        propName = properties["inline"]["properties"][i]["id"]
        #print(i, propName)
        propertyIdx[propName] = i

    tags_all = properties["inline"]["properties"][propertyIdx["tags"]]["tags"]    
    values_all = properties["inline"]["properties"][propertyIdx[propertyName]]["values"]    
    ids_all = properties["inline"]["ids"]
        
    return ids_all, tags_all, values_all


def splitTagDataColumns(dataColumn):
    n = len(dataColumn)    
    col1 = np.zeros(n, dtype=int)
    col2 = np.zeros(n, dtype=int)
    col3 = np.zeros(n, dtype=int)
    for i in range(0,n):
        col1[i] = dataColumn[i][0]
        col2[i] = dataColumn[i][1]
        #col3[i] = dataColumn[i][2]
    return col1, col2, col3


def printValueRange(filename):
    with open(filename, encoding='utf-8-sig') as f:
        lines = f.readlines()
        headers = lines[0].rstrip().split(",")
        print(headers)

        allYearMonth = set()
        allLand = set()
        allAgeGroups = set()
        allGenders = set()
        sumCases = 0
        sumDeaths = 0

        def getColIdx(colName):
            return headers.index(colName)

        def getYearMonth(dateString):
            return dateString[0:7]

        def getLand(landkreisId):
            return landkreisId[:-3]

        for i in range(1,len(lines)):
            parts = lines[i].rstrip().split(",")

            dateString = parts[getColIdx("Meldedatum")]            
            allYearMonth.add(getYearMonth(dateString))

            landkreisId = parts[getColIdx("IdLandkreis")]
            allLand.add(getLand(landkreisId))

            ageGroup = parts[getColIdx("Altersgruppe")]
            allAgeGroups.add(ageGroup)

            gender = parts[getColIdx("Geschlecht")]
            allGenders.add(gender)

            neuerFall = int(parts[getColIdx("NeuerFall")])
            #if(neuerFall in [0,1,-1]):
            anzahlFall = int(parts[getColIdx("AnzahlFall")])                
            sumCases += anzahlFall

            neuerTodesfall = int(parts[getColIdx("NeuerTodesfall")])
            #if(neuerTodesfall in [1,-1]):
            anzahlTodesfall = int(parts[getColIdx("AnzahlTodesfall")])                
            sumDeaths += anzahlTodesfall

            
        allYearMonth = list(allYearMonth)
        allYearMonth.sort()
        for i in range(0,len(allYearMonth)):
            print(i,allYearMonth[i])       

        print(allLand)
        print(allAgeGroups)
        print(allGenders)
        print("cases", sumCases)
        print("deaths", sumDeaths)


if __name__ == "__main__":
    if(len(sys.argv) != 2):
        printUsageAndExit()

    dataFolder = sys.argv[1]

    baseFolder = os.path.join(dataFolder, "COVID")
    outfolder_channel0 = os.path.join(baseFolder, "channel0")
    outfolder_channel1 = os.path.join(baseFolder, "channel1")
    util.makeCleanDir(outfolder_channel0)
    util.makeCleanDir(outfolder_channel1)
        
    samplesFile0 = os.path.join(outfolder_channel0, "samples0")
    samplesFile1 = os.path.join(outfolder_channel0, "samples1")

    dataFile = os.path.join(dataFolder, "COVID", "Aktuell_Deutschland_SarsCov2_Infektionen.csv")
    printValueRange(dataFile)
    
    """
    ids, _, dataColumn = getNeuronProperties(propertiesFile, "tags")
    ids = util.convertIntFormat(ids)
        
    selection_properties = []

    layer_values, layer_id_value, layer_na = getLayer()
    bins = util.binTags(dataColumn, layer_values, layer_id_value, layer_na)
    util.writeBins(outfolder_channel0, "layer", bins, "layer", selection_properties)

    celltype_values, celltype_id_value, celltype_na = getCelltype()
    bins = util.binTags(dataColumn, celltype_values, celltype_id_value, celltype_na)
    util.writeBins(outfolder_channel0, "cell_type", bins, "cell type", selection_properties)

    neuronAnnotation_values, neuronAnnotation_id_value, neuronAnnotation_na = getNeuronAnnotation()
    bins = util.binTags(dataColumn, neuronAnnotation_values, neuronAnnotation_id_value, neuronAnnotation_na)
    util.writeBins(outfolder_channel0, "neuron_annotation", bins, "neuron annotation", selection_properties)

    otherAnnotation_values, otherAnnotation_id_value, otherAnnotation_na = getGlialAnnotation()
    bins = util.binTags(dataColumn, otherAnnotation_values, otherAnnotation_id_value, otherAnnotation_na)
    util.writeBins(outfolder_channel0, "other_annotation", bins, "misc. annotation", selection_properties)

    displayNames = {
        "NVx" : "volume (NVx)",
        "NAx" : "axon nodes (NAx)",
        "NDe" : "dendrite nodes (NDe)",
        "Sp" : "spinyness (Sp)",
        "NSO" : "synapses outgoing (NSO)",
        "NSI" : "synapses incoming (NSI)",
    }
    quantiles = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.91,0.92,0.93,0.94,0.95,0.96,0.97,0.98,0.99,0.992,0.994,0.996,0.998,0.999,1]

    for numericProperty in ["NVx", "NAx", "NDe", "NSO", "NSI"]:
        _, _, dataNumeric = getNeuronProperties(propertiesFile, numericProperty)        
        dataNumeric = np.array(dataNumeric)

        if(numericProperty == "Sp"):
            dataNumeric *=100

        np.savetxt("/tmp/{}".format(numericProperty), dataNumeric)
        bin_bounds = util.getBinsFromFixedQuantiles(dataNumeric, quantiles)
        bins = util.binNumericAttributesFixedBins(dataNumeric, bin_bounds)
        util.writeBins(outfolder_channel0, numericProperty, bins, displayNames[numericProperty], selection_properties)

    filenameMeta = os.path.join(dataFolder, "H01.json")
    channels = [
        {
            "display_name" : "cell count"
        }
    ],
    util.writeMeta(filenameMeta, selection_properties, channels)
    
    np.savetxt(samplesFile, ids, fmt="%d")
    """
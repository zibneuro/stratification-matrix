import sys
import os
import json
import numpy as np

import util 


def printUsageAndExit():
    print("python preprocess_COVID.py data-folder")
    exit()


def getDateIndex():
    return {
        "2020-01" : 0,
        "2020-02" : 1,
        "2020-03" : 2,
        "2020-04" : 3,
        "2020-05" : 4,
        "2020-06" : 5,
        "2020-07" : 6,
        "2020-08" : 7,
        "2020-09" : 8,
        "2020-10" : 9,
        "2020-11" : 10,
        "2020-12" : 11,
        "2021-01" : 12,
        "2021-02" : 13,
        "2021-03" : 14,
        "2021-04" : 15,
        "2021-05" : 16,
        "2021-06" : 17,
        "2021-07" : 18,
        "2021-08" : 19,
        "2021-09" : 20,
        "2021-10" : 21,
        "2021-11" : 22,
        "2021-12" : 23,
        "2022-01" : 24,
        "2022-02" : 25,
        "2022-03" : 26,
        "2022-04" : 27,
        "2022-05" : 28,
        "2022-06" : 29
    }


def getAgeIndex():
    return {
        'A00-A04' : 0, 
        'A05-A14' : 1,
        'A15-A34' : 2, 
        'A35-A59' : 3,         
        'A60-A79' : 4,         
        'A80+' : 5,
        'na' : 6
    }


def getGenderIndex():
    return {
        "M" : 0,
        "W" : 1,
        "na" : 2
    }

def getLandIndex():
    """
    - 01 Schleswig-Holstein (SH)
    - 02 Hamburg (HH)
    - 03 Niedersachsen (NI)
    - 04 Bremen (HB)
    - 05 Nordrhein-Westfalen (NW)
    - 06 Hessen (HE)
    - 07 Rheinland-Pfalz (RP)
    - 08 Baden-Württemberg (BW)
    - 09 Bayern (BY)
    - 10 Saarland (SL)
    - 11 Berlin (BE)
    - 12 Brandenburg (BB)
    - 13 Mecklenburg-Vorpommern (MV)
    - 14 Sachsen (SN)
    - 15 Sachsen-Anhalt (ST)
    - 16 Thüringen (TH)
    """
    return {
        "Schleswig-Holstein" : 1,
        "Hamburg" : 2,
        "Niedersachsen" : 3,
        "Bremen" : 4,
        "Nordrhein-Westfalen" : 5,
        "Hessen" : 6,
        "Rheinland-Pfalz" : 7,
        "Baden-Wuerttemberg" : 8,
        "Bayern" : 9,
        "Saarland" : 10,
        "Berlin" : 11,
        "Brandenburg" : 12,
        "Mecklenburg-Vorpommern" : 13,
        "Sachsen" : 14,
        "Sachsen-Anhalt" : 15,
        "Thueringen" : 16
    }



def aggregateData(filename, filenameAggregated):
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
            return int(landkreisId[:-3])

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
           
            anzahlFall = int(parts[getColIdx("AnzahlFall")])                
            sumCases += anzahlFall

            anzahlTodesfall = int(parts[getColIdx("AnzahlTodesfall")])                
            sumDeaths += anzahlTodesfall

        allYearMonth = list(allYearMonth)
        allYearMonth.sort()
        for i in range(0,len(allYearMonth)):
            print(allYearMonth[i], i)       

        print(allLand)
        print(allAgeGroups)
        print(allGenders)
        print("cases", sumCases)
        print("deaths", sumDeaths)

    	# aggregate 
        dateIndex = getDateIndex()
        ageIndex = getAgeIndex()
        genderIndex = getGenderIndex()

        cases = {} # (date, age, gender, land) => [cases, deaths]

        for i in range(1,len(lines)):
            parts = lines[i].rstrip().split(",")

            dateString = parts[getColIdx("Meldedatum")]            
            dateId = dateIndex[getYearMonth(dateString)]

            landkreisId = parts[getColIdx("IdLandkreis")]
            landId = getLand(landkreisId)

            ageGroup = parts[getColIdx("Altersgruppe")].replace("unbekannt","na")
            ageId = ageIndex[ageGroup]

            gender = parts[getColIdx("Geschlecht")].replace("unbekannt","na")
            genderId = genderIndex[gender]
           
            anzahlFall = int(parts[getColIdx("AnzahlFall")])                        
            anzahlTodesfall = int(parts[getColIdx("AnzahlTodesfall")])      

            caseKey = (dateId, landId, ageId, genderId)          
            if(caseKey not in cases):
                cases[caseKey] = [0, 0]

            cases[caseKey][0] += anzahlFall
            cases[caseKey][1] += anzahlTodesfall

        with open(filenameAggregated, "w") as f:
            f.write("date_id,age_id,gender_id,land_id,cases,deaths\n")
            for caseKey, values in cases.items():
                f.write("{},{},{},{},{},{}\n".format(*caseKey, *values))
    


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

    dataFile = os.path.join(dataFolder, "COVID", "Aktuell_Deutschland_SarsCov2_Infektionen.csv") # downloaded 2022-06-21
    dataFileAggregated = os.path.join(dataFolder, "COVID", "aggregated.csv")
    #aggregateData(dataFile, dataFileAggregated)
    
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
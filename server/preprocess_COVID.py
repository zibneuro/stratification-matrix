import sys
import os
import datetime
import numpy as np

import util 


def printUsageAndExit():
    print("python preprocess_COVID.py data-folder")
    exit()

"""
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
"""

def getDateIndex():
    return {
        "20-01":0,
        "20-04":1,
        "20-05":2,
        "20-06":3,
        "20-07":4,
        "20-08":5,
        "20-09":6,
        "20-10":7,
        "20-11":8,
        "20-12":9,
        "20-13":10,
        "20-14":11,
        "20-15":12,
        "20-16":13,
        "20-17":14,
        "20-18":15,
        "20-19":16,
        "20-20":17,
        "20-21":18,
        "20-22":19,
        "20-23":20,
        "20-24":21,
        "20-25":22,
        "20-26":23,
        "20-27":24,
        "20-28":25,
        "20-29":26,
        "20-30":27,
        "20-31":28,
        "20-32":29,
        "20-33":30,
        "20-34":31,
        "20-35":32,
        "20-36":33,
        "20-37":34,
        "20-38":35,
        "20-39":36,
        "20-40":37,
        "20-41":38,
        "20-42":39,
        "20-43":40,
        "20-44":41,
        "20-45":42,
        "20-46":43,
        "20-47":44,
        "20-48":45,
        "20-49":46,
        "20-50":47,
        "20-51":48,
        "20-52":49,
        "20-53":50,
        "21-01":51,
        "21-02":52,
        "21-03":53,
        "21-04":54,
        "21-05":55,
        "21-06":56,
        "21-07":57,
        "21-08":58,
        "21-09":59,
        "21-10":60,
        "21-11":61,
        "21-12":62,
        "21-13":63,
        "21-14":64,
        "21-15":65,
        "21-16":66,
        "21-17":67,
        "21-18":68,
        "21-19":69,
        "21-20":70,
        "21-21":71,
        "21-22":72,
        "21-23":73,
        "21-24":74,
        "21-25":75,
        "21-26":76,
        "21-27":77,
        "21-28":78,
        "21-29":79,
        "21-30":80,
        "21-31":81,
        "21-32":82,
        "21-33":83,
        "21-34":84,
        "21-35":85,
        "21-36":86,
        "21-37":87,
        "21-38":88,
        "21-39":89,
        "21-40":90,
        "21-41":91,
        "21-42":92,
        "21-43":93,
        "21-44":94,
        "21-45":95,
        "21-46":96,
        "21-47":97,
        "21-48":98,
        "21-49":99,
        "21-50":100,
        "21-51":101,
        "21-52":102,
        "22-01":103,
        "22-02":104,
        "22-03":105,
        "22-04":106,
        "22-05":107,
        "22-06":108,
        "22-07":109,
        "22-08":110,
        "22-09":111,
        "22-10":112,
        "22-11":113,
        "22-12":114,
        "22-13":115,
        "22-14":116,
        "22-15":117,
        "22-16":118,
        "22-17":119,
        "22-18":120,
        "22-19":121,
        "22-20":122,
        "22-21":123,
        "22-22":124,
        "22-23":125,
        "22-24":126,
        "22-25":127
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
        "SH" : 1,
        "HH" : 2,
        "NI" : 3,
        "HB" : 4,
        "NW" : 5,
        "HE" : 6,
        "RP" : 7,
        "BW" : 8,
        "BY" : 9,
        "SL" : 10,
        "BE" : 11,
        "BB" : 12,
        "MV" : 13,
        "SN" : 14,
        "ST" : 15,
        "TH" : 16
    }


def getLandPopulation():
    return {
        "SH" : 2922005,
        "HH" : 1853935,
        "NI" : 8027031,
        "HB" : 676463,
        "NW" : 17924591,
        "HE" : 6295017,
        "RP" : 4106485,
        "BW" : 11124642,
        "BY" : 13176989,
        "SL" : 982348,
        "BE" : 3677472,
        "BB" : 2537868,
        "MV" : 1611160,
        "SN" : 4043002,
        "ST" : 2169253,
        "TH" : 2108863
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

        def getYearWeek(dateString):            
            year = int(dateString[0:4])
            month = int(dateString[5:7])
            day = int(dateString[8:10])
            year_week_day = datetime.date(year,month,day).isocalendar()
            yearString = str(year_week_day[0])[2:4]
            week = year_week_day[1]
            return "{}-{:02d}".format(yearString, week)

        def getLand(landkreisId):
            return int(landkreisId[:-3])

        for i in range(1,len(lines)):
            parts = lines[i].rstrip().split(",")

            dateString = parts[getColIdx("Meldedatum")]            
            #allYearMonth.add(getYearMonth(dateString))
            allYearMonth.add(getYearWeek(dateString))

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
            #dateId = dateIndex[getYearMonth(dateString)]
            dateId = dateIndex[getYearWeek(dateString)]

            landkreisId = parts[getColIdx("IdLandkreis")]
            landId = getLand(landkreisId)

            ageGroup = parts[getColIdx("Altersgruppe")].replace("unbekannt","na")
            ageId = ageIndex[ageGroup]

            gender = parts[getColIdx("Geschlecht")].replace("unbekannt","na")
            genderId = genderIndex[gender]
           
            anzahlFall = int(parts[getColIdx("AnzahlFall")])                        
            anzahlTodesfall = int(parts[getColIdx("AnzahlTodesfall")])      

            caseKey = (dateId, ageId, genderId, landId)          
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
        
    dataFile = os.path.join(dataFolder, "COVID", "Aktuell_Deutschland_SarsCov2_Infektionen.csv") # downloaded 2022-06-21
    dataFileAggregated = os.path.join(dataFolder, "COVID", "aggregated.csv")

    aggregateData(dataFile, dataFileAggregated)
    data = np.loadtxt(dataFileAggregated, skiprows=1, delimiter=",")

    samplesFile0 = os.path.join(baseFolder, "samples0")
    samplesFile1 = os.path.join(baseFolder, "samples1")
    np.savetxt(samplesFile0, data[:,4])
    np.savetxt(samplesFile1, data[:,5])

    selection_properties = []

    date_values = sorted(getDateIndex().keys())
    bins = util.binCategoricalAttributes(data[:,0], date_values, util.revertDict(getDateIndex()))
    util.writeBins(outfolder_channel0, "date", bins, "year/week", selection_properties)
    util.writeBins(outfolder_channel1, "date", bins, "year/week")

    age_values = sorted(getAgeIndex().keys())    
    bins = util.binCategoricalAttributes(data[:,1], age_values, util.revertDict(getAgeIndex()))
    util.writeBins(outfolder_channel0, "age", bins, "age group", selection_properties)
    util.writeBins(outfolder_channel1, "age", bins, "age group")

    gender_values = ["M","W","na"]
    bins = util.binCategoricalAttributes(data[:,2], gender_values, util.revertDict(getGenderIndex()))
    util.writeBins(outfolder_channel0, "gender", bins, "gender", selection_properties)
    util.writeBins(outfolder_channel1, "gender", bins, "gender")

    land_values = sorted(getLandIndex())
    bins = util.binCategoricalAttributes(data[:,3], land_values, util.revertDict(getLandIndex()))
    util.writeBins(outfolder_channel0, "land", bins, "state", selection_properties)
    util.writeBins(outfolder_channel1, "land", bins, "state")

    filenameMeta = os.path.join(dataFolder, "COVID.json")
    channels = [
        {
            "display_name" : "cases"
        },
        {
            "display_name" : "deaths"
        }
    ]
    options = {
        "samples_are_weights" : True
    }
    util.writeMeta(filenameMeta, selection_properties, channels, options)    
    
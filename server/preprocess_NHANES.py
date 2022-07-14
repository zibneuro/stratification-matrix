from email.mime import base
import sys
import os
import json
import numpy as np

import util 

"""
ClassLabel [1. 2. 4.]
normal, prediabetic, diabetic

"""

if __name__ == "__main__":
    dataFolder = sys.argv[1]
    baseFolder = os.path.join(dataFolder, "NHANES-ext")
    plotFolder = os.path.join(baseFolder, "plots")
    util.makeCleanDir(plotFolder)
    channel0Folder = os.path.join(baseFolder, "channel0")
    util.makeCleanDir(channel0Folder)    
    samplesFile = os.path.join(baseFolder, "samples0")

    filename = os.path.join(baseFolder, "Ordered_dataset.csv")    
    #filename = os.path.join(baseFolder, "NHANES_0910_NEGATIVE_NORMALANDPREDIABETES_POSITIVE_UNDIAGNOSEDDIABETES_FINAL.csv")
    #data = np.loadtxt(filename, skiprows=1, delimiter=",")

    headerCols = util.getHeaderCols(filename)
    print(headerCols[0:20])    
    def getColIdx(name):
        return headerCols.index(name)
    
    property_values = {}
    for col in headerCols:
        property_values[col] = []

    with open(filename) as f:
        lines = f.readlines()
        for i in range(1, len(lines)):
            parts = lines[i].rstrip().split(",")
            for k in range(0, len(parts)):
                value = parts[k].replace("NA", "-1")
                property_values[headerCols[k]].append(float(value))

    
    def printValueRange(propertyName):
        print("==============================================")
        print("==============================================")
        print(propertyName)
        print("----------------------------------------------")
        values, counts = np.unique(property_values[propertyName], return_counts=True)
        print(values)
        print("----------------------------------------------")
        print(counts)

    for propertyName in headerCols:
        printValueRange(propertyName)

    print(len(headerCols))
    exit()

    def getAgeValuesBinned():
        ageValues = []
        age_ageValue = {}
        ageStep = 5
        for ageLow in range(20,81,ageStep):
            ageHigh = ageLow + ageStep - 1 
            ageRange = "{}-{}".format(ageLow, ageHigh)
            ageValues.append(ageRange)
            for age in range(ageLow, ageHigh+1):
                age_ageValue[age] = ageRange
        return ageValues, age_ageValue

    selection_properties = []    

    bins_classlabel = util.binIntegerValuedAttributes(data[:,getColIdx("Classlabel")])
    util.writeBins(channel0Folder, "classlabel", bins_classlabel, "classlabel", selection_properties)

    bins_gender = util.binIntegerValuedAttributes(data[:,getColIdx("Gender")])
    util.writeBins(channel0Folder, "gender", bins_gender, "gender", selection_properties)

    bins_age = util.binIntegerValuedAttributes(data[:,getColIdx("Age")])
    util.writeBins(channel0Folder, "age_1Y", bins_age, "age", selection_properties)

    ageValues, age_ageValues = getAgeValuesBinned()
    age_binned = util.binCategoricalAttributes(data[:,getColIdx("Age")], ageValues, age_ageValues)
    util.writeBins(channel0Folder, "age_5Y", age_binned, "age group (5 year steps)", selection_properties)    

    age_quantiles, age_quantileValues, age_quantileIdValue = util.getQuantilesForDataVector(data[:,getColIdx("Age")], "Age", plotFolder, 0.125)
    age_quantiles_binned = util.binCategoricalAttributes(age_quantiles, age_quantileValues, age_quantileIdValue)
    util.writeBins(channel0Folder, "age_Q8", age_quantiles_binned, "age (Q1-Q8)", selection_properties)    

    bins_race = util.binIntegerValuedAttributes(data[:,getColIdx("Race")])
    util.writeBins(channel0Folder, "race", bins_race, "race", selection_properties)

    bins_education = util.binIntegerValuedAttributes(data[:,getColIdx("Education")])
    util.writeBins(channel0Folder, "education", bins_education, "education", selection_properties)

    bins_familyHistory = util.binIntegerValuedAttributes(data[:,getColIdx("FamilyHistory")])
    util.writeBins(channel0Folder, "family_history", bins_familyHistory, "family history", selection_properties)

    bins_highBloodSugar = util.binIntegerValuedAttributes(data[:,getColIdx("HighBloodSugar")])
    util.writeBins(channel0Folder, "high_blood_sugar", bins_highBloodSugar, "high blood sugar", selection_properties)

    bmi_quantiles, bmi_quantileValues, bmi_quantileIdValue = util.getQuantilesForDataVector(data[:,getColIdx("BMI")], "BMI", plotFolder, 0.125)
    bmi_quantiles_binned = util.binCategoricalAttributes(bmi_quantiles, bmi_quantileValues, bmi_quantileIdValue)
    util.writeBins(channel0Folder, "bmi_Q8", bmi_quantiles_binned, "BMI (Q1-Q8)", selection_properties)    

    waist_quantiles, waist_quantileValues, waist_quantileIdValue = util.getQuantilesForDataVector(data[:,getColIdx("WaistCircumference")], "WaistCircumference", plotFolder, 0.125)
    waist_quantiles_binned = util.binCategoricalAttributes(waist_quantiles, waist_quantileValues, waist_quantileIdValue)
    util.writeBins(channel0Folder, "waist_Q8", waist_quantiles_binned, "waist (Q1-Q8)", selection_properties)    

    systolic_quantiles, systolic_quantileValues, systolic_quantileIdValue = util.getQuantilesForDataVector(data[:,getColIdx("SystolicBP")], "SystolicBP", plotFolder, 0.125)
    systolic_quantiles_binned = util.binCategoricalAttributes(systolic_quantiles, systolic_quantileValues, systolic_quantileIdValue)
    util.writeBins(channel0Folder, "systolic_Q8", systolic_quantiles_binned, "syst. BP (Q1-Q8)", selection_properties)    

    diastolic_quantiles, diastolic_quantileValues, diastolic_quantileIdValue = util.getQuantilesForDataVector(data[:,getColIdx("DiastolicBP")], "DiastolicBP", plotFolder, 0.125)
    diastolic_quantiles_binned = util.binCategoricalAttributes(diastolic_quantiles, diastolic_quantileValues, diastolic_quantileIdValue)
    util.writeBins(channel0Folder, "diastolic_Q8", diastolic_quantiles_binned, "diast. BP (Q1-Q8)", selection_properties)    

    bins_hypertension = util.binIntegerValuedAttributes(data[:,getColIdx("Hypertension")])
    util.writeBins(channel0Folder, "hypertension", bins_hypertension, "hypertension", selection_properties)

    bins_physicalActivity = util.binIntegerValuedAttributes(data[:,getColIdx("PhysicalActivity")])
    util.writeBins(channel0Folder, "physical_activity", bins_physicalActivity, "physical activity", selection_properties)

    channels = [{
        "display_name" : "count",
    }]
    metaFile = os.path.join(dataFolder, "NHANES.json") 
    util.writeMeta(metaFile, selection_properties, channels)

    samples = np.arange(data.shape[0])
    np.savetxt(samplesFile, samples, fmt="%d")
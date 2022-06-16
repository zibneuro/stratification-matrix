import os
import numpy as np

import util

class QueryProcessor:

    def __init__(self, dataFolder, profileName):
        self.dataFolder = dataFolder
        self.profileName = profileName        
        self.property_value_mask = {} 

        profileMetaFile = os.path.join(self.dataFolder, "{}.json".format(profileName))
        self.profileMeta = util.loadJson(profileMetaFile)


    def getMaskFolder(self, propertyName):
        return os.path.join(self.dataFolder, self.profileName, propertyName)


    def loadMasks(self):
        selectionProperties = self.profileMeta["selection_properties"]
        #useList = ["cell_type", "cortical_column", "subregion"]
        for selectionProperty in selectionProperties:
            propertyName = selectionProperty["name"]
            propertyValues = selectionProperty["values"]            
            self.property_value_mask[propertyName] = {}
            for propertyValue in propertyValues:    
                #if(propertyName in ["cell_type", "subregion"] or propertyValue in ["A1", "C2", "A3", "A4"]):                
                maskFile = os.path.join(self.getMaskFolder(propertyName), propertyValue)
                self.property_value_mask[propertyName][propertyValue] = np.loadtxt(maskFile).astype(bool)
                print("loaded mask {} {}".format(propertyName, propertyValue))
    

    def computeTileData(self, requestData):
        rowSelectionStack = requestData["rowSelectionStack"]
        colSelectionStack = requestData["colSelectionStack"]

        def computeStack(nestedSelections):
            propertName_0 = nestedSelections[0][0]
            value_0 = nestedSelections[0][1]
            mask = np.copy(self.property_value_mask[propertName_0][value_0])
            for k in range(1, len(nestedSelections)):
                propertName_k = nestedSelections[k][0]
                value_k = nestedSelections[k][1]
                mask &= self.property_value_mask[propertName_k][value_k]
            return mask

        rowMasks = []                
        for row in rowSelectionStack:            
            rowMasks.append(computeStack(row))
        
        colMasks = []                
        for col in colSelectionStack:            
            colMasks.append(computeStack(col))

        tileData = []
        for mask_row in rowMasks:
            valuesRow = []
            for mask_col in colMasks:
                mask_cell = mask_row & mask_col
                valuesRow.append(np.count_nonzero(mask_cell))
            tileData.append(valuesRow)

        return tileData
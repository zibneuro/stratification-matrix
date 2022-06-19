import os
import numpy as np

import util

class QueryProcessor:

    def __init__(self, dataFolder, profileName):
        self.dataFolder = dataFolder
        self.profileName = profileName        
        self.property_value_mask = [{},{}] # per channel

        profileMetaFile = os.path.join(self.dataFolder, "{}.json".format(profileName))
        self.profileMeta = util.loadJson(profileMetaFile)
        self.numChannels = len(self.profileMeta["channels"])


    def getMaskFolder(self, channelIdx, propertyName):
        return os.path.join(self.dataFolder, self.profileName, "channel{}".format(channelIdx), propertyName)


    def loadMasks(self):
        for channelIdx in range(0, self.numChannels):
            selectionProperties = self.profileMeta["selection_properties"]
            for selectionProperty in selectionProperties:
                propertyName = selectionProperty["name"]
                propertyValues = selectionProperty["values"]            
                self.property_value_mask[channelIdx][propertyName] = {}
                for propertyValue in propertyValues:    
                    maskFile = os.path.join(self.getMaskFolder(channelIdx, propertyName), propertyValue)
                    self.property_value_mask[channelIdx][propertyName][propertyValue] = np.loadtxt(maskFile).astype(bool)
                    print("loaded mask {} {}".format(propertyName, propertyValue))
    

    def computeTileData(self, requestData):
        rowSelectionStack = requestData["rowSelectionStack"]
        colSelectionStack = requestData["colSelectionStack"]

        result_per_channel = []

        for channelIdx in range(0, self.numChannels):

            def computeStack(nestedSelections):
                propertName_0 = nestedSelections[0][0]
                value_0 = nestedSelections[0][1]
                mask = np.copy(self.property_value_mask[channelIdx][propertName_0][value_0])
                for k in range(1, len(nestedSelections)):
                    propertName_k = nestedSelections[k][0]
                    value_k = nestedSelections[k][1]
                    mask &= self.property_value_mask[channelIdx][propertName_k][value_k]
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

            result_per_channel.append(tileData)

        return result_per_channel
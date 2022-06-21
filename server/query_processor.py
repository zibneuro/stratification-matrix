import os
import numpy as np

import util

class QueryProcessor:

    def __init__(self, dataFolder, profileName):
        self.dataFolder = dataFolder
        self.profileName = profileName        
        self.property_value_mask = [{},{}] # per channel
        self.samples = [None, None]
        self.maxSamples = 1000

        profileMetaFile = os.path.join(self.dataFolder, "{}.json".format(profileName))
        self.profileMeta = util.loadJson(profileMetaFile)
        self.numChannels = len(self.profileMeta["channels"])
        if("options" in self.profileMeta):
            self.options = self.profileMeta["options"]
        else:
            self.options = {}


    def getMaskFolder(self, channelIdx, propertyName):
        return os.path.join(self.dataFolder, self.profileName, "channel{}".format(channelIdx), propertyName)


    def getSamplesFile(self, channelIdx):
        return os.path.join(self.dataFolder, self.profileName, "samples{}".format(channelIdx))


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
            # load samples
            samples = np.atleast_2d(np.loadtxt(self.getSamplesFile(channelIdx)).astype(int))            
            if(samples.shape[0] < samples.shape[1]):
                samples = samples.reshape(-1,1)
            self.samples[channelIdx] = samples


    def computeTileData(self, requestData, computeSamples = False):
        rowSelectionStack = requestData["rowSelectionStack"]
        colSelectionStack = requestData["colSelectionStack"]
        requestedTiles = requestData["requestedTiles"]

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

            if(computeSamples):
                samples = self.getSamples(rowMasks, colMasks, requestedTiles, channelIdx)
                result_per_channel.append(samples)
            elif("samples_are_weights" in self.options):
                tileData = self.getWeightedCounts(rowMasks, colMasks, requestedTiles, channelIdx)
                result_per_channel.append(tileData)
            else:
                tileData = []
                for mask_row in rowMasks:
                    valuesRow = []
                    for mask_col in colMasks:
                        mask_cell = mask_row & mask_col
                        valuesRow.append(np.count_nonzero(mask_cell))
                    tileData.append(valuesRow)
                result_per_channel.append(tileData)                

        return result_per_channel


    def getSamples(self, rowMasks, colMasks, requestedTiles, channelIdx):
        samples = set()       
        for requestedTile in requestedTiles:
            mask_row = rowMasks[requestedTile[0]]
            mask_col = colMasks[requestedTile[1]]            
            mask_cell = mask_row & mask_col
            samples_cell = self.samples[channelIdx][mask_cell,:].flatten()
            samples |= set(samples_cell)
        samples_subset = util.getRandomSubset(samples, self.maxSamples)
        samples_subset_list = list(samples_subset)
        samples_subset_list.sort()        
        return util.convertIntFormat(samples_subset_list)


    def getWeightedCounts(self, rowMasks, colMasks, requestedTiles, channelIdx):
        tileData = []
        for mask_row in rowMasks:
            valuesRow = []
            for mask_col in colMasks:
                mask_cell = mask_row & mask_col
                valuesRow.append(int(np.sum(self.samples[channelIdx][mask_cell])))
            tileData.append(valuesRow)
        return tileData
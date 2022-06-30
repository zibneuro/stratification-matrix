import os
import numpy as np

import util

class QueryProcessor:

    def __init__(self, dataFolder, profileName):
        self.dataFolder = dataFolder
        self.profileName = profileName        
        self.property_value_mask = [{}, {}] # per channel
        self.valueKey_aggregatedCount = [{}, {}] # per channel
        self.propertyNames = []
        self.propertyName_values = {}
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

    def getAggregatedChannelFile(self, channelIdx):
        return os.path.join(self.dataFolder, self.profileName, "channel{}.csv".format(channelIdx))

    def getSamplesFile(self, channelIdx):
        return os.path.join(self.dataFolder, self.profileName, "samples{}".format(channelIdx))

    def loadAggregatedCounts(self, filename):
        aggregatedCounts = {}
        values_count = np.loadtxt(filename, skiprows=1, delimiter=",").astype(int)
        for i in range(values_count.shape[0]):
            valueKey = tuple(values_count[i,:-1])
            count = values_count[i,-1]
            aggregatedCounts[valueKey] = count
        return aggregatedCounts

    def loadMasks(self):
        if("aggregated_by_property_values" in self.options):

            for channelIdx in range(0, self.numChannels):
                channelFile = self.getAggregatedChannelFile(channelIdx)
                self.valueKey_aggregatedCount[channelIdx] = self.loadAggregatedCounts(channelFile)

            selectionProperties = self.profileMeta["selection_properties"]            
            for selectionProperty in selectionProperties:                                
                propertyName = selectionProperty["name"]
                propertyValues = selectionProperty["values"]        
                self.propertyNames.append(propertyName)
                self.propertyName_values[propertyName] = propertyValues 

        else:                

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

        if("aggregated_by_property_values" in self.options):
            for channelIdx in range(0, self.numChannels):
                tileData = self.getAggregateCounts(rowSelectionStack, colSelectionStack, requestedTiles, channelIdx, computeSamples)
                result_per_channel.append(tileData)
        else:

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


    def getAggregateCounts(self, rowSelectionStack, colSelectionStack, requestedTiles, channelIdx, computeSamples):
        if(computeSamples):
            return []

        tileData = []

        def getValuesForStack(stack, numProperties):
            values = -1 * np.ones(numProperties)
            for level in stack:
                propertyName = level[0]
                propertyValue = level[1]
                propertyIdx = self.propertyNames.index(propertyName)
                value = self.propertyName_values[propertyName].index(propertyValue)
                values[propertyIdx] = value
            return np.array(values)
        
        def getValueKey(rowValues, colValues):
            combined = []
            for k in range(0, numProperties):
                valueRow = rowValues[k]
                valueCol = colValues[k]
                if(valueRow == -1):
                    combined.append(valueCol)
                elif(valueCol == -1):
                    combined.append(valueRow)
                elif(valueRow == valueCol):
                    combined.append(valueRow)
                else:
                    return None            
            return tuple(combined)

        numProperties = len(self.propertyName_values)        
        valueKey_aggregatedCount = self.valueKey_aggregatedCount[channelIdx] 

        rowValues = []
        for row in rowSelectionStack:
            rowValues.append(getValuesForStack(row, numProperties))

        colValues = []
        for col in colSelectionStack:
            colValues.append(getValuesForStack(col, numProperties))

        for row in rowValues:                      
            nextRow = []           
            for col in colValues:                                                    
                valueKey = getValueKey(row, col)
                if(valueKey is None):
                    nextRow.append(0)                    
                else:                
                    nextRow.append(valueKey_aggregatedCount[valueKey])                    
            tileData.append(nextRow)

        return tileData
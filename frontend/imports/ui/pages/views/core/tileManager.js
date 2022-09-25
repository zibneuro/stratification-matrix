import { LAYOUTPARAMS } from "../matrix/matrix_views/matrix_constants";
import { deepCopy } from "./utilCore";

export class TileManager {
    constructor(viewManager) {
        this.viewManager = viewManager;
        this.dataManager = viewManager.dataManager;
        this.channelSettings = this.getDefaultChannelSettings();            
        this.selectedTiles = {};     
        this.cachedData = {}; // hash of row/col leafs -> [dataFlat, dataFlat]

        this.activeExpandedSelectionHash = undefined;
        this.expandedLeafsRow = [];
        this.expandedLeafsCol = [];

        this.clearAll()

        this.OnTileDataChanged = new BABYLON.Observable();
        this.OnTileSelectionChanged = new BABYLON.Observable();       
    }

    // https://gist.github.com/hyamamoto/fd435505d29ebfa3d9716fd2be8d42f0
    getHashCode(s) {
        let h = 0, l = s.length, i = 0;
        if ( l > 0 )
            while (i < l)
            h = (h << 5) - h + s.charCodeAt(i++) | 0;
        return h;
    };    

    
    setActiveLeafs(leafsRow, leafsCol, expandedLeafsRow, expandedLeafsCol) {
        
        const isEmpty = (leafs) => {
            if(leafs.length == 0){
                return true;
            }
            if(leafs[0][0][0] == "na"){
                return true
            }
            return false;
        }

        const isTooLarge = (leafsRow, leafsCol) => {
            let numRows = leafsRow.length;
            let numCols = leafsCol.length;
            let numTiles = numRows * numCols;
            return numTiles > LAYOUTPARAMS.tileMaxCount;
        }

        // expanded selection 
        let stringRowExpanded = JSON.stringify(expandedLeafsRow);        
        let stringColExpanded = JSON.stringify(expandedLeafsCol);
        
        let hashCodeForExpandedSelection = this.getHashCode(stringRowExpanded + stringColExpanded);
        if(hashCodeForExpandedSelection !== this.activeExpandedSelectionHash){
            this.expandedLeafsRow = deepCopy(expandedLeafsRow);
            this.expandedLeafsCol = deepCopy(expandedLeafsCol);
            this.activeExpandedSelectionHash = hashCodeForExpandedSelection;
            this.cachedData = {}
        }
         
        // visible selection
        let stringRow = JSON.stringify(leafsRow);        
        let stringCol = JSON.stringify(leafsCol);
        let selectionEmpty = isEmpty(leafsRow) || isEmpty(leafsCol);
        
        let hashCodeForSelection = this.getHashCode(stringRow + stringCol);
        if(hashCodeForSelection !== this.activeSelectionHash){
            this.clearAll();
        } else {
            return;
        }
        this.activeSelectionHash = hashCodeForSelection;
        this.leafsRow = deepCopy(leafsRow);
        this.leafsCol = deepCopy(leafsCol);

        if(this.cachedData[hashCodeForSelection] !== undefined) {
            this.updateTilesDict();
        } else if (this.cachedData[hashCodeForExpandedSelection] !== undefined) {
            this.updateTilesDict();
        } else if (selectionEmpty) {            
            this.OnTileDataChanged.notifyObservers({});
        } else {

            if(isTooLarge(expandedLeafsRow, expandedLeafsCol)){
                console.log("served request aborted, selection too large");
                return;
            }

            // request data
            let request = {
                profile: this.dataManager.activeProfile,
                rowSelectionStack: deepCopy(expandedLeafsRow),
                colSelectionStack: deepCopy(expandedLeafsCol),
                selectionHashCode : hashCodeForExpandedSelection,
                requestedTiles : []
            }

            let that = this;
            this.dataManager.getTileData(request, (tileData) => {
                //console.log("server response", tileData);
                if(tileData.length){
                    that.cachedData[hashCodeForExpandedSelection] = tileData;
                    that.updateTilesDict();
                }                            
            });
        }            
    }

    aggregateFromExpanded() {
        //try {
        let tileDataExpanded = this.cachedData[this.activeExpandedSelectionHash];
    
        let nRowsExpanded = this.expandedLeafsRow.length;
        let nColsExpanded = this.expandedLeafsCol.length;
        let nRows = this.leafsRow.length;
        let nCols = this.leafsCol.length;
        let kRows = nRowsExpanded / nRows;
        let kCols = nColsExpanded / nCols;

        let tileDataAggregated = [];
        for (let channelIdx = 0; channelIdx < tileDataExpanded.length; channelIdx++) {
            let dataForChannel = tileDataExpanded[channelIdx];

            let aggregatedMatrix = [];
            for(let i=0; i<nRows; i++){
                let aggregatedRow = [];

                for(let j=0; j<nCols; j++){    
                    let aggregatedValue = 0;

                    for(let ki=0; ki<kRows; ki++){
                        let idx_i = i * kRows + ki;
                        for(let kj=0; kj<kCols; kj++){
                            let idx_j = j * kCols + kj;
                            aggregatedValue += dataForChannel[idx_i][idx_j]; 
                        }        
                    }
                    aggregatedRow.push(aggregatedValue);
                }
                aggregatedMatrix.push(aggregatedRow);
            }
            tileDataAggregated.push(aggregatedMatrix);
        }
        this.cachedData[this.activeSelectionHash] = tileDataAggregated;
        
        //} catch (e) {
        //    console.log(e)
        //}
    }


    updateTilesDict() {
        if(this.activeExpandedSelectionHash === undefined){
            return;
        }
        if(this.cachedData[this.activeExpandedSelectionHash] == undefined){
            return;
        }
        if(this.activeSelectionHash === undefined){
            return;
        }
        let tileData = this.cachedData[this.activeSelectionHash];
        if(tileData === undefined){
            this.aggregateFromExpanded();
            tileData = this.cachedData[this.activeSelectionHash];
        }
        if(tileData === undefined){
            return;
        }

        for (let channelIdx = 0; channelIdx < tileData.length; channelIdx++) {      

            let tileCache = {}
            this.tileCache[channelIdx] = tileCache;
            let maxValues = {
                maxPerRow : [],
                maxPerCol : []
            }
            this.maxValuesIndependent[channelIdx] = maxValues;
                                     
            let dataForChannel = tileData[channelIdx]      
            this.dataFlat[channelIdx] = dataForChannel;
            let numRows = dataForChannel.length;
            let numCols = dataForChannel[0].length;

            let cols = [];
            for (let j = 0; j < numCols; j++){
                cols.push([])
            }
            
            for (let i = 0; i < numRows; i++) {
                let rowValues = dataForChannel[i];
                maxValues.maxPerRow.push(Math.max(...rowValues))
                for (let j = 0; j < numCols; j++) {
                    let tileKeyString = i + "_" + j;
                    let value = rowValues[j];
                    cols[j].push(value);
                    tileCache[tileKeyString] = value;
                }
            }

            maxValues.max = Math.max(...maxValues.maxPerRow); 
            for (let j = 0; j < numCols; j++){
                maxValues.maxPerCol.push(Math.max(...cols[j]))
            }
                                   
        }
        this.setMaxValuesCombined(); 
        this.selectedTiles = {};
        this.OnTileDataChanged.notifyObservers({});
        this.OnTileSelectionChanged.notifyObservers({});
    }


    setMaxValuesCombined() {
        let channel0 = this.maxValuesIndependent[0];
        let channel1 = this.maxValuesIndependent[1];
        if(channel1 === undefined){
            this.maxValuesCombined = channel0;
            return;    
        }        
        let max = Math.max(channel0.max, channel1.max);
        let maxPerRow = [];
        let maxPerCol = [];

        for(let i = 0; i<channel0.maxPerRow.length; i++){
            maxPerRow.push(Math.max(channel0.maxPerRow[i], channel1.maxPerRow[i]));
        }

        for(let i = 0; i<channel0.maxPerCol.length; i++){
            maxPerCol.push(Math.max(channel0.maxPerCol[i], channel1.maxPerCol[i]));
        }

        this.maxValuesCombined = {
            max : max,
            maxPerRow : maxPerRow,
            maxPerCol : maxPerCol
        }
    }

    getSelectedTiles() {
        let tilesString = Object.keys(this.selectedTiles);        
        let tiles = []
        for(let i=0; i<tilesString.length; i++){
            tiles.push(JSON.parse(tilesString[i]));
        }
        return tiles;
    }

    getSamples(callback) {
        let emptySamples = [[],[]];
        let selectedTiles = this.getSelectedTiles();
        if(!selectedTiles.length){
            callback(emptySamples);
        }
        if(!this.leafsRow[0].length || !this.leafsCol[0].length){
            callback(emptySamples);
        }
    
        let request = {
            profile: this.dataManager.activeProfile,
            rowSelectionStack: this.leafsRow,
            colSelectionStack: this.leafsCol,
            requestedTiles : selectedTiles,
        }
        this.dataManager.getSamples(request, callback);
    }

    setTileSelected(tileKey, toggle) {
        let tileKeyString = JSON.stringify(tileKey);
        if(this.selectedTiles[tileKeyString] === undefined){                        
            this.selectedTiles[tileKeyString] = true;
            this.OnTileSelectionChanged.notifyObservers();
        } else {
            if(toggle){
                delete this.selectedTiles[tileKeyString];
                this.OnTileSelectionChanged.notifyObservers();    
            }            
        }                
    }

    clearSelectedTiles() {
        this.selectedTiles = {};
        this.OnTileSelectionChanged.notifyObservers();
    }

    getDefaultColorscale() {
        const viridisColorscale = [
            "#440154",
            "#482878",
            "#3e4989",
            "#31688e",
            "#26828e",
            "#1f9e89",
            "#35b779",
            "#6ece58",
            "#b5de2b",
            "#fde725"
        ]
        return viridisColorscale;
    }

    getDefaultChannelSettings() {
        return {
            display : "1",
            displayMode : "values_color",
            normalizationMode : "max_value",
            scale1: this.getDefaultColorscale(),
            scale2: this.getDefaultColorscale(),
            separateScales : false
        }
    }

    getDisplayedChannelIndices() {
        if(this.channelSettings.display == "1"){
            return [0];
        } else if (this.channelSettings.display == "2") {
            return [1];
        } else {
            return [0, 1];
        }
    }

    setChannelSettings(settings) {
        this.channelSettings = settings;
        this.OnTileDataChanged.notifyObservers({});
    }

    clearEvents() {
        this.OnTileDataChanged.clear();
    }

    clearAll() {
        this.leafsRow = [];
        this.leafsCol = [];
        this.dataFlat = [undefined, undefined];
        this.tileCache = [undefined, undefined];
        this.maxValuesIndependent = [undefined, undefined];
        this.maxValuesCombined = undefined;
    }


    getStackAsString(stack, separator) {
        let valuesString = ""
        for(let k=0; k<stack.length; k++){
            let value = stack[k][1];
            if(k==0){
                valuesString += value;
            } else {
                valuesString += separator + value;
            }
        }
        return valuesString;
    }

    getDescriptorForTile(tileKey) {
        try {                    
            let rowIdx = tileKey[0];
            let colIdx = tileKey[1];    
                        
            let rowDescriptor = this.getStackAsString(this.leafsRow[rowIdx], ",");            
            let colDescriptor = this.getStackAsString(this.leafsCol[colIdx], ",");
            
            return rowDescriptor + " - " + colDescriptor;

        } catch (e) {
            console.log(e)
            return "";
        }
    } 


    getValuesFlat(channelIdx) {
        let emptyData = [[]];
        try {
            let dataFlat = this.dataFlat[channelIdx];
            if(dataFlat === undefined){
                return emptyData;
            }
            return deepCopy(dataFlat);

        } catch(e) {
            console.log(e);
            return emptyData;
        }
    }


    getValuesAsCsv() {
        try {      
            const getAsString = (channelIdx) => {      
                let data = this.dataFlat[channelIdx];
                let csv = this.dataManager.getChannelDisplayName(channelIdx);
                for(let j=0; j<data[0].length; j++){                    
                    csv += "," + this.getStackAsString(this.leafsCol[j], "#");
                }
                csv += "\n";
                for(let i=0; i<data.length; i++){
                    csv += this.getStackAsString(this.leafsRow[i], "#");
                    for(let j=0; j<data[i].length; j++){
                        csv += "," + data[i][j]
                    }
                    csv += "\n";
                }
                return csv;
            }

            let csvAsString = "";
            if(this.dataFlat[0] !== undefined){
                csvAsString += getAsString(0);
            }            
            if(this.dataFlat[1] !== undefined){
                csvAsString += "\n\n";
                csvAsString += getAsString(1);
            }
            return csvAsString;

        } catch (e){
            console.log(e)
            return "csv generation failed or empty selection"
        }
    }

    getValueForTile(tileKey, channelIdx, context) {
        if(this.tileCache[channelIdx] === undefined){
            return undefined;
        }
        let rowIdx = tileKey[0];
        let colIdx = tileKey[1];
        let tileKeyString = rowIdx + "_" + colIdx;
        let value = this.tileCache[channelIdx][tileKeyString];
        if (value == undefined) {
            return undefined;
        }

        let maxValues = undefined;
        if(this.channelSettings.separateScales){
            maxValues = this.maxValuesIndependent[channelIdx];
        } else {
            maxValues = this.maxValuesCombined;
        }
        if(maxValues === undefined){
            throw Error
        }

        const getNormedValue = (val, maxVal) => {
            if(maxVal == 0){
                return val;
            } else {
                return val / maxVal;
            }
        }

        let normalizationMode = this.channelSettings.normalizationMode;
        if(context == "tile_text"){
            return value;
        }
        if(normalizationMode == "max_value"){         
            return getNormedValue(value, maxValues.max)         
        } else if (normalizationMode == "max_value_rows") {
            return getNormedValue(value, maxValues.maxPerRow[rowIdx]);
        } else if (normalizationMode == "max_value_cols") {
            return getNormedValue(value, maxValues.maxPerCol[colIdx]);
        } else {
            throw Error(normalizationMode)
        }
    }
}
import { LAYOUTPARAMS } from '../matrix_views/matrix_constants'
import { deepCopy } from '../../core/utilCore';

export class Layout {
    constructor(paper, canvas, selection, tileManager, dataManager) {
        this.tileManager = tileManager;
        this.dataManager = dataManager;
        this.paper = paper;
        this.canvas = canvas;
        this.selection = selection;
        this.w = canvas.width;
        this.h = canvas.height;
        this.reorderingActive = false;
        this.reorderingDepth_kr = undefined;
        this.reorderingDepth_kc = undefined;

        this.processSelection();
        this.compute("init");
    }


    processSelection() {
        this.leafsRow = this.selection.leafsRow;
        this.leafsCol = this.selection.leafsCol;
        this.numValuesPerLevelRow = this.selection.numValuesPerLevelRow;
        this.numValuesPerLevelCol = this.selection.numValuesPerLevelCol;       
    }


    resetReordering() {
        this.leafsPerLevelRow = deepCopy(this.leafsPerLevelRowDefaultOrder);
        this.leafsPerLevelCol = deepCopy(this.leafsPerLevelColDefaultOrder);
        this.reorderingActive = false;
        this.reorderingDepth_kr = undefined;
        this.reorderingDepth_kc = undefined;
    }

    checkResetReordering(kr, kc) {
        if(this.reorderingDepth_kr === undefined){
            return;
        }
        if(this.reorderingDepth_kr !== kr){
            this.resetReordering();
            return;
        }
        if(this.reorderingDepth_kc !== kc){
            this.resetReordering();
            return;
        }
    }


    setReordering(reordering){
        if(reordering.isReset) {
            this.resetReordering();
        } else {

            const getReorderedLeafs = (leafs, perm) =>{                
                let reorderedLeafs = [];
                for (let i = 0; i<perm.length; i++){
                    reorderedLeafs.push(leafs[perm[i]]);
                }
                return reorderedLeafs;                
            }

            let kr = this.baseLayout.ndra - 1;
            let kc = this.baseLayout.ndca - 1;
            this.reorderingDepth_kr = kr;
            this.reorderingDepth_kc = kc;

            if(reordering.permutation.rows !== undefined){                
                this.leafsPerLevelRow[kr] = getReorderedLeafs(this.leafsPerLevelRow[kr], reordering.permutation.rows);
            }

            if(reordering.permutation.cols !== undefined){                                            
                this.leafsPerLevelCol[kc] = getReorderedLeafs(this.leafsPerLevelCol[kc], reordering.permutation.cols);
            }
            this.reorderingActive = true;
        }
        
        this.computeBaseLayout(false);
        this.realizeLayout();
    }


    computeBaseLayout(reset) {

        const getNumTilesPerLevel = (numValuesPerLevel) => {
            let numTiles = [numValuesPerLevel[0]];
            for (let k = 1; k < numValuesPerLevel.length; k++) {
                numTiles[k] = numTiles[k - 1] * numValuesPerLevel[k];
            }
            return numTiles;
        }

        const getInitialSize = (numTilesPerLevel) => {
            let maxNumTiles = numTilesPerLevel[numTilesPerLevel.length - 1];
            return maxNumTiles * LAYOUTPARAMS.tileDesiredPixels;
        }

        const getMinSizePerLevel = (numTilesPerLevel) => {
            let minSizes = [];
            for (let k = 0; k < numTilesPerLevel.length; k++) {
                minSizes.push(LAYOUTPARAMS.tileMinPixels * numTilesPerLevel[k]);
            }
            return minSizes;
        }

        const getCollapsedLeafs = (numTilesPerLevel, leafsFlat) => {
            let leafsPerLevel = {}
            for(let level=0; level<numTilesPerLevel.length; level++){
                leafsPerLevel[level] = [];
                let numTiles = numTilesPerLevel[level];                
                let increment = leafsFlat.length / numTiles;
                for(let i=0; i<numTiles; i++){
                    let leafIdx = i * increment;                    
                    let newLeaf = [];
                    for(let k=0; k<=level; k++){
                        newLeaf.push(deepCopy(leafsFlat[leafIdx][k]))
                    } 
                    leafsPerLevel[level].push(newLeaf);
                }
            }
            return leafsPerLevel
        }

        if (reset) {
            this.baseLayoutConstants = {
                maxNestingDepthRow: this.numValuesPerLevelRow.length,
                numTilesPerLevelRow: getNumTilesPerLevel(this.numValuesPerLevelRow),
                maxNestingDepthCol: this.numValuesPerLevelCol.length,
                numTilesPerLevelCol: getNumTilesPerLevel(this.numValuesPerLevelCol),
            }
            this.baseLayoutConstants.initialSizeRow = getInitialSize(this.baseLayoutConstants.numTilesPerLevelRow);
            this.baseLayoutConstants.initialSizeCol = getInitialSize(this.baseLayoutConstants.numTilesPerLevelCol);
            this.baseLayoutConstants.minSizePerLevelRow = getMinSizePerLevel(this.baseLayoutConstants.numTilesPerLevelRow);
            this.baseLayoutConstants.minSizePerLevelCol = getMinSizePerLevel(this.baseLayoutConstants.numTilesPerLevelCol);

            this.leafsPerLevelRowDefaultOrder = getCollapsedLeafs(this.baseLayoutConstants.numTilesPerLevelRow, this.leafsRow);
            this.leafsPerLevelRow = deepCopy(this.leafsPerLevelRowDefaultOrder);
            this.leafsPerLevelColDefaultOrder = getCollapsedLeafs(this.baseLayoutConstants.numTilesPerLevelCol, this.leafsCol);            
            this.leafsPerLevelCol = deepCopy(this.leafsPerLevelColDefaultOrder);
        }

        const getCurrentSize = (initialSize, zoomValue) => {
            let currentSize = initialSize + zoomValue * LAYOUTPARAMS.zoomIncrementRelative * initialSize;
            return Math.max(currentSize, LAYOUTPARAMS.zoomMinSizePixels);
        }        

        const getVisibility = (currentSize, minSizePerLevel) => {
            let visibility = [true];
            for(let k=1; k<minSizePerLevel.length; k++){               
                visibility.push(currentSize >= minSizePerLevel[k]);                                
            }
            return visibility;

        }

        const getMaxVisibleDepth = (visibility) => {
            for(let k=visibility.length-1; k>=0; k--){
                if(visibility[k]) {
                    return k;
                }
            }            
            throw Error;
        }

        let currentSize_x = getCurrentSize(this.baseLayoutConstants.initialSizeCol, this.interactionState.zoom.x);
        let currentSize_y = getCurrentSize(this.baseLayoutConstants.initialSizeRow, this.interactionState.zoom.y);

        let visibility_cols = getVisibility(currentSize_x, this.baseLayoutConstants.minSizePerLevelCol);
        let visibility_rows = getVisibility(currentSize_y, this.baseLayoutConstants.minSizePerLevelRow);
        let kc = getMaxVisibleDepth(visibility_cols);
        let kr = getMaxVisibleDepth(visibility_rows);

        let nc = this.baseLayoutConstants.numTilesPerLevelCol[kc];       
        let nr = this.baseLayoutConstants.numTilesPerLevelRow[kr];

        let tw = currentSize_x / nc; 
        let th = currentSize_y / nr; 

        let ndra = kr + 1; //getDepth(this.leafsRow);
        let ndca = kc + 1; //getDepth(this.leafsCol);
        
        let ma_x = ndra * LAYOUTPARAMS.annotationHeight;
        let ma_y = ndca * LAYOUTPARAMS.annotationHeight;
        let maw = this.w - ndra * LAYOUTPARAMS.annotationHeight - LAYOUTPARAMS.panControlHeight;
        let mah = this.h - ndca * LAYOUTPARAMS.annotationHeight - LAYOUTPARAMS.panControlHeight;
        
        this.checkResetReordering(kr, kc);

        this.baseLayout = {
            ndra: ndra, // nesting depth row annotations
            ndca: ndca, // nesting depth col annotations
            nr: nr, // number of rows
            nc: nc, // number of cols
            s_x : currentSize_x, // full size in x at current zoom
            s_y : currentSize_y, // full size in y at current zoom
            ma_x: ma_x, // matrix area origin x
            ma_y: ma_y, // matrix area origin y
            maw: maw, // matrix area width 
            mah: mah, // matrix area height
            tw: tw, // tile width
            th: th, // tile height      
            reordered : this.reorderingActive    
        }       

        this.tileManager.setActiveLeafs(this.leafsPerLevelRow[kr], this.leafsPerLevelCol[kc]);
    }


    compute(mode, event) {

        const processPan = (event) => {
            let delta = event.delta;
            
            if(this.layout.s_x > this.layout.maw){
                let dxRel = -delta.x / (this.layout.s_x - this.layout.maw)
                this.interactionState.pan.xRel += dxRel;
                this.interactionState.pan.xRel = Math.max(0, Math.min(1, this.interactionState.pan.xRel));                
            }
            
            if(this.layout.s_y > this.layout.mah){
                let dyRel = -delta.y / (this.layout.s_y - this.layout.mah)
                this.interactionState.pan.yRel += dyRel;
                this.interactionState.pan.yRel = Math.max(0, Math.min(1, this.interactionState.pan.yRel));                
            }
        }

        const processScrollbarPan = (displacementRel) => {
            if(displacementRel.x != 0) {
                this.interactionState.pan.xRel += displacementRel.x;
                this.interactionState.pan.xRel = Math.max(0, Math.min(1, this.interactionState.pan.xRel));                
            }
            if(displacementRel.y != 0) {
                this.interactionState.pan.yRel += displacementRel.y;
                this.interactionState.pan.yRel = Math.max(0, Math.min(1, this.interactionState.pan.yRel));      
            }
        }

        const processWheelZoom = (event) => {
            //console.log(event);
            let delta = event.deltaY > 0 ? -1 : 1;

            if (event.ctrlKey) {
                if (event.altKey) {
                    this.interactionState.zoom.x += delta;
                } else {
                    this.interactionState.zoom.y += delta;
                }
            } else {
                this.interactionState.zoom.x += delta;
                this.interactionState.zoom.y += delta;
            }

            this.interactionState.pan.xRel = 0;
            this.interactionState.pan.yRel = 0;
        }

        const processAnnotationZoom = (event) => {

            if (event.isRows) {
                this.interactionState.zoom.y += 0.2 * event.delta;
            } else {
                this.interactionState.zoom.x += 0.2 * event.delta;
            }
            this.interactionState.pan.xRel = 0;
            this.interactionState.pan.yRel = 0;
        }

        if (mode == "init") {
            this.interactionState = {
                zoom: {
                    x: 0,
                    y: 0
                },
                pan: {
                    x: 0,
                    y: 0,
                    xRel : 0,
                    yRel : 0,
                },
            }
            this.computeBaseLayout(true);
        } else if (mode == "wheelZoom") {
            processWheelZoom(event);
            this.computeBaseLayout(false);
        } else if (mode == "annotationZoom") {
            processAnnotationZoom(event);
            this.computeBaseLayout(false);
        } else if (mode == "tilePan") {
            processPan(event);
        } else if (mode == "scrollbarPan") {
            processScrollbarPan(event);            
        } else {
            throw Error(mode);
        }

        this.realizeLayout();
    }

    get() {
        return this.layout;
    }

    realizeLayout() {

        const getPanState = (currentSize, viewSize) => {
            if(viewSize >= currentSize) {
                return 1;
            } else {
                return viewSize / currentSize;
            }
        }

        this.layout = deepCopy(this.baseLayout);       
        this.layout.tiles = [];
        this.layout.rowAnnotations = [];
        this.layout.colAnnotations = [];

        let startRowIdx = 0;
        let endRowIdx = this.layout.nr;

        let startColIdx = 0;
        let endColIdx = this.layout.nc;
       
        let xRef = this.layout.ma_x - this.interactionState.pan.xRel * (this.layout.s_x - this.layout.maw);        
        let yRef = this.layout.ma_y - this.interactionState.pan.yRel * (this.layout.s_y - this.layout.mah); 
       

        this.layout.pan_wx = getPanState(this.layout.s_x, this.layout.maw);
        this.layout.pan_xRel = this.interactionState.pan.xRel;
        this.layout.pan_wy = getPanState(this.layout.s_y, this.layout.mah);
        this.layout.pan_yRel = this.interactionState.pan.yRel;

        for (let rowIdx = startRowIdx; rowIdx < endRowIdx; rowIdx++) {
            let y = yRef + rowIdx * this.layout.th;
            for (let colIdx = startColIdx; colIdx < endColIdx; colIdx++) {
                let x = xRef + colIdx * this.layout.tw;
                this.layout.tiles.push({
                    x: x,
                    y: y,
                    key: [rowIdx, colIdx]
                });

                // col annotations
                if (rowIdx == startRowIdx) {
                    let annotationStack = this.leafsPerLevelCol[this.layout.ndca-1][colIdx];
                    let annotationStackLayout = [];
                    for (let k = 0; k < this.layout.ndca; k++) {
                        let dims = {};
                        dims.x_min = x;
                        dims.x_max = x + this.layout.tw;
                        dims.y_min = k * LAYOUTPARAMS.annotationHeight;
                        dims.y_max = (k + 1) * LAYOUTPARAMS.annotationHeight;
                        annotationStackLayout.push({
                            content: annotationStack[k],
                            dims: dims,
                            merged: false
                        });
                    }
                    this.layout.colAnnotations.push(annotationStackLayout);
                }
            }

            // row annotations
            let annotationStack = this.leafsPerLevelRow[this.layout.ndra-1][rowIdx];
            let annotationStackLayout = [];
            for (let k = 0; k < annotationStack.length; k++) {
                let dims = {};
                dims.x_min = k * LAYOUTPARAMS.annotationHeight;
                dims.x_max = (k + 1) * LAYOUTPARAMS.annotationHeight;
                dims.y_min = y;
                dims.y_max = y + this.layout.th;;
                annotationStackLayout.push({
                    content: annotationStack[k],
                    dims: dims,
                    merged: false
                });
            }
            this.layout.rowAnnotations.push(annotationStackLayout);
        }

        this.postprocessAnnotations(this.layout.rowAnnotations, true);        
        this.postprocessAnnotations(this.layout.colAnnotations, false);        
    }

    postprocessAnnotations(annotations, isRows) {        
        const haveIdenticalKey = (nodeA, nodeB) => {
            let keyA = nodeA.content[0] + nodeA.content[1];
            let keyB = nodeB.content[0] + nodeB.content[1];
            return keyA == keyB;
        };

        let rootIndicesPrevious = [];
        for(let i=0; i<annotations.length; i++){
            rootIndicesPrevious.push(0);
        }
        
        for (let k = 0; k < annotations[0].length; k++) {
            let rootCounter = 0
            let rootIndices = [];
            let i = 0;

            while(i < annotations.length){            
                rootCounter += 1;
                let root = annotations[i][k];
                let rootIdxPrevious = rootIndicesPrevious[i];
                rootIndices.push(rootCounter);
            
                let i2 = i + 1
                i = i2;
                let canMerge = true;
                while (i2 < annotations.length && canMerge) {
                    let mergeCandidate = annotations[i2][k];
                    canMerge = haveIdenticalKey(root, mergeCandidate); 
                    canMerge &= rootIdxPrevious == rootIndicesPrevious[i2];                  
                    if (canMerge) {
                        mergeCandidate.merged = true;
                        rootIndices.push(rootCounter);
                        if (isRows) {
                            root.dims.y_max = mergeCandidate.dims.y_max;
                        } else {
                            root.dims.x_max = mergeCandidate.dims.x_max;
                        }
                        i = i2 + 1;
                    } else {
                        i = i2;
                    }
                    i2++;
                }                                
            }
            rootIndicesPrevious = rootIndices;
        }
    }
}
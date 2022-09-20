import chroma from "chroma-js";
import { Layout } from '../matrix_layout/layout.js';
import { LAYOUTPARAMS } from './matrix_constants';


export class MainView {
    constructor(viewManager, canvas, paper) {
        this.viewManager = viewManager;
        this.dataManager = viewManager.dataManager;
        this.tileManager = viewManager.tileManager;
        this.canvas = canvas;
        this.width = canvas.width;
        this.height = canvas.height;
        this.paper = paper;
        this.layout = new Layout(this.paper, this.canvas, this.dataManager.selection, this.tileManager, this.dataManager);
        this.canvasBounds = new this.paper.Rectangle(0, 0, this.canvas.width, this.canvas.height);

        paper.setup(canvas);

        this.renderBackground();

        this.tiles = new this.paper.Group();
        this.tiles.bringToFront();        
        this.rowAnnotations = new this.paper.Group();
        this.rowAnnotations.bringToFront();
        this.colAnnotations = new this.paper.Group();
        this.colAnnotations.bringToFront();
        this.errorMessage = new this.paper.Group();

        this.selectionIndicators = new this.paper.Group();
        this.selectionIndicators.bringToFront();
        this.selectionAnimations = new this.paper.Group();
        this.selectionAnimations.bringToFront();
        this.selectionAnimationTimeout = undefined;

        this.panControls = new this.paper.Group();
        this.panControls.bringToFront();                   
        
        this.render();

        let that = this;
        this.tileManager.OnTileDataChanged.add(() => {
            that.render();
        });
    }

    updateSelection(selection) {
        this.layout = new Layout(this.paper, this.canvas, this.dataManager.selection, this.tileManager, this.dataManager);
        this.render();
    }

    updateReordering(reordering){
        this.layout.setReordering(reordering);
        this.render();
    }


    applyTilePan(event) {
        this.layout.compute("tilePan", event);       
        this.render();            
    }

    applyScrollbarPan(event) {
        this.layout.compute("scrollbarPan", event);       
        this.render();            
    }

    applyAnnotationZoom(event, isRows) {   
        let eventArgs = {}
        if(isRows){
            eventArgs.isRows = true;
            eventArgs.delta = event.delta.y;
        } else {
            eventArgs.isRows = false;
            eventArgs.delta = event.delta.x;
        }
        this.layout.compute("annotationZoom", eventArgs);       
        this.render(); 
    }
    
    applyWheelZoom(event) {
        this.layout.compute("wheelZoom", event);       
        this.render(); 
    }

    updateTileSelection() {
        let selectionSymbols = this.selectionIndicators.getItems();
        if (!selectionSymbols) {
            return;
        }
        for (let i = 0; i < selectionSymbols.length; i++) {
            let selectionSymbol = selectionSymbols[i];
            let tileKey = JSON.stringify(selectionSymbol.tileKey);
            if (tileKey in this.tileManager.selectedTiles) {
                selectionSymbol.visible = true;
            } else {
                selectionSymbol.visible = false;
            }
        }
    }

    clearCellSelection() {
        let selections = this.getItem("selections");
        selections.removeChildren();
    }


    isDark(color) {
        if (color == undefined) {
            return false;
        } else {
            return color.luminance() < 0.4;
        }
    }


    renderTiles() {            
        let that = this;
        let channelSettings = this.tileManager.channelSettings;

        // display channel        
        let data1_idx = 0;
        let data2_idx = -1;
        let onlySecond = false;
        if(channelSettings.display == "2"){
            data1_idx = 1;
            onlySecond = true;
        } else if (channelSettings.display == "1_2")
            data2_idx = 1;
        let showSecond = data2_idx != -1;
        
        // display mode
        let useColor = true;
        let useText = true;
        if(channelSettings.displayMode == "color"){
            useText = false;
        } else if (channelSettings.displayMode == "values") {
            useColor = false;
        }        
        
        // color scale
        let scale1 = chroma.scale(channelSettings.scale1);
        let scale2 = chroma.scale(channelSettings.scale2);
        if(onlySecond){
            scale1 = scale2;
        }

        let layout = this.layout.get();      
        this.errorMessage.removeChildren();          
        this.tiles.removeChildren();
        this.selectionIndicators.removeChildren();
        this.selectionAnimations.removeChildren();

        for (let i = 0; i < layout.tiles.length; i++) {
            let t = layout.tiles[i];            
                let r = new this.paper.Rectangle(t.x, t.y, layout.tw, layout.th);

                let symbolItem = this.paper.Path.Rectangle(r)                  
                symbolItem.tileKey = t.key;

                // create selection symbol 
                let selectionSymbol = this.paper.Path.Rectangle(r)
                selectionSymbol.strokeColor = "red"
                selectionSymbol.strokeWidth = 2
                selectionSymbol.tileKey = t.key
                selectionSymbol.visible = false;
                this.selectionIndicators.addChild(selectionSymbol);

                let color0 = undefined;
                if (useColor) {
                    let tileValue = this.tileManager.getValueForTile(symbolItem.tileKey, data1_idx, "tile_color");
                    color0 = scale1(tileValue);
                    symbolItem.fillColor = color0.hex();
                } else {
                    symbolItem.fillColor = "white";
                }              
                symbolItem.strokeColor = "black";                                     
                symbolItem.strokeWidth = 1;
                this.tiles.addChild(symbolItem);

                let color1 = undefined;
                let symbolItem1 = undefined;
                if (showSecond) {
                    if (useColor) {
                        let tileValue = this.tileManager.getValueForTile(symbolItem.tileKey, data2_idx, "tile_color");
                        color1 = scale2(tileValue);
                        let p1 = new this.paper.Point(r.topRight);
                        let p2 = new this.paper.Point(r.bottomRight);
                        let p3 = new this.paper.Point(r.topLeft);
                        let triangle = new this.paper.Path([p1, p2, p3]);
                        triangle.fillColor = color1.hex();
                        triangle.tileKey = t.key;
                        this.tiles.addChild(triangle);
                        symbolItem1 = triangle;

                        let separatorLine = new this.paper.Path.Line(p3, p2);                        
                        separatorLine.strokeWidth = 1;                        
                        if (this.isDark(color1)) {
                            separatorLine.strokeColor = 'white';
                        } else {
                            separatorLine.strokeColor = 'black';
                        }                        
                        this.tiles.addChild(separatorLine);
                    }
                }

                let textItem0 = undefined;
                if (useText) {
                    let text = new this.paper.PointText(new this.paper.Point(t.x, t.y));
                    text.tileKey = t.key;
                    text.justification = 'left';
                    if (this.isDark(color0)) {
                        text.fillColor = 'white';
                    } else {
                        text.fillColor = 'black';
                    }

                    if (showSecond) {
                        text.fontSize = LAYOUTPARAMS.fontSizeTileSmall;
                    } else {
                        text.fontSize = LAYOUTPARAMS.fontSizeTileDefault;
                    }

                    //text.fontWeight = "bold";    
                    let tileValue = this.tileManager.getValueForTile(symbolItem.tileKey, data1_idx, "tile_text");
                    if (tileValue !== undefined) {
                        text.content = String(tileValue);
                        if (showSecond) {
                            text.bounds.bottomLeft = new this.paper.Point(r.bottomLeft.x + 2, r.bottomLeft.y - 2);
                        } else {
                            text.bounds.center = new this.paper.Point(r.center.x, r.center.y);
                        }
                        this.tiles.addChild(text);
                        textItem0 = text;
                    }
                    
                }

                let textItem1 = undefined;
                if (useText && showSecond) {
                    let text = new this.paper.PointText(new this.paper.Point(t.x, t.y));
                    text.tileKey = t.key;
                    text.justification = 'left';
                    if (this.isDark(color1)) {
                        text.fillColor = 'white';
                    } else {
                        text.fillColor = 'black';
                    }
                    text.fontSize = LAYOUTPARAMS.fontSizeTileSmall;

                    let tileValue = this.tileManager.getValueForTile(symbolItem.tileKey, data2_idx, "tile_text");
                    if (tileValue !== undefined) {
                        text.content = String(tileValue);
                        text.bounds.topRight = new this.paper.Point(r.topRight.x - 2, r.topRight.y + 2);
                        this.tiles.addChild(text);
                        textItem1 = text;
                    }
                }
                
                symbolItem.onMouseDrag = function (event) {
                    that.applyTilePan(event);
                };

                const attachSelection = (target, isClick) => {
                    if (!target.tileKey) {
                        return;
                    }                    
                    that.tileManager.setTileSelected(target.tileKey, isClick);                                        
                }

                const onMoveAction = (event) => {
                    if (event.event.shiftKey) {
                        let circle = new that.paper.Path.Circle(new that.paper.Point(event.point), 15)
                        circle.fillColor = "red";
                        circle.opacity = 0.5;
                        if (that.selectionAnimationTimeout) {
                            clearTimeout(that.selectionAnimationTimeout)
                        }
                        that.selectionAnimations.removeChildren();
                        that.selectionAnimations.addChild(circle);
                        that.selectionAnimationTimeout = setTimeout(() => {
                            that.selectionAnimations.removeChildren();
                        }, 500);
                        attachSelection(event.target, false);
                    }
                }

                const onClickAction = (event) => {
                    attachSelection(event.target, true);
                }

                symbolItem.onMouseMove = (event) => {
                    onMoveAction(event);
                }
                symbolItem.onClick = (event) => {
                    onClickAction(event);
                };

                if (symbolItem1) {
                    symbolItem1.onMouseMove = (event) => {
                        onMoveAction(event);
                    }
                    symbolItem1.onClick = (event) => {
                        onClickAction(event);
                    };
                    symbolItem1.onMouseDrag = function (event) {
                        that.applyTilePan(event);
                    };
                }     
                
                if(textItem0 !== undefined){
                    textItem0.onMouseMove = (event) => {
                        onMoveAction(event);
                    }
                    textItem0.onClick = (event) => {
                        onClickAction(event);
                    };
                    textItem0.onMouseDrag = function (event) {
                        that.applyTilePan(event);
                    };
                }

                if(textItem1 !== undefined){
                    textItem1.onMouseMove = (event) => {
                        onMoveAction(event);
                    }
                    textItem1.onClick = (event) => {
                        onClickAction(event);
                    };
                    textItem1.onMouseDrag = function (event) {
                        that.applyTilePan(event);
                    };
                }
            
        }
        this.selectionIndicators.bringToFront();
    }


    renderAnnotations(isRows) {      
        let that = this;  
        let group = undefined;        
        let layout = undefined;
        let layoutBase = this.layout.get();
        if (isRows) {            
            group = this.rowAnnotations;
            layout = layoutBase.rowAnnotations;
        } else {            
            group = this.colAnnotations;
            layout = layoutBase.colAnnotations;
        }
        group.removeChildren();

        for (let i = 0; i < layout.length; i++) {
            for (let k = 0; k < layout[i].length; k++) {
                let currentAnnotation = layout[i][k];
                if (!currentAnnotation.merged) {
                    let x_min = currentAnnotation.dims.x_min;
                    let y_min = currentAnnotation.dims.y_min;
                    let x_max = currentAnnotation.dims.x_max;
                    let y_max = currentAnnotation.dims.y_max;
                    let p1 = new this.paper.Point(x_min, y_min);
                    let p2 = new this.paper.Point(x_max, y_max);
                    let box = this.paper.Path.Rectangle(p1, p2);
                    box.strokeColor = "black";
                    box.fillColor = this.viewManager.colorManager.getPropertyColor(currentAnnotation.content[0]);
                    group.addChild(box)

                    box.onMouseDrag = function (event) {
                        that.applyAnnotationZoom(event, isRows);
                    };

                    let text = new this.paper.PointText(new this.paper.Point(x_min, y_max));
                    text.justification = 'left';
                    text.fillColor = 'black';
                    text.fontWeight = 'bold';
                    text.fontSize = LAYOUTPARAMS.fontSizeAnnotations;
                    //text.fontWeight = "bold";    
                    text.content = currentAnnotation.content[1];
                    if (isRows) {
                        let rotationPoint = new this.paper.Point(text.bounds.center);
                        text.rotate(-90, rotationPoint);
                    }
                    text.bounds.center = new this.paper.Point(box.bounds.center.x, box.bounds.center.y);
                    let overflow = false;
                    if(isRows){
                        overflow = text.bounds.height > box.bounds.height;
                    } else {
                        overflow = text.bounds.width > box.bounds.width;
                    }
                    if(overflow){
                        text.content = ".";
                        text.bounds.center = new this.paper.Point(box.bounds.center.x, box.bounds.center.y);
                    }
                    group.addChild(text);
                }
            }
        }
    }


    renderPanControls() {
        let that = this;

        let layout = this.layout.get();

        this.panControls.removeChildren();
        
        const getSliderWidth = (sizePercentage, sizeSliderFrame) => {
            return Math.max(LAYOUTPARAMS.sliderMinSizePixels, sizePercentage * sizeSliderFrame);
        }

        const getSliderPosition = (frameSize, sliderSize, panRel, rowCol) => {                
            let pos = panRel * (frameSize - sliderSize);
            return pos;

        }

        const getRelativeDisplacement = (delta, sliderSize, frameSize) => {
            return delta  / (frameSize - sliderSize);
        }

        // rows                
        let sliderFrameRows = new this.paper.Path.Rectangle(layout.ma_x + layout.maw, layout.ma_y, LAYOUTPARAMS.panControlHeight, layout.mah);        
        sliderFrameRows.fillColor = LAYOUTPARAMS.panControlBackgroundColor;
        sliderFrameRows.opacity = LAYOUTPARAMS.panControlOpacity;
        this.panControls.addChild(sliderFrameRows);

        let percentageRows = layout.pan_wy;        
        if(percentageRows < 1){
            let sliderHeight = getSliderWidth(percentageRows, sliderFrameRows.bounds.height);
            let sliderPosition = layout.ma_y + getSliderPosition(sliderFrameRows.bounds.height, sliderHeight, layout.pan_yRel, "row");           
            let slider = new this.paper.Path.Rectangle(sliderFrameRows.bounds.x, sliderPosition, LAYOUTPARAMS.panControlHeight, sliderHeight);
            slider.fillColor = LAYOUTPARAMS.sliderColor;
            this.panControls.addChild(slider);    

            slider.onMouseDrag = function (event) {
                let relativeDisplacement = getRelativeDisplacement(event.delta.y, sliderHeight, layout.mah);                
                that.applyScrollbarPan({x:0, y:relativeDisplacement});    
            };
        }        
       
        // columns                    
        let sliderFrameCols = new this.paper.Path.Rectangle(layout.ma_x, layout.ma_y  + layout.mah, layout.maw, LAYOUTPARAMS.panControlHeight);            
        sliderFrameCols.fillColor = LAYOUTPARAMS.panControlBackgroundColor;;
        sliderFrameCols.opacity = LAYOUTPARAMS.panControlOpacity;
        this.panControls.addChild(sliderFrameCols);

        let percentageCols = layout.pan_wx;        
        if(percentageCols < 1){        
            let sliderWidth = getSliderWidth(percentageCols, sliderFrameCols.bounds.width);
            let sliderPosition = layout.ma_x + getSliderPosition(sliderFrameCols.bounds.width, sliderWidth, layout.pan_xRel, "col");
            let slider = new this.paper.Path.Rectangle(sliderPosition, sliderFrameCols.bounds.y, sliderWidth, LAYOUTPARAMS.panControlHeight);
            slider.fillColor = LAYOUTPARAMS.sliderColor;
            this.panControls.addChild(slider);    

            slider.onMouseDrag = function (event) {
                let relativeDisplacement = getRelativeDisplacement(event.delta.x, sliderWidth, layout.maw);                
                that.applyScrollbarPan({x:relativeDisplacement, y:0});
            };            
        } 
        
        // blends
        let blendTopLeft = new this.paper.Path.Rectangle(0, 0, layout.ma_x, layout.ma_y);
        blendTopLeft.fillColor = LAYOUTPARAMS.backgroundColor;
        this.panControls.addChild(blendTopLeft);  

        if(layout.reordered) {
            let text = new this.paper.PointText(new this.paper.Point(0, 0));                    
            text.justification = 'center';                    
            text.fillColor = 'red';
            text.fontSize = 20;
            text.fontWeight = "bold";
            text.content = "R";
            text.bounds.center = new this.paper.Point(blendTopLeft.bounds.center.x, blendTopLeft.bounds.center.y)
            this.panControls.addChild(text);  
        }

        let blendLeftBottom = new this.paper.Path.Rectangle(0, this.height - LAYOUTPARAMS.panControlHeight, layout.ma_x, LAYOUTPARAMS.panControlHeight);
        blendLeftBottom.fillColor = LAYOUTPARAMS.backgroundColor;
        this.panControls.addChild(blendLeftBottom);  

        let blendRightBottom = new this.paper.Path.Rectangle(this.width - LAYOUTPARAMS.panControlHeight, this.height - LAYOUTPARAMS.panControlHeight, LAYOUTPARAMS.panControlHeight, LAYOUTPARAMS.panControlHeight);
        blendRightBottom.fillColor = LAYOUTPARAMS.backgroundColor;
        this.panControls.addChild(blendRightBottom);          

        let blendRightTop = new this.paper.Path.Rectangle(this.width-LAYOUTPARAMS.panControlHeight, 0, LAYOUTPARAMS.panControlHeight, layout.ma_y);
        blendRightTop.fillColor = LAYOUTPARAMS.backgroundColor;
        this.panControls.addChild(blendRightTop);  
    }

    renderBackground() {
        let background = new this.paper.Path.Rectangle(0, 0, this.width, this.height);
        background.fillColor = LAYOUTPARAMS.backgroundColor;       
    }    

    render() {       
        const isOverflow = this.layout.get().tiles.length > LAYOUTPARAMS.tileMaxCount;
        if(isOverflow){
            this.renderErrorMessage();
        } else {            
            this.renderTiles();
            this.renderPanControls();
            this.renderAnnotations(true);
            this.renderAnnotations(false);
            this.updateTileSelection();
        }        
    }

    renderErrorMessage() {
        this.errorMessage.removeChildren();
        this.tiles.removeChildren();
        this.panControls.removeChildren();
        this.selectionIndicators.removeChildren();
        this.selectionAnimations.removeChildren();
        this.rowAnnotations.removeChildren();
        this.colAnnotations.removeChildren();
        let text = new this.paper.PointText(new this.paper.Point(5, 5 + LAYOUTPARAMS.fontSizeErrorMessage));                    
        text.justification = 'left';                    
        text.fillColor = 'red';
        text.fontSize = LAYOUTPARAMS.fontSizeErrorMessage;
        text.content = "Reduce size of row and/or column selection.";
        this.errorMessage.addChild(text);
    }
}


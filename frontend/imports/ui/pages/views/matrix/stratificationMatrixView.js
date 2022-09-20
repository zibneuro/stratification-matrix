import './stratificationMatrixView.html';

import { MainView } from './matrix_views/matrix_main_view.js';
import { Template } from 'meteor/templating';

Template.stratificationMatrix.onCreated(function onCreated() {
    let viewManager = Template.currentData();
    this.viewManager = viewManager;
    this.dataManager = viewManager.dataManager;
    this.tileManager = viewManager.tileManager;
});

Template.stratificationMatrix.onRendered(function onRendered() {
    let that = this;
    const canvas = document.getElementById('matrixCanvas');

    const initCanvas = () => {
        let parentElement = canvas.parentElement.parentElement;
        let width = parentElement.clientWidth;
        let height = parentElement.clientHeight;
        canvas.width = width;
        canvas.height = height;

        if (that.paper) {
            that.paper.remove();
        }
        that.paper = require('paper');

        that.mainView = new MainView(that.viewManager, canvas, that.paper);
    }

    this.viewManager.OnContainerResized.add((container) => {
        if (container.getState().name == "matrix-viewer") {
            that.viewManager.tileManager.clearEvents();
            initCanvas();          
            if(that.mainView){
                that.mainView.updateSelection();
            }
        }
    });    

    this.dataManager.OnMatrixSelectionChanged.add((selection) => {
        if (that.mainView) {
            that.mainView.updateSelection();
        }
    });

    this.dataManager.OnMatrixReordered.add((reordering) => {
        if (that.mainView) {
            that.mainView.updateReordering(reordering);
        }
    });

    this.tileManager.OnTileSelectionChanged.add(() => {
        if (that.mainView) {
            that.mainView.updateTileSelection();
        }
    });    

    initCanvas();

    canvas.addEventListener('wheel',function(event){
        event.preventDefault();
        if(that.mainView) {
            that.mainView.applyWheelZoom(event);
        }        
        return false; 
    }, false);

});

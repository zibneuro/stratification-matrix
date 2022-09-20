export class MatrixView {
    constructor(canvasProps, viewManager) {         
        this.canvasProps = canvasProps;       
        this.viewManager = viewManager;        
        this.init();
    }

    init() {
        this.paper = require('paper');        
        let canvas = document.getElementById(this.canvasProps.name);
        canvas.width = this.canvasProps.width;
        canvas.height = this.canvasProps.height;
        
        this.paper.setup(canvas);   
        this.projectIndex = this.paper.projects.length - 1;
    }

    getItem(itemName){        
        let items = this.paper.projects[this.projectIndex].getItems({name: itemName});
        if (!items.length) {
            throw Error('Item ' + itemName + ' not found.');
        }
        return items[0];
    }

    activate(){
        this.paper.projects[this.projectIndex].activate();
    }

    

}
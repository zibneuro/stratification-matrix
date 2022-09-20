import { ColorManager } from './colorManager';
import { DataManager } from './dataManager';
import { TileManager } from './tileManager';

export class ViewManager {
    constructor() {
        this.views = [];
        this.OnContainerResized = new BABYLON.Observable();
        this.OnTileClicked = new BABYLON.Observable();
        this.OnActiveProfileChanged = new BABYLON.Observable();

        this.dataManager = new DataManager(this);
        this.tileManager = new TileManager(this);
        this.colorManager = new ColorManager(this);
    }


    registerView(view) {
        this.views.push(view);
    }


    notifyClickedTile(tileKey) {
        let tileKeyCopy = JSON.parse(JSON.stringify(tileKey));
        this.OnTileClicked.notifyObservers(tileKeyCopy);
    }


    notifyActiveProfileChanged() {
        this.OnActiveProfileChanged.notifyObservers(this.dataManager.getActiveProfile())
    }


    onResize(container) {
        this.OnContainerResized.notifyObservers(container);
    }
}
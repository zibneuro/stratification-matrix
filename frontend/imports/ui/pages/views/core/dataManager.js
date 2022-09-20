import { deepCopy } from './utilCore.js';

export class DataManager {
    constructor(viewManager) {
        this.viewManager = viewManager;

        this.OnDataChanged = new BABYLON.Observable();        
        this.OnMatrixSelectionChanged = new BABYLON.Observable();
        this.OnMatrixReordered = new BABYLON.Observable();
        this.OnSelectedNeuronsChanged = new BABYLON.Observable();

        this.lastTreeSelection = undefined;        
        this.processSelection(this.lastTreeSelection);
    }

    loadInitialData(callback) {
        let that = this;
        this.getProfiles((profiles) => {
            that.profiles = profiles;
            that.activeProfile = profiles.default_profile;

            let selectedProfile = window.sessionStorage.getItem("default_profile");            
            if(selectedProfile){
                that.activeProfile = selectedProfile;
            }
            
            that.viewManager.notifyActiveProfileChanged();
            callback();
        });
    }

    activateProfile(profileName){
        window.sessionStorage.setItem("default_profile", profileName);
        location.reload();
    }

    processSelection(treeSelection) {
        this.selection = {
            leafsRow : undefined,
            leafsCol : undefined,
            numValuesPerLevelRow : undefined,
            numValuesPerLevelCol : undefined,       
        }

        const emptyRowLeafs = [[["na", "1"]], [["na", "2"]], [["na", "3"]], [["na", "4"]], [["na", "5"]]];
        const emptyColLeafs = [[["na", "1"]], [["na", "2"]], [["na", "3"]], [["na", "4"]], [["na", "5"]], [["na", "6"]], [["na", "7"]], [["na", "8"]]];

        if (treeSelection === undefined) {
            this.selection.leafsRow = emptyRowLeafs;
            this.selection.leafsCol = emptyColLeafs;
            this.selection.numValuesPerLevelRow = [emptyRowLeafs.length];
            this.selection.numValuesPerLevelCol = [emptyColLeafs.length];
            return;
        }

        const getLeafs = (node, filterStack, list) => {
            if (node.functionalDescriptor) {
                filterStack.push([node.functionalDescriptor, node.value])
            }
            if (node.children.length) {
                for (let k = 0; k < node.children.length; k++) {
                    let filterStackCopy = JSON.parse(JSON.stringify(filterStack));
                    getLeafs(node.children[k], filterStackCopy, list);
                }
            } else {
                let filterStackCopy = JSON.parse(JSON.stringify(filterStack));
                list.push(filterStackCopy);
            }
        }

        const getNumValuesPerLevel = (node, numValues) => {
            if (node.children.length) {
                numValues.push(node.children.length);
                getNumValuesPerLevel(node.children[0], numValues);
            }
        }

        if (treeSelection.rows.children.length) {
            this.selection.leafsRow = [];
            this.selection.numValuesPerLevelRow = [];
            getLeafs(treeSelection.rows, [], this.selection.leafsRow);
            getNumValuesPerLevel(treeSelection.rows, this.selection.numValuesPerLevelRow)
        } else {
            this.selection.numValuesPerLevelRow = [emptyRowLeafs.length];
            this.selection.leafsRow = emptyRowLeafs;
        }

        if (treeSelection.cols.children.length) {
            this.selection.leafsCol = [];
            this.selection.numValuesPerLevelCol = [];
            getLeafs(treeSelection.cols, [], this.selection.leafsCol);
            getNumValuesPerLevel(treeSelection.cols, this.selection.numValuesPerLevelCol)
        } else {
            this.selection.numValuesPerLevelCol = [emptyColLeafs.length];
            this.selection.leafsCol = emptyColLeafs;
        }
    }

    setMatrixSelection(selection) {
        this.lastTreeSelection = deepCopy(selection);
        this.processSelection(this.lastTreeSelection);
        this.OnMatrixSelectionChanged.notifyObservers();
    }

    applyMatrixPermutation(permutation) {
        this.OnMatrixReordered.notifyObservers({
            isReset : false,
            permutation : permutation
        });           
    }

    clearMatrixPermutation() {
        this.OnMatrixReordered.notifyObservers({
            isReset : true,
            permutation : undefined
        });
    }

    getActiveProfile() {
        if(this.activeProfile){
            return this.profiles[this.activeProfile]
        } else {
            return undefined;
        }
    }

    getChannelDisplayName(channelIdx) {
        let name = this.getActiveProfile().channels[channelIdx].display_name;
        if(name !== undefined){
            return name;
        } else {
            return "n/a";
        }
    }    

    getMatrixServerURL(endpoint) {
        if (endpoint[0] !== '/') {
            endpoint = '/' + endpoint;
        }
        if (Meteor.settings.public.DEV) {
            return Meteor.settings.public.MATRIX_SERVER_DEV + endpoint;
        } else {
            return Meteor.settings.public.MATRIX_SERVER_PROD + endpoint;
        }
    }

    getMatrixComputeServerURL(endpoint) {
        if (endpoint[0] !== '/') {
            endpoint = '/' + endpoint;
        }
        if (Meteor.settings.public.DEV) {
            return Meteor.settings.public.MATRIX_COMPUTE_SERVER_DEV + endpoint;
        } else {
            return Meteor.settings.public.MATRIX_COMPUTE_SERVER_PROD + endpoint;
        }
    }

    getServerURL(endpoint) {
        if (endpoint[0] !== '/') {
            endpoint = '/' + endpoint;
        }
        if (Meteor.settings.public.DEV) {
            return Meteor.settings.public.SERVER_DEV + endpoint;
        } else {
            return Meteor.settings.public.SERVER_PROD + endpoint;
        }
    }


    /*  ##############################################
                    matrix view queries
        ##############################################        
    */

    getTileData(requestData, callback) {
        HTTP.post(this.getMatrixComputeServerURL('/getTiles'), {data:requestData}, function (error, response) {
            if (error) {
                console.log(error);
            } else {
                let tileData = JSON.parse(response.content);
                //console.log(tileData);
                callback(tileData);
            }
        });
    }

    getSamples(requestData, callback) {
        HTTP.post(this.getMatrixComputeServerURL('/getSamples'), {data:requestData}, function (error, response) {
            if (error) {
                console.log(error);
            } else {
                let samples = JSON.parse(response.content);
                callback(samples);
            }
        });
    }
    
    getProfiles(callback) {
        HTTP.post(this.getMatrixServerURL('/getProfiles'), { data: {} }, function (error, response) {
            if (error) {
                console.log(error);
            } else {
                let profiles = JSON.parse(response.content);
                callback(profiles);
            }
        });
    }
}
import './treeView.html';
import 'react-complex-tree/lib/style.css';

import { Template } from 'meteor/templating';
import React, { useState } from 'react';
import { ControlledTreeEnvironment, Tree } from 'react-complex-tree';
import TreeModel from 'tree-model';
import parse from "html-react-parser";

import { deepCopy } from './core/utilCore.js';


const styleObj = {
    fontSize: 10
}

const stylePropertyRootNode = {
    fontSize: 14,
    fontStyle: "italic",
}

const styleItemTitle = {
    fontSize: 14,
}

const styleItemCount = {
    textAlign: "right",
    fontSize: 14,
}

const styleItemCheckbox = {
    textAlign: "right",
    fontSize: 14,
}

const styleTreeColumn = {
    overflowY: 'auto',
    float: 'left',
    width: '100%',
    height: '750px',
    position: 'relative'
};

function getParentNode(node){
    let path = node.getPath();
    if(path.length > 1){
        return path[path.length-2];
    } else {
        return undefined;
    }
}

function getNumEnabledChildren(node) {
    let numEnabled = 0;
    for(let i=0; i<node.children.length; i++){
        if(node.children[i].model.isSelected){
            numEnabled += 1;
        }
    }
    return numEnabled;
}

class TreeViewer extends React.Component {
    constructor(props) {
        super(props);

        this.viewManager = props.data;
        this.dataManager = this.viewManager.dataManager;

        this.dataModel = new TreeModel();
        this.dataModelRoot = this.dataModel.parse({ name: 'root', children: [{ name: 'row_selection_tree_root' }, { name: 'col_selection_tree_root' }] });

        this.populateSelectionProperties("row");
        this.populateSelectionProperties("col");

        this.state = {
            viewState: {
                row_selection_tree: { focusedItem: undefined, expandedItems: ["row_selection_tree_root"], selectedItems: [] },
                col_selection_tree: { focusedItem: undefined, expandedItems: ["col_selection_tree_root"], selectedItems: [] },
            },
            items: this.getTreeItems(),
            message : "",
            filterQuery: {}
        }

        this.userItemCount = 0
    }

    cloneNode(existingNodeName) {
        let nodeData = this.getNode(existingNodeName).model;
        let newNodeData = {
            name: this.userItemCount.toString(),
            functionalDescriptor: nodeData.functionalDescriptor,
            nodeType: nodeData.nodeType,
            displayName: nodeData.displayName,
            symbol: nodeData.symbol
        }
        this.userItemCount += 1;
        let newNodeModel = new TreeModel();
        let newNode = newNodeModel.parse(newNodeData);
        return newNode;
    }

    forceItemUpdate() {
        this.setState((state, props) => {
            state.items = this.getTreeItems();
            return state;
        });
    }


    getTreeOfNode(node) {
        if (node.model.name == "root") {
            return "n/a";
        } else if (node.model.name == "row_selection_tree_root") {
            return "row_selection_tree";
        } else if (node.model.name == "col_selection_tree_root") {
            return "col_selection_tree";
        } else {
            let path = node.getPath();
            let subtreeRoot = path[1].model.name;
            if (subtreeRoot == "row_selection_tree_root") {
                return "row_selection_tree";
            } else if (subtreeRoot == "col_selection_tree_root") {
                return "col_selection_tree";
            } else {
                throw Error(subtreeRoot);
            }
        }
    }

    getNodesByDisplayNames(rootNode, displayNames) {
        let nodeByDisplayName = {};
        for (let i = 0; i < displayNames.length; i++) {
            nodeByDisplayName[displayNames[i]] = undefined;
        }
        rootNode.walk(node => {
            let displayName = node.model.displayName;
            if (displayNames.indexOf(displayName) != -1) {
                if (!nodeByDisplayName.displayName) {
                    nodeByDisplayName[displayName] = node.model.name;
                }
            }
        });
        return nodeByDisplayName;
    }


    getTreeItems() {
        //console.log("--- get tree items ---");

        let items = {};

        const nodeHasButton = (nodeType) => {
            if (nodeType == "property_categorical_root") {
                return true;
            } else if (nodeType == "property_categorical_value") {
                return true;
            } else {
                return false;
            }
        }

        this.getNode("root").walk((node) => {
            let displayName = node.model.displayName;
            if (!displayName) {
                displayName = "n/a";
            }
            let symbol = node.model.symbol;
            if (!symbol) {
                symbol = "";
            }

            let data = {
                symbol: symbol,
                displayName: displayName,
                name: node.model.name,
                nodeType: node.model.nodeType,
                hasButton: nodeHasButton(node.model.nodeType),
                isSelected: node.model.isSelected,
                functionalDescriptor: node.model.functionalDescriptor,
                count: node.model.count,
                tree: this.getTreeOfNode(node),
            }
            let children = []
            for (let i = 0; i < node.children.length; i++) {
                let childNode = node.children[i];
                children.push(childNode.model.name);
            }
            let hasChildren = true;
            if (!children.length) {
                children = undefined;
                hasChildren = false;
            }

            items[node.model.name] = {
                index: node.model.name,
                title: node.model.name,
                data: data,
                hasChildren: hasChildren,
                children: children,
                canRename: false,
                canMove: true,
            }

        });
        return items;
    }

    getNode(name) {
        return this.dataModelRoot.first((node) => { return node.model.name == name });
    }

    getRegionsAsTreeModel(regions) {
        let treeData = {
            name: "regionsRoot",
            nodeType: "header",
            displayName: "<b>Regions</b>",
        }

        let getRegionColorSymbol = (node) => {
            this.nodeManager.pathManager.regionColors[node.name] = [node.color, node.alpha];
            return `<svg style=\"width: 13; height: 13; margin-right: 2\"><circle cx=6 cy=6 r=5.5 fill=${node.color} fill-opacity=${node.alpha} /></svg>`
        }

        let getProperties = (node) => {
            return {
                name: node._id,
                nodeType: "predicatedEntity",
                hasButton: true,
                functionalDescriptor: node.name,
                symbol: getRegionColorSymbol(node),
                displayName: node.name,
            }
        }

        let traverse = (node) => {
            let tree = getProperties(node);
            if (node.children) {
                tree.children = []
                for (let i = 0; i < node.children.length; i++) {
                    tree.children.push(traverse(node.children[i]));
                }
            }
            return tree;
        }

        treeData.children = [traverse(regions)];

        let regionsSubtree = new TreeModel();
        let regionsRootNode = regionsSubtree.parse(treeData);
        return regionsRootNode;
    }


    getPropertySubtreeCategorical(propertyMeta, rowCol) {

        let subtreeData = {
            name: propertyMeta.name + "_" + rowCol,
            nodeType: "property_categorical_root",
            functionalDescriptor: propertyMeta.name,
            displayName: propertyMeta.display_name,
            children: [],
            isSelected: false,
        }

        for (let i = 0; i < propertyMeta.values.length; i++) {
            let value_name = propertyMeta.values[i];
            let child = {
                name: propertyMeta.name + "_" + value_name + "_" + rowCol,
                nodeType: "property_categorical_value",
                functionalDescriptor: value_name,
                displayName: value_name,
                isSelected: false,
            }
            subtreeData.children.push(child);
        }

        let subtree = new TreeModel();
        return subtree.parse(subtreeData);
    }

    populateSelectionProperties(rowCol) {
        let root = this.getNode(rowCol + "_selection_tree_root");

        const rowSelectionRootData = {
            name: "row_selection_root",
            nodeType: "header_node",
            symbol: "&#8649;",
            displayName: "<b>row selection</b>",
        }
        
        const colSelectionRootData = {
            name: "col_selection_root",
            nodeType: "header_node",
            symbol: "&#8650;",
            displayName: "<b>column selection</b>",
        }

        if(rowCol == "row"){
            let header = new TreeModel();
            root.addChild(header.parse(rowSelectionRootData))
        } else {
            let header = new TreeModel();
            root.addChild(header.parse(colSelectionRootData))
        }


        const profile = this.dataManager.getActiveProfile();
        for (let i = 0; i < profile.selection_properties.length; i++) {
            let propertyMeta = profile.selection_properties[i];
            if (propertyMeta.property_type == "categorical") {
                root.addChild(this.getPropertySubtreeCategorical(propertyMeta, rowCol))
            } else {
                throw Error()
            }
        }

        let terminal = new TreeModel();
        root.addChild(terminal.parse({name:rowCol + "_terminal_node", nodeType:"terminal_node", functionalDescriptor:"", displayName:"foo"}))
    }


    onFocusItem(item) {
        return;       
    }

    getCollapsedOperatorNodes(expandedItems) {
        let collapsedNodes = [];
        try {
            let queryRootNode = this.getNode("queryRoot");
            queryRootNode.walk((node) => {
                if (node.model.functionalDescriptor == "union" || node.model.functionalDescriptor == "intersect") {
                    let nodeName = node.model.name;
                    if (expandedItems.indexOf(nodeName) == -1) {
                        collapsedNodes.push(nodeName);
                    }
                }
            });
        } catch (e) {
            console.log(e);
        }
        return collapsedNodes;
    }

    onExpandItem(item) {
        let tree = item.data.tree;
        this.setState((state, props) => {
            let expandedItems = state.viewState[tree].expandedItems;
            state.viewState[tree].expandedItems = [...expandedItems, item.index];
            return state;
        });
    }

    onCollapsedItem(item) {
        let tree = item.data.tree;
        this.setState((state, props) => {
            let expandedItems = state.viewState[tree].expandedItems;
            state.viewState[tree].expandedItems = expandedItems.filter(expandedItemIndex => expandedItemIndex !== item.index);
            return state;
        });
    }

    canDropAt(items, target) {        
        try {            
            /*
            if (target.targetType !== "between-items") {
                return false;
            }*/
            if(items.length != 1){
                return false;
            }            
            let sourceNode = this.getNode(items[0].data.name);             
            if(sourceNode.model.nodeType.indexOf("property_") == -1){
                return false;
            } else {
                return true;
            }   
            /*
            let sourceNodeParent = getParentNode(sourceNode);
            let targetNodeParent = this.getNode(target.parentItem);
            if(sourceNodeParent !== targetNodeParent){
                return false;                
            }
            //console.log("can drop", target.parentItem, target.childIndex);
            return true;            
            */
        } catch (e) {
            console.log(e);
            return false;
        }        
    }

    onDrop(items, target) {
        console.log("do drop", target);
        try {
            let sourceNode = this.getNode(items[0].data.name);  
            let sourceNodeParent = getParentNode(sourceNode);
            let sourceIndex = sourceNode.getIndex();            
            
            if(target.targetType == "between-items"){                
                let targetNodeParent = this.getNode(target.parentItem);
                if(sourceNodeParent !== targetNodeParent){
                    return;                
                }
                let targetIndex = target.childIndex;
                if(sourceIndex < targetIndex){
                    targetIndex -= 1;
                }
                if(sourceNode.model.nodeType == "property_categorical_root" && targetIndex == 0){                    
                    return; // drop on header
                }
                sourceNode.setIndex(targetIndex);
                this.forceItemUpdate();
                this.updateFilterQuery();

            } else if (target.targetType == "item") {
                //console.log("nonstandard", target);
                let targetNode = this.getNode(target.targetItem);
                let targetNodeParent = getParentNode(targetNode);
                if(sourceNodeParent !== targetNodeParent){
                    return;                
                }
                let targetIndex = targetNode.getIndex();                
                if(sourceNode.model.nodeType == "property_categorical_root" && targetIndex == 0){                    
                    return; // drop on header
                }
                if(targetNode.model.nodeType == "terminal_node"){
                    targetIndex -= 1; // drop on terminal node
                }
                //console.log("before", sourceIndex, targetIndex);
                sourceNode.setIndex(targetIndex);
                //console.log("after", sourceNode.getIndex(), targetNode.getIndex());
                this.forceItemUpdate();
                this.updateFilterQuery();
            } else {
                console.log("unknown targetType", target.targetType)
            }
                                
        } catch (e) {
            console.log(e);
        }
    }

    onRenameItem(item, name, treeId) {
        return;
    }

    updateFilterQuery() {
        const getLinearFilters = (rootNode) => {
            let filters = [];
            if (!rootNode.children) {
                return filters;
            }
            for (let i = 0; i < rootNode.children.length; i++) {
                let filterEntry = {}
                let propertyRootNode = rootNode.children[i];
                filterEntry.functionalDescriptor = propertyRootNode.model.functionalDescriptor;
                filterEntry.values = [];
                for (let k = 0; k < propertyRootNode.children.length; k++) {
                    let valueNode = propertyRootNode.children[k];
                    if (valueNode.model.isSelected) {
                        filterEntry.values.push(valueNode.model.functionalDescriptor)
                    }
                }
                if (filterEntry.values.length) {
                    filters.push(filterEntry);
                }
            }
            return filters;
        }

        const getNumLeafs = (filterEntries) => {
            if(filterEntries.length == 0){
                return 0;
            }
            let count = 1;
            for(let i=0; i<filterEntries.length; i++){
                count *= filterEntries[i].values.length;
            }
            return count;
        }

        const convertToTreeLayout = (filters, isRoot) => {
            if (isRoot) {
                let root = { children: convertToTreeLayout(filters, false) };
                return root;
            } else {
                if (!filters.length) {
                    return [];
                }
                let remainingFilters = []
                for (let k = 1; k < filters.length; k++) {
                    remainingFilters.push(filters[k]);
                }
                let children = convertToTreeLayout(remainingFilters, false)
                let nodes = []
                let functionalDescriptor = filters[0].functionalDescriptor;
                let values = filters[0].values;
                for (let k = 0; k < values.length; k++) {
                    nodes.push({
                        functionalDescriptor: functionalDescriptor,
                        value: values[k],
                        children: children
                    });
                }
                return nodes;
            }

        }

        let rootRows = this.getNode("row_selection_tree_root");
        let rootCols = this.getNode("col_selection_tree_root");

        let selection = {};
        
        let linearFiltersRow = getLinearFilters(rootRows);
        let linearFiltersCol = getLinearFilters(rootCols);
        let numLeafsRow = getNumLeafs(linearFiltersRow);
        let numLeafsCol = getNumLeafs(linearFiltersCol);        
        //let numMatrixCells = numLeafsRow * numLeafsCol;
        let message = "expanded rows: " + numLeafsRow.toString() + "; expanded columns: " + numLeafsCol.toString();        

        this.setState((state, props) => {
            state.message = message;
            return state;
        });

        selection.rows = convertToTreeLayout(linearFiltersRow, true);
        selection.cols = convertToTreeLayout(linearFiltersCol, true);

        this.dataManager.setMatrixSelection(selection);
    }

    getChildRegions(node) {
        let regions = [];
        try {
            node.walk((node) => {
                if (node.model.nodeType == "predicatedEntity") {
                    let isLeft = false;
                    let isRight = false;
                    //console.log("node", node);
                    if (node.children) {
                        for (let i = 0; i < node.children.length; i++) {
                            let childNode = node.children[i];
                            if (childNode.model.nodeType != "predicate") {
                                throw Error
                            }
                            isLeft |= childNode.model.functionalDescriptor == "leftHemisphere";
                            isRight |= childNode.model.functionalDescriptor == "rightHemisphere";
                        }
                    }
                    let newRegions = this.nodeManager.pathManager.getPathNodesLeftRight(isLeft, isRight, node.model.displayName);
                    for (let i = 0; i < newRegions.length; i++) {
                        let newRegion = newRegions[i];
                        if (regions.indexOf(newRegion) == -1) {
                            regions.push(newRegion);
                        }
                    }

                }
            });
        } catch (e) {
            console.log(e);
        }
        return regions;
    }

    updateSelectedNodes(selectedItems) {
        let itemChildRegions = {}
        if (selectedItems) {
            for (let i = 0; i < selectedItems.length; i++) {
                let item = selectedItems[i]
                itemChildRegions[item] = this.getChildRegions(this.getNode(item));
            }
        }
        try {
            this.nodeManager.setSelectedTreeItems(deepCopy(selectedItems));
        } catch (e) {
            console.log(e);
        }
        try {
            this.nodeManager.updateContours(itemChildRegions);
        } catch (e) {
            console.log(e);
        }
    }

    onSelectItems(items) {
        return;
    }


    onClickCheckbox(event) {
        let node = this.getNode(event.target.id);
        node.model.isSelected = event.target.checked;

        if(node.model.nodeType == "property_categorical_root"){
           for(let i=0; i<node.children.length; i++){
            node.children[i].model.isSelected = event.target.checked;
           } 
        } else if (node.model.nodeType == "property_categorical_value") {
            let parentNode = getParentNode(node);
            parentNode.model.isSelected = Boolean(getNumEnabledChildren(parentNode));            
        }

        this.forceItemUpdate();
        this.updateFilterQuery();
    }


    onRenderItem(item) {

        const getCount = data => {
            if (typeof data.count !== "undefined") {
                if (data.count == -1) {
                    return parse("&#9888;")
                } else {
                    return data.count;
                }
            } else {
                return "";
            }
        }

        const getSymbol = (symbolString) => {
            if (!symbolString) {
                return ""
            } else {
                return parse(symbolString)
            }
        }

        const getSymbolCol = (symbolString) => {
            if (symbolString) {
                return <col style={{ width: "20px" }}></col>
            } else {
                return <col></col>
            }
        }

        const truncateDisplayName = (name) => {
            if (name.includes("<")) {
                return name;
            }
            if (name.length < 25) {
                return name;
            }
            let shortened = "";
            for (let i = 0; i < 5; i++) {
                shortened += name[i];
            }
            shortened += "..."
            for (let i = 15; i >= 1; i--) {
                shortened += name[name.length - i]
            }
            return shortened;
        }

        const getNumSelectedString = (nodeName) => {
            let node = this.getNode(nodeName);
            let numEnabled = getNumEnabledChildren(node);
            let numChildren = node.children.length;
            return String(numEnabled) + "/" + String(numChildren);
        }

        const getColorSymbol = (propertyType) => {            
            let color = this.viewManager.colorManager.getPropertyColor(propertyType);
            return <div style={{width:"13px", height:"13px", background:color}}></div>;
        }

        let data = item.item.data;
        if (data.nodeType == "property_categorical_root") {
            return <table style={{ width: "100%" }}>
                <colgroup>                    
                    <col style={{ width: "20px" }}></col>
                    <col></col>                    
                    <col></col>                    
                </colgroup>
                <tbody >
                    <tr>
                    <td>{getColorSymbol(data.functionalDescriptor)}</td>
                    <td style={stylePropertyRootNode}>{parse(truncateDisplayName(data.displayName))}</td>                    
                    <td style={styleItemCheckbox}>{getNumSelectedString(data.name)} <input type="checkbox" onChange={this.onClickCheckbox.bind(this)} id={data.name} checked={data.isSelected} /></td></tr>
                </tbody>
            </table>
        } else if (data.nodeType == "property_categorical_value") {
            return <table style={{ width: "100%" }}>
                <colgroup>
                    {getSymbolCol(data.symbol)}
                    <col></col>
                    <col></col>
                </colgroup>
                <tbody >
                    <tr><td style={styleItemTitle}>{getSymbol(data.symbol)}</td><td style={styleItemTitle}>{parse(truncateDisplayName(data.displayName))}</td><td style={styleItemCheckbox}><input type="checkbox" onChange={this.onClickCheckbox.bind(this)} id={data.name} checked={data.isSelected} /></td></tr>
                </tbody>
            </table>
        } else if (data.nodeType == "terminal_node") {
            return <table style={{ width: "100%" }}>
                <colgroup>                   
                    <col></col>
                </colgroup>
                <tbody >
                    <tr>
                        <td><div></div></td>
                    </tr>                    
                </tbody>
            </table>
        } else {
            return <table style={{ width: "100%" }}>
                <colgroup>
                    {getSymbolCol(data.symbol)}
                    <col></col>
                    <col></col>
                </colgroup>
                <tbody >
                    <tr ><td style={styleItemTitle}>{getSymbol(data.symbol)}</td><td style={styleItemTitle}>{parse(truncateDisplayName(data.displayName))}</td><td style={styleItemCount}>{getCount(data)}</td></tr>
                </tbody>
            </table>
        }
    }

    render() {

        let formatQuery = (query) => {
            let keys = Object.keys(query);
            keys.sort();
            let rows = []
            for (let i = 0; i < keys.length; i++) {
                let key = keys[i]
                let item = <tr key={"q" + i.toString()}><td>{key}</td><td>{query[key]}</td></tr>
                rows.push(item)
            }
            return <table style={styleObj}><tbody>{rows}</tbody></table>
        }

        return <table style={{ width: '100%', height: "1000px" }}><tbody>
            <tr><td style={{ textAlign: "top", verticalAlign: "top", textAnchor: "top" }}>
            <ControlledTreeEnvironment
                items={this.state.items}
                viewState={this.state.viewState}
                getItemTitle={item => item.data.displayName}
                renderItemTitle={this.onRenderItem.bind(this)}

                defaultInteractionMode={'click-arrow-to-expand'}
                onFocusItem={this.onFocusItem.bind(this)}
                onExpandItem={this.onExpandItem.bind(this)}
                onCollapseItem={this.onCollapsedItem.bind(this)}
                onSelectItems={this.onSelectItems.bind(this)}
                onDrop={this.onDrop.bind(this)}
                onRenameItem={this.onRenameItem.bind(this)}

                canDropAt={this.canDropAt.bind(this)}
                canDropOnItemWithoutChildren={true}
                canDropOnItemWithChildren={true}
                canDragAndDrop={true}
                canReorderItems={true}>

                <table style={{ width: '100%' }}>
                    <colgroup>
                        <col style={{ width: '50%' }}></col>
                        <col style={{ width: "50%" }}></col>
                    </colgroup>
                    <tbody>                     
                        <tr>
                            <td style={{ textAlign: "top", verticalAlign: "top", textAnchor: "top" }}><div style={styleTreeColumn}><Tree treeId="row_selection_tree" rootItem="row_selection_tree_root" /></div>
                            </td>
                            <td style={{ textAlign: "top", verticalAlign: "top", textAnchor: "top" }}><div style={styleTreeColumn}><Tree treeId="col_selection_tree" rootItem="col_selection_tree_root" /></div></td>
                        </tr>
                        <tr>
                            <td style={styleItemTitle} colSpan={2}>{parse(this.state.message)}</td>
                        </tr>
                    </tbody>
                </table>
            </ControlledTreeEnvironment>
        </td>
        </tr>           
        </tbody>
        </table>
    }
}


Template.treeView.onCreated(function () {
    this.viewManager = Template.currentData();
});


Template.treeView.helpers({
    TreeViewer() {
        return TreeViewer;
    },

    viewManager() {
        return Template.instance().viewManager;
    }
});




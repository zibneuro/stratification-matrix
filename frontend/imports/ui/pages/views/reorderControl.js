import './matrix/matrix.css'
import React, { useState } from 'react';

var reorder = require('/lib/reorder.js');

const styleDefault = {
    fontSize: 14,
}


export class ReorderControl extends React.Component {
    constructor(props) {
        super(props);

        this.viewManager = props.data;
        this.dataManager = this.viewManager.dataManager;
        this.tileManager = this.viewManager.tileManager;
        this.activeProfile = this.viewManager.dataManager.getActiveProfile();
        this.hasSecond = this.activeProfile.channels.length > 1;

        this.state = {
            targetValue: "1",
            reorderMode: "rows_cols"
        }
    }

    onChangeTargetValue(event) {
        this.setState((state, props) => {
            state.targetValue = event.target.value;
            return state;
        });
    }

    onChangeReorderMode(event) {
        this.setState((state, props) => {
            state.reorderMode = event.target.value;
            return state;
        });
    }


    flip(isRows) {

        const getInvertedIndices = (numIndices) => {
            let invertedIndices = [];
            for (let i = numIndices - 1; i >= 0; i--) {
                invertedIndices.push(i);
            }
            return invertedIndices;
        }

        try {
            let mat = this.tileManager.getValuesFlat(0);            

            if (!this.isValidData(mat)) {
                return;
            }

            let numRows = mat.length;
            let numCols = mat[0].length;
            let permutation = {
                rows: undefined,
                cols: undefined,
            }

            if (isRows) {
                permutation.rows = getInvertedIndices(numRows);
            } else {
                permutation.cols = getInvertedIndices(numCols);
            }

            this.dataManager.applyMatrixPermutation(permutation);

        } catch (e) {
            console.log(e);
        }

    }

    isValidData(matrix) {
        if (matrix.length == 0) {
            return false;
        }
        if (matrix[0].length == 0) {
            return false;
        }
        return true
    }

    reorderMatrix() {
        try {

            const getAbsDelta = (mat1, mat2) => {
                let rows = []
                let numRows = mat1.length;
                let numCols = mat1[0].length;
                for (let i = 0; i < numRows; i++) {
                    let cols = [];
                    for (let j = 0; j < numCols; j++) {
                        cols.push(Math.abs(mat1[i][j] - mat2[i][j]));
                    }
                    rows.push(cols);
                }
                return rows;
            }

            let mat = undefined;
            if (this.state.targetValue == "1") {
                mat = this.tileManager.getValuesFlat(0);
            } else if (this.state.targetValue == "2") {
                mat = this.tileManager.getValuesFlat(1);
            } else if (this.state.targetValue == "absdiff_1_2") {
                let mat1 = this.tileManager.getValuesFlat(0);
                let mat2 = this.tileManager.getValuesFlat(1);
                mat = getAbsDelta(mat1, mat2);
            }

            if (!this.isValidData(mat)) {
                return;
            }

            let matRows = mat;
            let matCols = reorder.transpose(matRows);

            // algorithm
            var leafOrder = reorder.optimal_leaf_order(); //.distance(reorder.distance.manhattan)

            let permutationRows = leafOrder(matRows);
            let permutationCols = leafOrder(matCols);

            let permutation = {
                rows: undefined,
                cols: undefined
            }

            if(this.state.reorderMode == "rows") {
                permutation.rows = permutationRows;
            } else if (this.state.reorderMode == "cols") {
                permutation.cols = permutationCols;
            } else if (this.state.reorderMode == "rows_cols") {
                permutation.rows = permutationRows;
                permutation.cols = permutationCols;
            } else {
                throw Error
            }

            this.dataManager.applyMatrixPermutation(permutation);

        } catch (e) {
            console.log(e);
        }
    }

    clear() {
        this.dataManager.clearMatrixPermutation();
    }

    render() {

        const getTargetValueRadioButtons = () => {
            return <div style={styleDefault}>
                <table>
                    <tbody>
                        <tr>
                            <td colSpan={3}>auto-reorder based on channel:</td>
                        </tr>
                        <tr>
                            <td>
                                <label>
                                    <input type="radio" value="1" name="targetValue" onChange={this.onChangeTargetValue.bind(this)} checked={this.state.targetValue == "1"} /> 1
                                </label>
                            </td>
                            <td style={{ paddingLeft: 15 }}>
                                <label>
                                    <input type="radio" value="2" name="targetValue" onChange={this.onChangeTargetValue.bind(this)} checked={this.state.targetValue == "2"} disabled={!this.hasSecond} /> 2
                                </label>
                            </td>
                            <td style={{ paddingLeft: 15 }}>
                                <label>
                                    <input type="radio" value="absdiff_1_2" name="targetValue" onChange={this.onChangeTargetValue.bind(this)} checked={this.state.targetValue == "absdiff_1_2"} disabled={!this.hasSecond} /> |1-2|
                                </label>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        }

        const getReorderModeRadioButtons = () => {
            return <div style={styleDefault}>
                <table>
                    <tbody>
                        <tr>
                            <td colSpan={3}>auto-reorder mode:</td>
                        </tr>
                        <tr>
                            <td>
                                <label>
                                    <input type="radio" value="rows" name="reorderMode" onChange={this.onChangeReorderMode.bind(this)} checked={this.state.reorderMode == "rows"} /> rows
                                </label>
                            </td>
                            <td style={{ paddingLeft: 15 }}>
                                <label>
                                    <input type="radio" value="cols" name="reorderMode" onChange={this.onChangeReorderMode.bind(this)} checked={this.state.reorderMode == "cols"} /> columns
                                </label>
                            </td>
                            <td style={{ paddingLeft: 15 }}>
                                <label>
                                    <input type="radio" value="rows_cols" name="reorderMode" onChange={this.onChangeReorderMode.bind(this)} checked={this.state.reorderMode == "rows_cols"} /> both
                                </label>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        }

        return <table>
            <tbody>
                <tr>
                    <td>
                        {getTargetValueRadioButtons()}
                    </td>
                </tr>
                <tr>
                    <td>
                        {getReorderModeRadioButtons()}
                    </td>
                </tr>
                <tr>
                    <td>
                        <table>
                            <tbody>
                                <tr>
                                    <td>
                                        <button className='matrixButton' onClick={this.reorderMatrix.bind(this)}>auto-reorder</button>
                                    </td>                                    
                                    <td>
                                        <button className='matrixButton' onClick={this.flip.bind(this, true)}>flip rows</button>
                                    </td>
                                    <td>
                                        <button className='matrixButton' onClick={this.flip.bind(this, false)}>flip columns</button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </td>
                </tr>
                <tr>
                    <td>
                        <table>
                            <tbody>
                                <tr>                                   
                                    <td>
                                        <button className='matrixButton' onClick={this.clear.bind(this)}>clear reordering</button>
                                    </td>                                    
                                </tr>
                            </tbody>
                        </table>
                    </td>
                </tr>
            </tbody>
        </table>
    }
}
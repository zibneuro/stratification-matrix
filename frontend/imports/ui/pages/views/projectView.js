import './projectView.html'
import { Template } from 'meteor/templating';
import React, { useState } from 'react';
import { deepCopy } from './core/utilCore';
import './matrix/matrix.css'

const styleMenuHeader = {
    fontSize: 14,
    fontWeight: "bold",
}

const styleDefault = {
    fontSize: 14,
}

const styleButton = {
    borderWidth: 1
}

class ProjectControl extends React.Component {
    constructor(props) {
        super(props);

        this.viewManager = props.data;
        this.dataManager = this.viewManager.dataManager;
        this.profiles = this.dataManager.profiles;        
    }

    onColorscaleChanged(idx, event) {        
        this.setState((state, props) => {
            state[idx].scale = event;
            this.tileManager.setChannelSettings(deepCopy(state));
            return state;
        });
    }

    onCheckboxColorChanged(idx, event) {
        this.setState((state, props) => {
            state[idx].useColor = event.target.checked;
            this.tileManager.setChannelSettings(deepCopy(state));            
            return state;
        });
    }

    onCheckboxUseTextChanged(idx, event) {
        this.setState((state, props) => {
            state[idx].useText = event.target.checked;
            this.tileManager.setChannelSettings(deepCopy(state));
            return state;
        });
    }

    onActivateProfile(profileName) {
        this.dataManager.activateProfile(profileName);
    }

    getProfilesForRendering() {
        let profileNames = [];
        let profileKeys = Object.keys(this.profiles);
        for (let i = 0; i < profileKeys.length; i++) {
            if (profileKeys[i] != "default_profile") {
                profileNames.push(profileKeys[i]);
            }
        }
        
        let rows = []
        for (let i = 0; i < profileNames.length; i++) {
            let profileName = profileNames[i];
            rows.push(
                <tr key={i}>
                    <td>
                        <table>
                            <tbody>
                                <tr>
                                    <td>
                                        <button onClick={this.onActivateProfile.bind(this, profileName)} className="matrixButton">
                                            activate
                                        </button>
                                    </td>
                                    <td>
                                        <div style={{ paddingLeft: 10 }}>{this.profiles[profileName].display_name}</div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </td>
                </tr>
            );
        }
        return rows;
    }

    render() {
        return <table>
            <tbody style={styleDefault}>
                <tr>
                    <td>
                        <div className='badge badge-secondary matrixHeader'>
                            active project
                        </div>
                        
                    </td>
                </tr>
                <tr>
                    <td>
                        <table>
                            <tbody>
                                <tr>
                                    <td>
                                        &#10004;
                                    </td>
                                    <td>
                                        <div style={{ paddingLeft: 10 }}>{this.dataManager.getActiveProfile().display_name}</div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </td>
                </tr>
                <tr>
                    <td>
                        <div style={{ marginTop: 20 }} className='badge badge-secondary matrixHeader'>available projects</div>
                    </td>
                </tr>
                {this.getProfilesForRendering()}
                <tr>
                    <td style={{paddingTop:20}}>
                        <b>data courtesy:</b>
                    </td>
                </tr>
                <tr>
                    <td style={{paddingTop:5}}>
                        <i>rat barrel cortex:</i> Udvary et al. (2022)
                    </td>
                </tr>
                <tr>
                    <td >
                        <a href='https://doi.org/10.1016/j.celrep.2022.110677'>doi.org/10.1016/j.celrep.2022.110677</a>
                    </td>
                </tr>
                <tr>
                    <td style={{paddingTop:5}}>
                        <i>human temporal cortex:</i> Shapson-Coe et al. (2021)
                    </td>
                </tr>
                <tr>
                    <td>
                        <a href='https://doi.org/10.1101/2021.05.29.446289'>doi.org/10.1101/2021.05.29.446289</a>
                    </td>
                </tr>
                <tr>
                    <td style={{paddingTop:5}}>
                        <i>mouse visual cortex:</i> MICrONS Consortium et al. (2021)
                    </td>
                </tr>
                <tr>                
                    <td>
                        <a href='https://doi.org/10.1101/2021.07.28.454025'>doi.org/10.1101/2021.07.28.454025</a>
                    </td>
                </tr>
                <tr>
                    <td style={{paddingTop:5}}>
                        <i>COVID Germany:</i> Robert Koch-Institut (2022)
                    </td>
                </tr>
                <tr>                
                    <td>
                        <a href='https://doi.org/10.5281/zenodo.6672879'>doi.org/10.5281/zenodo.6672879</a>
                    </td>
                </tr>                
            </tbody>
        </table>;
    }
}


Template.projectView.onCreated(function () {
    this.viewManager = Template.currentData();    
});

Template.projectView.onRendered(function () {
    this.viewManager = Template.currentData();    
});


Template.projectView.helpers({
    ProjectControl() {
        return ProjectControl;
    },

    viewManager() {
        return Template.instance().viewManager;
    }
});

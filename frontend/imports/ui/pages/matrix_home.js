import './matrix_home.html'
import '/imports/ui/css/goldenlayout-base.css';
import '/imports/ui/css/goldenlayout-light-theme.css';

import './views/projectView';
import './views/treeView.js';
import './views/channelView.js';
import './views/matrix/stratificationMatrixView.js';
import './views/detailView.js';

import { Template } from 'meteor/templating';
import { ViewManager } from './views/core/viewManager';

Template.matrixHome.onCreated(() => {
    $(document).ready(function () {
        $('#homeNav').removeClass('active');
        $('#exploreNav').removeClass('active');
        $('#experimentNav').addClass('active');
        $('#downloadNav').removeClass('active');
        $('#computationalConnectomicsNav').removeClass('active');
        $('#accountNav').removeClass('active');
    });
});

Template.matrixHome.onRendered(() => {

    const GoldenLayout = require('golden-layout');
    const viewManager = new ViewManager()

    viewManager.dataManager.loadInitialData(() => {

        let config = {
            dimensions: {
            },
            settings: {
                showPopoutIcon: false,
                reorderEnabled: false,
            },
            content: [{
                type: 'row',
                content: [
                    {
                        type: 'column',
                        width: 30,
                        content: [
                            {
                                type: 'stack',
                                id: "sidebar",
                                content: [
                                    {
                                        type: 'component',
                                        componentName: 'viewer',
                                        title: 'Project',
                                        isClosable: false,
                                        componentState: { name: 'project-viewer', id: 'project-viewer', uuid: "new", loaded: 'false' }
                                    },
                                    {
                                        type: 'component',
                                        componentName: 'viewer',
                                        title: 'Selection',
                                        isClosable: false,
                                        componentState: { name: 'tree-viewer', id: 'tree-viewer', uuid: "new", loaded: 'false' }
                                    }, {
                                        type: 'component',
                                        componentName: 'viewer',
                                        title: 'Data channels',
                                        isClosable: false,
                                        componentState: { name: 'channel-viewer', id: 'channel-viewer', uuid: "new", loaded: 'false' }
                                    } , {
                                        type: 'component',
                                        componentName: 'viewer',
                                        title: 'Toolbox',
                                        id: 'detail-viewer',
                                        isClosable: false,
                                        componentState: { name: 'detail-viewer', id: 'detail-viewer', uuid: "new", loaded: 'false' }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        type: 'column',
                        width: 70,
                        content: [
                            {
                                type: 'stack',
                                id: "sidebar",
                                content: [

                                    {
                                        type: 'component',
                                        componentName: 'viewer',
                                        title: 'Stratification matrix',
                                        id: 'matrix-viewer',
                                        isClosable: false,
                                        componentState: { name: 'matrix-viewer', id: 'matrix-viewer', uuid: "new", loaded: 'false' }
                                    }
                                ]
                            },
                        ]
                    }                   
                ]
            }]
        };

        let container = document.getElementById('matrixContainer');
        myLayout = new GoldenLayout(config, container);

        myLayout.registerComponent('viewer', function (container, componentState) {
            container.getElement().html('<div class="' + componentState.name + '"></div>');
            container.on('show', function () {
                if (container.getState().loaded == 'false') {
                    $(function () {
                        createTemplate(container.getState().name, viewManager);
                        container.extendState({ loaded: 'true' });
                    });
                }
            });
            container.on('resize', function () {
                if (container.getState().loaded == 'true') {
                    viewManager.onResize(container);
                }
            });
        });

        myLayout.init();

    });

});


function createTemplate(name, viewManager) {

    if (name == 'project-viewer') {
        Blaze.renderWithData(Template.projectView, viewManager, $('.project-viewer')[0]);
    }

    if (name == 'tree-viewer') {
        Blaze.renderWithData(Template.treeView, viewManager, $('.tree-viewer')[0]);
    }

    if (name == 'channel-viewer') {
        Blaze.renderWithData(Template.channelView, viewManager, $('.channel-viewer')[0]);
    }

    if (name == 'matrix-viewer') {
        Blaze.renderWithData(Template.stratificationMatrix, viewManager, $('.matrix-viewer')[0]);
    }

    if (name == 'detail-viewer') {
        Blaze.renderWithData(Template.detailView, viewManager, $('.detail-viewer')[0]);
    }
}

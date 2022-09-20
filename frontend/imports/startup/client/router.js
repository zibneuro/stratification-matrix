import '/imports/ui/layouts/layout.html';

import * as BABYLON from 'babylonjs';
import '/imports/ui/pages/cortexinsilico3d.scss';
import '/imports/ui/pages/matrix.css';
import 'bootstrap/dist/js/bootstrap.bundle';
import '/imports/ui/pages/matrix_home.js';

import {Router} from 'meteor/iron:router';

Router.configure({
    layoutTemplate: 'layout',
});

Router.route('/', {
    name: 'matrixHome',    
});


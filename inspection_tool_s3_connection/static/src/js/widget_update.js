odoo.define('inspection_tool_s3_connection.widget_update_s3', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var basicFields = require('web.basic_fields');
var concurrency = require('web.concurrency');
var ControlPanel = require('web.ControlPanel');
var dialogs = require('web.view_dialogs');
var core = require('web.core');
var data = require('web.data');
var Dialog = require('web.Dialog');
var KanbanRenderer = require('web.KanbanRenderer');
var ListRenderer = require('web.ListRenderer');
var Pager = require('web.Pager');

var _t = core._t;
var qweb = core.qweb;

var Many2many_bin = require('web.relational_fields');


    

Many2many_bin.FieldMany2ManyBinaryMultiFiles.include({

    fieldsToFetch: {
        name: {type: 'char'},
        datas_fname: {type: 'char'},
        mimetype: {type: 'char'},
        enable_selection:{type: 'boolean'},
        image_select : {type:'boolean'},
        url : {type:'char'}
    },


});


    
});



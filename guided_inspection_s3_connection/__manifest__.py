# -*- coding: utf-8 -*-
{
    'name': "Guided Inspection S3",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Lyra Infosystems",
    'website': "http://www.lyrainfo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['inspection_tool','pr1_s3','guided_inspection','guided_inspection_report','inspection_tool_s3_connection'],

    # always loaded 
    'data': [],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}

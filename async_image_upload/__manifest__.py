# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Cron For Async Upload',
    'version': '1.0',
    'category': ' Cron For Async Upload',
    'author': 'credativ software (India) pvt. ltd.',
    'website': 'http://www.credativ.in',
    'summary': ' Cron For Async Upload',
    'description': """
Cron For Async Upload
 """,
    'website': '',
    'depends': ['guided_inspection','base','inspection_tool','pr1_s3'],
    'data': [
       "views/cron_for_image_upload.xml",
    ],
    'qweb': [],
    'demo': [],
    'css': [],
    'installable': True,
    'auto_install': False,
}

# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)

from datetime import datetime
from datetime import date
import pdb
import base64
import hashlib
try:
    import boto3
except:
    _logger.debug('boto3 package is required!!')
    
import requests


class GuidedInspectionInheritS3(models.Model):
    _inherit = 'guided.inspection'
    
    
    @api.multi
    def s3_upload(self):

        s3_connection = self.env['pr1_s3.s3_connection'].search([('s3_for_inspection','=',True)])
        if not s3_connection:
            raise ValidationError(_('Please add S3 bucket connection for Inspection tool'))
        else :
            for connection in s3_connection:
                connection.sudo().upload_all_existing_guided_inspection_docs(self)
                
        
    #@api.multi
    #def submit_guided_inspection(self):
        
        #record =  super(GuidedInspectionInheritS3, self).submit_guided_inspection()
        #self.s3_upload()
    
        #return record
        
    
    
    

    
#class InspectionToolGuidedS3Inherit(models.Model):
    #_inherit = 'inspection.tool.main'
    
    #@api.multi
    #def generate_guided_inspection_main_report(self):
        #if self.guided_inspection_id.pdf_attachment_ids:
            #return {                   
                    #'name'     : 'Guided Inspection PDF',
                    #'res_model': 'ir.actions.act_url',
                    #'type'     : 'ir.actions.act_url',
                    #'target'   : 'new',
                    #'url'      : self.guided_inspection_id.pdf_attachment_ids[0].url
               #}
            
            ##return self.guided_inspection_id.pdf_attachment_ids[0].url
        #else:
            #return False
       

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


class InspectionToolInheritS3(models.Model):
    _inherit = 'inspection.tool.main'
    
    
    @api.multi
    def s3_upload(self):
        inspection_details = self.env['inspection.details'].search([('main_inspection_id','=',self.id)])
        inspection_ids =[i.id for i in inspection_details] 
        inspection_ids.append(self.id)
        s3_connection = self.env['pr1_s3.s3_connection'].search([('s3_for_inspection','=',True)])
        if not s3_connection:
            raise ValidationError(_('Please add S3 bucket connection for Inspection tool'))
        else :
            for connection in s3_connection:
                connection.sudo().upload_all_existing_inspection_docs(tuple(inspection_ids))
                
        
            
class InspectionPreviewInherit(models.TransientModel):
    _inherit = 'inspection.preview'
    
    #@api.multi
    #def submit_inspection(self):
        #record =  super(InspectionPreviewInherit, self).submit_inspection()
        #self.inspection_id.s3_upload()
    
        #return record
    
    
    

    
    

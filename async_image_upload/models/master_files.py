# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


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
from io import BytesIO
from PIL import Image as pil

try:
    import boto3
except:
    _logger.debug('boto3 package is required!!')
    
import requests
from PIL import Image



class GuidedInspection(models.Model):
    _inherit = 'guided.inspection'
    
    image_upload=fields.Integer('Image Upload',default=1)
    
   
    @api.multi
    def s3_upload_cron(self):

        s3_connection = self.env['pr1_s3.s3_connection'].search([('s3_for_inspection','=',True)])
        if not s3_connection:
            raise ValidationError(_('Please add S3 bucket connection for Inspection tool'))
        else :
            for connection in s3_connection:
                
                get_inspection = self.env['guided.inspection'].search([('image_upload','=',1),('state','=','submitted')],order='id asc',limit=1)
                print(get_inspection)
                connection.sudo().upload_all_existing_guided_inspection_docs_cron_fun(get_inspection)
                
        
    

class S3ConnectionImages(models.Model):
    _inherit = 'pr1_s3.s3_connection'
    
    
    no_of_pics=fields.Integer('No. of images to upload',default=10,required=True)
    
    
    
    @api.multi
    def upload_all_existing_guided_inspection_docs_cron_fun(self,guided_inspection_id):
        
        s = requests.session() 
        s.keep_alive = False
        for record in self:
            if(record.can_use(record)==False):
                continue
            connection=False
            connection=record
            s3_bucket,s3_service = connection.get_bucket()
            
            for items in guided_inspection_id:
                
                count_check=self.env['ir.attachment'].sudo().search_count([('is_in_s3','=',False),('type','=','binary'),('res_model','=','guided.inspection'),('res_id','=',items.id)])
                
                if count_check>0:
                    images = items.get_all_attachment_ids()
                    attachments_guided_inspection=self.env['ir.attachment'].sudo().search([('is_in_s3','=',False),('type','=','binary'),('res_model','=','guided.inspection'),('res_id','=',items.id)])
                    images.extend([item for item in attachments_guided_inspection])
                    
                    attachments = [image for image in images if image.is_in_s3 == False and image.type == 'binary'][:record.no_of_pics]
                                
                    i = 0
                    for attach in attachments:
                        value = attach.datas
                        bin_data = base64.b64decode(value) if value else b''
                        fname = ''
                        fname = items.property_id_hb + '/' +str(items.name.split('/')[-1])
                        
                        if attach.mimetype in ('application/xml','text/xml'):
                            fname = fname+'/XML'
                        elif attach.mimetype in ('image/jpeg','image/gif','image/bmp','image/tiff','image/vnd.microsoft.icon','image/png','image/svg+xml','image/webp'):
                            fname = fname+'/PHOTOS'
                        elif attach.mimetype in ('application/vnd.ms-excel','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
                            fname = fname+'/XLS'
                        elif attach.mimetype == 'application/pdf':
                            fname = fname+'/PDF'
                        else :
                            
                            fname = fname
                        if(attach.datas_fname!=False):
                            Metadata={
                                'FileName': attach.datas_fname
                                }
                        else:
                            Metadata={}
                        
                        if(connection.append_file_name_to_start):
                            if(attach.datas_fname!=False):
                                fname=fname+"/"+attach.datas_fname
                            else:
                                fname = hashlib.sha1(bin_data).hexdigest()
                        
                        fname_delta = "Guided Inspection"+" Delta/"+fname
                        fname="Guided Inspection"+"/"+fname
                        try:
                            s3_bucket.put_object(Key=fname,Body=bin_data,ACL='public-read',ContentType=attach.mimetype,Metadata=Metadata)
                            s3_bucket.put_object(Key=fname_delta,Body=bin_data,ACL='public-read',ContentType=attach.mimetype,Metadata=Metadata)
                            i+=1
                            
                            #if attach.file_size > 150000 and fname[-4:] in ('.jpg','.JPG','.png','.PNG'): 
                                #key_list = []
                                #key_list.extend([obj1 for obj1 in s3_bucket.objects.filter(Prefix=fname)])
                                #key_list.extend([obj2 for obj2 in s3_bucket.objects.filter(Prefix=fname_delta)])
                                #for obj in key_list:
                                    #self.compress_inspection_images(obj)
                                        
                        except Exception as e:
                            raise exceptions.UserError(e.message)
                        
                        
                        
                        vals = {
                            'checksum': attach._compute_checksum(bin_data),
                            'url': connection.get_s3_url(fname,s3_service),
                            'file_size': len(bin_data),
                            'index_content': attach._index(bin_data, attach.datas_fname, attach.mimetype),
                            'is_in_s3':True,
                            'store_fname': fname,
                            'db_datas': False,
                            'type': 'url',
                        }
                        
                        attach.write(vals)
                        
                        
                        
                        
                else:
                    items.image_upload=2
                    
                    
                    
                    
    @api.multi
    def upload_all_existing_inspection_docs_asyn_upload(self,get_main_id):
        s = requests.session() 
        s.keep_alive = False
        for record in self:
            if(record.can_use(record)==False):
                continue
            connection=False
            connection=record
            
            s3_bucket,s3_service = connection.get_bucket()
            
            for vals in get_main_id:
                inspection_ids=[]
                
            
            
                inspection_details=self.env['inspection.details'].search([('main_inspection_id','=',vals.id)])
                inspection_ids =[i.id for i in inspection_details] 
                inspection_ids.append(vals.id)
                
                count_check=self.env['ir.attachment'].sudo().search_count([('is_in_s3','=',False),('type','=','binary'),('res_model','in',('inspection.tool.main','inspection.details')),('res_id','in',inspection_ids)])
                print(inspection_ids)
                if count_check>0:
                
                    attachments=self.env['ir.attachment'].sudo().search([('is_in_s3','=',False),('type','=','binary'),('res_model','in',('inspection.tool.main','inspection.details')),('res_id','in',inspection_ids)])
                        
                    attachments = attachments._filter_protected_attachments()
                    attachments = attachments.filtered('datas')
                    attachments=attachments[:record.no_of_pics]
                    
                    image_list_compress = []
                    
                    for attach in attachments:
                        value = attach.datas
                        bin_data = base64.b64decode(value) if value else b''
                        fname = ''
                        if attach.res_model == 'inspection.details':
                            detail_obj=self.env['inspection.details'].browse(attach.res_id).main_inspection_id
                            if detail_obj and detail_obj.property_id_hb:
                                
                                fname = detail_obj.property_id_hb + '/' +str(detail_obj.name.split('/')[-1])
                                print(fname)
                        else:
                            obj = self.env['inspection.tool.main'].browse(attach.res_id)
                            fname = obj.property_id_hb + '/' + str(obj.name.split('/')[-1])
                        if attach.mimetype in ('application/xml','text/xml'):
                            fname = fname+'/XML'
                        elif attach.mimetype in ('image/jpeg','image/gif','image/bmp','image/tiff','image/vnd.microsoft.icon','image/png','image/svg+xml','image/webp'):
                            fname = fname+'/PHOTOS'
                        elif attach.mimetype in ('application/vnd.ms-excel','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
                            fname = fname+'/XLS'
                        elif attach.mimetype == 'application/pdf':
                            fname = fname+'/PDF'
                        else :
                            
                            fname = fname
                        if(attach.datas_fname!=False):
                            Metadata={
                                'FileName': attach.datas_fname
                                }
                        else:
                            Metadata={}
                        
                        if(connection.append_file_name_to_start):
                            if(attach.datas_fname!=False):
                                fname=fname+"/"+attach.datas_fname
                            else:
                                fname = hashlib.sha1(bin_data).hexdigest()
                        if(connection.sub_folder!="" and connection.sub_folder!=False):
                            fname_delta = connection.sub_folder+" Delta/"+fname
                            fname=connection.sub_folder+"/"+fname
                        try:
                            s3_bucket.put_object(Key=fname,Body=bin_data,ACL='public-read',ContentType=attach.mimetype,Metadata=Metadata)
                            s3_bucket.put_object(Key=fname_delta,Body=bin_data,ACL='public-read',ContentType=attach.mimetype,Metadata=Metadata)
                            
                            if attach.file_size > 150000 and fname[-4:] in ('.jpg','.JPG','.png','.PNG'): 
                                key_list = []
                                key_list.extend([obj1 for obj1 in s3_bucket.objects.filter(Prefix=fname)])
                                key_list.extend([obj2 for obj2 in s3_bucket.objects.filter(Prefix=fname_delta)])
                                for obj in key_list:
                                    self.compress_inspection_images(obj)
                                        
                        except Exception as e:
                            raise exceptions.UserError(e.message)
                        
                        
                        
                        vals = {
                            'checksum': attach._compute_checksum(bin_data),
                            'url': connection.get_s3_url(fname,s3_service),
                            'file_size': len(bin_data),
                            'index_content': attach._index(bin_data, attach.datas_fname, attach.mimetype),
                            'is_in_s3':True,
                            'store_fname': fname,
                            'db_datas': False,
                            'type': 'url',
                        }
                        
                        attach.write(vals)
                        print(attach)
                        
                else:
                    vals.image_upload=2
                    
 

class InspectionTool(models.Model):
    _inherit = 'inspection.tool.main'
    
    image_upload=fields.Integer('Image Upload',default=1)  
    
    
    
     
    @api.multi
    def s3_upload_inspection_cron(self):
        inspection_ids=[]
        get_main_id=self.env['inspection.tool.main'].search([('image_upload','=',1),('state','=','submitted')],order='id asc',limit=1)
        #for items in get_main_id:
            
            
            #inspection_details = self.env['inspection.details'].search([('main_inspection_id','=',items.id)])
            #inspection_ids =[i.id for i in inspection_details] 
            #inspection_ids.append(items.id)
        s3_connection = self.env['pr1_s3.s3_connection'].search([('s3_for_inspection','=',True)])
        if not s3_connection:
            raise ValidationError(_('Please add S3 bucket connection for Inspection tool'))
        else :
            for connection in s3_connection:
                connection.sudo().upload_all_existing_inspection_docs_asyn_upload(get_main_id)
                
                
                
                
                
    
                
            
                

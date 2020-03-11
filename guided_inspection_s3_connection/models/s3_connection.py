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
from io import BytesIO
from PIL import Image as pil

try:
    import boto3
except:
    _logger.debug('boto3 package is required!!')
    
import requests
from PIL import Image


class S3ConnectionInherit(models.Model):
    _inherit = 'pr1_s3.s3_connection'
    
    
            
    
    
    @api.multi
    def upload_all_existing_guided_inspection_docs(self,guided_inspection_id):
        
        s = requests.session() 
        s.keep_alive = False
        for record in self:
            if(record.can_use(record)==False):
                continue
            connection=False
            connection=record
            s3_bucket,s3_service = connection.get_bucket()
            
            images = guided_inspection_id.get_all_attachment_ids()
            attachments_guided_inspection =self.env['ir.attachment'].sudo().search([('is_in_s3','=',False),('type','=','binary'),('res_model','=','guided.inspection'),('res_id','=',guided_inspection_id.id)])
            images.extend([item for item in attachments_guided_inspection])
            
            attachments = [image for image in images if image.is_in_s3 == False and image.type == 'binary']
                        
            i = 0
            for attach in attachments:
                value = attach.datas
                bin_data = base64.b64decode(value) if value else b''
                fname = ''
                fname = guided_inspection_id.property_id_hb + '/' +str(guided_inspection_id.name.split('/')[-1])
                
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
            
            
                
                
                
    #@api.multi
    #def compress_inspection_images(self,image):
        #input_file = BytesIO(image.get()['Body'].read())
        #img = pil.open(input_file)
        #tmp = BytesIO()
        
        #if img.mode == 'RGBA':
           #img = img.convert('RGB')
        #img.save(tmp, 'JPEG', quality=50)
        #tmp.seek(0)
        #output_data = tmp.getvalue()

        #content_type = 'image/jpeg'
        #content_length = len(output_data)
        #cache_control  = 'max-age = 604800'

        #image.put(Body=output_data, CacheControl=cache_control, ContentLength=content_length, ContentType=content_type, ServerSideEncryption='AES256', ACL='public-read')

        #tmp.close()
        #input_file.close()
        
        
        
        
        
        
        
        
            
    
    
    

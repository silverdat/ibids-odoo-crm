from odoo import models, fields

class TenderTag(models.Model):
    _name = 'govcon.tender.tag'
    _description = 'Tender Tags'
    
    name = fields.Char('Tag Name', required=True)
    color = fields.Integer('Color Index') 
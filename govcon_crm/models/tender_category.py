from odoo import models, fields

class TenderCategory(models.Model):
    _name = 'govcon.tender.category'
    _description = 'Tender Categories'
    
    name = fields.Char('Category Name', required=True)
    description = fields.Text('Description') 
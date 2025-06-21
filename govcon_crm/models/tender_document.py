from odoo import models, fields

class TenderDocument(models.Model):
    _name = 'govcon.tender.document'
    _description = 'Tender Documents'
    
    name = fields.Char('Document Name', required=True)
    tender_id = fields.Many2one('govcon.tender', string='Tender', required=True)
    document_file = fields.Binary('Document File')
    document_filename = fields.Char('Filename') 
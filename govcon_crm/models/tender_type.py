from odoo import models, fields, api, _

class TenderType(models.Model):
    _name = 'govcon.tender.type'
    _description = 'Dominican Republic Government Tender Types (Law 340-06)'
    _order = 'sequence, name'
    
    name = fields.Char('Type Name', required=True)
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')
    sequence = fields.Integer('Sequence', default=10)
    
    # Stage Configuration
    stage_ids = fields.One2many('govcon.tender.stage', 'tender_type_id', 'Stages')
    
    # Document Templates
    document_template_ids = fields.Many2many('govcon.document.template', 'tender_type_document_template_rel', 'tender_type_id', 'document_template_id', 'Document Templates')
    
    # Auto-classification from API
    api_classification_keywords = fields.Text('API Classification Keywords')
    
    # Tender count
    tender_count = fields.Integer('Number of Tenders', compute='_compute_tender_count')
    
    @api.depends('tender_ids')
    def _compute_tender_count(self):
        for record in self:
            record.tender_count = len(record.tender_ids)
    
    # Related field for tender count
    tender_ids = fields.One2many('govcon.tender', 'tender_type_id', 'Tenders')
    
    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Tender type code must be unique!')
    ] 
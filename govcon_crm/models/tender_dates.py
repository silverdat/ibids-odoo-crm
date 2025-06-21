from odoo import models, fields, api, _
from datetime import datetime

class DateField(models.Model):
    _name = 'govcon.date.field'
    _description = 'Auto-Discovered Date Field Definitions'
    _order = 'usage_count desc, name'
    
    name = fields.Char('Display Name', required=True)
    api_field_name = fields.Char('API Field Name', required=True)
    spanish_name = fields.Char('Spanish Name')
    
    data_type = fields.Selection([
        ('date', 'Date Only'),
        ('datetime', 'Date & Time'),
        ('time', 'Time Only')
    ], default='datetime')
    
    # Auto-discovered characteristics
    is_deadline = fields.Boolean('Is Deadline', default=False)
    is_milestone = fields.Boolean('Is Milestone', default=False)
    is_critical = fields.Boolean('Critical Date', default=False)
    
    # Usage tracking
    usage_count = fields.Integer('Times Used', default=0)
    first_seen_date = fields.Datetime('First Discovered', default=fields.Datetime.now)
    used_in_tender_types = fields.Many2many('govcon.tender.type', 
                                           compute='_compute_used_in_types', 
                                           string='Used in Tender Types')
    
    # Related field for tender dates
    tender_date_ids = fields.One2many('govcon.tender.date', 'date_field_id', 'Tender Dates')
    
    @api.depends('tender_date_ids')
    def _compute_used_in_types(self):
        """Compute which tender types use this date field"""
        for record in self:
            tender_types = record.tender_date_ids.mapped('tender_id.tender_type_id')
            record.used_in_tender_types = [(6, 0, tender_types.ids)]
    
    _sql_constraints = [
        ('unique_api_field_name', 'unique(api_field_name)', 
         'API field name must be unique!')
    ]

class TenderDateValue(models.Model):
    _name = 'govcon.tender.date'
    _description = 'Tender Date Values'
    _rec_name = 'date_field_id'
    _order = 'tender_id, date_field_id'
    
    tender_id = fields.Many2one('govcon.tender', 'Tender', required=True, ondelete='cascade')
    date_field_id = fields.Many2one('govcon.date.field', 'Date Field', required=True)
    date_value = fields.Datetime('Date Value')
    
    # Tracking
    is_estimated = fields.Boolean('Is Estimated')
    source = fields.Selection([
        ('api', 'API Import'),
        ('manual', 'Manual Entry'),
        ('calculated', 'Calculated'),
        ('api_sync', 'API Sync Update')
    ], default='manual')
    last_updated = fields.Datetime('Last Updated', default=fields.Datetime.now)
    previous_value = fields.Datetime('Previous Value')  # Track changes
    
    # Ensure unique date fields per tender
    _sql_constraints = [
        ('unique_tender_date_field', 'unique(tender_id, date_field_id)', 
         'Each date field can only have one value per tender!')
    ]
    
    @api.onchange('date_value')
    def _onchange_date_value(self):
        """Update last_updated when date value changes"""
        if self.date_value:
            self.last_updated = fields.Datetime.now()
    
    def write(self, vals):
        """Track previous value before updating"""
        if 'date_value' in vals and self.date_value:
            vals['previous_value'] = self.date_value
        return super().write(vals) 
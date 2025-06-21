from odoo import models, fields

class TenderTeam(models.Model):
    _name = 'govcon.tender.team'
    _description = 'Tender Teams'
    
    name = fields.Char('Team Name', required=True)
    member_ids = fields.Many2many('res.users', string='Team Members') 
from odoo import models, fields, api

class TenderStage(models.Model):
    _name = 'govcon.tender.stage'
    _description = 'Tender Stages'
    _order = 'sequence, name'
    
    name = fields.Char('Stage Name', required=True)
    sequence = fields.Integer('Sequence', default=1)
    
    # Fold this stage in the kanban view
    fold = fields.Boolean('Folded in Kanban')
    
    # This stage is for a won tender
    is_won = fields.Boolean('Is Won Stage')
    
    # This stage is considered as a default stage
    is_default = fields.Boolean('Is Default Stage')

    # This field is to determine if the stage is for a specific tender type
    tender_type_id = fields.Many2one('govcon.tender.type', 'Tender Type')

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """
        This method is overriden to display all stages in the kanban view,
        even if they are empty.
        """
        # We are filtering here the stages that are not related to any tender type
        stage_ids = self.search([('tender_type_id', '=', False)])
        return stage_ids 
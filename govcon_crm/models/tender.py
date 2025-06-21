from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class GovconTender(models.Model):
    _name = 'govcon.tender'
    _description = 'Government Contract Tender'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # Basic Information (from ibiDs API)
    tender_id = fields.Char('Tender ID', required=True, tracking=True, help="Tender ID from compras")
    procuring_entity = fields.Char('Procuring Entity', tracking=True, help="Procuring entity from compras")
    tender_value = fields.Float('Tender Value', tracking=True, help="Tender value from compras")
    description = fields.Text('Description', tracking=True, help="Tender description from compras")
    
    # Dates and Timeline
    all_tender_dates = fields.Datetime('All Tender Dates', tracking=True, help="Returns all dates in the tender's timeline")
    
    # Budget and Financial Information
    budget_appropriation_certificate = fields.Char('Budget Appropriation Certificate', tracking=True, help="PDF S3 link")
    budget_appropriation_value = fields.Float('Budget Appropriation Value', tracking=True, help="Budget appropriation value")
    budget_source = fields.Char('Budget Source', tracking=True, help="Budget source information")
    
    # Payment and Warranty Information
    define_advance_payments = fields.Boolean('Define Advance Payments', tracking=True, help="Whether advance payments are defined")
    advance_payment_pct = fields.Float('Advance Payment %', tracking=True, help="Advance payment percentage")
    define_warranties = fields.Boolean('Define Warranties', tracking=True, help="Whether warranties are defined")
    
    # Compliance and Requirements
    seriousness_of_the_offer = fields.Boolean('Seriousness of the Offer', tracking=True, help="Seriousness of the offer requirement")
    offer_seriousness_pct = fields.Float('Offer Seriousness %', tracking=True, help="Offer seriousness percentage")
    compliance = fields.Boolean('Compliance', tracking=True, help="Compliance requirement")
    compliance_pct = fields.Float('Compliance %', tracking=True, help="Compliance percentage")
    extra_civil_contractual_liability = fields.Boolean('Extra Civil Contractual Liability', tracking=True, help="Extra civil contractual liability requirement")
    
    # Documents and Links
    link_all_pliego_docs = fields.Char('Link All Pliego Docs', tracking=True, help="S3 link to all pliego documents")
    tender_url = fields.Char('Tender URL', tracking=True, help="URL to the tender")
    ibids_gpt_url = fields.Char('ibiDs GPT URL', tracking=True, help="URL to the tender in ibiDs GPT")
    tender_generator_link_other = fields.Char('Tender Generator Link Other', tracking=True, help="Link for generation of standard docs per generator")
    f33_tender_link = fields.Char('F33 Tender Link', tracking=True, help="Link to the prep of the F33 form")
    
    # Messages and Communication
    tender_messages = fields.Text('Tender Messages', tracking=True, help="Daily scrape to see if new comments/addenda are added")
    tender_mail_summary_gpt = fields.Text('Tender Mail Summary GPT', tracking=True, help="Summary of requirements for the tender included in the email")
    
    # Procurement Method
    procurement_method = fields.Char('Procurement Method', tracking=True, help="Procurement method from compras")
    
    # Classification and Type
    tender_type_id = fields.Many2one('govcon.tender.type', string='Tender Type', tracking=True)
    stage_id = fields.Many2one('govcon.tender.stage', string='Stage', default=lambda self: self._get_default_stage(), tracking=True, group_expand='_read_group_stage_ids')
    
    # Status and State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('evaluation', 'Under Evaluation'),
        ('awarded', 'Awarded'),
        ('cancelled', 'Cancelled'),
        ('closed', 'Closed')
    ], string='Status', default='draft', tracking=True)
    
    # Priority and Scoring
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Very High')
    ], string='Priority', default='1', tracking=True)
    
    # Tags and Categories
    tag_ids = fields.Many2many('govcon.tender.tag', 'tender_tag_rel', 'tender_id', 'tag_id', string='Tags')
    category_ids = fields.Many2many('govcon.tender.category', 'tender_category_rel', 'tender_id', 'category_id', string='Categories')
    
    # Team and Assignment
    user_id = fields.Many2one('res.users', string='Assigned To', default=lambda self: self.env.user, tracking=True)
    team_id = fields.Many2one('govcon.tender.team', string='Team', tracking=True)
    
    # Dates (computed from all_tender_dates)
    date_created = fields.Date('Date Created', compute='_compute_dates', store=True)
    date_published = fields.Date('Date Published', compute='_compute_dates', store=True)
    date_deadline = fields.Date('Submission Deadline', compute='_compute_dates', store=True)
    date_evaluation = fields.Date('Evaluation Date', compute='_compute_dates', store=True)
    date_awarded = fields.Date('Date Awarded', compute='_compute_dates', store=True)
    
    # Performance Metrics
    win_probability = fields.Float('Win Probability (%)', default=0.0, tracking=True)
    estimated_value = fields.Float('Estimated Value', tracking=True)
    actual_value = fields.Float('Actual Value', tracking=True)
    
    # Notes and Additional Information
    notes = fields.Html('Notes')
    internal_notes = fields.Text('Internal Notes')
    
    # Related Records
    line_ids = fields.One2many('govcon.tender.line', 'tender_id', string='Tender Lines')
    document_ids = fields.One2many('govcon.tender.document', 'tender_id', string='Documents')
    activity_ids = fields.One2many('mail.activity', 'res_id', domain=[('res_model', '=', 'govcon.tender')], string='Activities')
    
    # Computed Fields
    total_line_value = fields.Float('Total Line Value', compute='_compute_total_line_value', store=True)
    line_count = fields.Integer('Line Count', compute='_compute_line_count', store=True)
    document_count = fields.Integer('Document Count', compute='_compute_document_count', store=True)
    
    # Constraints
    _sql_constraints = [
        ('tender_id_unique', 'unique(tender_id)', 'Tender ID must be unique!')
    ]

    @api.model
    def _get_default_stage(self):
        """Get default stage for new tenders"""
        default_stage = self.env['govcon.tender.stage'].search([('is_default', '=', True)], limit=1)
        return default_stage.id if default_stage else False

    @api.depends('all_tender_dates')
    def _compute_dates(self):
        """Compute individual date fields from all_tender_dates"""
        for tender in self:
            if tender.all_tender_dates:
                # Parse the all_tender_dates to extract individual dates
                # This is a placeholder - actual implementation depends on date format
                tender.date_created = tender.all_tender_dates.date()
                tender.date_published = tender.all_tender_dates.date()
                tender.date_deadline = tender.all_tender_dates.date()
                tender.date_evaluation = tender.all_tender_dates.date()
                tender.date_awarded = tender.all_tender_dates.date()
            else:
                tender.date_created = False
                tender.date_published = False
                tender.date_deadline = False
                tender.date_evaluation = False
                tender.date_awarded = False

    @api.depends('line_ids.total_price')
    def _compute_total_line_value(self):
        """Compute total value from tender lines"""
        for tender in self:
            tender.total_line_value = sum(tender.line_ids.mapped('total_price'))

    @api.depends('line_ids')
    def _compute_line_count(self):
        """Compute number of tender lines"""
        for tender in self:
            tender.line_count = len(tender.line_ids)

    @api.depends('document_ids')
    def _compute_document_count(self):
        """Compute number of documents"""
        for tender in self:
            tender.document_count = len(tender.document_ids)

    @api.model
    def create(self, vals):
        """Override create to set default values"""
        if not vals.get('tender_id'):
            raise ValidationError(_('Tender ID is required'))
        return super().create(vals)

    def write(self, vals):
        """Override write to handle stage transitions"""
        result = super().write(vals)
        
        # Handle stage transitions
        if 'stage_id' in vals:
            for tender in self:
                tender._handle_stage_transition(vals['stage_id'])
        
        return result

    def _handle_stage_transition(self, new_stage_id):
        """Handle stage transition logic"""
        new_stage = self.env['govcon.tender.stage'].browse(new_stage_id)
        
        if new_stage.is_won:
            self.state = 'awarded'
        elif new_stage.is_lost:
            self.state = 'cancelled'
        elif new_stage.is_closed:
            self.state = 'closed'
        else:
            self.state = 'active'

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """
        This method is overriden to display all stages in the kanban view,
        even if they are empty.
        """
        # We are filtering here the stages that are not related to any tender type
        stage_ids = self.env['govcon.tender.stage'].search([('tender_type_id', '=', False)])
        return stage_ids

    def action_view_lines(self):
        """Action to view tender lines"""
        return {
            'name': _('Tender Lines'),
            'type': 'ir.actions.act_window',
            'res_model': 'govcon.tender.line',
            'view_mode': 'tree,form',
            'domain': [('tender_id', '=', self.id)],
            'context': {'default_tender_id': self.id},
        }

    def action_view_documents(self):
        """Action to view documents"""
        return {
            'name': _('Documents'),
            'type': 'ir.actions.act_window',
            'res_model': 'govcon.tender.document',
            'view_mode': 'tree,form',
            'domain': [('tender_id', '=', self.id)],
            'context': {'default_tender_id': self.id},
        }

    def action_generate_documents(self):
        """Generate required documents for this tender"""
        self.ensure_one()
        # Implementation for document generation
        return True

    def action_sync_with_api(self):
        """Sync tender data with external API"""
        self.ensure_one()
        # Implementation for API sync
        return True

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """Custom name search for tenders"""
        args = args or []
        domain = []
        if name:
            domain = ['|', '|', '|',
                     ('tender_id', operator, name),
                     ('procuring_entity', operator, name),
                     ('description', operator, name),
                     ('procurement_method', operator, name)]
        return self._search(domain + args, limit=limit)

    def name_get(self):
        """Custom name display for tenders"""
        result = []
        for tender in self:
            name = f"{tender.tender_id} - {tender.procuring_entity}"
            if tender.tender_value:
                name += f" (${tender.tender_value:,.2f})"
            result.append((tender.id, name))
        return result 

class GovconTenderLine(models.Model):
    _name = 'govcon.tender.line'
    _description = 'Tender Line Item'
    _order = 'sequence, id'

    # Basic Information (from ibiDs API - tender articles)
    tender_id = fields.Many2one('govcon.tender', string='Tender', required=True, ondelete='cascade')
    article_number = fields.Char('Article Number', required=True, help="Article number from compras")
    article_description = fields.Text('Article Description', required=True, help="Article description from compras")
    lot_info = fields.Char('Lot Info', help="Lot information from compras")
    unit = fields.Char('Unit', help="Unit from compras")
    quantity = fields.Float('Quantity', help="Quantity from compras")
    unit_price = fields.Float('Unit Price', help="Unit price from compras")
    total_price = fields.Float('Total Price', compute='_compute_total_price', store=True, help="Total price from compras")
    
    # UNSPSC Classification
    unspsc_code = fields.Char('UNSPSC Code', help="UNSPSC code from compras")
    unspsc_description = fields.Char('UNSPSC Description', help="UNSPSC description from compras")
    
    # ibiDs Analytics and Pricing
    ibids_estimated_price = fields.Float('ibiDs Estimated Price', help="From ibiDs: as given by estimated vs awarded delta")
    avahi_price_25_quartile = fields.Float('Avahi Price 25th Quartile', help="From ibiDs: avg of where 25% of prices are")
    avahi_price_75_quartile = fields.Float('Avahi Price 75th Quartile', help="From ibiDs: avg of where 75% of prices are")
    competitiveness_rank = fields.Float('Competitiveness Rank', help="From ibiDs: #of tenders for given unspsc / # of offers for that unspsc")
    
    # Additional Fields
    sequence = fields.Integer('Sequence', default=10)
    notes = fields.Text('Notes')
    
    # Computed Fields
    price_variance = fields.Float('Price Variance', compute='_compute_price_variance', store=True)
    price_competitiveness = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], string='Price Competitiveness', compute='_compute_price_competitiveness', store=True)

    @api.depends('unit_price', 'quantity')
    def _compute_total_price(self):
        """Compute total price from unit price and quantity"""
        for line in self:
            line.total_price = line.unit_price * line.quantity

    @api.depends('unit_price', 'ibids_estimated_price')
    def _compute_price_variance(self):
        """Compute price variance from estimated price"""
        for line in self:
            if line.ibids_estimated_price and line.unit_price:
                line.price_variance = ((line.unit_price - line.ibids_estimated_price) / line.ibids_estimated_price) * 100
            else:
                line.price_variance = 0.0

    @api.depends('competitiveness_rank')
    def _compute_price_competitiveness(self):
        """Compute price competitiveness based on rank"""
        for line in self:
            if line.competitiveness_rank:
                if line.competitiveness_rank < 0.3:
                    line.price_competitiveness = 'high'
                elif line.competitiveness_rank < 0.7:
                    line.price_competitiveness = 'medium'
                else:
                    line.price_competitiveness = 'low'
            else:
                line.price_competitiveness = 'medium'

    @api.constrains('quantity', 'unit_price')
    def _check_positive_values(self):
        """Ensure quantity and unit price are positive"""
        for line in self:
            if line.quantity < 0:
                raise ValidationError(_('Quantity must be positive'))
            if line.unit_price < 0:
                raise ValidationError(_('Unit price must be positive'))

    def name_get(self):
        """Custom name display for tender lines"""
        result = []
        for line in self:
            name = f"{line.article_number} - {line.article_description}"
            if line.total_price:
                name += f" (${line.total_price:,.2f})"
            result.append((line.id, name))
        return result 
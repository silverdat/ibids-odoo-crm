from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
import requests
import json
from datetime import datetime, timedelta
import pytz

_logger = logging.getLogger(__name__)

class GovconSyncService(models.Model):
    _name = 'govcon.sync.service'
    _description = 'Government Contract Sync Service'

    name = fields.Char('Service Name', required=True)
    api_url = fields.Char('API URL', required=True)
    api_key = fields.Char('API Key', required=True)
    is_active = fields.Boolean('Active', default=True)
    
    # Sync Configuration
    sync_interval_hours = fields.Integer('Sync Interval (Hours)', default=24)
    last_sync_date = fields.Datetime('Last Sync Date', readonly=True)
    next_sync_date = fields.Datetime('Next Sync Date', compute='_compute_next_sync_date', store=True)
    
    # Sync Statistics
    total_tenders_synced = fields.Integer('Total Tenders Synced', default=0)
    total_articles_synced = fields.Integer('Total Articles Synced', default=0)
    last_sync_status = fields.Selection([
        ('success', 'Success'),
        ('error', 'Error'),
        ('partial', 'Partial Success')
    ], string='Last Sync Status', default='success')
    last_sync_message = fields.Text('Last Sync Message')

    @api.depends('last_sync_date', 'sync_interval_hours')
    def _compute_next_sync_date(self):
        """Compute next sync date based on last sync and interval"""
        for service in self:
            if service.last_sync_date:
                next_sync = service.last_sync_date + timedelta(hours=service.sync_interval_hours)
                service.next_sync_date = next_sync
            else:
                service.next_sync_date = fields.Datetime.now()

    def sync_tenders_from_api(self):
        """Sync tenders from ibiDs API"""
        self.ensure_one()
        
        try:
            # Fetch tender data from API
            tender_data = self._fetch_tender_data()
            
            # Process each tender
            synced_count = 0
            for tender_info in tender_data:
                try:
                    self._process_tender_data(tender_info)
                    synced_count += 1
                except Exception as e:
                    _logger.error(f"Error processing tender {tender_info.get('tender_id')}: {str(e)}")
                    continue
            
            # Update sync statistics
            self._update_sync_stats(synced_count, len(tender_data))
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Complete'),
                    'message': _('Successfully synced %d tenders') % synced_count,
                    'type': 'success',
                }
            }
            
        except Exception as e:
            _logger.error(f"Sync error: {str(e)}")
            self._update_sync_stats(0, 0, 'error', str(e))
            raise ValidationError(_('Sync failed: %s') % str(e))

    def _fetch_tender_data(self):
        """Fetch tender data from ibiDs API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(f"{self.api_url}/tenders", headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            _logger.error(f"API request failed: {str(e)}")
            raise ValidationError(_('Failed to fetch data from API: %s') % str(e))

    def _process_tender_data(self, tender_info):
        """Process individual tender data from API"""
        # Map API fields to model fields
        tender_vals = {
            'tender_id': tender_info.get('tender_id'),
            'procuring_entity': tender_info.get('procuring_entity'),
            'tender_value': tender_info.get('tender_value'),
            'description': tender_info.get('description'),
            'all_tender_dates': tender_info.get('all_tender_dates'),
            'budget_appropriation_certificate': tender_info.get('budget_appropriation_certificate'),
            'budget_appropriation_value': tender_info.get('budget_appropriation_value'),
            'budget_source': tender_info.get('budget_source'),
            'define_advance_payments': tender_info.get('define_advance_payments'),
            'advance_payment_pct': tender_info.get('advance_payment_pct'),
            'define_warranties': tender_info.get('define_warranties'),
            'seriousness_of_the_offer': tender_info.get('seriousness_of_the_offer'),
            'offer_seriousness_pct': tender_info.get('offer_seriousness_pct'),
            'compliance': tender_info.get('compliance'),
            'compliance_pct': tender_info.get('compliance_pct'),
            'extra_civil_contractual_liability': tender_info.get('extra_civil_contractual_liability'),
            'link_all_pliego_docs': tender_info.get('link_all_pliego_docs'),
            'tender_messages': tender_info.get('tender_messages'),
            'tender_url': tender_info.get('tender_url'),
            'procurement_method': tender_info.get('procurement_method'),
            'ibids_gpt_url': tender_info.get('ibids_gpt_url'),
            'tender_mail_summary_gpt': tender_info.get('tender_mail_summary_gpt'),
            'tender_generator_link_other': tender_info.get('tender_generator_link_other'),
            'f33_tender_link': tender_info.get('f33_tender_link'),
        }
        
        # Find existing tender or create new one
        existing_tender = self.env['govcon.tender'].search([
            ('tender_id', '=', tender_vals['tender_id'])
        ], limit=1)
        
        if existing_tender:
            # Update existing tender
            existing_tender.write(tender_vals)
            tender = existing_tender
        else:
            # Create new tender
            tender = self.env['govcon.tender'].create(tender_vals)
        
        # Sync tender articles/line items
        self._sync_tender_articles(tender, tender_info.get('tender_id'))
        
        return tender

    def _sync_tender_articles(self, tender, tender_id):
        """Sync tender articles/line items from API"""
        try:
            # Fetch articles for this tender
            articles_data = self._fetch_tender_articles(tender_id)
            
            # Clear existing lines
            tender.line_ids.unlink()
            
            # Create new lines
            for article_info in articles_data:
                line_vals = {
                    'tender_id': tender.id,
                    'article_number': article_info.get('article_number'),
                    'article_description': article_info.get('article_description'),
                    'lot_info': article_info.get('lot_info'),
                    'unit': article_info.get('unit'),
                    'quantity': article_info.get('quantity'),
                    'unit_price': article_info.get('unit_price'),
                    'unspsc_code': article_info.get('unspsc_code'),
                    'unspsc_description': article_info.get('unspsc_description'),
                    'ibids_estimated_price': article_info.get('ibids_estimated_price'),
                    'avahi_price_25_quartile': article_info.get('avahi_price_25_quartile'),
                    'avahi_price_75_quartile': article_info.get('avahi_price_75_quartile'),
                    'competitiveness_rank': article_info.get('competitiveness_rank'),
                }
                
                self.env['govcon.tender.line'].create(line_vals)
                
        except Exception as e:
            _logger.error(f"Error syncing articles for tender {tender_id}: {str(e)}")
            raise

    def _fetch_tender_articles(self, tender_id):
        """Fetch tender articles from ibiDs API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(
                f"{self.api_url}/tenders/{tender_id}/articles", 
                headers=headers, 
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to fetch articles for tender {tender_id}: {str(e)}")
            return []

    def _update_sync_stats(self, synced_count, total_count, status='success', message=''):
        """Update sync statistics"""
        self.write({
            'last_sync_date': fields.Datetime.now(),
            'total_tenders_synced': synced_count,
            'last_sync_status': status,
            'last_sync_message': message or f"Synced {synced_count} of {total_count} tenders"
        })

    def action_test_connection(self):
        """Test API connection"""
        self.ensure_one()
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f"{self.api_url}/health", headers=headers, timeout=10)
            response.raise_for_status()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Test'),
                    'message': _('API connection successful'),
                    'type': 'success',
                }
            }
            
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Test'),
                    'message': _('API connection failed: %s') % str(e),
                    'type': 'danger',
                }
            }

    def action_manual_sync(self):
        """Manual sync action"""
        return self.sync_tenders_from_api()

    @api.model
    def _cron_sync_tenders(self):
        """Cron job for automatic tender sync"""
        active_services = self.search([('is_active', '=', True)])
        
        for service in active_services:
            if service.next_sync_date <= fields.Datetime.now():
                try:
                    service.sync_tenders_from_api()
                except Exception as e:
                    _logger.error(f"Automatic sync failed for service {service.name}: {str(e)}")
                    service._update_sync_stats(0, 0, 'error', str(e)) 
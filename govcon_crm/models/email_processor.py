from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
import re
from datetime import datetime
import pytz

_logger = logging.getLogger(__name__)

class GovconEmailProcessor(models.Model):
    _name = 'govcon.email.processor'
    _description = 'Email Processor for Government Tenders'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Processor Name', required=True)
    email_address = fields.Char('Email Address', required=True)
    is_active = fields.Boolean('Active', default=True)
    
    # Processing Configuration
    auto_classify_tenders = fields.Boolean('Auto-classify Tenders', default=True)
    auto_create_tenders = fields.Boolean('Auto-create Tenders', default=True)
    notification_enabled = fields.Boolean('Enable Notifications', default=True)
    
    # Processing Statistics
    total_emails_processed = fields.Integer('Total Emails Processed', default=0)
    total_tenders_created = fields.Integer('Total Tenders Created', default=0)
    last_processing_date = fields.Datetime('Last Processing Date', readonly=True)
    
    # Email Content Fields
    email_subject = fields.Char('Email Subject')
    email_body = fields.Html('Email Body')
    email_date = fields.Datetime('Email Date')
    sender_email = fields.Char('Sender Email')
    sender_name = fields.Char('Sender Name')
    
    # Extracted Data
    extracted_tender_id = fields.Char('Extracted Tender ID')
    extracted_entity = fields.Char('Extracted Entity')
    extracted_description = fields.Text('Extracted Description')
    extracted_value = fields.Float('Extracted Value')
    extracted_deadline = fields.Date('Extracted Deadline')
    extracted_url = fields.Char('Extracted URL')
    
    # Processing Status
    processing_status = fields.Selection([
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('error', 'Error')
    ], string='Processing Status', default='pending')
    processing_message = fields.Text('Processing Message')

    def process_email_content(self, email_data):
        """Process email content and extract tender information"""
        self.ensure_one()
        
        try:
            self.write({
                'processing_status': 'processing',
                'email_subject': email_data.get('subject', ''),
                'email_body': email_data.get('body', ''),
                'email_date': email_data.get('date'),
                'sender_email': email_data.get('sender_email'),
                'sender_name': email_data.get('sender_name')
            })
            
            # Extract tender information
            extracted_data = self._extract_tender_data(email_data)
            
            if extracted_data:
                self.write(extracted_data)
                
                # Auto-create tender if enabled
                if self.auto_create_tenders:
                    tender = self._create_tender_from_email(extracted_data)
                    if tender:
                        self.total_tenders_created += 1
                        self._send_notification(tender)
                
                self.processing_status = 'completed'
                self.processing_message = 'Email processed successfully'
            else:
                self.processing_status = 'error'
                self.processing_message = 'No tender information found in email'
            
            self.total_emails_processed += 1
            self.last_processing_date = fields.Datetime.now()
            
        except Exception as e:
            _logger.error(f"Error processing email: {str(e)}")
            self.processing_status = 'error'
            self.processing_message = str(e)
            raise ValidationError(_('Email processing failed: %s') % str(e))

    def _extract_tender_data(self, email_data):
        """Extract tender data from email content"""
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        
        extracted_data = {}
        
        # Extract tender ID (common patterns)
        tender_id_patterns = [
            r'tender[:\s]*([A-Z0-9\-]+)',
            r'licitación[:\s]*([A-Z0-9\-]+)',
            r'convocatoria[:\s]*([A-Z0-9\-]+)',
            r'ID[:\s]*([A-Z0-9\-]+)',
            r'Reference[:\s]*([A-Z0-9\-]+)'
        ]
        
        for pattern in tender_id_patterns:
            match = re.search(pattern, subject + ' ' + body, re.IGNORECASE)
            if match:
                extracted_data['extracted_tender_id'] = match.group(1)
                break
        
        # Extract procuring entity
        entity_patterns = [
            r'entidad[:\s]*([^,\n]+)',
            r'entity[:\s]*([^,\n]+)',
            r'procuring[:\s]*([^,\n]+)',
            r'organismo[:\s]*([^,\n]+)'
        ]
        
        for pattern in entity_patterns:
            match = re.search(pattern, subject + ' ' + body, re.IGNORECASE)
            if match:
                extracted_data['extracted_entity'] = match.group(1).strip()
                break
        
        # Extract description
        if body:
            # Try to extract description from email body
            lines = body.split('\n')
            for line in lines:
                if len(line.strip()) > 20 and not line.startswith('http'):
                    extracted_data['extracted_description'] = line.strip()[:500]
                    break
        
        # Extract value
        value_patterns = [
            r'valor[:\s]*\$?([0-9,]+\.?[0-9]*)',
            r'value[:\s]*\$?([0-9,]+\.?[0-9]*)',
            r'monto[:\s]*\$?([0-9,]+\.?[0-9]*)',
            r'amount[:\s]*\$?([0-9,]+\.?[0-9]*)'
        ]
        
        for pattern in value_patterns:
            match = re.search(pattern, subject + ' ' + body, re.IGNORECASE)
            if match:
                try:
                    value_str = match.group(1).replace(',', '')
                    extracted_data['extracted_value'] = float(value_str)
                    break
                except ValueError:
                    continue
        
        # Extract deadline
        deadline_patterns = [
            r'fecha límite[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})',
            r'deadline[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})',
            r'fecha de cierre[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})',
            r'closing date[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})'
        ]
        
        for pattern in deadline_patterns:
            match = re.search(pattern, subject + ' ' + body, re.IGNORECASE)
            if match:
                try:
                    date_str = match.group(1)
                    # Parse date (simplified - you might need more robust date parsing)
                    if '/' in date_str:
                        parts = date_str.split('/')
                    else:
                        parts = date_str.split('-')
                    
                    if len(parts) == 3:
                        if len(parts[2]) == 2:
                            parts[2] = '20' + parts[2]
                        extracted_data['extracted_deadline'] = f"{parts[2]}-{parts[1]}-{parts[0]}"
                    break
                except Exception:
                    continue
        
        # Extract URL
        url_pattern = r'https?://[^\s<>"]+'
        match = re.search(url_pattern, subject + ' ' + body)
        if match:
            extracted_data['extracted_url'] = match.group(0)
        
        return extracted_data

    def _create_tender_from_email(self, extracted_data):
        """Create tender record from extracted email data"""
        try:
            # Map extracted data to tender fields
            tender_vals = {
                'tender_id': extracted_data.get('extracted_tender_id', f"EMAIL_{fields.Datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                'procuring_entity': extracted_data.get('extracted_entity', ''),
                'description': extracted_data.get('extracted_description', ''),
                'tender_value': extracted_data.get('extracted_value', 0.0),
                'tender_url': extracted_data.get('extracted_url', ''),
                'state': 'draft',
                'user_id': self.env.user.id,
            }
            
            # Set deadline if available
            if extracted_data.get('extracted_deadline'):
                tender_vals['date_deadline'] = extracted_data['extracted_deadline']
            
            # Auto-classify tender type if enabled
            if self.auto_classify_tenders:
                tender_type = self._classify_tender_type(extracted_data)
                if tender_type:
                    tender_vals['tender_type_id'] = tender_type.id
            
            # Create tender
            tender = self.env['govcon.tender'].create(tender_vals)
            
            _logger.info(f"Created tender {tender.tender_id} from email")
            return tender
            
        except Exception as e:
            _logger.error(f"Error creating tender from email: {str(e)}")
            raise

    def _classify_tender_type(self, extracted_data):
        """Auto-classify tender type based on content"""
        description = (extracted_data.get('extracted_description', '') + 
                      extracted_data.get('email_subject', '')).lower()
        
        # Simple classification logic
        if any(word in description for word in ['construcción', 'construction', 'obra', 'building']):
            return self.env['govcon.tender.type'].search([('name', 'ilike', 'construction')], limit=1)
        elif any(word in description for word in ['servicio', 'service', 'consultoría', 'consulting']):
            return self.env['govcon.tender.type'].search([('name', 'ilike', 'service')], limit=1)
        elif any(word in description for word in ['bien', 'goods', 'equipo', 'equipment', 'suministro', 'supply']):
            return self.env['govcon.tender.type'].search([('name', 'ilike', 'goods')], limit=1)
        else:
            return self.env['govcon.tender.type'].search([('is_default', '=', True)], limit=1)

    def _send_notification(self, tender):
        """Send notification about new tender creation"""
        if not self.notification_enabled:
            return
        
        try:
            # Create activity for assigned user
            self.env['mail.activity'].create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'note': f'New tender created from email: {tender.tender_id}',
                'res_id': tender.id,
                'res_model_id': self.env['ir.model']._get('govcon.tender').id,
                'user_id': tender.user_id.id,
                'date_deadline': fields.Date.today(),
            })
            
            # Send internal message
            tender.message_post(
                body=f'Tender created from email notification. Source: {self.email_address}',
                subject=f'New Tender: {tender.tender_id}'
            )
            
        except Exception as e:
            _logger.error(f"Error sending notification: {str(e)}")

    def action_process_emails(self):
        """Manual action to process emails"""
        # This would typically be called by a cron job or external system
        # For now, it's a placeholder for manual processing
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Email Processing'),
                'message': _('Email processing completed'),
                'type': 'success',
            }
        }

    @api.model
    def _cron_process_emails(self):
        """Cron job for automatic email processing"""
        active_processors = self.search([('is_active', '=', True)])
        
        for processor in active_processors:
            try:
                # This would typically fetch emails from the configured email address
                # For now, it's a placeholder
                _logger.info(f"Processing emails for {processor.name}")
                
            except Exception as e:
                _logger.error(f"Error processing emails for {processor.name}: {str(e)}")
                processor.write({
                    'processing_status': 'error',
                    'processing_message': str(e)
                }) 
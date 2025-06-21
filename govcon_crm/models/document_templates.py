from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class DocumentTemplate(models.Model):
    _name = 'govcon.document.template'
    _description = 'Dominican Republic Standard Document Templates (SNCC Forms)'
    _order = 'form_code, name'
    
    name = fields.Char('Template Name', required=True)
    description = fields.Text('Description', help='Detailed description of the document template')
    form_code = fields.Char('SNCC Form Code', help='Official SNCC form code (e.g., SNCC.F.047)')
    
    # Standard Dominican Republic Procurement Forms
    template_type = fields.Selection([
        # Commitment and Authorization Forms
        ('ethical_commitment', 'Compromiso Ético de Proveedores'),
        ('manufacturer_auth', 'SNCC.F.047 - Autorización del Fabricante'),
        ('bidder_info', 'SNCC.F.042 - Formulario de Información sobre el Oferente'),
        
        # Personnel and Equipment Forms
        ('staff_personnel', 'SNCC.F.037 - Personal de Plantilla del Oferente'),
        ('bidder_equipment', 'SNCC.F.036 - Equipos del Oferente'),
        ('technical_support', 'SNCC.F.035 - Estructura para Brindar Soporte Técnico'),
        
        # Bid Submission Forms
        ('bid_presentation', 'SNCC.F.034 - Presentación de Oferta'),
        ('economic_offer', 'SNCC.F.033 - Oferta Económica'),
        
        # Agent Authorization Documents
        ('agent_acceptance', 'SNCC.D.052 - Carta de Aceptación de Designación como Agente Autorizado'),
        ('agent_designation', 'SNCC.D.051 - Carta de Designación o Sustitución de Agente Autorizado'),
        
        # Experience Documentation
        ('contractor_experience', 'SNCC.D.049 - Experiencia como Contratista'),
        ('professional_experience', 'SNCC.D.048 - Experiencia Profesional del Personal Principal'),
        ('professional_cv', 'SNCC.D.045 - Currículo del Personal Profesional Propuesto'),
        
        # Methodology and Approach
        ('methodology_plan', 'SNCC.D.044 - Descripción del Enfoque Metodología y Plan de Actividades'),
        ('consultant_organization', 'SNCC.D.043 - Organización y Experiencia del Consultor'),
        
        # Guarantees and Warranties
        ('performance_guarantee', 'SNCC.D.038 - Garantía de Fiel Cumplimiento de Contrato'),
        
        # Additional Standard Templates
        ('technical_proposal', 'Technical Proposal'),
        ('financial_proposal', 'Financial Proposal'),
        ('compliance_matrix', 'Compliance Matrix'),
        ('company_profile', 'Company Profile'),
        ('method_statement', 'Method Statement')
    ], required=True)
    
    # Document Classification
    document_category = fields.Selection([
        ('commitment', 'Commitment & Ethics'),
        ('authorization', 'Authorization & Legal'),
        ('personnel', 'Personnel & Staffing'),
        ('equipment', 'Equipment & Resources'),
        ('experience', 'Experience & Qualifications'),
        ('methodology', 'Methodology & Approach'),
        ('financial', 'Financial & Economic'),
        ('guarantee', 'Guarantees & Warranties'),
        ('technical', 'Technical Specifications'),
        ('compliance', 'Compliance & Legal')
    ], string='Document Category')
    
    # Form Requirements by Tender Type
    required_for_procedures = fields.Selection([
        ('all', 'All Procedures'),
        ('licitacion_publica', 'Licitación Pública Only'),
        ('consultoria', 'Consulting Services Only'),
        ('obras', 'Construction Works Only'),
        ('bienes', 'Goods/Supplies Only'),
        ('servicios', 'Services Only'),
        ('exception_procedures', 'Exception Procedures'),
        ('international_scope', 'International Scope')
    ], string='Required for Procedures', default='all')
    
    # SNCC Form Specifications
    is_sncc_standard_form = fields.Boolean('Is SNCC Standard Form', default=False)
    sncc_version = fields.Char('SNCC Form Version', help='Official version of the SNCC form')
    mandatory_fields_count = fields.Integer('Mandatory Fields Count')
    
    # Form Complexity
    estimated_completion_time = fields.Integer('Estimated Completion Time (minutes)')
    requires_notarization = fields.Boolean('Requires Notarization')
    requires_legal_review = fields.Boolean('Requires Legal Review')
    requires_translation = fields.Boolean('Requires Translation')
    
    # Dependencies
    prerequisite_forms = fields.Many2many(
        'govcon.document.template', 
        'template_prerequisite_rel', 
        'template_id', 
        'prerequisite_id',
        string='Prerequisite Forms'
    )
    
    # Auto-population capabilities  
    auto_populate_from_crm = fields.Boolean('Auto-populate from CRM Data', default=True)
    auto_populate_from_company = fields.Boolean('Auto-populate from Company Profile', default=True)
    
    # Tender Type Association  
    tender_type_ids = fields.Many2many('govcon.tender.type', 'document_template_tender_type_rel', 'document_template_id', 'tender_type_id', 'Applicable Tender Types')
    
    # ibiDs Integration from original prompt
    ibids_template_id = fields.Char('ibiDs Template ID')
    ibids_api_url = fields.Char('ibiDs API URL')
    
    # Field Mappings
    field_mappings = fields.One2many('govcon.template.field.mapping', 'template_id', 'Field Mappings')
    
    # Configuration
    is_required = fields.Boolean('Required Document')
    auto_generate = fields.Boolean('Auto Generate')
    
    # Usage tracking
    usage_count = fields.Integer('Times Used', default=0)
    
    @api.model
    def _get_sncc_form_definitions(self):
        """Returns standard SNCC form definitions with metadata"""
        return {
            'SNCC.F.047': {
                'name': 'Autorización del Fabricante',
                'category': 'authorization',
                'mandatory_fields': 8,
                'estimated_time': 15,
                'requires_notarization': True,
                'required_for': ['bienes'],
                'description': 'Carta oficial del fabricante autorizando al oferente como distribuidor autorizado'
            },
            'SNCC.F.042': {
                'name': 'Formulario de Información sobre el Oferente',
                'category': 'authorization',
                'mandatory_fields': 25,
                'estimated_time': 45,
                'required_for': ['all'],
                'description': 'Información detallada sobre la empresa oferente, incluyendo datos legales y financieros'
            },
            'SNCC.F.037': {
                'name': 'Personal de Plantilla del Oferente',
                'category': 'personnel',
                'mandatory_fields': 12,
                'estimated_time': 30,
                'required_for': ['servicios', 'consultoria'],
                'description': 'Listado del personal permanente con sus calificaciones y experiencia'
            },
            'SNCC.F.036': {
                'name': 'Equipos del Oferente',
                'category': 'equipment',
                'mandatory_fields': 15,
                'estimated_time': 35,
                'required_for': ['obras', 'servicios'],
                'description': 'Inventario de equipos disponibles para la ejecución del contrato'
            },
            'SNCC.F.035': {
                'name': 'Estructura para Brindar Soporte Técnico',
                'category': 'technical',
                'mandatory_fields': 10,
                'estimated_time': 25,
                'required_for': ['bienes', 'servicios'],
                'description': 'Organización y recursos para soporte técnico post-venta'
            },
            'SNCC.F.034': {
                'name': 'Presentación de Oferta',
                'category': 'compliance',
                'mandatory_fields': 18,
                'estimated_time': 40,
                'required_for': ['all'],
                'description': 'Formulario principal de presentación de la oferta técnica y económica'
            },
            'SNCC.F.033': {
                'name': 'Oferta Económica',
                'category': 'financial',
                'mandatory_fields': 20,
                'estimated_time': 50,
                'required_for': ['all'],
                'description': 'Desglose detallado de precios y condiciones económicas de la oferta'
            },
            'SNCC.D.052': {
                'name': 'Carta de Aceptación de Designación como Agente Autorizado',
                'category': 'authorization',
                'mandatory_fields': 6,
                'estimated_time': 10,
                'requires_notarization': True,
                'required_for': ['international_scope'],
                'description': 'Aceptación formal del representante legal en República Dominicana'
            },
            'SNCC.D.051': {
                'name': 'Carta de Designación o Sustitución de Agente Autorizado',
                'category': 'authorization', 
                'mandatory_fields': 8,
                'estimated_time': 15,
                'requires_notarization': True,
                'required_for': ['international_scope'],
                'description': 'Designación oficial de representante legal para empresas extranjeras'
            },
            'SNCC.D.049': {
                'name': 'Experiencia como Contratista',
                'category': 'experience',
                'mandatory_fields': 22,
                'estimated_time': 60,
                'required_for': ['obras', 'servicios'],
                'description': 'Historial de contratos ejecutados como contratista principal'
            },
            'SNCC.D.048': {
                'name': 'Experiencia Profesional del Personal Principal',
                'category': 'experience',
                'mandatory_fields': 16,
                'estimated_time': 45,
                'required_for': ['consultoria', 'servicios'],
                'description': 'Experiencia detallada del personal clave asignado al proyecto'
            },
            'SNCC.D.045': {
                'name': 'Currículo del Personal Profesional Propuesto',
                'category': 'personnel',
                'mandatory_fields': 14,
                'estimated_time': 35,
                'required_for': ['consultoria', 'servicios'],
                'description': 'CV detallado del personal profesional propuesto para el proyecto'
            },
            'SNCC.D.044': {
                'name': 'Descripción del Enfoque Metodología y Plan de Actividades',
                'category': 'methodology',
                'mandatory_fields': 25,
                'estimated_time': 90,
                'required_for': ['consultoria', 'servicios'],
                'description': 'Metodología de trabajo y cronograma detallado de actividades'
            },
            'SNCC.D.043': {
                'name': 'Organización y Experiencia del Consultor',
                'category': 'experience',
                'mandatory_fields': 18,
                'estimated_time': 55,
                'required_for': ['consultoria'],
                'description': 'Estructura organizacional y experiencia específica en consultoría'
            },
            'SNCC.D.038': {
                'name': 'Garantía de Fiel Cumplimiento de Contrato',
                'category': 'guarantee',
                'mandatory_fields': 12,
                'estimated_time': 25,
                'requires_notarization': True,
                'required_for': ['all'],
                'description': 'Garantía bancaria o póliza de seguro para cumplimiento del contrato'
            },
            'COMPROMISO_ETICO': {
                'name': 'Compromiso Ético de Proveedores',
                'category': 'commitment',
                'mandatory_fields': 10,
                'estimated_time': 20,
                'requires_notarization': True,
                'required_for': ['all'],
                'description': 'Compromiso de cumplimiento de normas éticas y anticorrupción'
            }
        }
    
    @api.model
    def create_standard_sncc_forms(self):
        """Create all standard SNCC forms automatically"""
        sncc_forms = self._get_sncc_form_definitions()
        
        for form_code, form_data in sncc_forms.items():
            existing = self.search([('form_code', '=', form_code)])
            if not existing:
                # Map template_type based on form_code
                template_type_mapping = {
                    'SNCC.F.047': 'manufacturer_auth',
                    'SNCC.F.042': 'bidder_info', 
                    'SNCC.F.037': 'staff_personnel',
                    'SNCC.F.036': 'bidder_equipment',
                    'SNCC.F.035': 'technical_support',
                    'SNCC.F.034': 'bid_presentation',
                    'SNCC.F.033': 'economic_offer',
                    'SNCC.D.052': 'agent_acceptance',
                    'SNCC.D.051': 'agent_designation',
                    'SNCC.D.049': 'contractor_experience',
                    'SNCC.D.048': 'professional_experience',
                    'SNCC.D.045': 'professional_cv',
                    'SNCC.D.044': 'methodology_plan',
                    'SNCC.D.043': 'consultant_organization',
                    'SNCC.D.038': 'performance_guarantee',
                    'COMPROMISO_ETICO': 'ethical_commitment'
                }
                
                self.create({
                    'name': form_data['name'],
                    'form_code': form_code,
                    'template_type': template_type_mapping.get(form_code, 'technical_proposal'),
                    'document_category': form_data['category'],
                    'mandatory_fields_count': form_data['mandatory_fields'],
                    'estimated_completion_time': form_data['estimated_time'],
                    'requires_notarization': form_data.get('requires_notarization', False),
                    'is_sncc_standard_form': True,
                    'required_for_procedures': form_data['required_for'][0] if form_data['required_for'] != ['all'] else 'all',
                    'auto_generate': True
                })
    
    # Smart Form Dependencies
    @api.model
    def get_required_forms_for_tender(self, tender_type, procurement_method, scope='national'):
        """Get list of required forms based on tender characteristics"""
        required_forms = []
        
        # Always required forms
        always_required = ['SNCC.F.042', 'SNCC.F.034', 'SNCC.F.033', 'COMPROMISO_ETICO']
        required_forms.extend(always_required)
        
        # Conditional forms based on tender type
        if 'obras' in procurement_method.lower() or tender_type.code in ['LICIT_PUB', 'LICIT_REST']:
            required_forms.extend(['SNCC.D.049', 'SNCC.F.036'])
            
        if 'consultoria' in procurement_method.lower() or 'servicios' in procurement_method.lower():
            required_forms.extend(['SNCC.F.037', 'SNCC.D.048', 'SNCC.D.045', 'SNCC.D.044', 'SNCC.D.043'])
            
        if 'bienes' in procurement_method.lower():
            required_forms.extend(['SNCC.F.047', 'SNCC.F.035'])
            
        # International scope requirements
        if scope == 'international':
            required_forms.extend(['SNCC.D.051', 'SNCC.D.052'])
            
        # Contract value determines guarantee requirements
        required_forms.append('SNCC.D.038')  # Always required for significant contracts
        
        return list(set(required_forms))  # Remove duplicates

class TemplateFieldMapping(models.Model):
    _name = 'govcon.template.field.mapping'
    _description = 'Template Field Mappings'
    
    template_id = fields.Many2one('govcon.document.template', 'Template')
    template_field_name = fields.Char('Template Field')  # {{company_name}}
    odoo_field_path = fields.Char('Odoo Field Path')     # tender_id.company_id.name
    default_value = fields.Text('Default Value')
    is_required = fields.Boolean('Required')

class GeneratedDocument(models.Model):
    _name = 'govcon.generated.document'
    _description = 'Generated Documents'
    _order = 'generation_date desc'
    
    tender_id = fields.Many2one('govcon.tender', 'Tender', required=True)
    template_id = fields.Many2one('govcon.document.template', 'Template')
    document_name = fields.Char('Document Name')
    
    # File Storage
    document_file = fields.Binary('Document File')
    document_filename = fields.Char('Filename')
    document_url = fields.Char('External URL')
    
    # Generation Info
    generation_date = fields.Datetime('Generated On', default=fields.Datetime.now)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('error', 'Error')
    ], default='draft')
    
    def generate_document(self):
        """Generate document using ibiDs API"""
        template_data = self.tender_id._collect_template_data(self.template_id)
        
        if self.template_id.ibids_template_id:
            result = self._call_ibids_api(template_data)
        else:
            result = self._generate_internal_template(template_data)
        
        self.write({
            'document_file': result.get('content'),
            'document_filename': result.get('filename'),
            'document_url': result.get('url'),
            'status': 'generated'
        })
    
    def _call_ibids_api(self, template_data):
        """Call ibiDs API for document generation"""
        # Placeholder for ibiDs API integration
        return {
            'content': b'Generated document content',
            'filename': f"{self.document_name}.pdf",
            'url': None
        }
    
    def _generate_internal_template(self, template_data):
        """Generate document using internal template system"""
        # Placeholder for internal template generation
        return {
            'content': b'Generated document content',
            'filename': f"{self.document_name}.pdf",
            'url': None
        }
    
    def download_document(self):
        """Download the generated document"""
        if not self.document_file:
            raise UserError(_('No document file available for download'))
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model={self._name}&id={self.id}&field=document_file&filename_field=document_filename&download=true',
            'target': 'self',
        } 
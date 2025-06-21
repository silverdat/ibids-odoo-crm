# Government Contracting CRM - Dominican Republic

A comprehensive Odoo module for managing Dominican Republic government contracting processes with automated workflows, document generation, and intelligent tender tracking based on Law 340-06 procurement procedures.

## Features

### 🎯 Core Functionality
- **Email-to-CRM Workflow**: One-click import from bid notification emails
- **Auto-Discovery System**: Automatically handles any date fields from your API without configuration
- **Dominican Republic Compliance**: All 16 official procurement procedures from Law 340-06
- **Standard SNCC Forms**: Complete set of 16 official Dominican Republic procurement forms with smart recommendations
- **Dynamic Workflows**: Different stage flows based on tender type
- **Automated Sync**: Nightly monitoring of tender changes with smart change detection
- **Smart Alerts**: Context-aware notifications for deadline changes
- **Document Generation**: Integration with ibiDs for proposal automation
- **Performance Tracking**: Win rates, pipeline analysis, and forecasting
- **Compliance Management**: Track all requirements, budgets, and certifications
- **Line Item Management**: Detailed cost breakdown with price analysis from Avahi data
- **Form Intelligence**: Automatic form recommendations based on tender type and procurement method

### 📋 Standard SNCC Forms Included

**Always Required:**
- Compromiso Ético de Proveedores
- SNCC.F.042 - Formulario de Información sobre el Oferente
- SNCC.F.034 - Presentación de Oferta
- SNCC.F.033 - Oferta Económica
- SNCC.D.038 - Garantía de Fiel Cumplimiento de Contrato

**Goods/Supplies (Bienes):**
- SNCC.F.047 - Autorización del Fabricante
- SNCC.F.035 - Estructura para Brindar Soporte Técnico

**Construction Works (Obras):**
- SNCC.D.049 - Experiencia como Contratista
- SNCC.F.036 - Equipos del Oferente

**Services/Consulting (Servicios/Consultoría):**
- SNCC.F.037 - Personal de Plantilla del Oferente
- SNCC.D.048 - Experiencia Profesional del Personal Principal
- SNCC.D.045 - Currículo del Personal Profesional Propuesto
- SNCC.D.044 - Descripción del Enfoque Metodología y Plan de Actividades
- SNCC.D.043 - Organización y Experiencia del Consultor

**International Scope:**
- SNCC.D.051 - Carta de Designación o Sustitución de Agente Autorizado
- SNCC.D.052 - Carta de Aceptación de Designación como Agente Autorizado

## Installation

### 1. Module Installation
```bash
# Copy the module to your Odoo addons directory
cp -r govcon_crm /path/to/odoo/addons/

# Update the addons list in Odoo
# Go to Apps > Update Apps List

# Install the module
# Go to Apps > Search "Government Contracting CRM" > Install
```

### 2. API Configuration
Configure your government API credentials in Odoo settings:

```python
# In Odoo Settings > Technical > Parameters
govcon.api_url = https://your-api-endpoint.com
govcon.api_token = your-api-token
govcon.notify_date_changes = True
```

### 3. Email Integration
Set up email gateway for bid notifications:

1. Configure email alias (e.g., `bids@yourcompany.com`)
2. Set up email routing to process incoming bid notifications
3. Configure email processing rules

### 4. ibiDs Integration
Set up API credentials for document generation:

```python
# In Odoo Settings > Technical > Parameters
govcon.ibids_api_url = https://your-ibids-api.com
govcon.ibids_api_token = your-ibids-token
```

## Usage

### Creating a New Tender

1. **Manual Creation**:
   - Go to Government CRM > Tenders > Create
   - Fill in basic information
   - Select tender type (auto-classified based on description)
   - Add line items and important dates

2. **Email Import**:
   - Forward bid notification emails to configured email address
   - System automatically processes and creates tender records
   - Auto-classifies tender type and extracts dates

3. **API Sync**:
   - Use "Sync from API" button on tender form
   - System fetches latest data and updates all fields
   - Detects and notifies about changes

### Document Generation

1. **Automatic Generation**:
   - Click "Generate Documents" on tender form
   - System creates all required SNCC forms based on tender type
   - Documents are pre-populated with tender data

2. **Manual Generation**:
   - Go to Document Templates
   - Select specific forms to generate
   - Customize field mappings as needed

### Monitoring and Alerts

- **Dashboard**: View all tenders with deadline indicators
- **Kanban View**: Drag and drop tenders between stages
- **Alerts**: Automatic notifications for:
  - Deadline changes
  - New documents/amendments
  - Sync errors
  - Overdue tenders

## Configuration

### Tender Types
The module includes all 16 Dominican Republic procurement procedures:

**Regular Procedures:**
- Licitación Pública
- Licitación Restringida
- Subasta Inversa
- Sorteo de Obras
- Comparación de Precios
- Compra Menor
- Compra por Debajo del Umbral

**Exception Procedures (Competitive):**
- Seguridad Nacional
- Emergencia Nacional
- Urgencia
- Exclusividad
- MIPYMES
- Rescisión de Contratos

**Exception Procedures (Direct):**
- Proveedor Único
- Obras Científicas/Técnicas/Artísticas
- Servicio Exterior
- Publicidad

### Stages
Each tender type has configurable stages:
- Publication
- Pre-bid Meeting
- Questions & Answers
- Submission
- Evaluation
- Award
- Contract Execution

### Document Templates
All 16 standard SNCC forms are pre-configured with:
- Field mappings to Odoo data
- Prerequisites and dependencies
- Auto-population rules
- Notarization requirements

## API Integration

### Required API Endpoints

```python
# Fetch tender data
GET /api/tenders/{tender_id}

# Response format
{
    "tender_id": "string",
    "description": "string",
    "procuring_entity": "string",
    "tender_value": float,
    "submission_deadline": "datetime",
    "award_date": "datetime",
    "publication_date": "datetime",
    # ... any additional datetime fields
}
```

### Customization
The auto-discovery system handles any datetime fields from your API:
- Automatically creates date field definitions
- Tracks usage patterns
- Provides intelligent field naming
- Supports change detection and notifications

## Troubleshooting

### Common Issues

1. **Sync Errors**:
   - Check API credentials in settings
   - Verify API endpoint accessibility
   - Review sync error logs

2. **Document Generation Issues**:
   - Verify ibiDs API configuration
   - Check template field mappings
   - Review document template settings

3. **Email Processing Issues**:
   - Verify email gateway configuration
   - Check email routing rules
   - Review email processing logs

### Logs
Check Odoo logs for detailed error information:
```bash
tail -f /var/log/odoo/odoo-server.log | grep govcon
```

## Support

For technical support or customization requests:
- Email: support@yourcompany.com
- Documentation: https://docs.yourcompany.com/govcon-crm
- GitHub Issues: https://github.com/yourcompany/govcon-crm/issues

## License

This module is licensed under LGPL-3. See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Version History

- **v1.0.0**: Initial release with all core features
  - Complete Dominican Republic procurement procedures
  - All 16 standard SNCC forms
  - Auto-discovery date system
  - Email-to-CRM workflow
  - Nightly sync service
  - Document generation with ibiDs integration 
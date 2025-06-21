{
    'name': 'Government Contracting CRM - Dominican Republic',
    'version': '1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Dominican Republic Government Contracting Management System',
    'description': """
        Comprehensive CRM for managing Dominican Republic government contracting processes
        based on Law 340-06 procurement procedures.
        
        Features:
        - Email-to-CRM workflow for bid notifications
        - Auto-discovery of date fields from API
        - Dynamic stage management by tender type
        - Nightly synchronization with government APIs
        - Document automation with ibiDs integration
        - All 16 standard SNCC procurement forms
        - Performance tracking and analytics
        - Compliance management
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'mail',
        'contacts',
        'project',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/tender_data.xml',
        'views/tender_views.xml',
        'views/tender_type_views.xml',
        'views/document_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
} 
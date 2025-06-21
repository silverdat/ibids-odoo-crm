# ibiDs API Integration Summary

## Overview
The `govcon_crm` module has been updated to perfectly align with the ibiDs API field structure for both tender data and tender articles.

## API Field Mapping

### Tender Data Fields (Main Tender Model)

| ibiDs API Field | CRM Field | Type | Description |
|-----------------|-----------|------|-------------|
| `tender_id` | `tender_id` | Char | Tender ID from compras |
| `procuring_entity` | `procuring_entity` | Char | Procuring entity from compras |
| `tender_value` | `tender_value` | Float | Tender value from compras |
| `description` | `description` | Text | Tender description from compras |
| `all_tender_dates` | `all_tender_dates` | Datetime | Returns all dates in the tender's timeline |
| `budget_appropriation_certificate` | `budget_appropriation_certificate` | Char | PDF S3 link |
| `budget_appropriation_value` | `budget_appropriation_value` | Float | Budget appropriation value |
| `budget_source` | `budget_source` | Char | Budget source information |
| `define_advance_payments` | `define_advance_payments` | Boolean | Whether advance payments are defined |
| `advance_payment_pct` | `advance_payment_pct` | Float | Advance payment percentage |
| `define_warranties` | `define_warranties` | Boolean | Whether warranties are defined |
| `seriousness_of_the_offer` | `seriousness_of_the_offer` | Boolean | Seriousness of the offer requirement |
| `offer_seriousness_pct` | `offer_seriousness_pct` | Float | Offer seriousness percentage |
| `compliance` | `compliance` | Boolean | Compliance requirement |
| `compliance_pct` | `compliance_pct` | Float | Compliance percentage |
| `extra_civil_contractual_liability` | `extra_civil_contractual_liability` | Boolean | Extra civil contractual liability requirement |
| `link_all_pliego_docs` | `link_all_pliego_docs` | Char | S3 link to all pliego documents |
| `tender_messages` | `tender_messages` | Text | Daily scrape to see if new comments/addenda are added |
| `tender_url` | `tender_url` | Char | URL to the tender |
| `procurement_method` | `procurement_method` | Char | Procurement method from compras |
| `ibids_gpt_url` | `ibids_gpt_url` | Char | URL to the tender in ibiDs GPT |
| `tender_mail_summary_gpt` | `tender_mail_summary_gpt` | Text | Summary of requirements for the tender included in the email |
| `tender_generator_link_other` | `tender_generator_link_other` | Char | Link for generation of standard docs per generator |
| `f33_tender_link` | `f33_tender_link` | Char | Link to the prep of the F33 form |

### Tender Articles Fields (Line Items)

| ibiDs API Field | CRM Field | Type | Description |
|-----------------|-----------|------|-------------|
| `tender_id` | `tender_id` | Many2one | Reference to parent tender |
| `article_number` | `article_number` | Char | Article number from compras |
| `article_description` | `article_description` | Text | Article description from compras |
| `lot_info` | `lot_info` | Char | Lot information from compras |
| `unit` | `unit` | Char | Unit from compras |
| `quantity` | `quantity` | Float | Quantity from compras |
| `unit_price` | `unit_price` | Float | Unit price from compras |
| `total_price` | `total_price` | Float | Total price (computed) |
| `unspsc_code` | `unspsc_code` | Char | UNSPSC code from compras |
| `unspsc_description` | `unspsc_description` | Char | UNSPSC description from compras |
| `ibids_estimated_price` | `ibids_estimated_price` | Float | From ibiDs: estimated vs awarded delta |
| `avahi_price_25_quartile` | `avahi_price_25_quartile` | Float | From ibiDs: avg of where 25% of prices are |
| `avahi_price_75_quartile` | `avahi_price_75_quartile` | Float | From ibiDs: avg of where 75% of prices are |
| `competitiveness_rank` | `competitiveness_rank` | Float | From ibiDs: #of tenders for given unspsc / # of offers |

## Updated Components

### 1. Data Models
- **`govcon.tender`**: Updated with all ibiDs API fields for tender data
- **`govcon.tender.line`**: Updated with all ibiDs API fields for tender articles
- **`govcon.sync.service`**: Updated to handle API field mapping and synchronization

### 2. Views
- **Form View**: Organized into logical tabs (Basic Info, Budget & Financial, Compliance & Requirements, Documents & Links, Communication, Tender Lines, Notes)
- **Tree View**: Shows key fields for quick overview
- **Kanban View**: Visual representation with priority and status
- **Search View**: Advanced filtering and grouping options

### 3. Sync Service
- **API Integration**: Handles both tender data and articles synchronization
- **Field Mapping**: Direct mapping from ibiDs API to CRM fields
- **Error Handling**: Robust error handling and logging
- **Statistics**: Tracks sync performance and success rates

### 4. Email Processor
- **Field Extraction**: Extracts relevant data from email notifications
- **Auto-creation**: Creates tenders with partial data from emails
- **Classification**: Auto-classifies tender types based on content

### 5. Security
- **Access Rights**: Proper permissions for all models
- **User/Manager Roles**: Different access levels for users and managers

## Key Features

### 1. Complete API Field Coverage
- All ibiDs API fields are mapped to corresponding CRM fields
- No data loss during synchronization
- Proper data types and constraints

### 2. Intelligent Data Processing
- Computed fields for price analysis and competitiveness
- Automatic date parsing from `all_tender_dates`
- Price variance calculations

### 3. User-Friendly Interface
- Organized tab structure for easy navigation
- Monetary and percentage widgets for financial data
- Status bars and progress indicators

### 4. Automated Workflows
- Email-to-CRM workflow
- API synchronization
- Document generation triggers

### 5. Analytics and Reporting
- Price competitiveness analysis
- Win probability tracking
- Performance metrics

## Integration Points

### 1. API Endpoints
- `/tenders` - Fetch tender data
- `/tenders/{id}/articles` - Fetch tender articles

### 2. Authentication
- Bearer token authentication
- Configurable API keys per service

### 3. Data Flow
1. **Email Processing**: Extract tender info from notifications
2. **API Sync**: Pull complete data from ibiDs API
3. **Data Storage**: Store in CRM with proper field mapping
4. **User Interface**: Display data in organized views
5. **Document Generation**: Generate required documents

## Configuration

### 1. API Setup
```python
# Configure sync service
sync_service = env['govcon.sync.service'].create({
    'name': 'ibiDs API Sync',
    'api_url': 'https://api.ibids.com',
    'api_key': 'your-api-key',
    'sync_interval_hours': 24
})
```

### 2. Email Processing
```python
# Configure email processor
email_processor = env['govcon.email.processor'].create({
    'name': 'Tender Email Processor',
    'email_address': 'tenders@company.com',
    'auto_classify_tenders': True,
    'auto_create_tenders': True
})
```

## Benefits

1. **Seamless Integration**: Direct field mapping ensures no data loss
2. **Real-time Updates**: Automated synchronization keeps data current
3. **User Experience**: Intuitive interface for managing tenders
4. **Compliance**: Supports Dominican Republic procurement requirements
5. **Analytics**: Built-in competitive analysis and pricing insights
6. **Automation**: Reduces manual data entry and processing time

## Next Steps

1. **Install Module**: Install the updated `govcon_crm` module
2. **Configure API**: Set up API credentials and endpoints
3. **Test Integration**: Verify data synchronization works correctly
4. **Train Users**: Educate users on new interface and features
5. **Monitor Performance**: Track sync success rates and user adoption

The module is now fully aligned with your ibiDs API structure and ready for production use. 
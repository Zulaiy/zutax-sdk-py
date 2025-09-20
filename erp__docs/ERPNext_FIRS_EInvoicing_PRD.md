# Product Requirements Document (PRD)
## ERPNext App for Nigerian FIRS E-Invoicing

### Document Information
- **Version**: 1.0
- **Date**: September 20, 2025
- **Author**: Development Team
- **Status**: Draft

---

## 1. Executive Summary

### 1.1 Product Overview
The ERPNext FIRS E-Invoicing App is a comprehensive solution that integrates with ERPNext to provide automated compliance with Nigerian Federal Inland Revenue Service (FIRS) e-invoicing requirements. The app leverages the Zutax Python SDK to handle TIN validation, invoice generation, IRN creation, digital signing, QR code generation, and real-time status tracking.

### 1.2 Business Objectives
- **Compliance**: Ensure 100% compliance with Nigerian FIRS e-invoicing regulations
- **Automation**: Reduce manual processes and eliminate human errors in invoice submission
- **Efficiency**: Streamline invoice processing workflow within ERPNext
- **Transparency**: Provide real-time visibility into invoice status and compliance
- **Integration**: Seamless integration with existing ERPNext sales workflow

### 1.3 Success Metrics
- 95% successful invoice submissions on first attempt
- <30 seconds average processing time per invoice
- 100% accurate TIN validation
- Zero compliance violations
- 90% user satisfaction score

---

## 2. Product Scope

### 2.1 In Scope
- **Core Features**:
  - TIN validation for transacting parties
  - IRN (Invoice Reference Number) generation
  - Local and remote invoice validation
  - FIRS API integration for invoice submission
  - Real-time status tracking and updates
  - QR code generation for invoices
  - Digital signing capabilities
  - Batch processing support
  - Error handling and retry mechanisms
  - Audit trail and compliance reporting

- **ERPNext Integration**:
  - Sales Invoice integration
  - Customer and Supplier TIN management
  - Custom DocType for FIRS Invoice tracking
  - Workflow automation
  - Custom buttons and UI enhancements
  - Report generation

### 2.2 Out of Scope (Future Phases)
- Credit notes and debit notes (Phase 2)
- Purchase invoice compliance (Phase 2)
- Multi-company support (Phase 2)
- Advanced analytics dashboard (Phase 3)
- Mobile app integration (Phase 3)

---

## 3. User Stories and Requirements

### 3.1 Primary Users

#### 3.1.1 Accounts Manager
- **Role**: Manages invoicing process and ensures compliance
- **Goals**: Efficient invoice processing, compliance assurance, error resolution
- **Pain Points**: Manual compliance checks, delayed submissions, tracking difficulties

#### 3.1.2 Sales Representative
- **Role**: Creates and submits sales invoices
- **Goals**: Quick invoice generation, customer satisfaction
- **Pain Points**: Complex compliance requirements, submission delays

#### 3.1.3 System Administrator
- **Role**: Manages system configuration and troubleshooting
- **Goals**: System reliability, user support, configuration management
- **Pain Points**: Complex integrations, error debugging, user training

### 3.2 Core User Stories

#### Story 1: TIN Validation
**As an** Accounts Manager  
**I want to** automatically validate customer and supplier TIN numbers  
**So that** I can ensure compliance before invoice submission  

**Acceptance Criteria**:
- System validates TIN format (8-15 digits)
- Real-time validation feedback
- Integration with Customer and Supplier masters
- Bulk TIN validation capability
- Error messaging for invalid TINs

#### Story 2: FIRS Invoice Generation
**As a** Sales Representative  
**I want to** generate FIRS-compliant invoices from Sales Invoice  
**So that** I can submit invoices to FIRS without manual intervention  

**Acceptance Criteria**:
- One-click generation from submitted Sales Invoice
- Automatic IRN generation
- Invoice validation before submission
- Preview capability before submission
- Error handling with clear messages

#### Story 3: Real-time Status Tracking
**As an** Accounts Manager  
**I want to** track the real-time status of submitted invoices  
**So that** I can monitor compliance and resolve issues promptly  

**Acceptance Criteria**:
- Real-time status updates
- Status history tracking
- Automated retry for failed submissions
- Alert notifications for status changes
- Bulk status checking

#### Story 4: QR Code Integration
**As a** Sales Representative  
**I want to** generate and attach QR codes to invoices  
**So that** customers can easily verify invoice authenticity  

**Acceptance Criteria**:
- Automatic QR code generation
- QR code attachment to PDF invoices
- QR code verification capability
- Custom QR code positioning
- Batch QR code generation

---

## 4. Functional Requirements

### 4.1 Core Functionality

#### 4.1.1 TIN Management and Validation
- **FR-01**: The system SHALL validate TIN format for all parties (8-15 digits, numeric only)
- **FR-02**: The system SHALL provide real-time TIN validation feedback
- **FR-03**: The system SHALL integrate TIN validation with Customer and Supplier DocTypes
- **FR-04**: The system SHALL support bulk TIN validation
- **FR-05**: The system SHALL maintain TIN validation history and audit trail

#### 4.1.2 Invoice Processing
- **FR-06**: The system SHALL generate FIRS Invoice from submitted Sales Invoice
- **FR-07**: The system SHALL automatically generate IRN using FIRS-compliant format
- **FR-08**: The system SHALL perform local validation before submission
- **FR-09**: The system SHALL submit invoices to FIRS API with proper authentication
- **FR-10**: The system SHALL handle batch invoice processing

#### 4.1.3 Status Management
- **FR-11**: The system SHALL track invoice status in real-time
- **FR-12**: The system SHALL provide status update notifications
- **FR-13**: The system SHALL maintain complete audit trail
- **FR-14**: The system SHALL support invoice cancellation
- **FR-15**: The system SHALL implement automatic retry mechanism

#### 4.1.4 QR Code and Digital Signing
- **FR-16**: The system SHALL generate FIRS-compliant QR codes
- **FR-17**: The system SHALL attach QR codes to invoice PDFs
- **FR-18**: The system SHALL support digital signing of invoices
- **FR-19**: The system SHALL verify QR code authenticity
- **FR-20**: The system SHALL handle certificate management

### 4.2 Integration Requirements

#### 4.2.1 ERPNext Integration
- **IR-01**: The system SHALL integrate seamlessly with Sales Invoice DocType
- **IR-02**: The system SHALL extend Customer and Supplier DocTypes for TIN storage
- **IR-03**: The system SHALL provide custom buttons in Sales Invoice
- **IR-04**: The system SHALL create workflow automation
- **IR-05**: The system SHALL generate compliance reports

#### 4.2.2 Zutax SDK Integration
- **IR-06**: The system SHALL use Zutax Python SDK for all FIRS interactions
- **IR-07**: The system SHALL handle SDK errors gracefully
- **IR-08**: The system SHALL implement SDK retry logic
- **IR-09**: The system SHALL maintain SDK configuration
- **IR-10**: The system SHALL log all SDK interactions

### 4.3 Data Requirements

#### 4.3.1 Data Storage
- **DR-01**: The system SHALL store all invoice submissions with complete data
- **DR-02**: The system SHALL maintain referential integrity with ERPNext data
- **DR-03**: The system SHALL implement data archiving for compliance
- **DR-04**: The system SHALL support data export for auditing
- **DR-05**: The system SHALL encrypt sensitive data

#### 4.3.2 Data Validation
- **DR-06**: The system SHALL validate all required fields before submission
- **DR-07**: The system SHALL ensure data consistency across systems
- **DR-08**: The system SHALL validate business rules compliance
- **DR-09**: The system SHALL handle data transformation requirements
- **DR-10**: The system SHALL support data cleansing operations

---

## 5. Non-Functional Requirements

### 5.1 Performance Requirements
- **PF-01**: System response time SHALL be <3 seconds for single invoice processing
- **PF-02**: Batch processing SHALL handle minimum 100 invoices per batch
- **PF-03**: System SHALL support concurrent users (minimum 20 users)
- **PF-04**: API calls SHALL have timeout handling (30 seconds maximum)
- **PF-05**: System SHALL maintain 99.5% uptime

### 5.2 Security Requirements
- **SC-01**: All API communications SHALL use HTTPS/TLS 1.3
- **SC-02**: API credentials SHALL be encrypted and stored securely
- **SC-03**: User access SHALL be role-based and auditable
- **SC-04**: Sensitive data SHALL be encrypted at rest
- **SC-05**: System SHALL implement session management and timeout

### 5.3 Reliability Requirements
- **RL-01**: System SHALL implement comprehensive error handling
- **RL-02**: Failed operations SHALL be retried automatically (max 3 attempts)
- **RL-03**: System SHALL maintain operation logs for 7 years
- **RL-04**: System SHALL support graceful degradation
- **RL-05**: Data backup SHALL be performed daily

### 5.4 Usability Requirements
- **UX-01**: User interface SHALL follow ERPNext design patterns
- **UX-02**: Error messages SHALL be clear and actionable
- **UX-03**: System SHALL provide contextual help
- **UX-04**: All operations SHALL have progress indicators
- **UX-05**: System SHALL support keyboard shortcuts

### 5.5 Compatibility Requirements
- **CP-01**: System SHALL be compatible with ERPNext v16+
- **CP-02**: System SHALL support Python 3.8+
- **CP-03**: System SHALL work with major web browsers
- **CP-04**: System SHALL be mobile-responsive
- **CP-05**: System SHALL support database clustering

---

## 6. Technical Architecture

### 6.1 System Architecture

#### 6.1.1 High-Level Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   ERPNext UI    │───▶│  FIRS E-Invoice  │───▶│   Zutax SDK     │
│                 │    │      App         │    │                 │
│ • Sales Invoice │    │ • FIRS Invoice   │    │ • TIN Validation│
│ • Customers     │    │ • Status Track   │    │ • IRN Generation│
│ • Suppliers     │    │ • QR Code Gen    │    │ • API Client    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  ERPNext DB     │    │   App Database   │    │   FIRS API      │
│                 │    │                  │    │                 │
│ • Sales Invoice │    │ • FIRS Invoice   │    │ • Validation    │
│ • Customer TIN  │    │ • Status Log     │    │ • Submission    │
│ • Supplier TIN  │    │ • Error Log      │    │ • Status Check  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

#### 6.1.2 Component Diagram
- **ERPNext Integration Layer**: Handles ERPNext-specific operations
- **Business Logic Layer**: Implements core business rules
- **SDK Integration Layer**: Manages Zutax SDK interactions
- **Data Access Layer**: Handles database operations
- **API Communication Layer**: Manages external API calls

### 6.2 Data Architecture

#### 6.2.1 New DocTypes

##### FIRS Invoice
```python
# Primary DocType for tracking FIRS invoice submissions
{
    "name": "FIRS Invoice",
    "fields": [
        {"fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice"},
        {"fieldname": "irn", "fieldtype": "Data"},
        {"fieldname": "invoice_hash", "fieldtype": "Data"},
        {"fieldname": "qr_code", "fieldtype": "Attach Image"},
        {"fieldname": "submission_status", "fieldtype": "Select"},
        {"fieldname": "firs_status", "fieldtype": "Select"},
        {"fieldname": "error_message", "fieldtype": "Long Text"},
        {"fieldname": "submission_date", "fieldtype": "Datetime"},
        {"fieldname": "last_updated", "fieldtype": "Datetime"},
        # Additional fields for compliance tracking
    ]
}
```

##### FIRS Status Log
```python
# Child DocType for status tracking
{
    "name": "FIRS Status Log",
    "fields": [
        {"fieldname": "timestamp", "fieldtype": "Datetime"},
        {"fieldname": "status", "fieldtype": "Data"},
        {"fieldname": "message", "fieldtype": "Text"},
        {"fieldname": "response_data", "fieldtype": "JSON"},
    ]
}
```

#### 6.2.2 Extended DocTypes

##### Customer Extension
- Add `tin` field with validation
- Add `firs_validation_status` field
- Add `tin_validation_date` field

##### Supplier Extension  
- Add `tin` field with validation
- Add `firs_validation_status` field  
- Add `tin_validation_date` field

### 6.3 Integration Patterns

#### 6.3.1 Workflow Integration
```python
# Sales Invoice workflow hooks
def on_submit(doc, method):
    """Enable FIRS invoice generation after submission"""
    pass

def before_cancel(doc, method):
    """Handle FIRS invoice cancellation"""
    pass
```

#### 6.3.2 API Integration Patterns
- Asynchronous processing for bulk operations
- Retry mechanism with exponential backoff
- Circuit breaker pattern for API failures
- Request/response logging for audit

---

## 7. User Experience Design

### 7.1 User Interface Requirements

#### 7.1.1 Sales Invoice Enhancements
- **Custom Button**: "Generate FIRS Invoice" button in toolbar
- **Status Indicator**: Visual indicator showing FIRS compliance status
- **TIN Validation**: Real-time TIN validation for customer/supplier
- **QR Code Preview**: Inline QR code display after generation

#### 7.1.2 FIRS Invoice Form
- **Clean Layout**: Follows ERPNext design guidelines
- **Status Dashboard**: Visual status tracking with progress indicators
- **Error Handling**: Clear error messages with resolution suggestions
- **Action Buttons**: Submit, Retry, Cancel, View Status buttons

#### 7.1.3 Dashboard Integration
- **FIRS Compliance Dashboard**: Overview of invoice statuses
- **Quick Stats**: Submitted, Pending, Failed, Cancelled counts
- **Recent Activity**: Latest submission activities
- **Error Summary**: Common errors and resolution tips

### 7.2 User Workflows

#### 7.2.1 Standard Invoice Processing Workflow
1. User creates and submits Sales Invoice
2. System validates customer/supplier TIN
3. User clicks "Generate FIRS Invoice" button
4. System creates FIRS Invoice record
5. System validates invoice data locally
6. User reviews and submits to FIRS
7. System tracks status and updates accordingly

#### 7.2.2 Bulk Processing Workflow
1. User selects multiple submitted Sales Invoices
2. User initiates bulk FIRS processing
3. System processes invoices in background
4. System provides progress updates
5. User reviews results and handles exceptions

#### 7.2.3 Error Resolution Workflow
1. System identifies submission error
2. System notifies user with clear error message
3. User resolves underlying issue
4. User initiates retry operation
5. System reprocesses and updates status

---

## 8. Implementation Plan

### 8.1 Development Phases

#### Phase 1: Foundation (Weeks 1-4)
- **Week 1-2**: Environment setup and SDK integration
- **Week 3-4**: Core DocTypes and basic validation

#### Phase 2: Core Features (Weeks 5-10)  
- **Week 5-6**: TIN validation and management
- **Week 7-8**: IRN generation and invoice processing
- **Week 9-10**: FIRS API integration and submission

#### Phase 3: Advanced Features (Weeks 11-16)
- **Week 11-12**: QR code generation and digital signing
- **Week 13-14**: Status tracking and batch processing
- **Week 15-16**: Error handling and retry mechanisms

#### Phase 4: Polish & Deploy (Weeks 17-20)
- **Week 17-18**: UI enhancements and user testing
- **Week 19-20**: Final testing, documentation, and deployment

### 8.2 Technical Dependencies
- ERPNext v14+ installation
- Python 3.8+ environment
- Zutax SDK installation and configuration
- FIRS API access credentials
- SSL certificates for production

### 8.3 Resource Requirements
- **Development Team**: 2-3 developers
- **QA Team**: 1 tester
- **DevOps**: 1 infrastructure engineer
- **Product Owner**: 1 business analyst
- **Timeline**: 20 weeks for complete implementation

---

## 9. Risk Assessment

### 9.1 Technical Risks

#### High Risk
- **FIRS API Changes**: Risk of breaking changes in FIRS API
  - *Mitigation*: Regular API monitoring, version management
- **SDK Updates**: Risk of incompatible Zutax SDK updates
  - *Mitigation*: Version pinning, thorough testing

#### Medium Risk  
- **Performance Issues**: Risk of slow processing with large volumes
  - *Mitigation*: Performance testing, optimization
- **Data Consistency**: Risk of data sync issues between systems
  - *Mitigation*: Transaction management, data validation

#### Low Risk
- **UI Compatibility**: Risk of ERPNext UI changes affecting app
  - *Mitigation*: Standard ERPNext patterns, regular testing

### 9.2 Business Risks

#### High Risk
- **Compliance Changes**: Risk of regulatory requirement changes
  - *Mitigation*: Regular compliance review, flexible architecture
- **User Adoption**: Risk of low user adoption
  - *Mitigation*: User training, intuitive design

#### Medium Risk
- **Data Migration**: Risk of data loss during migration
  - *Mitigation*: Backup strategy, phased rollout
- **Integration Issues**: Risk of disrupting existing workflows  
  - *Mitigation*: Thorough testing, rollback plan

---

## 10. Success Criteria

### 10.1 Functional Success Criteria
- [ ] 100% of submitted Sales Invoices can generate FIRS Invoice
- [ ] TIN validation works for 100% of valid Nigerian TINs
- [ ] IRN generation follows FIRS specification exactly
- [ ] Invoice submission success rate >95%
- [ ] Status tracking updates within 30 seconds
- [ ] QR code generation works for 100% of submitted invoices

### 10.2 Performance Success Criteria
- [ ] Single invoice processing <3 seconds
- [ ] Batch processing handles 100+ invoices
- [ ] System supports 20+ concurrent users
- [ ] API response time <2 seconds average
- [ ] 99.5% system uptime maintained

### 10.3 Business Success Criteria
- [ ] Zero compliance violations post-deployment
- [ ] 90%+ user satisfaction score
- [ ] 50% reduction in manual processing time
- [ ] 95% first-time submission success rate
- [ ] Complete audit trail for all transactions

---

## 11. Appendices

### Appendix A: Technical Specifications
- Detailed API specifications
- Database schema definitions
- Integration architecture diagrams

### Appendix B: Compliance Requirements
- FIRS e-invoicing regulations
- Data retention requirements
- Security compliance standards

### Appendix C: User Documentation
- User guide outline
- Training material structure
- Help documentation framework

---

**Document Control**
- Document Version: 1.0
- Last Updated: September 20, 2025
- Next Review Date: October 20, 2025
- Approval Status: Draft
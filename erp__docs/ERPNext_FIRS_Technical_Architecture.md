# ERPNext FIRS E-Invoicing App - Technical Architecture Specification

## 1. App Structure

### 1.1 Directory Structure
```
erpnext_firs_einvoice/
├── __init__.py
├── hooks.py                    # ERPNext app hooks
├── install.py                 # Installation script
├── uninstall.py              # Uninstallation script
├── config/
│   ├── __init__.py
│   ├── settings.py           # App configuration
│   └── constants.py          # FIRS-specific constants
├── erpnext_firs_einvoice/
│   ├── __init__.py
│   ├── doctype/
│   │   ├── firs_invoice/
│   │   │   ├── __init__.py
│   │   │   ├── firs_invoice.py
│   │   │   ├── firs_invoice.json
│   │   │   └── firs_invoice.js
│   │   ├── firs_status_log/
│   │   │   ├── __init__.py
│   │   │   ├── firs_status_log.py
│   │   │   ├── firs_status_log.json
│   │   │   └── firs_status_log.js
│   │   └── firs_settings/
│   │       ├── __init__.py
│   │       ├── firs_settings.py
│   │       ├── firs_settings.json
│   │       └── firs_settings.js
│   ├── api/
│   │   ├── __init__.py
│   │   ├── firs_client.py    # Zutax SDK wrapper
│   │   ├── invoice_api.py    # Invoice processing API
│   │   └── validation_api.py # TIN validation API
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── tin_validator.py  # TIN validation utilities
│   │   ├── irn_generator.py  # IRN generation
│   │   └── error_handler.py  # Error handling utilities
│   ├── reports/
│   │   ├── __init__.py
│   │   ├── firs_compliance_report/
│   │   └── invoice_status_report/
│   └── patches/
│       ├── __init__.py
│       └── v1_0/
│           ├── __init__.py
│           └── add_tin_fields.py
├── requirements.txt           # Python dependencies
├── README.md
└── setup.py
```

### 1.2 ERPNext App Configuration

#### hooks.py
```python
app_name = "erpnext_firs_einvoice"
app_title = "ERPNext FIRS E-Invoicing"
app_publisher = "Your Organization"
app_description = "FIRS E-Invoicing compliance for ERPNext"
app_version = "1.0.0"

# Document Events
doc_events = {
    "Sales Invoice": {
        "on_submit": "erpnext_firs_einvoice.api.invoice_api.on_sales_invoice_submit",
        "before_cancel": "erpnext_firs_einvoice.api.invoice_api.before_sales_invoice_cancel"
    },
    "Customer": {
        "validate": "erpnext_firs_einvoice.utils.tin_validator.validate_customer_tin"
    },
    "Supplier": {
        "validate": "erpnext_firs_einvoice.utils.tin_validator.validate_supplier_tin"
    }
}

# Custom Fields
fixtures = [
    {
        "doctype": "Custom Field",
        "filters": {"module": "ERPNext FIRS E-Invoicing"}
    }
]

# Scheduled Jobs
scheduler_events = {
    "cron": {
        "0 */2 * * *": [  # Every 2 hours
            "erpnext_firs_einvoice.api.invoice_api.update_pending_invoice_status"
        ],
        "0 0 * * *": [    # Daily at midnight
            "erpnext_firs_einvoice.api.invoice_api.retry_failed_submissions"
        ]
    }
}

# Jinja Environment
jinja = {
    "methods": [
        "erpnext_firs_einvoice.utils.tin_validator.validate_tin_format"
    ]
}
```

## 2. DocType Specifications

### 2.1 FIRS Invoice DocType

#### JSON Schema (firs_invoice.json)
```json
{
    "allow_copy": 0,
    "allow_events_in_timeline": 1,
    "allow_guest_to_view": 0,
    "allow_import": 0,
    "allow_rename": 0,
    "autoname": "field:irn",
    "creation": "2025-09-20 10:00:00.000000",
    "doctype": "DocType",
    "document_type": "Document",
    "engine": "InnoDB",
    "field_order": [
        "section_break_1",
        "sales_invoice",
        "irn",
        "invoice_hash",
        "column_break_3",
        "submission_status",
        "firs_status", 
        "section_break_5",
        "qr_code",
        "qr_code_data",
        "column_break_7",
        "submission_date",
        "last_updated",
        "section_break_9",
        "error_message",
        "response_data",
        "section_break_11",
        "status_logs"
    ],
    "fields": [
        {
            "fieldname": "section_break_1",
            "fieldtype": "Section Break",
            "label": "Invoice Information"
        },
        {
            "fieldname": "sales_invoice",
            "fieldtype": "Link",
            "label": "Sales Invoice",
            "options": "Sales Invoice",
            "reqd": 1,
            "unique": 1
        },
        {
            "fieldname": "irn",
            "fieldtype": "Data",
            "label": "IRN (Invoice Reference Number)",
            "read_only": 1,
            "unique": 1
        },
        {
            "fieldname": "invoice_hash",
            "fieldtype": "Data",
            "label": "Invoice Hash",
            "read_only": 1
        },
        {
            "fieldname": "column_break_3",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "submission_status",
            "fieldtype": "Select",
            "label": "Submission Status",
            "options": "Draft\nPending\nSubmitted\nFailed\nCancelled",
            "default": "Draft",
            "reqd": 1
        },
        {
            "fieldname": "firs_status",
            "fieldtype": "Select", 
            "label": "FIRS Status",
            "options": "\nReceived\nProcessing\nApproved\nRejected\nCancelled",
            "read_only": 1
        },
        {
            "fieldname": "section_break_5",
            "fieldtype": "Section Break",
            "label": "QR Code"
        },
        {
            "fieldname": "qr_code",
            "fieldtype": "Attach Image",
            "label": "QR Code Image"
        },
        {
            "fieldname": "qr_code_data",
            "fieldtype": "Long Text",
            "label": "QR Code Data",
            "read_only": 1
        },
        {
            "fieldname": "column_break_7",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "submission_date",
            "fieldtype": "Datetime",
            "label": "Submission Date",
            "read_only": 1
        },
        {
            "fieldname": "last_updated",
            "fieldtype": "Datetime",
            "label": "Last Updated",
            "read_only": 1
        },
        {
            "fieldname": "section_break_9",
            "fieldtype": "Section Break",
            "label": "Error Details",
            "collapsible": 1
        },
        {
            "fieldname": "error_message",
            "fieldtype": "Long Text",
            "label": "Error Message",
            "read_only": 1
        },
        {
            "fieldname": "response_data",
            "fieldtype": "JSON",
            "label": "API Response Data",
            "read_only": 1
        },
        {
            "fieldname": "section_break_11",
            "fieldtype": "Section Break",
            "label": "Status History"
        },
        {
            "fieldname": "status_logs",
            "fieldtype": "Table",
            "label": "Status Logs",
            "options": "FIRS Status Log",
            "read_only": 1
        }
    ],
    "links": [
        {
            "link_doctype": "Sales Invoice",
            "link_fieldname": "name"
        }
    ],
    "modified": "2025-09-20 10:00:00.000000",
    "module": "ERPNext FIRS E-Invoicing",
    "name": "FIRS Invoice",
    "naming_rule": "By fieldname",
    "owner": "Administrator",
    "permissions": [
        {
            "create": 1,
            "delete": 1,
            "email": 1,
            "export": 1,
            "print": 1,
            "read": 1,
            "report": 1,
            "role": "Accounts Manager",
            "share": 1,
            "write": 1
        }
    ],
    "sort_field": "modified",
    "sort_order": "DESC",
    "states": [],
    "title_field": "sales_invoice",
    "track_changes": 1,
    "track_seen": 1,
    "track_views": 1
}
```

#### Python Controller (firs_invoice.py)
```python
import frappe
from frappe.model.document import Document
from datetime import datetime
import json

class FIRSInvoice(Document):
    def validate(self):
        """Validate FIRS Invoice before save"""
        self.validate_sales_invoice()
        self.set_defaults()
    
    def validate_sales_invoice(self):
        """Ensure linked Sales Invoice is submitted"""
        if self.sales_invoice:
            sales_invoice = frappe.get_doc("Sales Invoice", self.sales_invoice)
            if sales_invoice.docstatus != 1:
                frappe.throw("Sales Invoice must be submitted before creating FIRS Invoice")
    
    def set_defaults(self):
        """Set default values"""
        if not self.submission_status:
            self.submission_status = "Draft"
        
        self.last_updated = datetime.now()
    
    def before_submit(self):
        """Validate before submission to FIRS"""
        self.validate_tin_numbers()
        self.generate_irn()
    
    def validate_tin_numbers(self):
        """Validate customer and supplier TIN numbers"""
        from erpnext_firs_einvoice.utils.tin_validator import validate_party_tin
        
        sales_invoice = frappe.get_doc("Sales Invoice", self.sales_invoice)
        
        # Validate customer TIN
        customer = frappe.get_doc("Customer", sales_invoice.customer)
        if not validate_party_tin(customer.get("tin")):
            frappe.throw(f"Invalid TIN for customer {customer.name}")
        
        # Validate company TIN (supplier)
        company = frappe.get_doc("Company", sales_invoice.company)
        if not validate_party_tin(company.get("tin")):
            frappe.throw(f"Invalid TIN for company {company.name}")
    
    def generate_irn(self):
        """Generate IRN if not already set"""
        if not self.irn:
            from erpnext_firs_einvoice.utils.irn_generator import generate_irn
            self.irn = generate_irn(self)
    
    def submit_to_firs(self):
        """Submit invoice to FIRS API"""
        from erpnext_firs_einvoice.api.invoice_api import submit_invoice_to_firs
        return submit_invoice_to_firs(self)
    
    def update_status(self, status, message=None, response_data=None):
        """Update invoice status and log"""
        self.submission_status = status
        self.last_updated = datetime.now()
        
        if message:
            self.error_message = message
        
        if response_data:
            self.response_data = json.dumps(response_data)
        
        # Add status log entry
        self.append("status_logs", {
            "timestamp": datetime.now(),
            "status": status,
            "message": message or "",
            "response_data": json.dumps(response_data) if response_data else ""
        })
        
        self.save()
    
    def generate_qr_code(self):
        """Generate QR code for the invoice"""
        sales_invoice = frappe.get_doc("Sales Invoice", self.sales_invoice)
        
        # Convert to FIRS format
        from erpnext_firs_einvoice.firs_client import firs_client
        firs_format_invoice = firs_client.convert_sales_invoice_to_firs_format(sales_invoice)
        
        # Generate IRN first
    from zutax.crypto.irn import IRNGenerator
        irn_generator = IRNGenerator()
        irn = irn_generator.generate_irn(firs_format_invoice)
        
        # Generate QR code using SDK with IRN
    from zutax.crypto.firs_qrcode import FIRSQRCodeGenerator
        qr_code_base64 = FIRSQRCodeGenerator.generate_qr_code(irn)
        
        # Update this invoice with QR code and IRN
        self.qr_code_data = qr_code_base64
        self.irn = irn
        self.save()
        
        return qr_code_base64
    
    def check_firs_status(self):
        """Check status from FIRS API"""
        from erpnext_firs_einvoice.api.invoice_api import check_invoice_status
        return check_invoice_status(self.irn)
    
    def cancel_firs_invoice(self, reason):
        """Cancel invoice in FIRS"""
        from erpnext_firs_einvoice.api.invoice_api import cancel_firs_invoice
        return cancel_firs_invoice(self.irn, reason)

@frappe.whitelist()
def create_firs_invoice(sales_invoice):
    """Create FIRS Invoice from Sales Invoice"""
    # Check if FIRS Invoice already exists
    existing = frappe.db.exists("FIRS Invoice", {"sales_invoice": sales_invoice})
    if existing:
        return existing
    
    # Create new FIRS Invoice
    firs_invoice = frappe.new_doc("FIRS Invoice")
    firs_invoice.sales_invoice = sales_invoice
    firs_invoice.insert()
    
    return firs_invoice.name

@frappe.whitelist()
def submit_to_firs(firs_invoice_name):
    """Submit FIRS Invoice to FIRS API"""
    firs_invoice = frappe.get_doc("FIRS Invoice", firs_invoice_name)
    return firs_invoice.submit_to_firs()

@frappe.whitelist()
def check_status(firs_invoice_name):
    """Check FIRS status for invoice"""
    firs_invoice = frappe.get_doc("FIRS Invoice", firs_invoice_name)
    return firs_invoice.check_firs_status()
```

### 2.2 FIRS Status Log (Child DocType)

#### JSON Schema (firs_status_log.json)
```json
{
    "creation": "2025-09-20 10:00:00.000000",
    "doctype": "DocType",
    "engine": "InnoDB",
    "field_order": [
        "timestamp",
        "status",
        "message",
        "response_data"
    ],
    "fields": [
        {
            "fieldname": "timestamp",
            "fieldtype": "Datetime",
            "label": "Timestamp",
            "reqd": 1,
            "default": "now"
        },
        {
            "fieldname": "status",
            "fieldtype": "Data",
            "label": "Status",
            "reqd": 1
        },
        {
            "fieldname": "message",
            "fieldtype": "Text",
            "label": "Message"
        },
        {
            "fieldname": "response_data",
            "fieldtype": "JSON",
            "label": "Response Data"
        }
    ],
    "istable": 1,
    "modified": "2025-09-20 10:00:00.000000",
    "module": "ERPNext FIRS E-Invoicing",
    "name": "FIRS Status Log",
    "owner": "Administrator",
    "permissions": [],
    "sort_field": "creation",
    "sort_order": "DESC"
}
```

### 2.3 Custom Fields for Existing DocTypes

#### Customer TIN Field
```python
# Custom field for Customer
{
    "doctype": "Custom Field",
    "dt": "Customer",
    "fieldname": "tin",
    "fieldtype": "Data",
    "label": "TIN (Tax Identification Number)",
    "insert_after": "tax_id",
    "description": "Nigerian Tax Identification Number (8-15 digits)",
    "length": 15
}

# TIN Validation Status for Customer
{
    "doctype": "Custom Field", 
    "dt": "Customer",
    "fieldname": "tin_validation_status",
    "fieldtype": "Select",
    "label": "TIN Validation Status",
    "options": "\nValid\nInvalid\nPending",
    "insert_after": "tin",
    "read_only": 1
}
```

#### Supplier TIN Field  
```python
# Custom field for Supplier
{
    "doctype": "Custom Field",
    "dt": "Supplier", 
    "fieldname": "tin",
    "fieldtype": "Data",
    "label": "TIN (Tax Identification Number)",
    "insert_after": "tax_id",
    "description": "Nigerian Tax Identification Number (8-15 digits)",
    "length": 15
}

# TIN Validation Status for Supplier
{
    "doctype": "Custom Field",
    "dt": "Supplier",
    "fieldname": "tin_validation_status", 
    "fieldtype": "Select",
    "label": "TIN Validation Status",
    "options": "\nValid\nInvalid\nPending",
    "insert_after": "tin",
    "read_only": 1
}
```

#### Company TIN Field
```python
# Custom field for Company (Supplier TIN)
{
    "doctype": "Custom Field",
    "dt": "Company",
    "fieldname": "tin",
    "fieldtype": "Data", 
    "label": "Company TIN",
    "insert_after": "tax_id",
    "description": "Company Tax Identification Number",
    "length": 15
}
```

## 3. API Integration Layer

### 3.1 FIRS Client Wrapper (api/firs_client.py)
```python
import frappe
from zutax import (
    ZutaxClient as FIRSClient,
    ZutaxConfig as FIRSConfig,
    Party,
    Address,
    LineItem,
    InvoiceType,
    PaymentDetails,
    PaymentMethod,
)
from zutax.models.enums import StateCode, UnitOfMeasure
from decimal import Decimal
import json

class ERPNextFIRSClient:
    """ERPNext-specific wrapper for Zutax FIRS SDK"""
    
    def __init__(self):
        self.settings = self.get_firs_settings()
        
        # Create FIRSConfig object
        config = FIRSConfig(
            api_key=self.settings.api_key,
            api_secret=self.settings.api_secret,
            business_id=self.settings.business_id,
            business_name=self.settings.business_name,
            tin=self.settings.tin,
            service_id=self.settings.service_id
        )
        
        # Initialize client with config
        self.client = FIRSClient(config=config)
    
    def get_firs_settings(self):
        """Get FIRS settings from ERPNext"""
        return frappe.get_single("FIRS Settings")
    
    def convert_sales_invoice_to_firs_format(self, sales_invoice_name):
        """Convert ERPNext Sales Invoice to FIRS Invoice format"""
        sales_invoice = frappe.get_doc("Sales Invoice", sales_invoice_name)
        customer = frappe.get_doc("Customer", sales_invoice.customer)
        company = frappe.get_doc("Company", sales_invoice.company)
        
        # Create supplier party (company) with Address
        supplier_address = self._convert_company_address(company)
        supplier_party = Party(
            business_id=company.name,
            tin=company.tin,
            name=company.company_name,
            email=company.email or "",
            phone=company.phone or "",
            address=supplier_address,
            vat_registered=bool(company.tin),
            registration_number=company.registration_details or company.name
        )
        
        # Create customer party with Address
        customer_address = self._convert_customer_address(customer, sales_invoice)
        customer_party = Party(
            business_id=customer.name,
            tin=customer.tin,
            name=customer.customer_name,
            email=customer.email_id or "",
            phone=customer.mobile_no or "",
            address=customer_address,
            vat_registered=bool(customer.tin)
        )
        
        # Create payment details
        payment_details = PaymentDetails(
            method=PaymentMethod.BANK_TRANSFER,
            terms=sales_invoice.payment_terms_template or "Net 30",
            due_date=sales_invoice.due_date,
            reference=sales_invoice.name
        )
        
        # Start building invoice using the fluent builder
        invoice_builder = self.client.create_invoice_builder()
        
        # Use the correct method names with fluent interface
        invoice_builder = (invoice_builder
                          .with_invoice_number(sales_invoice.name)
                          .with_invoice_type(InvoiceType.STANDARD)
                          .with_invoice_date(sales_invoice.posting_date)
                          .with_supplier(supplier_party)
                          .with_customer(customer_party)
                          .with_payment_details(payment_details)
                          .with_reference_number(sales_invoice.po_no or "")
                          .with_notes(sales_invoice.remarks or "")
                          .with_terms_and_conditions(sales_invoice.terms or ""))
        
        # Add line items using the line item builder
        line_item_builder = self.client.create_line_item_builder()
        
        for item in sales_invoice.items:
            # Create line item with proper builder pattern
            line_item = (line_item_builder
                        .with_description(item.item_name or item.description)
                        .with_hsn_code(item.gst_hsn_code or "0000")
                        .with_product_code(item.item_code)
                        .with_quantity(Decimal(str(item.qty)), UnitOfMeasure.UNIT)
                        .with_unit_price(Decimal(str(item.rate)))
                        .with_tax(Decimal(str(item.tax_rate or 7.5)))
                        .build())
            
            # Add item to invoice builder
            invoice_builder.add_line_item(line_item)
            
            # Reset builder for next item
            line_item_builder.reset()
        
        # Build the final invoice
        return invoice_builder.build()
    
    def _convert_company_address(self, company):
        """Convert company address to FIRS Address format"""
        # Get company address
        address_name = frappe.db.get_value("Dynamic Link", 
                                          {"link_doctype": "Company", "link_name": company.name}, 
                                          "parent")
        if address_name:
            address_doc = frappe.get_doc("Address", address_name)
            return Address(
                street=address_doc.address_line1,
                street2=address_doc.address_line2,
                city=address_doc.city,
                state_code=self._get_state_code(address_doc.state),
                postal_code=address_doc.pincode,
                country_code="NG"
            )
        else:
            # Default address if none found
            return Address(
                street=company.company_name,
                city="Lagos",
                state_code=StateCode.LA,
                country_code="NG"
            )
    
    def _convert_customer_address(self, customer, sales_invoice):
        """Convert customer address to FIRS Address format"""
        # Try to get customer address from invoice
        if sales_invoice.customer_address:
            address_doc = frappe.get_doc("Address", sales_invoice.customer_address)
            return Address(
                street=address_doc.address_line1,
                street2=address_doc.address_line2,
                city=address_doc.city,
                state_code=self._get_state_code(address_doc.state),
                postal_code=address_doc.pincode,
                country_code="NG"
            )
        else:
            # Default address
            return Address(
                street=customer.customer_name,
                city="Abuja",
                state_code=StateCode.FC,
                country_code="NG"
            )
    
    def _get_state_code(self, state_name):
        """Convert state name to StateCode enum"""
        state_mapping = {
            "Lagos": StateCode.LA,
            "Abuja": StateCode.FC,
            "Federal Capital Territory": StateCode.FC,
            "Rivers": StateCode.RI,
            "Kano": StateCode.KN,
            # Add more mappings as needed
        }
        return state_mapping.get(state_name, StateCode.FC)
    
    async def validate_invoice(self, sales_invoice_name):
        """Validate invoice using FIRS SDK"""
        try:
            sales_invoice = frappe.get_doc("Sales Invoice", sales_invoice_name)
            firs_invoice = self.convert_sales_invoice_to_firs_format(sales_invoice)
            
            # Use SDK validator
            from firs_einvoice.validation.validator import InvoiceValidator
            validator = InvoiceValidator()
            validation_result = validator.validate_invoice(firs_invoice)
            
            if validation_result.is_valid:
                frappe.msgprint("Invoice validation successful")
                return validation_result
            else:
                frappe.throw(f"Invoice validation failed: {', '.join(validation_result.errors)}")
                
        except Exception as e:
            frappe.log_error(f"Validation error: {str(e)}", "FIRS Validation")
            frappe.throw(f"Error validating invoice: {str(e)}")
    
    async def submit_invoice(self, sales_invoice_name):
        """Submit invoice to FIRS"""
        try:
            sales_invoice = frappe.get_doc("Sales Invoice", sales_invoice_name)
            firs_invoice = self.convert_sales_invoice_to_firs_format(sales_invoice)
            
            # Submit to FIRS
            response = await self.client.invoice.create_invoice(firs_invoice)
            
            if response.success:
                # Update ERPNext invoice with FIRS data
                sales_invoice.custom_firs_invoice_number = response.data.get("invoice_number")
                sales_invoice.custom_firs_status = "Submitted"
                sales_invoice.custom_firs_irn = response.data.get("irn")
                sales_invoice.save()
                
                frappe.msgprint(f"Invoice successfully submitted to FIRS")
                return response
            else:
                frappe.throw(f"FIRS submission failed: {response.error}")
                
        except Exception as e:
            frappe.log_error(f"Submission error: {str(e)}", "FIRS Submission")
            frappe.throw(f"Error submitting invoice: {str(e)}")
    
    async def check_status(self, irn):
        """Check invoice status"""
        try:
            response = await self.client.invoice.get_invoice_status(irn)
            return response
        except Exception as e:
            frappe.log_error(f"Status check error: {str(e)}", "FIRS Status Check")
            frappe.throw(f"Error checking invoice status: {str(e)}")
    
    def generate_qr_code(self, sales_invoice_name):
        """Generate QR code for invoice"""
        try:
            sales_invoice = frappe.get_doc("Sales Invoice", sales_invoice_name)
            firs_invoice = self.convert_sales_invoice_to_firs_format(sales_invoice)
            
            # Generate IRN first if not available
            from firs_einvoice.crypto.irn import IRNGenerator
            irn_generator = IRNGenerator()
            irn = irn_generator.generate_irn(firs_invoice)
            
            # Generate QR code using SDK with IRN
            from firs_einvoice.crypto.firs_qrcode import FIRSQRCodeGenerator
            qr_code_base64 = FIRSQRCodeGenerator.generate_qr_code(irn)
            
            # Save QR code to invoice
            sales_invoice.custom_firs_qr_code = qr_code_base64
            sales_invoice.custom_firs_irn = irn
            sales_invoice.save()
            
            return qr_code_base64
            
        except Exception as e:
            frappe.log_error(f"QR code generation error: {str(e)}", "FIRS QR Code")
            frappe.throw(f"Error generating QR code: {str(e)}")

# Global client instance
firs_client = ERPNextFIRSClient()
```

### 3.2 Invoice Processing API (api/invoice_api.py)
```python
import frappe
from frappe import _
import json
from datetime import datetime
from .firs_client import firs_client

def on_sales_invoice_submit(doc, method):
    """Called when Sales Invoice is submitted"""
    # Add custom button to generate FIRS Invoice
    pass

def before_sales_invoice_cancel(doc, method):
    """Called before Sales Invoice is cancelled"""
    # Check if FIRS Invoice exists and handle cancellation
    firs_invoice = frappe.db.exists("FIRS Invoice", {"sales_invoice": doc.name})
    if firs_invoice:
        firs_doc = frappe.get_doc("FIRS Invoice", firs_invoice)
        if firs_doc.submission_status == "Submitted":
            frappe.throw(_("Cannot cancel Sales Invoice. FIRS Invoice has been submitted. Please cancel FIRS Invoice first."))

@frappe.whitelist()
async def submit_invoice_to_firs(firs_invoice_name):
    """Submit invoice to FIRS API"""
    try:
        firs_invoice = frappe.get_doc("FIRS Invoice", firs_invoice_name)
        
        # Update status to pending
        firs_invoice.update_status("Pending", "Submitting to FIRS...")
        
        # Submit to FIRS using async client
        result = await firs_client.submit_invoice(firs_invoice.sales_invoice)
        
        if result.success:
            # Update with success data
            firs_invoice.irn = result.data.get("irn")
            firs_invoice.qr_code_data = result.data.get("qr_code")
            firs_invoice.submission_date = datetime.now()
            firs_invoice.update_status("Submitted", "Successfully submitted to FIRS", result.data)
            
            # Generate QR code file
            firs_invoice.generate_qr_code()
            
            return {"success": True, "message": "Invoice successfully submitted to FIRS", "irn": result.data.get("irn")}
        else:
            # Update with error
            firs_invoice.update_status("Failed", result.error)
            return {"success": False, "message": result.error}
            
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "FIRS Invoice Submission Error")
        if 'firs_invoice' in locals():
            firs_invoice.update_status("Failed", str(e))
        return {"success": False, "message": str(e)}

@frappe.whitelist()
async def validate_invoice_with_firs(firs_invoice_name):
    """Validate invoice with FIRS API"""
    try:
        firs_invoice = frappe.get_doc("FIRS Invoice", firs_invoice_name)
        
        # Validate using FIRS client
        validation_result = await firs_client.validate_invoice(firs_invoice.sales_invoice)
        
        if validation_result.is_valid:
            return {"success": True, "message": "Invoice validation successful"}
        else:
            return {"success": False, "message": f"Validation failed: {', '.join(validation_result.errors)}"}
            
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "FIRS Invoice Validation Error")
        return {"success": False, "message": str(e)}
@frappe.whitelist()
async def check_invoice_status(irn):
    """Check invoice status from FIRS"""
    try:
        result = await firs_client.check_status(irn)
        
        if result.success:
            # Update local status
            firs_invoice = frappe.db.get_value("FIRS Invoice", {"irn": irn}, "name")
            if firs_invoice:
                doc = frappe.get_doc("FIRS Invoice", firs_invoice)
                doc.firs_status = result.data.get("status")
                doc.update_status(doc.submission_status, f"Status updated: {result.data.get('status')}", result.data)
        
        return {"success": result.success, "data": result.data, "message": result.error if not result.success else "Status retrieved successfully"}
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "FIRS Status Check Error")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def generate_qr_code_for_invoice(firs_invoice_name):
    """Generate QR code for FIRS invoice"""
    try:
        firs_invoice = frappe.get_doc("FIRS Invoice", firs_invoice_name)
        sales_invoice = frappe.get_doc("Sales Invoice", firs_invoice.sales_invoice)
        
        # Convert to FIRS format and generate IRN
        firs_format_invoice = firs_client.convert_sales_invoice_to_firs_format(sales_invoice)
        
        # Generate IRN first
        from firs_einvoice.crypto.irn import IRNGenerator
        irn_generator = IRNGenerator()
        irn = irn_generator.generate_irn(firs_format_invoice)
        
        # Generate QR code using SDK with IRN
        from firs_einvoice.crypto.firs_qrcode import FIRSQRCodeGenerator
        qr_code_base64 = FIRSQRCodeGenerator.generate_qr_code(irn)
        
        # Update invoice with QR code
        firs_invoice.qr_code_data = qr_code_base64
        firs_invoice.irn = irn
        firs_invoice.save()
        
        return {"success": True, "qr_code": qr_code_base64}
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "QR Code Generation Error")
        return {"success": False, "message": str(e)}

async def update_pending_invoice_status():
    """Scheduled job to update pending invoice statuses"""
    pending_invoices = frappe.get_all("FIRS Invoice", 
                                    filters={"submission_status": "Submitted", "firs_status": ["in", ["Received", "Processing"]]},
                                    fields=["name", "irn"])
    
    for invoice in pending_invoices:
        try:
            await check_invoice_status(invoice.irn)
        except Exception as e:
            frappe.log_error(f"Error updating status for {invoice.name}: {str(e)}", "FIRS Status Update")

async def retry_failed_submissions():
    """Scheduled job to retry failed submissions"""
    failed_invoices = frappe.get_all("FIRS Invoice",
                                   filters={"submission_status": "Failed", "modified": [">", frappe.utils.add_days(frappe.utils.nowdate(), -1)]},
                                   fields=["name"])
    
    for invoice in failed_invoices:
        try:
            await submit_invoice_to_firs(invoice.name)
        except Exception as e:
            frappe.log_error(f"Error retrying submission for {invoice.name}: {str(e)}", "FIRS Retry Submission")

@frappe.whitelist()
def cancel_firs_invoice(firs_invoice_name, reason):
    """Cancel FIRS invoice"""
    try:
        firs_invoice = frappe.get_doc("FIRS Invoice", firs_invoice_name)
        
        result = firs_client.cancel_invoice(firs_invoice.irn, reason)
        
        if result.get("success"):
            firs_invoice.update_status("Cancelled", f"Cancelled: {reason}", result)
            return {"success": True, "message": "Invoice successfully cancelled"}
        else:
            return {"success": False, "message": result.get("message", "Cancellation failed")}
            
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "FIRS Invoice Cancellation Error")
        return {"success": False, "message": str(e)}
```

## 4. Utility Functions

### 4.1 TIN Validator (utils/tin_validator.py)
```python
import frappe
import re
from zutax.schemas.validators_impl import validate_tin

def validate_customer_tin(doc, method):
    """Validate customer TIN on save"""
    if doc.tin:
        is_valid, message = validate_tin_format(doc.tin)
        doc.tin_validation_status = "Valid" if is_valid else "Invalid"
        if not is_valid:
            frappe.msgprint(f"TIN Validation Warning: {message}")

def validate_supplier_tin(doc, method):
    """Validate supplier TIN on save"""
    if doc.tin:
        is_valid, message = validate_tin_format(doc.tin)
        doc.tin_validation_status = "Valid" if is_valid else "Invalid"
        if not is_valid:
            frappe.msgprint(f"TIN Validation Warning: {message}")

def validate_tin_format(tin):
    """Validate TIN format using Zutax SDK"""
    try:
        is_valid, message = validate_tin(tin)
        return is_valid, message
    except Exception as e:
        return False, str(e)

def validate_party_tin(tin):
    """Validate party TIN and return boolean"""
    if not tin:
        return False
    is_valid, _ = validate_tin_format(tin)
    return is_valid

@frappe.whitelist()
def bulk_validate_tins(doctype, filters=None):
    """Bulk validate TINs for customers or suppliers"""
    if doctype not in ["Customer", "Supplier"]:
        frappe.throw("Invalid doctype for TIN validation")
    
    records = frappe.get_all(doctype, filters=filters or {}, fields=["name", "tin"])
    results = []
    
    for record in records:
        if record.tin:
            is_valid, message = validate_tin_format(record.tin)
            results.append({
                "name": record.name,
                "tin": record.tin,
                "valid": is_valid,
                "message": message
            })
            
            # Update validation status
            frappe.db.set_value(doctype, record.name, "tin_validation_status", "Valid" if is_valid else "Invalid")
    
    frappe.db.commit()
    return results
```

### 4.2 QR Code Generation (Using FIRS SDK)

QR code generation is now handled directly by the FIRS E-Invoice SDK using the `FIRSQRCodeGenerator` class. The ERPNext integration uses this SDK component directly rather than implementing custom QR code utilities.

**Key Changes:**
- QR code generation now uses `FIRSQRCodeGenerator.generate_qr_code(irn)` 
- Requires IRN (Invoice Reference Number) as input parameter
- Returns base64-encoded PNG image data
- Handles FIRS-compliant QR code encryption and signing

**Usage Example:**
```python
from zutax.crypto.irn import IRNGenerator
from zutax.crypto.firs_qrcode import FIRSQRCodeGenerator

# Generate IRN first
irn_generator = IRNGenerator()
irn = irn_generator.generate_irn(firs_invoice)

# Generate QR code using IRN
qr_code_base64 = FIRSQRCodeGenerator.generate_qr_code(irn)
```

## 5. JavaScript Enhancements

### 5.1 Sales Invoice JS (Custom Script)
```javascript
// Custom script for Sales Invoice
frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        // Add FIRS Invoice button for submitted invoices
        if (frm.doc.docstatus === 1) {
            // Check if FIRS Invoice exists
            frappe.db.exists('FIRS Invoice', {'sales_invoice': frm.doc.name})
                .then(exists => {
                    if (exists) {
                        // Show manage FIRS invoice button
                        frm.add_custom_button(__('Manage FIRS Invoice'), function() {
                            frappe.set_route('Form', 'FIRS Invoice', exists);
                        }, __('FIRS'));
                        
                        frm.add_custom_button(__('Check FIRS Status'), function() {
                            check_firs_status(exists);
                        }, __('FIRS'));
                    } else {
                        // Show generate FIRS invoice button
                        frm.add_custom_button(__('Generate FIRS Invoice'), function() {
                            generate_firs_invoice(frm.doc.name);
                        }, __('FIRS'));
                    }
                });
        }
        
        // Add TIN validation indicators
        if (frm.doc.customer) {
            validate_customer_tin(frm);
        }
    },
    
    customer: function(frm) {
        if (frm.doc.customer) {
            validate_customer_tin(frm);
        }
    }
});

function validate_customer_tin(frm) {
    frappe.db.get_value('Customer', frm.doc.customer, ['tin', 'tin_validation_status'])
        .then(r => {
            if (r.message) {
                const tin_data = r.message;
                if (tin_data.tin) {
                    let indicator = tin_data.tin_validation_status === 'Valid' ? 
                        ['Valid TIN', 'green'] : ['Invalid TIN', 'red'];
                    frm.dashboard.add_indicator(__('TIN Status: {0}', [indicator[0]]), indicator[1]);
                } else {
                    frm.dashboard.add_indicator(__('TIN Status: Not Set'), 'orange');
                }
            }
        });
}

function generate_firs_invoice(sales_invoice) {
    frappe.call({
        method: 'erpnext_firs_einvoice.doctype.firs_invoice.firs_invoice.create_firs_invoice',
        args: {
            sales_invoice: sales_invoice
        },
        callback: function(r) {
            if (r.message) {
                frappe.set_route('Form', 'FIRS Invoice', r.message);
            }
        }
    });
}

function check_firs_status(firs_invoice_name) {
    frappe.call({
        method: 'erpnext_firs_einvoice.doctype.firs_invoice.firs_invoice.check_status',
        args: {
            firs_invoice_name: firs_invoice_name
        },
        callback: function(r) {
            if (r.message) {
                frappe.msgprint({
                    title: __('FIRS Status'),
                    message: __('Current Status: {0}', [r.message.status || 'Unknown']),
                    indicator: 'blue'
                });
                cur_frm.reload_doc();
            }
        }
    });
}
```

### 5.2 FIRS Invoice Form JS
```javascript
frappe.ui.form.on('FIRS Invoice', {
    refresh: function(frm) {
        // Add custom buttons based on status
        if (frm.doc.submission_status === 'Draft') {
            frm.add_custom_button(__('Submit to FIRS'), function() {
                submit_to_firs(frm);
            }).addClass('btn-primary');
        }
        
        if (frm.doc.submission_status === 'Submitted') {
            frm.add_custom_button(__('Check Status'), function() {
                check_firs_status(frm);
            });
            
            frm.add_custom_button(__('Cancel Invoice'), function() {
                cancel_firs_invoice(frm);
            });
        }
        
        if (frm.doc.submission_status === 'Failed') {
            frm.add_custom_button(__('Retry Submission'), function() {
                submit_to_firs(frm);
            }).addClass('btn-warning');
        }
        
        // Add status indicators
        add_status_indicators(frm);
        
        // Show QR code if available
        if (frm.doc.qr_code) {
            show_qr_code(frm);
        }
    }
});

function submit_to_firs(frm) {
    frappe.confirm(__('Submit invoice to FIRS? This action cannot be undone.'), function() {
        frappe.call({
            method: 'erpnext_firs_einvoice.doctype.firs_invoice.firs_invoice.submit_to_firs',
            args: {
                firs_invoice_name: frm.doc.name
            },
            btn: $('.btn-primary'),
            callback: function(r) {
                if (r.message) {
                    if (r.message.success) {
                        frappe.show_alert({
                            message: __('Successfully submitted to FIRS. IRN: {0}', [r.message.irn]),
                            indicator: 'green'
                        });
                    } else {
                        frappe.msgprint({
                            title: __('Submission Failed'),
                            message: r.message.message,
                            indicator: 'red'
                        });
                    }
                    frm.reload_doc();
                }
            }
        });
    });
}

function check_firs_status(frm) {
    frappe.call({
        method: 'erpnext_firs_einvoice.doctype.firs_invoice.firs_invoice.check_status',
        args: {
            firs_invoice_name: frm.doc.name
        },
        callback: function(r) {
            if (r.message && r.message.success) {
                frappe.show_alert({
                    message: __('Status updated successfully'),
                    indicator: 'green'
                });
                frm.reload_doc();
            }
        }
    });
}

function cancel_firs_invoice(frm) {
    let d = new frappe.ui.Dialog({
        title: __('Cancel FIRS Invoice'),
        fields: [
            {
                label: __('Reason for Cancellation'),
                fieldname: 'reason',
                fieldtype: 'Text',
                reqd: 1
            }
        ],
        primary_action_label: __('Cancel Invoice'),
        primary_action: function() {
            let values = d.get_values();
            frappe.call({
                method: 'erpnext_firs_einvoice.api.invoice_api.cancel_firs_invoice',
                args: {
                    firs_invoice_name: frm.doc.name,
                    reason: values.reason
                },
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frappe.show_alert({
                            message: __('Invoice cancelled successfully'),
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    } else {
                        frappe.msgprint({
                            title: __('Cancellation Failed'),
                            message: r.message.message,
                            indicator: 'red'
                        });
                    }
                    d.hide();
                }
            });
        }
    });
    d.show();
}

function add_status_indicators(frm) {
    let status_color = {
        'Draft': 'blue',
        'Pending': 'orange', 
        'Submitted': 'green',
        'Failed': 'red',
        'Cancelled': 'gray'
    };
    
    frm.dashboard.add_indicator(
        __('Submission: {0}', [frm.doc.submission_status]), 
        status_color[frm.doc.submission_status] || 'gray'
    );
    
    if (frm.doc.firs_status) {
        frm.dashboard.add_indicator(
            __('FIRS: {0}', [frm.doc.firs_status]),
            frm.doc.firs_status === 'Approved' ? 'green' : 'orange'
        );
    }
}

function show_qr_code(frm) {
    if (frm.doc.qr_code) {
        let qr_html = `<div class="qr-code-container" style="text-align: center; padding: 10px;">
            <h5>QR Code</h5>
            <img src="${frm.doc.qr_code}" alt="QR Code" style="max-width: 200px; max-height: 200px;">
        </div>`;
        
        frm.dashboard.add_section(qr_html, __('QR Code'));
    }
}
```

This technical specification provides a comprehensive foundation for implementing the ERPNext FIRS E-Invoicing app, including detailed DocType structures, API integration patterns, utility functions, and user interface enhancements.
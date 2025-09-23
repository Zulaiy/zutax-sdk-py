# NRS E-Invoice App Integration Guide

This guide explains how to build an ERPNext app that integrates the zutax-sdk-py for FIRS e-invoicing compliance.

## Overview

The NRS E-Invoice app provides:
- Automatic e-invoice generation from Sales Invoices
- FIRS compliance validation using zutax-sdk-py
- IRN generation and QR code creation
- Submission tracking and status management
- Audit logging for compliance

## App Structure

```
nrs_einvoice/
├── __init__.py
├── hooks.py
├── modules.txt
├── patches.txt
├── config/
│   ├── __init__.py
│   └── desktop.py
├── nrs_einvoice/
│   ├── __init__.py
│   └── doctype/
│       ├── firs_settings/
│       ├── firs_invoice/
│       └── firs_invoice_log/
├── api/
│   ├── __init__.py
│   └── invoice_api.py

└── utils/
    ├── __init__.py
    ├── tin_validator.py
    └── zutax_integration.py
```

## Installation Steps

### 1. Create ERPNext App

```bash
cd ~/frappe-bench
bench new-app nrs_einvoice
cd apps/nrs_einvoice
```

### 2. Install zutax-sdk-py Dependency

Add to `requirements.txt`:
```
zutax-firs-einvoice>=1.0.0
```

Or install in bench environment:
```bash
bench pip install zutax-firs-einvoice
```

### 3. Configure App Module

Create `modules.txt`:
```
NRS eInvoice
```

## DocType Implementation

### 1. FIRS Settings (Single DocType)

**Purpose**: Store FIRS API configuration and app behavior settings.

**Key Fields**:
- `api_base_url`: FIRS API endpoint
- `api_key`: FIRS API key (Password field)
- `api_secret`: FIRS API secret (Password field)
- `business_id`: Your business identifier
- `business_name`: Your registered business name
- `tin`: Your Tax Identification Number
- `service_id`: Service identifier for IRN generation
- `firs_public_key`: FIRS public key for signing (Base64-encoded PEM) - Optional
- `firs_certificate`: FIRS certificate for QR generation (Base64-encoded) - Optional
- `auto_submit`: Auto-submit invoices on Sales Invoice submission
- `validate_tin`: Enable TIN validation

**Complete DocType JSON** (`firs_settings.json`):
```json
{
  "actions": [],
  "allow_copy": 0,
  "allow_rename": 0,
  "creation": "2025-09-22 00:00:00.000000",
  "doctype": "DocType",
  "engine": "InnoDB",
  "field_order": [
    "section_api",
    "api_base_url",
    "api_key",
    "api_secret",
    "business_id",
    "business_name",
    "tin",
    "service_id",
    "section_behavior",
    "auto_create",
    "auto_submit",
    "validate_tin"
  ],
  "fields": [
    {
      "fieldname": "section_api",
      "fieldtype": "Section Break",
      "label": "API Configuration"
    },
    {
      "fieldname": "api_base_url",
      "fieldtype": "Data",
      "label": "API Base URL",
      "default": "https://api.firs.gov.ng/api/v1",
      "reqd": 1
    },
    {
      "fieldname": "api_key",
      "fieldtype": "Password",
      "label": "API Key",
      "reqd": 1
    },
    {
      "fieldname": "api_secret",
      "fieldtype": "Password",
      "label": "API Secret",
      "reqd": 1
    },
    {
      "fieldname": "business_id",
      "fieldtype": "Data",
      "label": "Business ID",
      "reqd": 1
    },
    {
      "fieldname": "business_name",
      "fieldtype": "Data",
      "label": "Business Name",
      "reqd": 1
    },
    {
      "fieldname": "tin",
      "fieldtype": "Data",
      "label": "Company TIN",
      "reqd": 1
    },
    {
      "fieldname": "service_id",
      "fieldtype": "Data",
      "label": "Service ID",
      "description": "8-character service identifier for IRN generation",
      "reqd": 1
    },
    {
      "fieldname": "firs_public_key",
      "fieldtype": "Long Text",
      "label": "FIRS Public Key",
      "description": "Base64-encoded PEM public key for FIRS signing (optional)"
    },
    {
      "fieldname": "firs_certificate",
      "fieldtype": "Long Text",
      "label": "FIRS Certificate",
      "description": "Base64-encoded certificate for QR generation (optional)"
    },
    {
      "fieldname": "section_behavior",
      "fieldtype": "Section Break",
      "label": "Behavior Settings"
    },
    {
      "fieldname": "auto_create",
      "fieldtype": "Check",
      "label": "Auto-create FIRS Invoice on Sales Invoice Submit",
      "default": "1"
    },
    {
      "fieldname": "auto_submit",
      "fieldtype": "Check",
      "label": "Auto-submit to FIRS on Submit",
      "default": "0"
    },
    {
      "fieldname": "validate_tin",
      "fieldtype": "Check",
      "label": "Validate TIN Format",
      "default": "1"
    }
  ],
  "index_web_pages_for_search": 0,
  "is_submittable": 0,
  "issingle": 1,
  "links": [],
  "module": "NRS eInvoice",
  "name": "FIRS Settings",
  "owner": "Administrator",
  "permissions": [
    {
      "role": "System Manager",
      "read": 1,
      "write": 1
    },
    {
      "role": "Accounts Manager",
      "read": 1
    }
  ],
  "sort_field": "modified",
  "sort_order": "DESC"
}
```

### 2. FIRS Invoice (Main DocType)

**Purpose**: Track e-invoice lifecycle and FIRS compliance status.

**Key Fields**:
- `erpnext_invoice`: Link to Sales Invoice (required)
- `firs_status`: Select (Draft/Queued/Submitted/Accepted/Rejected/Error)
- `irn`: Generated Invoice Reference Number
- `qr_code_data`: Base64 QR code data
- `qr_image`: Attached QR code image
- `payload_json`: JSON payload sent to FIRS
- `firs_invoice_logs`: Table of submission/status logs

**Complete DocType JSON** (`firs_invoice.json`):
```json
{
  "actions": [],
  "creation": "2025-09-22 00:00:00",
  "default_view": "List",
  "doctype": "DocType",
  "engine": "InnoDB",
  "naming_rule": "Expression (old style)",
  "autoname": "field:irn",
  "field_order": [
    "firs_status",
    "section_invoice_validation",
    "col_iv_left",
    "erpnext_invoice",
    "customer_name",
    "col_iv_right",
    "tin",
    "invoice_data_status",
    "section_compliance",
    "col_comp_left",
    "irn",
    "col_comp_right",
    "qr_preview",
    "qr_image",
    "qr_code_data",
    "section_firs_invoice_logs",
    "firs_invoice_logs",
    "section_payload",
    "payload_json",
    "amended_from"
  ],
  "fields": [
    {
      "default": "Draft",
      "fieldname": "firs_status",
      "fieldtype": "Select",
      "label": "FIRS Status",
      "options": "Draft\nQueued\nSubmitted\nAccepted\nRejected\nError",
      "in_list_view": 1,
      "in_standard_filter": 1,
      "allow_on_submit": 1,
      "read_only": 1
    },
    {
      "fieldname": "section_invoice_validation",
      "fieldtype": "Section Break",
      "label": "Invoice & Validation"
    },
    {
      "fieldname": "col_iv_left",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "erpnext_invoice",
      "fieldtype": "Link",
      "options": "Sales Invoice",
      "label": "ERPNext Invoice",
      "reqd": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "customer_name",
      "fieldtype": "Data",
      "label": "Customer Name",
      "read_only": 1,
      "fetch_from": "erpnext_invoice.customer_name"
    },
    {
      "fieldname": "col_iv_right",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "tin",
      "fieldtype": "Data",
      "label": "Customer TIN",
      "read_only": 1,
      "in_standard_filter": 1
    },
    {
      "fieldname": "invoice_data_status",
      "fieldtype": "Select",
      "label": "Invoice Data Status",
      "options": "Valid\nInvalid\nUnknown",
      "default": "Unknown",
      "read_only": 1
    },
    {
      "fieldname": "section_compliance",
      "fieldtype": "Section Break",
      "label": "FIRS Compliance"
    },
    {
      "fieldname": "col_comp_left",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "irn",
      "fieldtype": "Data",
      "label": "IRN (Invoice Reference Number)",
      "read_only": 1,
      "allow_on_submit": 1,
      "unique": 1
    },
    {
      "fieldname": "col_comp_right",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "qr_preview",
      "fieldtype": "HTML",
      "label": "QR Code Preview",
      "read_only": 1,
      "allow_on_submit": 1
    },
    {
      "fieldname": "qr_image",
      "fieldtype": "Attach Image",
      "label": "QR Code Image",
      "read_only": 1,
      "allow_on_submit": 1
    },
    {
      "fieldname": "qr_code_data",
      "fieldtype": "Long Text",
      "label": "QR Code Data (Base64)",
      "read_only": 1,
      "hidden": 1,
      "allow_on_submit": 1
    },
    {
      "fieldname": "section_firs_invoice_logs",
      "fieldtype": "Section Break",
      "label": "FIRS Transaction Logs"
    },
    {
      "fieldname": "firs_invoice_logs",
      "fieldtype": "Table",
      "label": "Transaction Logs",
      "options": "FIRS Invoice Log",
      "read_only": 1,
      "allow_on_submit": 1
    },
    {
      "fieldname": "section_payload",
      "fieldtype": "Section Break",
      "label": "API Payload",
      "collapsible": 1,
      "collapsible_depends_on": "payload_json"
    },
    {
      "fieldname": "payload_json",
      "fieldtype": "Code",
      "label": "Invoice Payload (JSON)",
      "options": "JSON",
      "read_only": 1,
      "allow_on_submit": 1
    },
    {
      "fieldname": "amended_from",
      "fieldtype": "Link",
      "label": "Amended From",
      "options": "FIRS Invoice",
      "no_copy": 1,
      "print_hide": 1,
      "read_only": 1,
      "search_index": 1
    }
  ],
  "index_web_pages_for_search": 1,
  "is_submittable": 1,
  "links": [
    {
      "link_doctype": "Sales Invoice",
      "link_fieldname": "name",
      "parent_doctype": "FIRS Invoice",
      "parent_fieldname": "erpnext_invoice"
    }
  ],
  "modified": "2025-09-22 02:55:00",
  "modified_by": "Administrator",
  "module": "NRS eInvoice",
  "name": "FIRS Invoice",
  "owner": "Administrator",
  "permissions": [
    {
      "role": "Accounts Manager",
      "read": 1,
      "write": 1,
      "create": 1,
      "delete": 1,
      "email": 1,
      "print": 1,
      "submit": 1,
      "cancel": 1
    },
    {
      "role": "Accounts User",
      "read": 1,
      "write": 1,
      "create": 1,
      "email": 1,
      "print": 1,
      "submit": 1
    },
    {
      "role": "System Manager",
      "read": 1,
      "write": 1,
      "create": 1,
      "delete": 1,
      "email": 1,
      "print": 1,
      "share": 1,
      "submit": 1,
      "cancel": 1
    }
  ],
  "sort_field": "modified",
  "sort_order": "DESC",
  "states": [],
  "title_field": "erpnext_invoice",
  "track_changes": 1
}
```

**Python Controller** (`firs_invoice.py`):
```python
import frappe
from frappe.model.document import Document
from nrs_einvoice.utils.zutax_integration import ZutaxIntegrator

class FIRSInvoice(Document):
    def autoname(self):
        """Auto-generate IRN and use it as document name"""
        if not self.irn and self.erpnext_invoice:
            integrator = ZutaxIntegrator()
            self.irn = integrator.generate_irn(self.erpnext_invoice)
            self.name = self.irn
            
            # Also generate QR code since we have IRN
            self.generate_qr_code()

    def validate(self):
        """Validate invoice data and TINs using zutax-sdk-py"""
        integrator = ZutaxIntegrator()
        
        # Validate TIN if enabled
        if frappe.db.get_single_value("FIRS Settings", "validate_tin"):
            self.validate_tins()
        
        # Convert and validate invoice data
        try:
            zutax_invoice = integrator.convert_sales_invoice(self.erpnext_invoice)
            validation_result = integrator.validate_invoice(zutax_invoice)
            
            if not validation_result.valid:
                frappe.throw(f"Invoice validation failed: {validation_result.errors}")
                
            self.invoice_data_status = "Valid"
        except Exception as e:
            self.invoice_data_status = "Invalid"
            frappe.throw(f"Validation error: {str(e)}")

    def on_submit(self):
        """Optionally auto-submit to FIRS (IRN already generated)"""
        if frappe.db.get_single_value("FIRS Settings", "auto_submit"):
            self.queue_submission()

    def generate_qr_code(self):
        """Generate FIRS-compliant QR code"""
        if self.irn:
            integrator = ZutaxIntegrator()
            qr_data = integrator.generate_qr_code(self.irn, self.erpnext_invoice)
            
            self.qr_code_data = qr_data['base64']
            if qr_data.get('image_file'):
                self.qr_image = qr_data['image_file']

    def queue_submission(self):
        """Queue background job for FIRS submission"""
        frappe.enqueue(
            "nrs_einvoice.api.invoice_api.submit_invoice",
            invoice_name=self.name,
            queue="long",
            timeout=300
        )

    def before_cancel(self):
        """Handle FIRS Invoice cancellation"""
        if self.firs_status in ["Submitted", "Accepted"]:
            # Queue cancellation to FIRS
            frappe.enqueue(
                "nrs_einvoice.api.invoice_api.cancel_invoice",
                invoice_name=self.name,
                queue="long"
            )
            self.firs_status = "Cancelled"
            self.append("firs_invoice_logs", {
                "event_time": frappe.utils.now_datetime(),
                "log_type": "Cancellation",
                "action": "cancel_invoice",
                "status": "Pending",
                "message": "Cancellation request submitted"
            })
```

**Python Controller for Amendment** (`firs_invoice_amendment.py`):
```python
@frappe.whitelist()
def create_amendment(original_invoice_name: str, reason: str = None):
    """Create an amendment for a FIRS Invoice"""
    original = frappe.get_doc("FIRS Invoice", original_invoice_name)
    
    if original.docstatus != 2:
        frappe.throw("Original invoice must be cancelled first")
    
    # Create amended invoice
    amended = frappe.copy_doc(original)
    amended.amended_from = original.name
    amended.firs_status = "Draft"
    amended.irn = None  # Will be regenerated
    
    # Clear logs from previous submission
    amended.firs_invoice_logs = []
    
    # Add amendment note
    amended.append("firs_invoice_logs", {
        "event_time": frappe.utils.now_datetime(),
        "log_type": "Amendment",
        "action": "create_amendment",
        "status": "Created",
        "message": f"Amendment created from {original.name}. Reason: {reason or 'Not specified'}"
    })
    
    amended.insert()
    return amended.name

@frappe.whitelist()
def update_invoice_line_items(invoice_name: str, updates: dict):
    """Update line items before resubmission"""
    invoice = frappe.get_doc("FIRS Invoice", invoice_name)
    
    if invoice.firs_status not in ["Draft", "Rejected"]:
        frappe.throw("Can only update Draft or Rejected invoices")
    
    integrator = ZutaxIntegrator()
    
    # Apply updates to the linked Sales Invoice data
    si = frappe.get_doc("Sales Invoice", invoice.erpnext_invoice)
    
    for item_update in updates.get("line_items", []):
        # Update line item data
        for si_item in si.items:
            if si_item.name == item_update["name"]:
                si_item.update(item_update)
    
    # Revalidate with zutax
    zutax_invoice = integrator.convert_sales_invoice(si.name)
    validation_result = integrator.validate_invoice(zutax_invoice)
    
    if not validation_result.valid:
        frappe.throw(f"Validation failed after update: {validation_result.errors}")
    
    # Update payload
    invoice.payload_json = zutax_invoice.model_dump_json()
    invoice.invoice_data_status = "Valid"
    
    # Log the update
    invoice.append("firs_invoice_logs", {
        "event_time": frappe.utils.now_datetime(),
        "log_type": "Update",
        "action": "update_line_items",
        "status": "Success",
        "message": f"Updated {len(updates.get('line_items', []))} line items",
        "request_payload": json.dumps(updates)
    })
    
    invoice.save()
    return {"success": True, "message": "Invoice updated successfully"}
```

### 3. FIRS Invoice Log (Child Table)

**Purpose**: Audit trail for all FIRS API interactions.

**Key Fields**:
- `event_time`: When the event occurred
- `log_type`: Submission/Status/Error
- `action`: API action performed
- `status`: Response status
- `message`: Human-readable message
- `request_payload`: JSON request sent
- `response_data`: JSON response received
- `status_code`: HTTP status code
- `irn`: Associated IRN

**Complete DocType JSON** (`firs_invoice_log.json`):
```json
{
  "actions": [],
  "creation": "2025-09-22 00:00:00",
  "doctype": "DocType",
  "editable_grid": 1,
  "engine": "InnoDB",
  "field_order": [
    "event_time",
    "log_type",
    "action",
    "status",
    "message",
    "col_break_1",
    "status_code",
    "irn",
    "section_data",
    "request_payload",
    "response_data"
  ],
  "fields": [
    {
      "fieldname": "event_time",
      "fieldtype": "Datetime",
      "label": "Event Time",
      "reqd": 1,
      "in_list_view": 1,
      "width": "150px"
    },
    {
      "fieldname": "log_type",
      "fieldtype": "Select",
      "label": "Log Type",
      "options": "Submission\nStatus Check\nValidation\nError",
      "reqd": 1,
      "in_list_view": 1,
      "width": "100px"
    },
    {
      "fieldname": "action",
      "fieldtype": "Data",
      "label": "Action",
      "in_list_view": 1,
      "width": "120px"
    },
    {
      "fieldname": "status",
      "fieldtype": "Data",
      "label": "Status",
      "in_list_view": 1,
      "width": "100px"
    },
    {
      "fieldname": "message",
      "fieldtype": "Small Text",
      "label": "Message",
      "in_list_view": 1,
      "width": "200px"
    },
    {
      "fieldname": "col_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "status_code",
      "fieldtype": "Int",
      "label": "HTTP Status Code"
    },
    {
      "fieldname": "irn",
      "fieldtype": "Data",
      "label": "IRN"
    },
    {
      "fieldname": "section_data",
      "fieldtype": "Section Break",
      "label": "API Data",
      "collapsible": 1
    },
    {
      "fieldname": "request_payload",
      "fieldtype": "Code",
      "label": "Request Payload",
      "options": "JSON"
    },
    {
      "fieldname": "response_data",
      "fieldtype": "Code",
      "label": "Response Data",
      "options": "JSON"
    }
  ],
  "index_web_pages_for_search": 0,
  "is_submittable": 0,
  "istable": 1,
  "links": [],
  "modified": "2025-09-22 02:55:00",
  "modified_by": "Administrator",
  "module": "NRS eInvoice",
  "name": "FIRS Invoice Log",
  "owner": "Administrator",
  "permissions": [
    {
      "role": "System Manager",
      "read": 1,
      "write": 1,
      "create": 1,
      "delete": 1,
      "share": 1
    },
    {
      "role": "Accounts Manager",
      "read": 1,
      "write": 1,
      "create": 1,
      "delete": 1
    },
    {
      "role": "Accounts User",
      "read": 1
    }
  ],
  "sort_field": "event_time",
  "sort_order": "DESC"
}
```

## Zutax SDK Integration Layer

### Core Integration Module (`utils/zutax_integration.py`)

```python
import frappe
from zutax import ZutaxClient, ZutaxConfig, Invoice, Party, LineItem
from zutax.models.enums import StateCode, UnitOfMeasure, InvoiceType
from typing import Dict, Any, Optional

class ZutaxIntegrator:
    def __init__(self):
        self.config = self._get_zutax_config()
        self.client = ZutaxClient(config=self.config)

    def _get_zutax_config(self) -> ZutaxConfig:
        """Load configuration from FIRS Settings"""
        settings = frappe.get_single("FIRS Settings")
        
        return ZutaxConfig(
            api_key=settings.api_key,
            api_secret=settings.api_secret,
            business_id=settings.business_id,
            business_name=settings.business_name,
            tin=settings.tin,
            service_id=settings.service_id,
            base_url=settings.api_base_url,
            # Optional: FIRS keys for signing and QR generation
            # These fields should be added to FIRS Settings DocType
            firs_public_key=getattr(settings, 'firs_public_key', None),
            firs_certificate=getattr(settings, 'firs_certificate', None),
        )

    def convert_sales_invoice(self, sales_invoice_name: str) -> Invoice:
        """Convert ERPNext Sales Invoice to zutax Invoice model"""
        si = frappe.get_doc("Sales Invoice", sales_invoice_name)
        
        # Build supplier party (your company)
        supplier = self._build_supplier_party(si.company)
        
        # Build customer party
        customer = self._build_customer_party(si.customer)
        
        # Build line items
        line_items = []
        for item in si.items:
            line_item = self._build_line_item(item)
            line_items.append(line_item)
        
        # Create invoice using zutax builder
        invoice = (
            self.client.create_invoice_builder()
            .with_invoice_number(si.name)
            .with_invoice_date(si.posting_date)
            .with_invoice_type(InvoiceType.STANDARD)
            .with_supplier(supplier)
            .with_customer(customer)
            .with_line_items(line_items)
            .build()
        )
        
        return invoice

    def _build_supplier_party(self, company_name: str) -> Party:
        """Build supplier party from Company"""
        company = frappe.get_doc("Company", company_name)
        
        return Party(
            name=company.company_name,
            tin=company.tax_id or company.company_tax_id,
            address=self._build_address_from_company(company),
            phone=company.phone_no,
            email=company.email
        )

    def _build_customer_party(self, customer_name: str) -> Party:
        """Build customer party from Customer"""
        customer = frappe.get_doc("Customer", customer_name)
        
        return Party(
            name=customer.customer_name,
            tin=customer.tax_id,
            address=self._build_address_from_customer(customer),
            phone=customer.mobile_no,
            email=customer.email_id
        )

    def _build_line_item(self, si_item) -> LineItem:
        """Build line item from Sales Invoice Item"""
        return (
            self.client.create_line_item_builder()
            .with_description(si_item.description or si_item.item_name)
            .with_hsn_code(si_item.item_code)  # Map to actual HSN
            .with_quantity(si_item.qty, UnitOfMeasure.PIECE)
            .with_unit_price(si_item.rate)
            .with_tax_rate(self._calculate_tax_rate(si_item))
            .build()
        )

    def validate_invoice(self, invoice: Invoice):
        """Validate invoice using zutax client"""
        return self.client.validate_invoice(invoice)

    def generate_irn(self, sales_invoice_name: str) -> str:
        """Generate IRN for invoice"""
        invoice = self.convert_sales_invoice(sales_invoice_name)
        return self.client.generate_irn(invoice)

    def generate_qr_code(self, irn: str, sales_invoice_name: str) -> Dict[str, Any]:
        """Generate QR code for invoice"""
        invoice = self.convert_sales_invoice(sales_invoice_name)
        invoice.irn = irn
        
        # Generate QR code using zutax
        qr_base64 = self.client.generate_qr_code(invoice, format="base64")
        
        # Save as file attachment
        qr_image_file = self._save_qr_image(qr_base64, sales_invoice_name)
        
        return {
            'base64': qr_base64,
            'image_file': qr_image_file
        }

    async def submit_invoice(self, firs_invoice_name: str):
        """Submit invoice to FIRS API"""
        firs_invoice = frappe.get_doc("FIRS Invoice", firs_invoice_name)
        
        try:
            # Convert to zutax format
            invoice = self.convert_sales_invoice(firs_invoice.erpnext_invoice)
            invoice.irn = firs_invoice.irn
            
            # Submit to FIRS
            result = await self.client.submit_invoice(invoice)
            
            # Log successful submission
            firs_invoice.append("firs_invoice_logs", {
                "event_time": frappe.utils.now_datetime(),
                "log_type": "Submission",
                "action": "submit_invoice",
                "status": "Success",
                "message": "Invoice submitted successfully",
                "request_payload": invoice.model_dump_json(),
                "response_data": result.model_dump_json() if result else "",
            })
            
            firs_invoice.firs_status = "Submitted"
            firs_invoice.save()
            
        except Exception as e:
            # Log submission error
            firs_invoice.append("firs_invoice_logs", {
                "event_time": frappe.utils.now_datetime(),
                "log_type": "Submission",
                "action": "submit_invoice", 
                "status": "Error",
                "message": str(e),
                "request_payload": "",
                "response_data": ""
            })
            
            firs_invoice.firs_status = "Error"
            firs_invoice.save()
            raise
```

## API Integration (`api/invoice_api.py`)

```python
import frappe
import asyncio
from nrs_einvoice.utils.zutax_integration import ZutaxIntegrator

@frappe.whitelist()
def submit_invoice(invoice_name: str):
    """Background job to submit invoice to FIRS"""
    try:
        integrator = ZutaxIntegrator()
        
        # Run async submission
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(integrator.submit_invoice(invoice_name))
        loop.close()
        
    except Exception as e:
        frappe.log_error(f"FIRS submission failed for {invoice_name}: {str(e)}")
        raise

@frappe.whitelist()
def check_status(invoice_name: str):
    """Check invoice status from FIRS"""
    firs_invoice = frappe.get_doc("FIRS Invoice", invoice_name)
    
    if not firs_invoice.irn:
        frappe.throw("IRN not generated yet")
    
    try:
        integrator = ZutaxIntegrator()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        status = loop.run_until_complete(
            integrator.client.get_invoice_status(firs_invoice.irn)
        )
        loop.close()
        
        # Update status
        firs_invoice.firs_status = status.status
        firs_invoice.append("firs_invoice_logs", {
            "event_time": frappe.utils.now_datetime(),
            "log_type": "Status",
            "action": "check_status",
            "status": status.status,
            "message": status.message,
            "response_data": status.model_dump_json()
        })
        firs_invoice.save()
        
        return {"status": status.status, "message": status.message}
        
    except Exception as e:
        frappe.log_error(f"Status check failed for {invoice_name}: {str(e)}")
        raise

@frappe.whitelist()
def cancel_invoice(invoice_name: str):
    """Cancel invoice with FIRS"""
    firs_invoice = frappe.get_doc("FIRS Invoice", invoice_name)
    
    try:
        integrator = ZutaxIntegrator()
        
        # Send cancellation request to FIRS
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            integrator.client.cancel_invoice(firs_invoice.irn)
        )
        loop.close()
        
        # Log cancellation
        firs_invoice.append("firs_invoice_logs", {
            "event_time": frappe.utils.now_datetime(),
            "log_type": "Cancellation",
            "action": "cancel_invoice",
            "status": "Success",
            "message": "Invoice cancelled with FIRS",
            "response_data": result.model_dump_json() if result else ""
        })
        
        firs_invoice.firs_status = "Cancelled"
        firs_invoice.save()
        
    except Exception as e:
        frappe.log_error(f"Cancellation failed for {invoice_name}: {str(e)}")
        
        firs_invoice.append("firs_invoice_logs", {
            "event_time": frappe.utils.now_datetime(),
            "log_type": "Cancellation",
            "action": "cancel_invoice",
            "status": "Error",
            "message": str(e)
        })
        firs_invoice.save()
        raise

@frappe.whitelist()
def update_and_resubmit(invoice_name: str, corrections: dict):
    """Update rejected invoice and resubmit to FIRS"""
    firs_invoice = frappe.get_doc("FIRS Invoice", invoice_name)
    
    if firs_invoice.firs_status not in ["Rejected", "Error"]:
        frappe.throw("Can only update rejected or errored invoices")
    
    try:
        integrator = ZutaxIntegrator()
        
        # Apply corrections to invoice data
        updated_invoice = integrator.apply_corrections(
            firs_invoice.erpnext_invoice, 
            corrections
        )
        
        # Regenerate IRN for corrected invoice
        new_irn = integrator.generate_irn_for_correction(
            updated_invoice,
            original_irn=firs_invoice.irn
        )
        
        # Update document
        firs_invoice.irn = new_irn
        firs_invoice.payload_json = updated_invoice.model_dump_json()
        
        # Resubmit to FIRS
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            integrator.client.submit_invoice(updated_invoice)
        )
        loop.close()
        
        # Log resubmission
        firs_invoice.append("firs_invoice_logs", {
            "event_time": frappe.utils.now_datetime(),
            "log_type": "Resubmission",
            "action": "update_and_resubmit",
            "status": "Success",
            "message": "Invoice updated and resubmitted",
            "request_payload": updated_invoice.model_dump_json(),
            "response_data": result.model_dump_json() if result else ""
        })
        
        firs_invoice.firs_status = "Submitted"
        firs_invoice.save()
        
        return {"success": True, "new_irn": new_irn}
        
    except Exception as e:
        frappe.log_error(f"Update and resubmit failed for {invoice_name}: {str(e)}")
        raise
```

## Hooks Configuration

### Main Hooks File (`hooks.py`)

```python
app_name = "nrs_einvoice"
app_title = "NRS eInvoice"
app_publisher = "Your Company"
app_description = "FIRS E-Invoice compliance for ERPNext"
app_version = "1.0.0"

# Include in ERPNext namespace
app_include_js = "/assets/nrs_einvoice/js/nrs_einvoice.min.js"
app_include_css = "/assets/nrs_einvoice/css/nrs_einvoice.min.css"

# Document hooks - reference functions in api/hooks.py
doc_events = {
    "Sales Invoice": {
        "on_submit": "nrs_einvoice.api.hooks.create_firs_invoice",
        "on_cancel": "nrs_einvoice.api.hooks.cancel_firs_invoice"
    }
}

# Scheduled tasks
scheduler_events = {
    "hourly": [
        "nrs_einvoice.api.scheduled.check_pending_submissions"
    ]
}
```

### Hook Functions (`api/hooks.py`)

```python
import frappe
from frappe import _

def create_firs_invoice(doc, method):
    """Auto-create FIRS Invoice when Sales Invoice is submitted"""
    # Check if auto-create is enabled
    if not frappe.db.get_single_value("FIRS Settings", "auto_create"):
        return
    
    # Check if FIRS Invoice already exists
    existing = frappe.db.exists("FIRS Invoice", 
        {"erpnext_invoice": doc.name, "docstatus": ["!=", 2]})
    
    if existing:
        frappe.msgprint(_("FIRS Invoice already exists for this Sales Invoice"))
        return
    
    # Create new FIRS Invoice
    try:
        firs_invoice = frappe.new_doc("FIRS Invoice")
        firs_invoice.erpnext_invoice = doc.name
        firs_invoice.customer_name = doc.customer_name
        firs_invoice.tin = frappe.db.get_value("Customer", doc.customer, "tax_id")
        firs_invoice.insert()
        
        # Auto-submit if configured
        if frappe.db.get_single_value("FIRS Settings", "auto_submit"):
            firs_invoice.submit()
            frappe.msgprint(
                _("FIRS Invoice {0} created and submitted").format(firs_invoice.name),
                indicator="green"
            )
        else:
            frappe.msgprint(
                _("FIRS Invoice {0} created as draft").format(firs_invoice.name),
                indicator="blue"
            )
            
    except Exception as e:
        frappe.log_error(f"Failed to create FIRS Invoice: {str(e)}", 
                        f"Sales Invoice: {doc.name}")
        frappe.msgprint(
            _("Failed to create FIRS Invoice. Check Error Log for details."),
            indicator="red"
        )

def cancel_firs_invoice(doc, method):
    """Cancel related FIRS Invoice when Sales Invoice is cancelled"""
    firs_invoices = frappe.get_all("FIRS Invoice", 
        filters={"erpnext_invoice": doc.name, "docstatus": 1},
        fields=["name", "firs_status"])
    
    if not firs_invoices:
        return
    
    for firs_inv in firs_invoices:
        try:
            firs_doc = frappe.get_doc("FIRS Invoice", firs_inv.name)
            
            # Check if already submitted to FIRS
            if firs_doc.firs_status in ["Submitted", "Accepted"]:
                # Queue cancellation with FIRS first
                firs_doc.before_cancel()
                
            # Cancel the document
            firs_doc.cancel()
            frappe.msgprint(
                _("FIRS Invoice {0} cancelled").format(firs_doc.name),
                indicator="orange"
            )
            
        except Exception as e:
            frappe.log_error(f"Failed to cancel FIRS Invoice: {str(e)}", 
                            f"FIRS Invoice: {firs_inv.name}")
            frappe.msgprint(
                _("Failed to cancel FIRS Invoice {0}").format(firs_inv.name),
                indicator="red"
            )
```

## Installation and Setup

### 1. Install App in Site

```bash
bench get-app https://github.com/yourusername/nrs_einvoice.git
bench --site your-site.local install-app nrs_einvoice
```

### 2. Configure FIRS Settings

1. Go to **FIRS Settings** in ERPNext
2. Enter your FIRS API credentials
3. Configure business details
4. Enable auto-submit and TIN validation as needed

### 3. Test Integration

1. Create a Sales Invoice with proper customer TIN
2. Submit the Sales Invoice
3. Check if FIRS Invoice is auto-created
4. Verify IRN generation and QR code creation
5. Monitor submission status in FIRS Invoice Logs

## Best Practices

### Error Handling
- Always wrap zutax SDK calls in try-catch blocks
- Log errors to FIRS Invoice Log table
- Provide user-friendly error messages
- Implement retry logic for network failures

### Performance
- Use background jobs for API submissions
- Cache frequently accessed settings
- Implement rate limiting for FIRS API calls
- Use async/await for concurrent operations

### Security
- Store API credentials securely (Password fields)
- Validate all input data before sending to FIRS
- Implement proper user permissions
- Log all API interactions for audit

### Testing
- Create test cases for invoice conversion
- Mock FIRS API responses for unit tests
- Test error scenarios and edge cases
- Validate generated IRNs and QR codes

## Troubleshooting

### Common Issues

**1. Import Error: "No module named 'zutax'"**
- Ensure zutax-sdk-py is installed in bench environment
- Check requirements.txt includes correct version

**2. IRN Generation Fails**
- Verify FIRS Settings configuration
- Check invoice data completeness
- Validate TIN formats

**3. QR Code Not Generated**
- Check if PIL/qrcode libraries are installed
- Verify file upload permissions
- Check error logs for specific issues

**4. API Submission Timeout**
- Increase background job timeout
- Check network connectivity to FIRS API
- Verify API credentials are correct

This integration guide provides a complete framework for building FIRS e-invoice compliance into ERPNext using the zutax-sdk-py library.
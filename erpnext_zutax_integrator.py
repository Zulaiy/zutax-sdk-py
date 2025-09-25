"""
ERPNext to Zutax Integration Module

This module provides integration between ERPNext and Zutax FIRS E-Invoice SDK,
correctly mapping ERPNext doctypes to Zutax models with proper field names
based on official ERPNext documentation.
"""

import frappe
from zutax import ZutaxClient, ZutaxConfig
from zutax.models.party import Address, Party
from zutax.models.invoice import Invoice
from zutax.models.line_item import LineItem
from zutax.models.enums import StateCode, UnitOfMeasure, InvoiceType, Currency
from typing import Dict, Any, Optional
from decimal import Decimal
import re


class ZutaxIntegrator:
    """Main integrator class for ERPNext to Zutax conversion"""
    
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
            line_item = self._build_line_item(item, si)
            line_items.append(line_item)
        
        # Create invoice using zutax builder
        invoice = (
            self.client.create_invoice_builder()
            .with_invoice_number(si.name)
            .with_invoice_date(si.posting_date)  # Correct ERPNext field name
            .with_invoice_type(InvoiceType.STANDARD)
            .with_supplier(supplier)
            .with_customer(customer)
            .with_line_items(line_items)
            .with_currency(Currency.NGN)
            .build()
        )
        
        return invoice

    def _build_supplier_party(self, company_name: str) -> Party:
        """Build supplier party from ERPNext Company"""
        company = frappe.get_doc("Company", company_name)
        address = self._build_address_from_company(company)
        
        return Party(
            business_id=self._generate_business_id(company.name),
            tin=self._clean_tin(company.tax_id),
            name=company.company_name,
            email=company.email or f"noreply@{company.name.lower().replace(' ', '')}.com",
            phone=self._format_phone(company.phone_no or "08000000000"),  # Correct field: phone_no
            address=address,
            vat_registered=True,
            trade_name=getattr(company, 'abbr', None)
        )
        
    def _build_address_from_company(self, company) -> Address:
        """Build Address from Company's primary address"""
        # Get company address using proper linking
        address_name = getattr(company, 'company_address', None)
        
        if address_name:
            try:
                addr_doc = frappe.get_doc("Address", address_name)
                return Address(
                    street=addr_doc.address_line1 or "N/A",  # Correct field name
                    street2=addr_doc.address_line2,  # Correct field name
                    city=addr_doc.city or "Lagos", 
                    state_code=self._map_state_to_code(addr_doc.state),
                    postal_code=self._format_postal_code(addr_doc.pincode),  # Correct field: pincode
                    country_code="NG"
                )
            except Exception as e:
                frappe.log_error(f"Company address {address_name} error: {str(e)}")
        
        # Fallback address
        return Address(
            street="N/A",
            city="Lagos",
            state_code=StateCode.LA,
            country_code="NG"
        )
    
    def _build_customer_party(self, customer_name: str) -> Party:
        """Build customer party from ERPNext Customer"""
        customer = frappe.get_doc("Customer", customer_name)
        address = self._build_address_from_customer(customer)

        return Party(
            business_id=self._generate_business_id(customer.name),
            tin=self._clean_tin(customer.tax_id) or "00000000",  # Fallback TIN
            name=customer.customer_name,
            email=customer.email_id or f"customer@{customer.name.lower().replace(' ', '')}.com",  # Correct field: email_id
            phone=self._format_phone(customer.mobile_no or "08000000000"),  # Correct field: mobile_no
            address=address,
            vat_registered=bool(customer.tax_id)
        )
        
    def _build_address_from_customer(self, customer) -> Address:
        """Build Address from Customer's primary address"""
        # Get customer primary address
        address_name = getattr(customer, 'customer_primary_address', None)  # Correct field
        
        if address_name:
            try:
                addr_doc = frappe.get_doc("Address", address_name)
                return Address(
                    street=addr_doc.address_line1 or "N/A",  # Correct field name
                    street2=addr_doc.address_line2,  # Correct field name
                    city=addr_doc.city or "Lagos",
                    state_code=self._map_state_to_code(addr_doc.state),
                    postal_code=self._format_postal_code(addr_doc.pincode),  # Correct field: pincode
                    country_code="NG"
                )
            except Exception as e:
                frappe.log_error(f"Customer address {address_name} error: {str(e)}")
        
        # Fallback address
        return Address(
            street="N/A", 
            city="Lagos",
            state_code=StateCode.LA,
            country_code="NG"
        )
    
    def _build_line_item(self, si_item, sales_invoice) -> LineItem:
        """Build line item from Sales Invoice Item"""
        # Get HSN code from item - use correct field name
        hsn_code = self._get_hsn_code(si_item.item_code, si_item)
        tax_rate = self._calculate_tax_rate(si_item, sales_invoice)
        
        return (
            self.client.create_line_item_builder()
            .with_description(si_item.description or si_item.item_name)
            .with_hsn_code(hsn_code)
            .with_quantity(Decimal(str(si_item.qty)), UnitOfMeasure.PIECE)
            .with_unit_price(Decimal(str(si_item.rate)))
            .with_tax_rate(tax_rate)
            .build()
        )

    def _get_hsn_code(self, item_code: str, si_item) -> str:
        """Get HSN code from item - check multiple sources"""
        # First check if HSN code is directly in sales invoice item
        if hasattr(si_item, 'gst_hsn_code') and si_item.gst_hsn_code:  # Correct field name
            hsn = re.sub(r'\D', '', si_item.gst_hsn_code)
            if len(hsn) >= 4:
                return hsn[:8]
        
        # Then check Item master
        try:
            item = frappe.get_doc("Item", item_code)
            if hasattr(item, 'gst_hsn_code') and item.gst_hsn_code:
                hsn = re.sub(r'\D', '', item.gst_hsn_code)
                if len(hsn) >= 4:
                    return hsn[:8]
                    
            # Fallback based on item group
            return self._get_default_hsn_by_item_group(item.item_group)
            
        except Exception as e:
            frappe.log_error(f"HSN code error for item {item_code}: {str(e)}")
            return '9999'  # Default service HSN

    def _get_default_hsn_by_item_group(self, item_group: str) -> str:
        """Get default HSN code based on item group"""
        hsn_mapping = {
            'Services': '9999',
            'Software': '8471',
            'Consumables': '3926',
            'Raw Material': '3920',
            'Sub Assemblies': '8473',
            'Products': '3926',
            'Finished Goods': '3926',
            'Trading Goods': '3926'
        }
        
        return hsn_mapping.get(item_group, '9999')

    def _calculate_tax_rate(self, si_item, sales_invoice) -> Decimal:
        """Calculate tax rate from ERPNext tax templates"""
        try:
            # Get tax rate from item tax template or sales invoice taxes
            total_tax_rate = Decimal('0')
            
            # Check if item has item tax template
            if hasattr(si_item, 'item_tax_template') and si_item.item_tax_template:
                tax_template = frappe.get_doc("Item Tax Template", si_item.item_tax_template)
                for tax in tax_template.taxes:
                    total_tax_rate += Decimal(str(abs(tax.tax_rate)))
                return total_tax_rate
            
            # Check taxes table in sales invoice
            for tax in sales_invoice.taxes:
                if tax.charge_type == "On Net Total":
                    # This is likely VAT/GST
                    rate = abs(tax.rate) if tax.rate else Decimal('0')
                    total_tax_rate += Decimal(str(rate))
            
            # If no tax found, use default VAT rate
            if total_tax_rate == 0:
                return Decimal('7.5')  # Default Nigerian VAT rate
                
            return total_tax_rate
            
        except Exception as e:
            frappe.log_error(f"Tax rate calculation error: {str(e)}")
            return Decimal('7.5')  # Default VAT rate

    # Helper methods for data formatting and validation
    def _clean_tin(self, tin: str) -> Optional[str]:
        """Clean and validate TIN"""
        if not tin:
            return None
        
        # Remove non-digits
        clean_tin = re.sub(r'\D', '', tin)
        
        # Validate length (8-15 digits for TIN)
        if len(clean_tin) < 8:
            return None
            
        return clean_tin[:15]  # Max 15 digits

    def _format_phone(self, phone: str) -> str:
        """Format phone number for Nigerian standard"""
        if not phone:
            return "+2348000000000"  # Fallback
            
        # Remove all non-digits
        clean_phone = re.sub(r'\D', '', phone)
        
        # Handle Nigerian numbers
        if clean_phone.startswith('234'):
            if len(clean_phone) == 13:
                return f'+{clean_phone}'
        elif clean_phone.startswith('0'):
            if len(clean_phone) == 11:
                return f'+234{clean_phone[1:]}'
        
        # Fallback for invalid numbers
        return "+2348000000000"

    def _format_postal_code(self, pincode: str) -> Optional[str]:
        """Format postal code to 6 digits"""
        if not pincode:
            return None
            
        # Remove non-digits and pad/truncate to 6 digits
        clean_code = re.sub(r'\D', '', pincode)
        if len(clean_code) >= 3:
            return clean_code[:6].ljust(6, '0')
        
        return None

    def _map_state_to_code(self, state_name: str) -> StateCode:
        """Map state name to StateCode enum"""
        if not state_name:
            return StateCode.LA  # Default to Lagos
            
        state_mapping = {
            'Lagos': StateCode.LA,
            'Abuja': StateCode.FC,
            'Federal Capital Territory': StateCode.FC,
            'FCT': StateCode.FC,
            'Kano': StateCode.KN,
            'Rivers': StateCode.RI,
            'Ogun': StateCode.OG,
            'Kaduna': StateCode.KD,
            'Oyo': StateCode.OY,
            'Delta': StateCode.DE,
            'Edo': StateCode.ED,
            'Anambra': StateCode.AN,
            'Imo': StateCode.IM,
            'Enugu': StateCode.EN,
            'Abia': StateCode.AB,
            'Cross River': StateCode.CR,
            'Akwa Ibom': StateCode.AK,
            'Bayelsa': StateCode.BY,
            'Benue': StateCode.BE,
            'Borno': StateCode.BO,
            'Ebonyi': StateCode.EB,
            'Ekiti': StateCode.EK,
            'Gombe': StateCode.GO,
            'Jigawa': StateCode.JI,
            'Kebbi': StateCode.KE,
            'Kogi': StateCode.KO,
            'Kwara': StateCode.KW,
            'Nasarawa': StateCode.NA,
            'Niger': StateCode.NI,
            'Ondo': StateCode.ON,
            'Osun': StateCode.OS,
            'Plateau': StateCode.PL,
            'Sokoto': StateCode.SO,
            'Taraba': StateCode.TA,
            'Yobe': StateCode.YO,
            'Zamfara': StateCode.ZA
        }
        
        # Try exact match first
        if state_name in state_mapping:
            return state_mapping[state_name]
            
        # Try partial match (case insensitive)
        state_name_lower = state_name.lower()
        for state, code in state_mapping.items():
            if state.lower() in state_name_lower or state_name_lower in state.lower():
                return code
                
        return StateCode.LA  # Default fallback

    def _generate_business_id(self, name: str) -> str:
        """Generate business ID from name"""
        # Clean name and create ID
        clean_name = re.sub(r'[^A-Z0-9]', '', name.upper())
        return f"BIZ-{clean_name[:10]}-{frappe.utils.random_string(5)}"

    # Main integration methods
    def validate_invoice(self, invoice: Invoice):
        """Validate invoice using zutax client"""
        return self.client.validate_invoice(invoice)

    def generate_irn(self, sales_invoice_name: str) -> str:
        """Generate IRN for invoice"""
        return self.client.generate_irn(sales_invoice_name)

    def generate_qr_code(self, irn: str) -> str:
        """Generate QR code for invoice"""
        qr_base64 = self.client.generate_qr_code(irn, format="base64")
        return qr_base64
    
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

    def test_conversion(self, sales_invoice_name: str) -> Dict[str, Any]:
        """Test conversion without submitting to API"""
        try:
            invoice = self.convert_sales_invoice(sales_invoice_name)
            validation_result = self.validate_invoice(invoice)
            
            return {
                "success": True,
                "invoice_data": invoice.model_dump(),
                "validation": validation_result.model_dump() if validation_result else None,
                "message": "Invoice converted and validated successfully"
            }
        except Exception as e:
            frappe.log_error(f"Test conversion error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "invoice_data": None,
                "validation": None,
                "message": f"Conversion failed: {str(e)}"
            }

    def bulk_convert_invoices(self, sales_invoice_names: list) -> Dict[str, Any]:
        """Convert multiple invoices in bulk"""
        results = {
            "successful": [],
            "failed": [],
            "total": len(sales_invoice_names)
        }
        
        for invoice_name in sales_invoice_names:
            try:
                result = self.test_conversion(invoice_name)
                if result["success"]:
                    results["successful"].append({
                        "invoice": invoice_name,
                        "data": result
                    })
                else:
                    results["failed"].append({
                        "invoice": invoice_name,
                        "error": result["error"]
                    })
            except Exception as e:
                results["failed"].append({
                    "invoice": invoice_name,
                    "error": str(e)
                })
        
        return results


# Utility functions for ERPNext integration
def get_zutax_integrator() -> ZutaxIntegrator:
    """Get a configured ZutaxIntegrator instance"""
    return ZutaxIntegrator()

def convert_sales_invoice_to_zutax(sales_invoice_name: str) -> Invoice:
    """Convert a single Sales Invoice to Zutax format"""
    integrator = get_zutax_integrator()
    return integrator.convert_sales_invoice(sales_invoice_name)

def test_invoice_conversion(sales_invoice_name: str) -> Dict[str, Any]:
    """Test invoice conversion and validation"""
    integrator = get_zutax_integrator()
    return integrator.test_conversion(sales_invoice_name)
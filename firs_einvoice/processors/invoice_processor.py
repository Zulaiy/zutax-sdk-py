"""Invoice processing and validation utilities."""

from typing import Dict, List, Optional, Any
from decimal import Decimal
from pydantic import BaseModel

from ..schemas.input_schemas import validate_invoice_input
from ..models.invoice import Invoice, ValidationError
from ..builders.invoice_builder import InvoiceBuilder
from ..schemas.validators import InvoiceValidator
from ..crypto.irn import IRNGenerator
from ..crypto.firs_qrcode import FIRSQRCodeGenerator
from ..config.settings import BusinessContext


class ProcessingResult(BaseModel):
    """Invoice processing result model."""
    success: bool
    invoice: Optional[Invoice] = None
    irn: Optional[str] = None
    qr_code: Optional[str] = None
    errors: List[ValidationError] = []
    warnings: List[str] = []


class InvoiceProcessor:
    """Invoice processing and validation utilities."""
    
    @classmethod
    async def process_invoice(cls, invoice_input: Dict[str, Any], 
                            business_context: Optional[BusinessContext] = None) -> ProcessingResult:
        """
        Main processing function - converts input to complete invoice.
        """
        try:
            # 1. VALIDATE INPUT
            validation = validate_invoice_input(invoice_input)
            if not validation['success']:
                return ProcessingResult(
                    success=False,
                    errors=[
                        ValidationError(
                            field='.'.join(str(p) for p in error.get('path', [])),
                            message=error.get('message', 'Validation error'),
                            code='VALIDATION_ERROR'
                        ) for error in validation.get('errors', [])
                    ]
                )
            
            # 2. BUILD INVOICE
            builder = cls._create_invoice_builder(validation['data'], business_context)
            invoice = builder.build()
            
            # 3. FINAL VALIDATION
            validation_result = InvoiceValidator.validate_invoice(invoice)
            if not validation_result['valid']:
                return ProcessingResult(
                    success=False,
                    errors=validation_result.get('errors', []),
                    warnings=[w.get('message', '') for w in validation_result.get('warnings', [])]
                )
            
            # 4. GENERATE IRN & QR CODE
            irn = IRNGenerator.generate_irn(invoice)
            invoice.irn = irn
            
            qr_code = FIRSQRCodeGenerator.generate_qr_code(irn)
            invoice.qr_code = qr_code
            
            return ProcessingResult(
                success=True,
                invoice=invoice,
                irn=irn,
                qr_code=qr_code,
                warnings=[]
            )
            
        except Exception as error:
            return ProcessingResult(
                success=False,
                errors=[ValidationError(
                    field='general',
                    message=str(error),
                    code='PROCESSING_ERROR'
                )],
                warnings=[]
            )
    
    @classmethod
    def _create_invoice_builder(cls, input_data: Dict[str, Any], 
                               context: Optional[BusinessContext] = None) -> InvoiceBuilder:
        """Create invoice builder with input data."""
        builder = InvoiceBuilder(context)
        
        # Basic invoice fields
        builder.set_business_id(input_data['business_id'])
        builder.set_invoice_number(input_data['invoice_number'])
        builder.set_invoice_type(input_data['invoice_type'])
        builder.set_document_currency_code(input_data.get('document_currency_code', 'NGN'))
        builder.set_tax_currency_code(input_data.get('tax_currency_code', 'NGN'))
        builder.set_issue_date(input_data['issue_date'])
        
        # Optional fields
        if 'due_date' in input_data:
            builder.set_due_date(input_data['due_date'])
        if 'note' in input_data:
            builder.set_note(input_data['note'])
        
        # Parties
        builder.set_accounting_supplier_party(input_data['accounting_supplier_party'])
        builder.set_accounting_customer_party(input_data['accounting_customer_party'])
        
        # Line items
        for line_item_input in input_data['invoice_line']:
            line_item = {
                'id': line_item_input.get('id', ''),
                'description': line_item_input['item']['description'],
                'hsn_code': line_item_input['hsn_code'],
                'quantity': line_item_input['invoiced_quantity'],
                'unit_price': Decimal(str(line_item_input['price']['price_amount'])),
                'unit_of_measure': line_item_input['price'].get('price_unit', 'PIECE'),
                'discount': Decimal(str(line_item_input.get('discount_amount', 0))),
                'discount_rate': line_item_input.get('discount_rate'),
                'taxes': [],
                'total_tax': Decimal('0'),
                'line_total': Decimal(str(line_item_input.get('line_extension_amount', 
                                                           line_item_input['invoiced_quantity'] * line_item_input['price']['price_amount']))),
                'net_amount': Decimal(str(line_item_input.get('line_extension_amount',
                                                            line_item_input['invoiced_quantity'] * line_item_input['price']['price_amount'])))
            }
            
            builder.add_line_item(line_item)
        
        # Metadata
        if 'metadata' in input_data:
            for key, value in input_data['metadata'].items():
                builder.add_metadata(key, value)
        
        return builder
    
    @classmethod
    def validate_input(cls, input_data: Any) -> Dict[str, Any]:
        """Validate invoice input data."""
        validation = validate_invoice_input(input_data)
        
        if validation['success']:
            return {'valid': True, 'errors': []}
        
        errors = [
            ValidationError(
                field='.'.join(str(p) for p in error.get('path', [])),
                message=error.get('message', 'Validation error'),
                code='VALIDATION_ERROR'
            ) for error in validation.get('errors', [])
        ]
        
        return {
            'valid': False,
            'errors': errors
        }
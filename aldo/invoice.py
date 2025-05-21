"""
Invoice generation for Aldo
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class InvoiceGenerator:
    """Generates PDF invoices based on work hours data"""
    
    def __init__(self, config, storage):
        """Initialize the invoice generator with config and storage"""
        self.config = config
        self.storage = storage
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles for the invoice"""
        # Add custom styles - use a different name to avoid conflict
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20
        ))
        
        # Use custom InvoiceHeading instead of Heading1 to avoid conflict
        self.styles.add(ParagraphStyle(
            name='InvoiceHeading',
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=14,
        ))
        
        # Normal style already exists in getSampleStyleSheet(), so we'll override it
        # Only if we need custom settings
        if 'Normal' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='Normal',
                fontName='Helvetica',
                fontSize=10,
                leading=12,
            ))
        
        self.styles.add(ParagraphStyle(
            name='Small',
            fontName='Helvetica',
            fontSize=8,
            leading=10,
        ))
        
        self.styles.add(ParagraphStyle(
            name='Footer',
            fontName='Helvetica',  # Changed from Helvetica-Italic to Helvetica
            fontSize=8,
            leading=10,
            alignment=1  # Center
        ))
    
    def generate_invoice(self, start_date, end_date, entries, output_filename):
        """Generate a PDF invoice for the given date range and entries"""
        # Get config data
        cfg = self.config.get_config()
        company = cfg.get('company', {'name': 'Your Company Name'})
        client = cfg.get('client', {'name': 'Client Name', 'address': 'Client Address'})
        payment = cfg.get('payment', {'hourly_rate': 50.00})
        invoice_cfg = cfg.get('invoice', {'footer_text': 'Thank you for your business!'})
        
        # Calculate total amount
        total_hours = self.storage.get_total_hours(entries)
        hourly_rate = payment['hourly_rate']
        total_amount = total_hours * hourly_rate
        
        # Get invoice number
        invoice_number = self.config.get_next_invoice_number()
        
        # Prepare invoice date and due date (30 days from now)
        invoice_date = datetime.now().strftime('%Y-%m-%d')
        due_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Create PDF - use absolute path for better reliability
        output_path = Path(output_filename).resolve()
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Build the invoice content
        elements = []
        
        # Invoice header
        elements.append(Paragraph("Invoice", self.styles['InvoiceTitle']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Create the new 2x3 invoice information table
        # First row: Invoice Number, Date of Issue, Due Date
        # Second row: Billed To, From
        
        company_name = company.get('name')
        company_address = company.get('address', '')
        company_info = f"{company_name}\n{company_address}"
        
        client_name = client.get('name', 'Client Name')
        client_address = client.get('address', '')
        client_info = f"{client_name}\n{client_address}"
        
        # Create cell contents with title and value
        inv_num_cell = Paragraph(f"<b>INVOICE NUMBER</b><br/>{invoice_number}", self.styles['Normal'])
        date_cell = Paragraph(f"<b>DATE OF ISSUE</b><br/>{invoice_date}", self.styles['Normal'])
        due_date_cell = Paragraph(f"<b>DUE DATE</b><br/>{due_date}", self.styles['Normal'])
        billed_to_cell = Paragraph(f"<b>BILLED TO</b><br/>{client_info}", self.styles['Normal'])
        from_cell = Paragraph(f"<b>FROM</b><br/>{company_info}", self.styles['Normal'])
        period_cell = Paragraph(f"<b>PERIOD</b><br/>{start_date} to {end_date}", self.styles['Normal'])
        
        # Create the table with the cells
        invoice_info_data = [
            [inv_num_cell, date_cell, due_date_cell],
            [billed_to_cell, from_cell, period_cell]
        ]
        
        # Create the table with equal column widths
        col_width = doc.width / 3
        invoice_info_table = Table(invoice_info_data, colWidths=[col_width, col_width, col_width])
        
        # Style the table
        invoice_info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(invoice_info_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Work summary
        elements.append(Paragraph("WORK SUMMARY", self.styles['InvoiceHeading']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Create work details table
        work_data = [["Date", "Hours", "Amount"]]
        
        # Group entries by date
        entries_by_date = {}
        for entry in entries:
            date = entry["date"]
            if date not in entries_by_date:
                entries_by_date[date] = []
            entries_by_date[date].append(entry)
        
        # Add entries to table
        for date in sorted(entries_by_date.keys()):
            date_entries = entries_by_date[date]
            for i, entry in enumerate(date_entries):
                # Only show date for first entry of the day
                date_display = date if i == 0 else ""
                work_data.append([date_display, f"{entry['hours']:.2f}", entry['hours'] * hourly_rate])
        
        # Add total row
        work_data.append(["", "", ""])
        work_data.append(["TOTAL:", f"{total_hours:.2f}", ""])
        
        work_table = Table(work_data, colWidths=[1*inch, 0.75*inch, 0.75*inch])
        work_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -3), 0.25, colors.black),
            ('FONTNAME', (0, -2), (0, -1), 'Helvetica-Bold'),  # Total row
            ('FONTNAME', (1, -1), (1, -1), 'Helvetica-Bold'),  # Total amount
            ('SPAN', (2, -2), (-1, -2)),  # Span empty row
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),  # Line above total
        ]))
        elements.append(work_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Payment details
        elements.append(Paragraph("PAYMENT DETAILS", self.styles['InvoiceHeading']))
        elements.append(Spacer(1, 0.1*inch))
        
        payment_data = [
            ["Hourly Rate:", f"${hourly_rate:.2f}"],
            ["Total Amount Due:", f"${total_amount:.2f}"],
        ]
        payment_table = Table(payment_data, colWidths=[2*inch, 4*inch])
        payment_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 1), (1, 1), colors.lightgrey),  # Highlight total
        ]))
        elements.append(payment_table)
        elements.append(Spacer(1, inch))

        
        # Build the PDF
        doc.build(elements)
        
        return str(output_path)
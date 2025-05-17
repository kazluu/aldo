"""
Invoice generation for Aldo
"""

import os
from datetime import datetime
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
        # Add custom styles
        self.styles.add(ParagraphStyle(
            name='Title',
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            alignment=1  # Center
        ))
        
        self.styles.add(ParagraphStyle(
            name='Heading1',
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=14,
        ))
        
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
            fontName='Helvetica-Italic',
            fontSize=8,
            leading=10,
            alignment=1  # Center
        ))
    
    def generate_invoice(self, start_date, end_date, entries, output_filename):
        """Generate a PDF invoice for the given date range and entries"""
        # Get config data
        cfg = self.config.get_config()
        business = cfg['business']
        client = cfg['client']
        payment = cfg['payment']
        invoice_cfg = cfg['invoice']
        
        # Calculate total amount
        total_hours = self.storage.get_total_hours(entries)
        hourly_rate = payment['hourly_rate']
        total_amount = total_hours * hourly_rate
        
        # Get invoice number
        invoice_number = self.config.get_next_invoice_number()
        
        # Prepare invoice date and due date
        invoice_date = datetime.now().strftime('%Y-%m-%d')
        
        # Create PDF
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
        elements.append(Paragraph(f"INVOICE", self.styles['Title']))
        elements.append(Spacer(1, 0.25*inch))
        
        # Invoice metadata table
        invoice_data = [
            ["Invoice Number:", invoice_number],
            ["Invoice Date:", invoice_date],
            ["Period:", f"{start_date} to {end_date}"],
        ]
        invoice_table = Table(invoice_data, colWidths=[2*inch, 3*inch])
        invoice_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(invoice_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # From and To addresses
        address_data = [
            ["FROM:", "TO:"],
            [
                f"{business['name']}\n{business['address']}\n{business['city']}, {business['state']} {business['zip']}\n{business['country']}\nPhone: {business['phone']}\nEmail: {business['email']}",
                f"{client['name']}\n{client['address']}\n{client['city']}, {client['state']} {client['zip']}\n{client['country']}\nContact: {client['contact_person']}\nEmail: {client['email']}"
            ]
        ]
        address_table = Table(address_data, colWidths=[2.75*inch, 2.75*inch])
        address_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (1, 1), 'Helvetica'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(address_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Work summary
        elements.append(Paragraph("WORK SUMMARY", self.styles['Heading1']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Create work details table
        work_data = [["Date", "Hours", "Description"]]
        
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
                work_data.append([date_display, f"{entry['hours']:.2f}", entry['description']])
        
        # Add total row
        work_data.append(["", "", ""])
        work_data.append(["TOTAL HOURS:", f"{total_hours:.2f}", ""])
        
        work_table = Table(work_data, colWidths=[1*inch, 0.75*inch, 4.25*inch])
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
        elements.append(Spacer(1, 0.25*inch))
        
        # Payment details
        elements.append(Paragraph("PAYMENT DETAILS", self.styles['Heading1']))
        elements.append(Spacer(1, 0.1*inch))
        
        payment_data = [
            ["Hourly Rate:", f"{payment['currency']} {hourly_rate:.2f}"],
            ["Total Amount Due:", f"{payment['currency']} {total_amount:.2f}"],
            ["Payment Terms:", payment['payment_terms']],
            ["Bank:", payment['bank_name']],
            ["Account Name:", payment['account_name']],
            ["Account Number:", payment['account_number']],
            ["Routing/SWIFT:", payment['routing_number'] if payment['routing_number'] else payment['swift']],
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
        
        # Footer
        elements.append(Paragraph(invoice_cfg['footer_text'], self.styles['Footer']))
        
        # Build the PDF
        doc.build(elements)
        
        return str(output_path)

"""
Storage management for Aldo - handles persisting and retrieving work hour data
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import namedtuple
import appdirs

# Define the ConfirmedInvoice namedtuple
ConfirmedInvoice = namedtuple('ConfirmedInvoice', ['invoice_number', 'start_date', 'end_date'])

class WorkHoursStorage:
    """Manages the storage of work hours data and invoice tracking"""
    
    def __init__(self):
        """Initialize the storage with default paths"""
        # Use appdirs to get standard data locations
        self.data_dir = Path(appdirs.user_data_dir("aldo", "aldo"))
        self.data_file = self.data_dir / 'aldo_data.json'

        # Initialize with default structure
        self.aldo_data = {
            'last_confirmed_invoice': None,
            'last_unconfirmed_invoice': None,
            'confirmed_invoices': {},
            'work_entries': []
        }
        
        # Ensure storage exists and load data
        self.ensure_storage_exists()
        
        # Load data if it exists
        if self.data_file.exists():
            self.load_data()
    
    def ensure_storage_exists(self):
        """Ensure storage directory and file exist"""
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.data_file.exists():
            # Create empty data file
            self.save_data()
    
    def load_data(self):
        """Load data from file"""
        try:
            with open(self.data_file, 'r') as f:
                self.aldo_data = json.load(f)
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")
    
    def save_data(self):
        """Save data to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.aldo_data, f, indent=2)
        except Exception as e:
            raise Exception(f"Error saving data: {str(e)}")
    
    def log_work(self, date, hours, description=""):
        """Log work hours for a specific date"""
        # Convert date to string for JSON storage
        date_str = date.strftime('%Y-%m-%d')
        
        # Check if there's an existing entry for this date
        # If so, we'll remove it before adding the new one
        existing_entries = [
            i for i, entry in enumerate(self.aldo_data["work_entries"])
            if entry["date"] == date_str
        ]
        
        # If entry exists for this date, remove it and notify
        if existing_entries:
            for index in sorted(existing_entries, reverse=True):
                old_entry = self.aldo_data["work_entries"][index]
                del self.aldo_data["work_entries"][index]
                print(f"Replaced previous entry: {old_entry['hours']} hours on {date_str}")
        
        # Create new entry
        entry = {
            "date": date_str,
            "hours": hours,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to entries and save
        self.aldo_data["work_entries"].append(entry)
        self.save_data()
        return entry
    
    def get_work_entries(self, start_date, end_date):
        """Get work entries within a date range"""
        # Convert dates to strings for comparison, handling different input types
        if hasattr(start_date, 'strftime'):
            start_str = start_date.strftime('%Y-%m-%d')
        elif isinstance(start_date, str):
            start_str = start_date
        else:
            # Default to earliest date if we can't determine
            earliest = self.get_earliest_entry_date()
            start_str = earliest.strftime('%Y-%m-%d') if earliest else "1900-01-01"
            
        if hasattr(end_date, 'strftime'):
            end_str = end_date.strftime('%Y-%m-%d')
        elif isinstance(end_date, str):
            end_str = end_date
        else:
            # Default to today if we can't determine
            end_str = datetime.now().strftime('%Y-%m-%d')
        
        # Filter entries by date range
        filtered_entries = [
            entry for entry in self.aldo_data["work_entries"]
            if start_str <= entry["date"] <= end_str
        ]
        
        # Sort by date
        return sorted(filtered_entries, key=lambda x: x["date"])
    
    def get_summary(self, period):
        """Get summary of work hours for the specified period"""
        today = datetime.now().date()
        
        # Determine date range based on period
        if period == 'week':
            start_date = today - timedelta(days=7)
            end_date = today
        elif period == 'month':
            start_date = today.replace(day=1)
            # Find the last day of the month
            if today.month == 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        elif period == 'year':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        else:
            raise ValueError(f"Invalid period: {period}")
        
        # Get entries in date range
        entries = self.get_work_entries(start_date, end_date)
        
        # Group by date
        summary = {}
        for entry in entries:
            date = entry["date"]
            if date not in summary:
                summary[date] = []
            summary[date].append({
                "hours": entry["hours"],
                "description": entry["description"]
            })
        
        return summary
    
    def get_total_hours(self, entries):
        """Calculate total hours from a list of work entries"""
        return sum(entry["hours"] for entry in entries)
        
    def get_earliest_entry_date(self):
        """Get the date of the earliest work entry"""
        if not self.aldo_data["work_entries"]:
            return None
        
        # Find the earliest date in the entries
        earliest_entry = min(self.aldo_data["work_entries"], key=lambda x: x["date"])
        
        # Convert the string date to a date object
        date_str = earliest_entry["date"]
        return datetime.strptime(date_str, '%Y-%m-%d').date()

    def get_next_invoice_number(self):
        """Get the next invoice number"""
        last_confirmed = self.aldo_data['last_confirmed_invoice']
        if last_confirmed:
            return int(last_confirmed['invoice_number']) + 10
        else:
            # No confirmed invoices yet, start from default base number
            return 391
    
    def store_unconfirmed_invoice(self, invoice_number, start_date, end_date, config=None):
        """
        Store an unconfirmed invoice that was just generated
        
        Args:
            invoice_number: The invoice number (can be numeric part only or full with prefix)
            start_date: The start date of the invoice period
            end_date: The end date of the invoice period
            config: The configuration object (optional)
        """
        # Extract numeric part if full invoice number with prefix is provided
        if config:
            prefix = config.config['invoice']['prefix']
            if isinstance(invoice_number, str) and invoice_number.startswith(prefix):
                numeric_part = invoice_number[len(prefix):]
            else:
                numeric_part = str(invoice_number)
        else:
            numeric_part = str(invoice_number)
        
        # Convert dates to strings for JSON storage
        start_date_str = start_date.strftime('%Y-%m-%d') if hasattr(start_date, 'strftime') else str(start_date)
        end_date_str = end_date.strftime('%Y-%m-%d') if hasattr(end_date, 'strftime') else str(end_date)
        
        self.aldo_data['last_unconfirmed_invoice'] = {
            'invoice_number': numeric_part,
            'start_date': start_date_str,
            'end_date': end_date_str
        }
        self.save_data()
    
    def get_last_unconfirmed_invoice(self):
        """
        Get the last unconfirmed invoice
        
        Returns:
            ConfirmedInvoice namedtuple or None if no unconfirmed invoice exists
        """
        unconfirmed = self.aldo_data.get('last_unconfirmed_invoice')
        if not unconfirmed:
            return None
            
        return ConfirmedInvoice(
            invoice_number=unconfirmed['invoice_number'],
            start_date=unconfirmed['start_date'],
            end_date=unconfirmed['end_date']
        )

    def confirm_invoice(self, invoice_number, config):
        """
        Confirm an invoice was sent and store its information
        
        Args:
            invoice_number: The invoice number to confirm (with or without prefix)
            config: The configuration object to get invoice prefix
            
        Returns:
            bool: True if confirmation was successful, False otherwise
        """
        # Check if there's an unconfirmed invoice to confirm
        unconfirmed = self.aldo_data.get('last_unconfirmed_invoice')
        if not unconfirmed:
            raise Exception("No unconfirmed invoice found. Generate an invoice first before confirming.")
        
        # Extract the numeric part if the full invoice ID was provided
        prefix = config.config['invoice']['prefix']
        if isinstance(invoice_number, str) and invoice_number.startswith(prefix):
            invoice_number = int(invoice_number[len(prefix):])
        else:
            try:
                invoice_number = int(invoice_number)
            except (ValueError, TypeError):
                return False
        
        # Check if the invoice number matches the unconfirmed invoice
        if str(invoice_number) != unconfirmed['invoice_number']:
            raise Exception(f"Invoice number mismatch. Expected {unconfirmed['invoice_number']}, got {invoice_number}")
        
        # Format as string for storage
        invoice_id = str(invoice_number)
        
        # Create the confirmed invoice using the unconfirmed invoice data
        confirmed_invoice_data = {
            'invoice_number': invoice_id,
            'start_date': unconfirmed['start_date'],
            'end_date': unconfirmed['end_date']
        }
        
        # Store the invoice confirmation
        self.aldo_data['confirmed_invoices'][invoice_id] = confirmed_invoice_data
        
        # Update the last confirmed invoice
        self.aldo_data['last_confirmed_invoice'] = confirmed_invoice_data
        
        # Clear the unconfirmed invoice
        self.aldo_data['last_unconfirmed_invoice'] = None
        
        # Save changes
        self.save_data()
        
        return True
    
    def get_last_confirmed_invoice(self):
        """
        Get the last confirmed invoice
        
        Returns:
            ConfirmedInvoice namedtuple or None if no invoice has been confirmed
        """
        last_confirmed = self.aldo_data['last_confirmed_invoice']
        if not last_confirmed:
            return None
            
        return ConfirmedInvoice(
            invoice_number=last_confirmed['invoice_number'],
            start_date=last_confirmed['start_date'],
            end_date=last_confirmed['end_date']
        )
    
    def get_invoice_by_number(self, invoice_number, config):
        """
        Get a confirmed invoice by its number
        
        Args:
            invoice_number: The invoice number to look up (with or without prefix)
            config: The configuration object to get invoice prefix
            
        Returns:
            ConfirmedInvoice namedtuple or None if the invoice was not found
        """
        # Extract the numeric part if the full invoice ID was provided
        prefix = config.config['invoice']['prefix']
        if isinstance(invoice_number, str) and invoice_number.startswith(prefix):
            invoice_number = int(invoice_number[len(prefix):])
        else:
            try:
                invoice_number = int(invoice_number)
            except (ValueError, TypeError):
                return None
        
        # Format as string for lookup
        invoice_id = str(invoice_number)
        
        # Check if this invoice exists in confirmed invoices
        if invoice_id not in self.aldo_data['confirmed_invoices']:
            return None
            
        invoice_data = self.aldo_data['confirmed_invoices'][invoice_id]
        
        return ConfirmedInvoice(
            invoice_number=invoice_data['invoice_number'],
            start_date=invoice_data['start_date'],
            end_date=invoice_data['end_date']
        )
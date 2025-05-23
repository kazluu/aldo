#!/usr/bin/env python3
"""
Aldo - Work Hours Tracker and Invoice Generator
A CLI application for freelancers to track their hours and generate invoices.
"""

import os
import sys
import click
import traceback
from datetime import datetime, timedelta
from aldo.storage import WorkHoursStorage
from aldo.config import Config
from aldo.invoice import InvoiceGenerator
from aldo import __version__

# Initialize global config and storage
config = Config()
storage = WorkHoursStorage()

def validate_date(ctx, param, value):
    """Validate date format (YYYY-MM-DD) or handle aliases"""
    if not value:
        return value
    
    # Handle date aliases
    today = datetime.now().date()
    if value == "today":
        return today
    elif value == "yesterday":
        return today - timedelta(days=1)
    elif value == "tomorrow":
        return today + timedelta(days=1)
    elif value == "daybefore":
        return today - timedelta(days=2)
    
    # Handle regular date format
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        raise click.BadParameter('Date must be in YYYY-MM-DD format or one of: today, yesterday, tomorrow, daybefore')

def validate_hours(ctx, param, value):
    """Validate hours (must be a positive number)"""
    if value <= 0:
        raise click.BadParameter('Hours must be a positive number')
    return value

@click.group()
@click.version_option(version=__version__)
def cli():
    """
    Aldo - Work Hours Tracker and Invoice Generator for Freelancers

    A command-line tool to log work hours, view summaries, and generate invoices.
    """
    # Ensure config and data directories exist
    config.ensure_config_exists()
    storage.ensure_storage_exists()

@cli.command('log')
@click.argument('date', callback=validate_date)
@click.argument('hours', type=float, callback=validate_hours)
@click.argument('description', required=False)
def log_work(date, hours, description=""):
    """
    Record work hours for a specific date.

    DATE: Date in YYYY-MM-DD format or an alias (today, yesterday, tomorrow, daybefore)
    HOURS: Number of hours worked (positive number)
    DESCRIPTION: Optional description of the work performed
    
    If a log entry already exists for the specified date, it will be replaced.
    """
    try:
        storage.log_work(date, hours, description)
        date_str = date.strftime('%Y-%m-%d')
        if description:
            click.echo(f"Successfully logged {hours} hours on {date_str} - '{description}'")
        else:
            click.echo(f"Successfully logged {hours} hours on {date_str}")
    except Exception as e:
        click.echo(f"Error logging work: {str(e)}", err=True)
        sys.exit(1)

@cli.command('summary')
@click.argument('period', type=click.Choice(['week', 'month', 'year']), required=False)
def view_summary(period):
    """
    View summary of hours worked for the specified time period.

    PERIOD: One of: 'week', 'month', or 'year'. If not provided, shows all entries since last confirmed invoice.
    """
    try:
        if period:
            # Existing logic for specific periods
            summary = storage.get_summary(period)
            title = period.upper()
        else:
            # New logic for entries since last confirmed invoice
            last_confirmed = storage.get_last_confirmed_invoice()
            if not last_confirmed:
                # No confirmed invoice, get all entries
                earliest_date = storage.get_earliest_entry_date()
                if not earliest_date:
                    click.echo("No work hours recorded.")
                    return
                start_date = earliest_date
                end_date = datetime.now().date()
                title = "ALL ENTRIES"
            else:
                # Start from day after last confirmed invoice
                last_end_date = datetime.strptime(last_confirmed.end_date, '%Y-%m-%d').date()
                start_date = last_end_date + timedelta(days=1)
                end_date = datetime.now().date()
                title = f"SINCE LAST INVOICE ({last_confirmed.end_date})"
            
            # Get entries and convert to summary format
            entries = storage.get_work_entries(start_date, end_date)
            summary = {}
            for entry in entries:
                date = entry["date"]
                if date not in summary:
                    summary[date] = []
                summary[date].append({
                    "hours": entry["hours"],
                    "description": entry["description"]
                })
        
        # Print summary header
        click.echo(f"\n{'='*30}")
        click.echo(f"WORK SUMMARY FOR: {title}")
        click.echo(f"{'='*30}")

        click.echo("")
        if not summary:
            if period:
                click.echo("No work hours recorded for this period.")
            else:
                click.echo("No work hours recorded since last invoice.")
            return

        # Print details
        total_hours = 0
        for date_str, entries in summary.items():
            day_hours = sum(entry['hours'] for entry in entries)
            total_hours += day_hours
            click.echo(f"{date_str}: {day_hours:.2f} hours")
        
        # Print total
        click.echo(f"\n{'-'*30}")
        click.echo(f"TOTAL HOURS: {total_hours:.2f}")
        click.echo(f"{'='*30}\n")
        
    except Exception as e:
        click.echo(f"Error getting summary: {str(e)}", err=True)
        sys.exit(1)

def _parse_invoice_input(input_value):
    """Parse input as either invoice number or date and return appropriate values"""
    today = datetime.now().date()
    is_invoice_number = False
    invoice_number = None
    
    if input_value is None:
        return is_invoice_number, invoice_number, today
    
    # Try to parse as invoice number if it's a string
    if isinstance(input_value, str):
        try:
            # Check if it might be a full invoice ID with prefix
            prefix = config.config['invoice']['prefix']
            if input_value.startswith(prefix):
                invoice_number = int(input_value[len(prefix):])
                is_invoice_number = True
            else:
                # Try to parse as integer
                invoice_number = int(input_value)
                is_invoice_number = True
        except (ValueError, TypeError):
            # Not an invoice number, try to parse as date
            date_aliases = {
                "today": today,
                "yesterday": today - timedelta(days=1),
                "tomorrow": today + timedelta(days=1),
                "daybefore": today - timedelta(days=2)
            }
            
            if input_value in date_aliases:
                return is_invoice_number, invoice_number, date_aliases[input_value]
            
            try:
                # Handle regular date format
                return is_invoice_number, invoice_number, datetime.strptime(input_value, '%Y-%m-%d').date()
            except ValueError:
                raise click.BadParameter('Date must be in YYYY-MM-DD format or one of: today, yesterday, tomorrow, daybefore')
    
    return is_invoice_number, invoice_number, input_value

def _ensure_date_object(date_value, default_date=None):
    """Ensure we have a proper date object"""
    if default_date is None:
        default_date = datetime.now().date()
        
    if hasattr(date_value, 'strftime'):
        return date_value
    
    try:
        if isinstance(date_value, str):
            return datetime.strptime(date_value, '%Y-%m-%d').date()
        return default_datet
    except (ValueError, TypeError):
        return default_date

@cli.command('generate-invoice')
@click.argument('invoice_or_end_date', required=False)
@click.option('--output', '-o', default='invoice.pdf', help='Output PDF filename')
def generate_invoice(invoice_or_end_date, output):
    """
    Generate a PDF invoice.

    Supports two modes:
    
    1. Generate new invoice:
       - If a date is provided, it is used as the end date for the current billing period
       - The start date is automatically determined as the day after the last confirmed invoice
       - Example: aldo generate-invoice 2025-05-31
       - Example: aldo generate-invoice (uses today as the end date)
    
    2. Regenerate existing invoice:
       - If an invoice number is provided (format: number or INV-number), it will regenerate that invoice
       - This is useful for viewing past invoices that have been confirmed
       - Example: aldo generate-invoice 1000 or aldo generate-invoice INV-1000
    """
    try:
        today = datetime.now().date()
        is_invoice_number, invoice_number, parsed_date = _parse_invoice_input(invoice_or_end_date)
        
        # Handle regenerating existing invoice
        if is_invoice_number:
            confirmed_invoice = storage.get_invoice_by_number(invoice_number, config)
            if not confirmed_invoice:
                click.echo(f"Error: Invoice #{invoice_number} not found in confirmed invoices.")
                return
                
            start_date = datetime.strptime(confirmed_invoice.start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(confirmed_invoice.end_date, '%Y-%m-%d').date()
            full_invoice_number = f"{config.config['invoice']['prefix']}{invoice_number:04d}"
            
            click.echo(f"Regenerating confirmed invoice #{invoice_number}")
        
        # Handle generating new invoice    
        else:
            end_date = _ensure_date_object(parsed_date, today)
            last_invoice = storage.get_last_confirmed_invoice()
            if last_invoice:
                last_end_date = datetime.strptime(last_invoice.end_date, '%Y-%m-%d').date()
                start_date = last_end_date + timedelta(days=1)
                
                # Check for invalid date range when user specified an end date
                if invoice_or_end_date is not None and start_date > end_date:
                    click.echo(f"Error: Invalid date range. Next invoice must start from {start_date} (day after last invoice ended).")
                    click.echo(f"The specified end date {end_date} is before the required start date.")
                    click.echo(f"Please use a date on or after {start_date} as the end date.")
                    return
                
                # Only adjust end_date if no specific date was provided and start_date is in the future
                if invoice_or_end_date is None and start_date >= today:
                    end_date = start_date + timedelta(days=7)
                    
                # Check for entries
                if not storage.get_work_entries(start_date, end_date):
                    click.echo(f"No work hours recorded between {start_date} and {end_date}.")
                    return
            else:
                # No previous invoice
                start_date = storage.get_earliest_entry_date()
                if not start_date:
                    click.echo("No work hours recorded. Cannot generate invoice.")
                    return
            
            # Get invoice number
            full_invoice_number = f"{config.config['invoice']['prefix']}{storage.get_next_invoice_number()}"
            
        # Ensure dates are valid and get entries
        start_date = _ensure_date_object(start_date)
        end_date = _ensure_date_object(end_date)
        
        entries = storage.get_work_entries(start_date, end_date)
        if not entries:
            click.echo(f"No work hours recorded between {start_date} and {end_date}.")
            return
            
        # Generate the invoice
        invoice_generator = InvoiceGenerator(config, storage)
        output_path = invoice_generator.generate_invoice(full_invoice_number, start_date, end_date, entries, output)
        
        # Store unconfirmed invoice for new invoices only (not for regenerating existing ones)
        if not is_invoice_number:
            # Extract the numeric part of the invoice number
            storage.store_unconfirmed_invoice(full_invoice_number, start_date, end_date, config)
        
        # Show summary
        click.echo(f"Invoice #{full_invoice_number} generated successfully: {output_path}")
        
        # Show confirm prompt for new invoices
        if not is_invoice_number:
            numeric_part = full_invoice_number.replace(config.config['invoice']['prefix'], '')
            click.echo(f"To confirm this invoice has been sent, run: aldo confirm {numeric_part}")
            
    except Exception as e:
        click.echo(f"Error generating invoice: {str(e)}", err=True)
        click.echo(traceback.format_exc())
        sys.exit(1)

@cli.command('confirm')
@click.argument('invoice_number', required=True)
def confirm_invoice(invoice_number):
    """
    Confirm that an invoice has been sent to the client.
    
    INVOICE_NUMBER: The invoice number to confirm (e.g., 1000 or INV-1000)
    
    This command:
    1. Marks the invoice as confirmed
    2. Uses the original invoice end date as the confirmation date
    3. This end date becomes the starting point for the next automatic invoice
    
    The invoice being confirmed must match the last unconfirmed invoice.
    """
    try:
        # Format the expected invoice number for display
        prefix = config.config['invoice']['prefix']
        
        # Attempt to confirm the invoice
        success = storage.confirm_invoice(invoice_number, config)
        
        if success:
            # Get the confirmed invoice details
            confirmed_invoice = storage.get_last_confirmed_invoice()
            
            # Format for display
            full_invoice_id = f"{prefix}{int(confirmed_invoice.invoice_number):04d}"
            
            click.echo(f"Invoice #{full_invoice_id} confirmed.")
            click.echo(f"Invoice period: {confirmed_invoice.start_date} to {confirmed_invoice.end_date}")
            click.echo(f"Next invoice will start from {confirmed_invoice.end_date}.")
        else:
            click.echo(f"Error: Could not confirm invoice #{invoice_number}.")
            click.echo("Make sure the invoice number is valid and matches the unconfirmed invoice.")
            
    except Exception as e:
        click.echo(f"Error confirming invoice: {str(e)}", err=True)
        sys.exit(1)
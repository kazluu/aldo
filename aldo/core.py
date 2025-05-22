#!/usr/bin/env python3
"""
Aldo - Work Hours Tracker and Invoice Generator
A CLI application for freelancers to track their hours and generate invoices.
"""

import os
import sys
import click
from datetime import datetime, timedelta
from aldo.storage import WorkHoursStorage
from aldo.config import Config
from aldo.invoice import InvoiceGenerator

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
@click.version_option(version='1.0.0')
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
@click.argument('period', type=click.Choice(['week', 'month', 'year']))
def view_summary(period):
    """
    View summary of hours worked for the specified time period.

    PERIOD: One of: 'week', 'month', or 'year'
    """
    try:
        summary = storage.get_summary(period)
        
        # Print summary header
        click.echo(f"\n{'='*30}")
        click.echo(f"WORK SUMMARY FOR: {period.upper()}")
        click.echo(f"{'='*30}")

        click.echo("")
        if not summary:
            click.echo("No work hours recorded for this period.")
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
        
        # Check if the argument is an invoice number or a date
        is_invoice_number = False
        invoice_number = None
        
        if invoice_or_end_date is not None:
            # Try to parse as invoice number if it's a string
            if isinstance(invoice_or_end_date, str):
                try:
                    # Check if it might be a full invoice ID with prefix
                    prefix = config.config['invoice']['prefix']
                    if invoice_or_end_date.startswith(prefix):
                        invoice_number = int(invoice_or_end_date[len(prefix):])
                        is_invoice_number = True
                    else:
                        # Try to parse as integer
                        invoice_number = int(invoice_or_end_date)
                        is_invoice_number = True
                except (ValueError, TypeError):
                    # Not an invoice number, try to parse as date
                    try:
                        # Handle date aliases
                        if invoice_or_end_date == "today":
                            invoice_or_end_date = today
                        elif invoice_or_end_date == "yesterday":
                            invoice_or_end_date = today - timedelta(days=1)
                        elif invoice_or_end_date == "tomorrow":
                            invoice_or_end_date = today + timedelta(days=1)
                        elif invoice_or_end_date == "daybefore":
                            invoice_or_end_date = today - timedelta(days=2)
                        else:
                            # Handle regular date format
                            invoice_or_end_date = datetime.strptime(invoice_or_end_date, '%Y-%m-%d').date()
                    except ValueError:
                        raise click.BadParameter('Date must be in YYYY-MM-DD format or one of: today, yesterday, tomorrow, daybefore')
        
        # REGENERATE EXISTING INVOICE: invoice number provided
        if is_invoice_number:
            # Look up the confirmed invoice
            confirmed_invoice = storage.get_invoice_by_number(invoice_number, config)
            
            if not confirmed_invoice:
                click.echo(f"Error: Invoice #{invoice_number} not found in confirmed invoices.")
                return
            
            # Get the start and end dates from the confirmed invoice
            start_date = datetime.strptime(confirmed_invoice.start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(confirmed_invoice.end_date, '%Y-%m-%d').date()
            
            click.echo(f"Regenerating confirmed invoice #{invoice_number}")
            click.echo(f"Period: {start_date} to {end_date}")
            
            # Format invoice number with prefix for display
            full_invoice_number = f"{config.config['invoice']['prefix']}{invoice_number:04d}"
            
        # GENERATE NEW INVOICE: end date provided or no arguments
        else:
            # Default to today if no end date is provided
            if invoice_or_end_date is None:
                end_date = today
            else:
                # If a date object was provided, use it directly
                if hasattr(invoice_or_end_date, 'strftime'):
                    end_date = invoice_or_end_date
                else:
                    # Try to parse as date if it's a string
                    try:
                        end_date = datetime.strptime(invoice_or_end_date, '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        end_date = today
            
            # Get the last confirmed invoice to determine start date
            last_invoice = storage.get_last_confirmed_invoice()
            
            if last_invoice:
                # Start date is the day after the end date of the last invoice
                last_end_date = datetime.strptime(last_invoice.end_date, '%Y-%m-%d').date()
                start_date = last_end_date + timedelta(days=1)
                
                # For new invoices after confirmation, make sure end date is after start date
                end_date = datetime.now().date()
                
                # If the start date is today or in the future, we need an end date in the future
                if start_date >= today:
                    end_date = start_date + timedelta(days=7)  # Look ahead a week by default
                
                click.echo(f"Using day after last confirmed invoice as start date: {start_date}")
                click.echo(f"End date: {end_date}")
                
                # Pre-check if we have entries in this period
                test_entries = storage.get_work_entries(start_date, end_date)
                if not test_entries:
                    click.echo(f"No work hours recorded between {start_date} and {end_date}.")
                    click.echo("Cannot generate an invoice for this period.")
                    return
            else:
                # No previous invoice, start from earliest entry or today
                earliest_date = storage.get_earliest_entry_date()
                if not earliest_date:
                    click.echo("No work hours recorded. Cannot generate invoice.")
                    return
                start_date = earliest_date
                click.echo("No previous confirmed invoice. Using earliest entry date as start date.")
            
            click.echo(f"Generating new invoice for period: {start_date} to {end_date}")
            
            # Get next invoice number from config WITHOUT incrementing
            # We only increment when an invoice is confirmed, not when generating
            invoice_number = config.get_next_invoice_number(increment=False)
            # Extract numeric part for display
            numeric_invoice_number = int(invoice_number.replace(config.config['invoice']['prefix'], ''))
            full_invoice_number = invoice_number
        
        # Make sure we have proper date objects before continuing
        if hasattr(start_date, 'strftime'):
            start_date_str = start_date.strftime('%Y-%m-%d')
        else:
            # Try to convert to date if it's a string
            try:
                if isinstance(start_date, str):
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                    start_date_str = start_date.strftime('%Y-%m-%d')
                else:
                    # Default to earliest entry date if we can't parse
                    start_date = storage.get_earliest_entry_date() or datetime.now().date()
                    start_date_str = start_date.strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                start_date = datetime.now().date()
                start_date_str = start_date.strftime('%Y-%m-%d')
        
        if hasattr(end_date, 'strftime'):
            end_date_str = end_date.strftime('%Y-%m-%d')
        else:
            # Try to convert to date if it's a string
            try:
                if isinstance(end_date, str):
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                    end_date_str = end_date.strftime('%Y-%m-%d')
                else:
                    # Default to today if we can't parse
                    end_date = datetime.now().date()
                    end_date_str = end_date.strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                end_date = datetime.now().date()
                end_date_str = end_date.strftime('%Y-%m-%d')
        
        # Now we can safely compare the dates
        if start_date_str > end_date_str:
            click.echo("Warning: Start date is after end date. Using today as end date.")
            end_date = datetime.now().date()
        
        # Get work entries for the date range
        entries = storage.get_work_entries(start_date, end_date)
        
        if not entries:
            click.echo("No work hours recorded for this period. Cannot generate invoice.")
            return
        
        # Generate invoice
        invoice_generator = InvoiceGenerator(config, storage)
        output_path = invoice_generator.generate_invoice(start_date, end_date, entries, output)
        
        # Display invoice information
        click.echo(f"Invoice #{full_invoice_number} generated successfully: {output_path}")
        click.echo(f"Time period: {start_date} to {end_date}")
        click.echo(f"Total hours: {sum(entry['hours'] for entry in entries):.2f}")
        
        # Only show the confirm message for new invoices, not regenerated ones
        if not is_invoice_number:
            # Extract just the number part for the command example
            numeric_part = full_invoice_number.replace(config.config['invoice']['prefix'], '')
            click.echo(f"To confirm this invoice has been sent, run: aldo confirm {numeric_part}")
        
    except Exception as e:
        click.echo(f"Error generating invoice: {str(e)}", err=True)
        sys.exit(1)

@cli.command('confirm')
@click.argument('invoice_number', required=True)
@click.argument('confirmation_date', callback=validate_date, required=False)
def confirm_invoice(invoice_number, confirmation_date):
    """
    Confirm that an invoice has been sent to the client.
    
    INVOICE_NUMBER: The invoice number to confirm (e.g., 1000 or INV-1000)
    CONFIRMATION_DATE: Optional date to use as the confirmation date (defaults to today)
    
    This command:
    1. Marks the invoice as confirmed
    2. Records the confirmation date (today if not specified)
    3. This date becomes the starting point for the next automatic invoice
    
    The invoice being confirmed must be the successor of the last confirmed invoice.
    """
    try:
        # If confirmation_date is not provided, use today's date
        if confirmation_date is None:
            confirmation_date = datetime.now().date()
        
        # Format the expected invoice number for display
        prefix = config.config['invoice']['prefix']
        
        # Attempt to confirm with the specified date
        success = storage.confirm_invoice(invoice_number, config, confirmation_date)
        
        if success:
            # Get the confirmed invoice details
            invoice_id = str(invoice_number).replace(prefix, '')
            
            # Format for display
            full_invoice_id = f"{prefix}{int(invoice_id):04d}"
            confirmation_date_str = confirmation_date.strftime('%Y-%m-%d')
            
            click.echo(f"Invoice #{full_invoice_id} confirmed on {confirmation_date_str}.")
            click.echo(f"Next invoice will start from {confirmation_date_str}.")
        else:
            click.echo(f"Error: Could not confirm invoice #{invoice_number}.")
            click.echo("Make sure the invoice number is valid and follows the last confirmed invoice.")
            
    except Exception as e:
        click.echo(f"Error confirming invoice: {str(e)}", err=True)
        sys.exit(1)
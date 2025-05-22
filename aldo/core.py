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
def log_work(date, hours):
    """
    Record work hours for a specific date.

    DATE: Date in YYYY-MM-DD format or an alias (today, yesterday, tomorrow, daybefore)
    HOURS: Number of hours worked (positive number)
    
    If a log entry already exists for the specified date, it will be replaced.
    """
    try:
        storage.log_work(date, hours)
        date_str = date.strftime('%Y-%m-%d')
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
@click.argument('start_date', callback=validate_date, required=False)
@click.argument('end_date', callback=validate_date, required=False)
@click.option('--output', '-o', default='invoice.pdf', help='Output PDF filename')
def generate_invoice(start_date, end_date, output):
    """
    Generate a PDF invoice for the specified date range.

    Supports two modes:
    
    1. Automatic mode (no arguments):
       - Generates invoice for all work since the last confirmed invoice
       - Example: aldo generate-invoice
    
    2. Manual mode (with date arguments):
       - START_DATE: Start date in YYYY-MM-DD format
       - END_DATE: Optional end date in YYYY-MM-DD format (defaults to today)
       - Example: aldo generate-invoice 2025-05-01 2025-05-31
    """
    try:
        today = datetime.now().date()
        
        # AUTOMATIC MODE: No dates provided
        if start_date is None:
            last_confirmation_date = config.get_last_confirmation_date()
            
            if last_confirmation_date:
                # Convert string date to date object
                start_date = datetime.strptime(last_confirmation_date, '%Y-%m-%d').date()
                click.echo(f"Using last confirmation date ({last_confirmation_date}) as start date.")
            else:
                # If no previous confirmation, use all entries
                click.echo("No previous invoice confirmation found. Including all work entries.")
                # Get the earliest work entry date
                earliest_date = storage.get_earliest_entry_date()
                if not earliest_date:
                    click.echo("No work hours recorded. Cannot generate invoice.")
                    return
                start_date = earliest_date
                
            end_date = today
            click.echo(f"Generating invoice for period: {start_date} to {end_date}")
        
        # MANUAL MODE: Start date provided but no end date
        elif end_date is None:
            end_date = today
            click.echo(f"No end date provided. Using today ({end_date}) as end date.")
        
        # Validate date range
        if start_date > end_date:
            raise click.BadParameter("Start date must be before end date")
        
        # Get work entries for the date range
        entries = storage.get_work_entries(start_date, end_date)
        
        if not entries:
            click.echo("No work hours recorded for this period. Cannot generate invoice.")
            return
        
        # Generate invoice
        invoice_generator = InvoiceGenerator(config, storage)
        output_path = invoice_generator.generate_invoice(start_date, end_date, entries, output)
        
        # Display invoice information
        invoice_number = config.config['invoice']['next_number'] - 10
        prefix = config.config['invoice']['prefix']
        full_invoice_number = f"{prefix}{invoice_number:04d}"
        
        click.echo(f"Invoice #{full_invoice_number} generated successfully: {output_path}")
        click.echo(f"Time period: {start_date} to {end_date}")
        click.echo(f"Total hours: {sum(entry['hours'] for entry in entries):.2f}")
        click.echo(f"To set the end date for this billing period, run: aldo set-end-date {invoice_number}")
        
    except Exception as e:
        click.echo(f"Error generating invoice: {str(e)}", err=True)
        sys.exit(1)

@cli.command('set-end-date')
@click.argument('invoice_number', required=True)
@click.argument('confirmation_date', callback=validate_date, required=False)
def set_end_date(invoice_number, confirmation_date):
    """
    Set the end date for the current billing period.
    
    INVOICE_NUMBER: The invoice number to confirm (e.g., 1000 or INV-1000)
    CONFIRMATION_DATE: Optional date to use as the confirmation date (defaults to today)
    
    This command:
    1. Marks the invoice as confirmed
    2. Records the confirmation date (today if not specified)
    3. This date becomes the starting point for the next automatic invoice
    
    Only the latest generated invoice can be confirmed.
    """
    try:
        # If confirmation_date is not provided, use today's date
        if confirmation_date is None:
            confirmation_date = datetime.now().date()
        
        expected_number = config.config['invoice']['next_number'] - 10
        prefix = config.config['invoice']['prefix']
        expected_id = f"{prefix}{expected_number:04d}"
        
        # Attempt to confirm with the specified date
        success = config.set_end_date(invoice_number, confirmation_date)
        
        if success:
            confirmation_date_str = confirmation_date.strftime('%Y-%m-%d')
            click.echo(f"Invoice #{expected_id} end date set to {confirmation_date_str}.")
            click.echo(f"Next invoice will start from {confirmation_date_str}.")
            click.echo(f"Next invoice number will be #{prefix}{config.config['invoice']['next_number']:04d}.")
        else:
            click.echo(f"Error: Only the latest invoice (#{expected_id}) can have its end date set.")
            
    except Exception as e:
        click.echo(f"Error setting end date: {str(e)}", err=True)
        sys.exit(1)
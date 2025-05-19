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
@click.argument('period', type=click.Choice(['day', 'month', 'year']))
def view_summary(period):
    """
    View summary of hours worked for the specified time period.

    PERIOD: One of: 'day', 'month', or 'year'
    """
    try:
        summary = storage.get_summary(period)
        
        # Print summary header
        click.echo(f"\n{'='*60}")
        click.echo(f"WORK SUMMARY FOR: {period.upper()}")
        click.echo(f"{'='*60}")
        
        if not summary:
            click.echo("No work hours recorded for this period.")
            return
        
        # Print details
        total_hours = 0
        for date_str, entries in summary.items():
            day_hours = sum(entry['hours'] for entry in entries)
            total_hours += day_hours
            click.echo(f"\n{date_str} - {day_hours:.2f} hours:")
            for entry in entries:
                click.echo(f"  • {entry['hours']:.2f} hours")
        
        # Print total
        click.echo(f"\n{'-'*60}")
        click.echo(f"TOTAL HOURS: {total_hours:.2f}")
        click.echo(f"{'='*60}\n")
        
    except Exception as e:
        click.echo(f"Error getting summary: {str(e)}", err=True)
        sys.exit(1)

@cli.command('generate-invoice')
@click.argument('start_date', callback=validate_date)
@click.argument('end_date', callback=validate_date)
@click.option('--output', '-o', default='invoice.pdf', help='Output PDF filename')
def generate_invoice(start_date, end_date, output):
    """
    Generate a PDF invoice for the specified date range.

    START_DATE: Start date in YYYY-MM-DD format
    END_DATE: End date in YYYY-MM-DD format
    """
    try:
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
        
        click.echo(f"Invoice generated successfully: {output_path}")
        
    except Exception as e:
        click.echo(f"Error generating invoice: {str(e)}", err=True)
        sys.exit(1)
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from datetime import datetime
import json
from storage import WorkHoursStorage
from config import Config
from invoice import InvoiceGenerator

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Initialize global config and storage
config = Config()
storage = WorkHoursStorage()

# Ensure config and data directories exist
config.ensure_config_exists()
storage.ensure_storage_exists()

@app.route('/')
def index():
    """Home page with all the main options"""
    return render_template('index.html')

@app.route('/log', methods=['GET', 'POST'])
def log_work():
    """Log work hours via web interface"""
    if request.method == 'POST':
        try:
            date_str = request.form.get('date')
            hours_str = request.form.get('hours')
            description = request.form.get('description')
            
            # Validate input
            if not date_str:
                flash('Date is required', 'error')
                return redirect(url_for('log_work'))
            
            if not hours_str:
                flash('Hours are required', 'error')
                return redirect(url_for('log_work'))
                
            hours = float(hours_str)
            if hours <= 0:
                flash('Hours must be a positive number', 'error')
                return redirect(url_for('log_work'))
            
            # Description is now optional, so we don't need this check
            if description is None:
                description = ""
            
            # Convert date string to date object
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Log work
            storage.log_work(date, hours, description)
            flash(f'Successfully logged {hours} hours on {date_str} for: {description}', 'success')
            return redirect(url_for('log_work'))
        
        except ValueError as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('log_work'))
    
    # Default to today's date for the form
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('log_work.html', today=today)

@app.route('/summary')
def summary():
    """View work summary for day, month, or year"""
    period = request.args.get('period', 'day')
    if period not in ['day', 'month', 'year']:
        period = 'day'
    
    summary_data = storage.get_summary(period)
    
    # Calculate total hours
    total_hours = 0
    for date_str, entries in summary_data.items():
        for entry in entries:
            total_hours += entry['hours']
    
    return render_template('summary.html', 
                          period=period, 
                          summary=summary_data, 
                          total_hours=total_hours)

@app.route('/invoice', methods=['GET', 'POST'])
def invoice():
    """Generate invoice form and processing"""
    if request.method == 'POST':
        try:
            start_date_str = request.form.get('start_date')
            end_date_str = request.form.get('end_date')
            
            # Validate input
            if not start_date_str or not end_date_str:
                flash('Start and end dates are required', 'error')
                return redirect(url_for('invoice'))
            
            # Convert date strings to date objects
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            # Validate date range
            if start_date > end_date:
                flash('Start date must be before end date', 'error')
                return redirect(url_for('invoice'))
            
            # Get work entries for the date range
            entries = storage.get_work_entries(start_date, end_date)
            
            if not entries:
                flash('No work hours recorded for this period. Cannot generate invoice.', 'error')
                return redirect(url_for('invoice'))
            
            # Generate invoice
            output_filename = f"invoice_{start_date_str}_to_{end_date_str}.pdf"
            invoice_generator = InvoiceGenerator(config, storage)
            output_path = invoice_generator.generate_invoice(start_date, end_date, entries, output_filename)
            
            # Stream the PDF file as response
            return send_file(
                output_path, 
                as_attachment=True,
                download_name=output_filename,
                mimetype="application/pdf"
            )
        
        except ValueError as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('invoice'))
    
    # Default to current month for the form
    today = datetime.now()
    start_date = f"{today.year}-{today.month:02d}-01"
    last_day = 30  # Simplified approach
    if today.month in [1, 3, 5, 7, 8, 10, 12]:
        last_day = 31
    elif today.month == 2:
        if today.year % 4 == 0 and (today.year % 100 != 0 or today.year % 400 == 0):
            last_day = 29
        else:
            last_day = 28
    end_date = f"{today.year}-{today.month:02d}-{last_day}"
    
    return render_template('invoice.html', start_date=start_date, end_date=end_date)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """View and edit configuration settings"""
    if request.method == 'POST':
        try:
            # Update business information
            business = {
                "name": request.form.get('business_name'),
                "address": request.form.get('business_address'),
                "city": request.form.get('business_city'),
                "state": request.form.get('business_state'),
                "zip": request.form.get('business_zip'),
                "country": request.form.get('business_country'),
                "phone": request.form.get('business_phone'),
                "email": request.form.get('business_email'),
                "website": request.form.get('business_website'),
                "tax_id": request.form.get('business_tax_id')
            }
            
            # Update client information
            client = {
                "name": request.form.get('client_name'),
                "address": request.form.get('client_address'),
                "city": request.form.get('client_city'),
                "state": request.form.get('client_state'),
                "zip": request.form.get('client_zip'),
                "country": request.form.get('client_country'),
                "contact_person": request.form.get('client_contact_person'),
                "email": request.form.get('client_email'),
                "phone": request.form.get('client_phone')
            }
            
            # Update payment information
            hourly_rate_str = request.form.get('payment_hourly_rate', '0')
            try:
                hourly_rate = float(hourly_rate_str)
            except ValueError:
                hourly_rate = 0.0
                
            payment = {
                "bank_name": request.form.get('payment_bank_name', ''),
                "account_name": request.form.get('payment_account_name', ''),
                "account_number": request.form.get('payment_account_number', ''),
                "routing_number": request.form.get('payment_routing_number', ''),
                "iban": request.form.get('payment_iban', ''),
                "swift": request.form.get('payment_swift', ''),
                "payment_terms": request.form.get('payment_terms', ''),
                "currency": request.form.get('payment_currency', 'USD'),
                "hourly_rate": hourly_rate
            }
            
            # Update invoice settings
            invoice_prefix = request.form.get('invoice_prefix', '')
            invoice_next_number_str = request.form.get('invoice_next_number', '1')
            invoice_next_number = int(invoice_next_number_str) if invoice_next_number_str.isdigit() else 1
            
            invoice_settings = {
                "prefix": invoice_prefix,
                "next_number": invoice_next_number,
                "footer_text": request.form.get('invoice_footer_text', '')
            }
            
            # Create new config dictionary
            new_config = {
                "business": business,
                "client": client,
                "payment": payment,
                "invoice": invoice_settings
            }
            
            # Update configuration
            config.update_config(new_config)
            flash('Settings updated successfully', 'success')
            return redirect(url_for('settings'))
        
        except Exception as e:
            flash(f'Error updating settings: {str(e)}', 'error')
            return redirect(url_for('settings'))
    
    # Get current config for the form
    current_config = config.get_config()
    return render_template('settings.html', config=current_config)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
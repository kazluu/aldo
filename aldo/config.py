"""
Configuration management for Aldo
"""

import os
import json
from pathlib import Path
import appdirs

DEFAULT_CONFIG = {
    "company": {
        "name": "Your Company Name"
    },
    "payment": {
        "hourly_rate": 50.00
    },
    "invoice": {
        "prefix": "INV-",
        "next_number": 1000,
        "footer_text": "Thank you for your business!",
        "last_confirmed_number": None,
        "last_confirmation_date": None
    }
}

class Config:
    """Manages configuration for the Aldo application"""
    
    def __init__(self):
        """Initialize configuration with default values and paths"""
        # Use appdirs to get standard config locations
        self.config_dir = Path(appdirs.user_config_dir("aldo", "aldo"))
        self.config_file = self.config_dir / 'config.json'
        self.config = DEFAULT_CONFIG.copy()
        
        # Load config if it exists
        if self.config_file.exists():
            self.load_config()
    
    def ensure_config_exists(self):
        """Ensure config directory and file exist"""
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.config_file.exists():
            # Create default config
            self.save_config()
            print(f"Created default configuration file at {self.config_file}")
            print("Please update the configuration with your information.")
    
    def load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                loaded_config = json.load(f)
                # Update config with loaded values, keeping defaults for missing keys
                self._update_nested_dict(self.config, loaded_config)
        except Exception as e:
            raise Exception(f"Error loading configuration: {str(e)}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            raise Exception(f"Error saving configuration: {str(e)}")
    
    def get_config(self):
        """Get the current configuration"""
        return self.config
    
    def update_config(self, new_config):
        """Update configuration with new values"""
        self._update_nested_dict(self.config, new_config)
        self.save_config()
    
    def get_next_invoice_number(self):
        """Get and increment the next invoice number"""
        current = self.config['invoice']['next_number']
        # Increment by 10 instead of 1
        self.config['invoice']['next_number'] += 10
        self.save_config()
        return f"{self.config['invoice']['prefix']}{current:04d}"
        
    def get_last_confirmation_date(self):
        """Get the date of the last confirmed invoice"""
        return self.config['invoice'].get('last_confirmation_date')
        
    def get_last_confirmed_number(self):
        """Get the number of the last confirmed invoice"""
        return self.config['invoice'].get('last_confirmed_number')
        
    def set_end_date(self, invoice_number, confirmation_date=None):
        """
        Set the end date for an invoice's billing period
        
        Args:
            invoice_number: The invoice number (without prefix)
            confirmation_date: Optional date to use as the confirmation date (defaults to today)
        
        Returns:
            bool: True if setting the end date was successful, False otherwise
        """
        from datetime import datetime
        
        # Extract the numeric part if the full invoice ID was provided
        prefix = self.config['invoice']['prefix']
        if isinstance(invoice_number, str) and invoice_number.startswith(prefix):
            invoice_number = int(invoice_number[len(prefix):])
        else:
            try:
                invoice_number = int(invoice_number)
            except (ValueError, TypeError):
                return False
        
        # Check if this is the expected invoice number
        expected_number = self.config['invoice']['next_number'] - 10
        if invoice_number != expected_number:
            return False
        
        # If confirmation_date is not provided, use today's date
        if confirmation_date is None:
            confirmation_date_str = datetime.now().strftime('%Y-%m-%d')
        else:
            # Convert date object to string
            confirmation_date_str = confirmation_date.strftime('%Y-%m-%d')
        
        # Update end date tracking
        self.config['invoice']['last_confirmed_number'] = invoice_number
        self.config['invoice']['last_confirmation_date'] = confirmation_date_str
        self.save_config()
        
        return True
    
    def _update_nested_dict(self, d, u):
        """Recursively update nested dictionary"""
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._update_nested_dict(d[k], v)
            else:
                d[k] = v
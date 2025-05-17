"""
Configuration management for Aldo
"""

import os
import json
from pathlib import Path

DEFAULT_CONFIG = {
    "business": {
        "name": "Your Business Name",
        "address": "Your Business Address",
        "city": "City",
        "state": "State",
        "zip": "Zip Code",
        "country": "Country",
        "phone": "Phone Number",
        "email": "your.email@example.com",
        "website": "www.yourbusiness.com",
        "tax_id": "Your Tax ID"
    },
    "client": {
        "name": "Client Company Name",
        "address": "Client Address",
        "city": "Client City",
        "state": "Client State",
        "zip": "Client Zip Code",
        "country": "Client Country",
        "contact_person": "Client Contact Name",
        "email": "client.email@example.com",
        "phone": "Client Phone Number"
    },
    "payment": {
        "bank_name": "Your Bank Name",
        "account_name": "Your Account Name",
        "account_number": "Your Account Number",
        "routing_number": "Your Routing Number",
        "iban": "Your IBAN",
        "swift": "Your SWIFT/BIC",
        "payment_terms": "Due within 30 days",
        "currency": "USD",
        "hourly_rate": 50.00
    },
    "invoice": {
        "prefix": "INV-",
        "next_number": 1,
        "footer_text": "Thank you for your business!"
    }
}

class Config:
    """Manages configuration for the Aldo application"""
    
    def __init__(self):
        """Initialize configuration with default values and paths"""
        self.config_dir = Path.home() / '.aldo'
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
        self.config['invoice']['next_number'] += 1
        self.save_config()
        return f"{self.config['invoice']['prefix']}{current:04d}"
    
    def _update_nested_dict(self, d, u):
        """Recursively update nested dictionary"""
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._update_nested_dict(d[k], v)
            else:
                d[k] = v

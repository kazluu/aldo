"""
Tests for Aldo - Work Hours Tracker and Invoice Generator
"""

import os
import json
import tempfile
from pathlib import Path
from datetime import datetime, date
from unittest import TestCase, mock

# Import modules to test
from storage import WorkHoursStorage
from config import Config
from invoice import InvoiceGenerator

class TestWorkHoursStorage(TestCase):
    """Test the WorkHoursStorage class"""
    
    def setUp(self):
        """Set up for tests"""
        # Create a temporary directory for test data
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_dir_path = Path(self.test_dir.name)
        
        # Path to test data file
        self.test_data_dir = self.test_dir_path / 'data'
        self.test_data_dir.mkdir(exist_ok=True)
        self.test_data_file = self.test_data_dir / 'work_hours.json'
        
        # Mock the storage paths
        self.patcher = mock.patch.object(WorkHoursStorage, '__init__', return_value=None)
        self.mock_init = self.patcher.start()
        
        # Create test instance
        self.storage = WorkHoursStorage()
        self.storage.data_dir = self.test_data_dir
        self.storage.data_file = self.test_data_file
        self.storage.data = {"entries": []}
    
    def tearDown(self):
        """Clean up after tests"""
        self.patcher.stop()
        self.test_dir.cleanup()
    
    def test_ensure_storage_exists(self):
        """Test ensure_storage_exists creates necessary directories/files"""
        # Ensure directory and file don't exist yet
        if self.test_data_file.exists():
            self.test_data_file.unlink()
        if self.test_data_dir.exists():
            self.test_data_dir.rmdir()
        
        # Call ensure_storage_exists
        self.storage.ensure_storage_exists()
        
        # Check directory and file exist
        self.assertTrue(self.test_data_dir.exists())
        self.assertTrue(self.test_data_file.exists())
    
    def test_log_work(self):
        """Test logging work hours"""
        # Log some work
        test_date = date(2023, 5, 15)
        test_hours = 6
        test_description = "Test work"
        
        entry = self.storage.log_work(test_date, test_hours, test_description)
        
        # Check entry was added correctly
        self.assertEqual(len(self.storage.data["entries"]), 1)
        self.assertEqual(entry["date"], "2023-05-15")
        self.assertEqual(entry["hours"], 6)
        self.assertEqual(entry["description"], "Test work")
    
    def test_get_work_entries(self):
        """Test getting work entries for a date range"""
        # Add some test entries
        entries = [
            {"date": "2023-05-01", "hours": 4, "description": "Work 1", "timestamp": "2023-05-01T09:00:00"},
            {"date": "2023-05-15", "hours": 6, "description": "Work 2", "timestamp": "2023-05-15T09:00:00"},
            {"date": "2023-05-30", "hours": 8, "description": "Work 3", "timestamp": "2023-05-30T09:00:00"},
            {"date": "2023-06-15", "hours": 7, "description": "Work 4", "timestamp": "2023-06-15T09:00:00"},
        ]
        self.storage.data["entries"] = entries
        
        # Test date range filtering
        result = self.storage.get_work_entries(date(2023, 5, 10), date(2023, 6, 10))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["date"], "2023-05-15")
        self.assertEqual(result[1]["date"], "2023-05-30")
    
    def test_get_summary(self):
        """Test getting summary for different periods"""
        # Mock today's date
        today = date(2023, 5, 15)
        
        # Add test entries
        entries = [
            {"date": "2023-05-15", "hours": 6, "description": "Work 1", "timestamp": "2023-05-15T09:00:00"},
            {"date": "2023-05-15", "hours": 2, "description": "Work 2", "timestamp": "2023-05-15T14:00:00"},
            {"date": "2023-05-14", "hours": 4, "description": "Work 3", "timestamp": "2023-05-14T09:00:00"},
            {"date": "2023-04-15", "hours": 7, "description": "Work 4", "timestamp": "2023-04-15T09:00:00"},
        ]
        self.storage.data["entries"] = entries
        
        # Test day summary
        with mock.patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 5, 15, 18, 0, 0)
            
            day_summary = self.storage.get_summary('day')
            self.assertIn("2023-05-15", day_summary)
            self.assertEqual(len(day_summary["2023-05-15"]), 2)
            self.assertEqual(day_summary["2023-05-15"][0]["hours"], 6)
            self.assertEqual(day_summary["2023-05-15"][1]["hours"], 2)
    
    def test_get_total_hours(self):
        """Test calculating total hours"""
        entries = [
            {"date": "2023-05-15", "hours": 6, "description": "Work 1"},
            {"date": "2023-05-16", "hours": 2.5, "description": "Work 2"},
            {"date": "2023-05-17", "hours": 4, "description": "Work 3"},
        ]
        
        total = self.storage.get_total_hours(entries)
        self.assertEqual(total, 12.5)


class TestConfig(TestCase):
    """Test the Config class"""
    
    def setUp(self):
        """Set up for tests"""
        # Create a temporary directory for test config
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_dir_path = Path(self.test_dir.name)
        
        # Path to test config file
        self.test_config_dir = self.test_dir_path / '.aldo'
        self.test_config_dir.mkdir(exist_ok=True)
        self.test_config_file = self.test_config_dir / 'config.json'
        
        # Mock the config paths
        self.patcher = mock.patch.object(Config, '__init__', return_value=None)
        self.mock_init = self.patcher.start()
        
        # Create test instance
        self.config = Config()
        self.config.config_dir = self.test_config_dir
        self.config.config_file = self.test_config_file
        self.config.config = {
            "business": {"name": "Test Business"},
            "client": {"name": "Test Client"},
            "payment": {"hourly_rate": 50},
            "invoice": {"prefix": "INV-", "next_number": 1}
        }
    
    def tearDown(self):
        """Clean up after tests"""
        self.patcher.stop()
        self.test_dir.cleanup()
    
    def test_ensure_config_exists(self):
        """Test ensure_config_exists creates necessary files"""
        # Ensure file doesn't exist yet
        if self.test_config_file.exists():
            self.test_config_file.unlink()
        
        # Call ensure_config_exists
        self.config.ensure_config_exists()
        
        # Check file exists
        self.assertTrue(self.test_config_file.exists())
    
    def test_get_next_invoice_number(self):
        """Test getting and incrementing invoice numbers"""
        # Initial number
        initial_number = self.config.get_next_invoice_number()
        self.assertEqual(initial_number, "INV-0001")
        
        # Increment check
        next_number = self.config.get_next_invoice_number()
        self.assertEqual(next_number, "INV-0002")
        self.assertEqual(self.config.config["invoice"]["next_number"], 3)

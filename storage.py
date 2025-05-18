"""
Storage management for Aldo - handles persisting and retrieving work hour data
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta

class WorkHoursStorage:
    """Manages the storage of work hours data"""
    
    def __init__(self):
        """Initialize the storage with default paths"""
        self.data_dir = Path.home() / '.aldo' / 'data'
        self.data_file = self.data_dir / 'work_hours.json'
        self.data = {"entries": []}
        
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
                self.data = json.load(f)
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")
    
    def save_data(self):
        """Save data to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            raise Exception(f"Error saving data: {str(e)}")
    
    def log_work(self, date, hours, description=""):
        """Log work hours for a specific date"""
        # Convert date to string for JSON storage
        date_str = date.strftime('%Y-%m-%d')
        
        # Check if there's an existing entry for this date
        # If so, we'll remove it before adding the new one
        existing_entries = [
            i for i, entry in enumerate(self.data["entries"])
            if entry["date"] == date_str
        ]
        
        # If entry exists for this date, remove it and notify
        if existing_entries:
            for index in sorted(existing_entries, reverse=True):
                old_entry = self.data["entries"][index]
                del self.data["entries"][index]
                print(f"Replaced previous entry: {old_entry['hours']} hours on {date_str}")
        
        # Create new entry
        entry = {
            "date": date_str,
            "hours": hours,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to entries and save
        self.data["entries"].append(entry)
        self.save_data()
        return entry
    
    def get_work_entries(self, start_date, end_date):
        """Get work entries within a date range"""
        # Convert dates to strings for comparison
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        # Filter entries by date range
        filtered_entries = [
            entry for entry in self.data["entries"]
            if start_str <= entry["date"] <= end_str
        ]
        
        # Sort by date
        return sorted(filtered_entries, key=lambda x: x["date"])
    
    def get_summary(self, period):
        """Get summary of work hours for the specified period"""
        today = datetime.now().date()
        
        # Determine date range based on period
        if period == 'day':
            start_date = today
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

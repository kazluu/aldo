# Aldo - Work Hours Tracker and Invoice Generator

Aldo is a command-line interface (CLI) application designed for freelancers to track their work hours and generate professional PDF invoices. The name "Aldo" is inspired by "Aldo the Apache", representing reliability and precision in tracking your work.

## Features

- **Log Work Hours**: Record the number of hours worked on a specific date with a description of what was worked on.
- **View Summary**: Display hours worked for a specified time period (day, month, or year).
- **Generate Invoice**: Create a PDF invoice for a specified date range with all necessary business and client details.

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd aldo
   ```

2. Install the required dependencies:
   ```
   pip install click reportlab
   ```

3. Make the CLI executable:
   ```
   chmod +x aldo_cli.py
   ```

4. Optionally, create a symlink to use `aldo` from anywhere:
   ```
   ln -s $(pwd)/aldo_cli.py /usr/local/bin/aldo
   ```

## Usage

### First-time setup

When you run Aldo for the first time, it will create a default configuration file at `~/.aldo/config.json`. You should edit this file to add your business information, client details, payment information, and hourly rate.

### Log Work Hours


# Aldo Arch Linux Package - Quick Start Guide

This guide provides simple steps to build and install the Aldo CLI application on Arch Linux.

## Building and Installing

### Option 1: Using the Provided Script

```bash
# Clone the repository
git clone https://github.com/yourusername/aldo.git
cd aldo

# Run the build and installation script
./local_build_test.sh
```

When prompted, enter 'y' to install the package.

### Option 2: Manual Installation

```bash
# Install from AUR (once published)
yay -S aldo

# Or using another AUR helper
paru -S aldo
```

## Basic Usage

### Logging Work Hours

```bash
# Log hours for today
aldo log today 4.5

# Log hours for a specific date
aldo log 2025-05-15 6

# Log hours for yesterday
aldo log yesterday 3.5
```

### Viewing Work Summary

```bash
# View summary for current day
aldo summary day

# View summary for current month
aldo summary month

# View summary for current year
aldo summary year
```

### Generating Invoices

```bash
# Generate an invoice for the current month
aldo generate-invoice 2025-05-01 2025-05-31

# Save to a specific filename
aldo generate-invoice 2025-05-01 2025-05-31 --output may_invoice.pdf
```

## Configuration

The app stores configuration in standard locations:

- **Configuration file**: `~/.config/aldo/config.json`
- **Data file**: `~/.local/share/aldo/work_hours.json`

You can edit the configuration file to change:
- Your company name
- Hourly rate
- Invoice numbering

## Troubleshooting

If you encounter any issues:

1. Check that all dependencies are installed:
   ```bash
   pacman -Q python-click python-reportlab python-appdirs
   ```

2. Verify configuration files exist:
   ```bash
   ls -la ~/.config/aldo/
   ls -la ~/.local/share/aldo/
   ```

3. For detailed logs, run with Python's verbose mode:
   ```bash
   python -v $(which aldo) --help
   ```

## Getting Help

For more information, run:
```bash
aldo --help
aldo <command> --help
```
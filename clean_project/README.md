# Aldo - Work Hours Tracker and Invoice Generator

Aldo is a command-line application for freelancers to track their work hours and generate professional PDF invoices.

## Features

- Simple CLI interface for logging work hours
- Support for date aliases: today, yesterday, tomorrow, daybefore
- Summary views by day, month, or year
- Professional PDF invoice generation
- Configurable company name and hourly rate
- Automatic invoice numbering (increments by 10)

## Installation

### From AUR (Arch User Repository)

Once published, you can install Aldo using an AUR helper like `yay`:

```bash
yay -S aldo
```

### Manual Installation from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aldo.git
   cd aldo
   ```

2. Install the package:
   ```bash
   pip install .
   ```

## Usage

### Log Work Hours

```bash
# Log 5 hours for a specific date
aldo log 2025-05-15 5

# Log 4 hours for today
aldo log today 4

# Log 3 hours for yesterday
aldo log yesterday 3

# Log 2 hours for the day before yesterday
aldo log daybefore 2

# Log 6 hours for tomorrow
aldo log tomorrow 6
```

When you log hours for a date that already has an entry, the previous entry will be replaced.

### View Work Summary

```bash
# View summary for today
aldo summary day

# View summary for current month
aldo summary month

# View summary for current year
aldo summary year
```

### Generate Invoice

```bash
# Generate invoice for a date range
aldo generate-invoice 2025-05-01 2025-05-31

# Specify custom output filename
aldo generate-invoice 2025-05-01 2025-05-31 --output may_invoice.pdf
```

## Configuration

Aldo stores its configuration in standard system locations:

- **Config file**: `~/.config/aldo/config.json` (or equivalent for your platform)
- **Data file**: `~/.local/share/aldo/work_hours.json` (or equivalent for your platform)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
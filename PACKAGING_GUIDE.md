# Packaging Guide for Aldo CLI Application

This guide explains the steps taken to prepare the Aldo CLI application for Arch Linux packaging and the AUR (Arch User Repository).

## Package Structure

We've organized the Aldo application following Python packaging best practices:

```
aldo/
├── aldo/
│   ├── __init__.py      # Package initialization, version info
│   ├── cli.py           # Entry point for the command-line tool
│   ├── config.py        # Configuration management
│   ├── core.py          # Main application logic
│   ├── invoice.py       # Invoice generation
│   └── storage.py       # Data storage and retrieval
├── .SRCINFO             # AUR metadata
├── AUR_SUBMISSION.md    # Guide for submitting to AUR
├── LICENSE              # MIT license
├── local_build_test.sh  # Script for testing installation
├── PKGBUILD             # Arch Linux build definition
├── pyproject.toml       # Python package metadata
├── README.md            # Project documentation
└── setup.py             # Setup script (minimal, relies on pyproject.toml)
```

## Key Improvements Over the Original Code

1. **Proper Python Package Structure**: 
   - Organized code into modules with clear separation of concerns
   - Added proper package initialization

2. **Standard System Locations**:
   - Using `appdirs` to store configuration and data files in standard locations
   - Config files will be placed in `~/.config/aldo/` (or equivalent)
   - Data files will be placed in `~/.local/share/aldo/` (or equivalent)

3. **Command-line Accessibility**:
   - The application can be invoked as `aldo` instead of `python aldo_cli.py`
   - Entry point defined in pyproject.toml: `aldo = "aldo.cli:main"`

4. **Arch Linux Integration**:
   - Created PKGBUILD file with all necessary dependencies
   - Defined proper installation paths following Arch conventions
   - Added metadata for the Arch User Repository

## Dependencies

We've defined the following dependencies for the application:

- **Python Packages**:
  - click (for CLI interface)
  - reportlab (for PDF generation)
  - appdirs (for proper file locations)

- **Arch Build Dependencies**:
  - python-build
  - python-installer
  - python-wheel
  - python-setuptools

## Building and Testing

1. **To build the package locally**:
   ```bash
   cd aldo
   ./local_build_test.sh
   ```

2. **Manual installation**:
   ```bash
   cd aldo
   pip install .
   ```

3. **Testing the installation**:
   ```bash
   # Log work hours
   aldo log today 4
   
   # View summary
   aldo summary month
   
   # Generate an invoice
   aldo generate-invoice 2025-05-01 2025-05-31
   ```

## AUR Submission

Detailed instructions for submitting to the AUR are provided in the `AUR_SUBMISSION.md` file. 

The key steps are:
1. Create a source tarball
2. Calculate checksums
3. Test building locally
4. Clone the AUR repository
5. Add package files
6. Commit and push

## Version Updates

When creating a new version:

1. Update version number in `pyproject.toml`
2. Update version number in `aldo/aldo/__init__.py`
3. Update version number in `PKGBUILD`
4. Generate a new source tarball
5. Update checksums in PKGBUILD
6. Test locally
7. Update AUR repository

## Conclusion

With these changes, the Aldo CLI application is now properly structured for installation as a system command on Arch Linux. Users can install it using the AUR and run it from anywhere by simply typing `aldo [command]`.
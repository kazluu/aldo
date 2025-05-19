# Complete Guide to Packaging Aldo for Arch Linux

This document provides a comprehensive guide to building, installing, and submitting the Aldo CLI application to the Arch User Repository (AUR).

## 1. Project Structure

The Aldo project has been structured following Python packaging best practices and Arch Linux conventions:

```
aldo/
├── aldo/                  # Python package directory
│   ├── __init__.py        # Package initialization
│   ├── cli.py             # Command-line entry point
│   ├── config.py          # Configuration management
│   ├── core.py            # Core application logic
│   ├── invoice.py         # Invoice generation
│   └── storage.py         # Data storage handling
├── PKGBUILD               # Arch Linux build definition
├── .SRCINFO               # AUR metadata file
├── setup.py               # Python setup script
├── setup.cfg              # Python package configuration
├── pyproject.toml         # Python project metadata
├── LICENSE                # License file
└── README.md              # Documentation
```

## 2. Required Dependencies

### Python Package Dependencies
- click (CLI interface)
- reportlab (PDF generation)
- appdirs (standard file locations)

### Arch Build Dependencies
- python-build
- python-installer
- python-wheel
- python-setuptools

## 3. Building the Package Locally

The `local_build_test.sh` script automates the process of building and testing the package:

```bash
cd aldo
chmod +x local_build_test.sh
./local_build_test.sh
```

### Manual Build Process

If you prefer to build manually:

1. Create the source tarball:
   ```bash
   cd aldo
   mkdir -p build_tmp/aldo-1.0.0
   cp -r aldo setup.py setup.cfg pyproject.toml LICENSE README.md build_tmp/aldo-1.0.0/
   tar -czf aldo-1.0.0.tar.gz -C build_tmp aldo-1.0.0
   ```

2. Build the package:
   ```bash
   mkdir -p build_pkg
   cp aldo-1.0.0.tar.gz PKGBUILD build_pkg/
   cd build_pkg
   makepkg -si
   ```

## 4. AUR Submission Process

### Prerequisites

1. Create an account on the [Arch User Repository](https://aur.archlinux.org/)
2. Set up SSH keys for your AUR account
3. Install required tools:
   ```bash
   sudo pacman -S git base-devel
   ```

### Preparing AUR Submission

1. Generate the `.SRCINFO` file:
   ```bash
   cd aldo
   makepkg --printsrcinfo > .SRCINFO
   ```

2. Calculate the checksum and update the PKGBUILD:
   ```bash
   sha256sum aldo-1.0.0.tar.gz
   # Update the sha256sums value in PKGBUILD
   ```

3. Clone the AUR repository:
   ```bash
   git clone ssh://aur@aur.archlinux.org/aldo.git
   cd aldo
   ```

4. Add your package files:
   ```bash
   cp /path/to/your/aldo-1.0.0.tar.gz .
   cp /path/to/your/PKGBUILD .
   cp /path/to/your/.SRCINFO .
   ```

5. Commit and push:
   ```bash
   git add PKGBUILD .SRCINFO aldo-1.0.0.tar.gz
   git commit -m "Initial package submission: aldo 1.0.0"
   git push
   ```

## 5. Verifying the Installation

After installing the Aldo package, you should verify that:

1. The `aldo` command is available:
   ```bash
   aldo --version
   ```

2. Configuration files are stored in the correct location:
   ```bash
   ls -la ~/.config/aldo/
   ```

3. Data files are stored in the correct location:
   ```bash
   ls -la ~/.local/share/aldo/
   ```

4. All commands work as expected:
   ```bash
   aldo log today 4
   aldo summary day
   aldo generate-invoice 2025-05-01 2025-05-31
   ```

## 6. Handling Updates

When updating the Aldo application:

1. Update the version number in:
   - `aldo/aldo/__init__.py`
   - `pyproject.toml`
   - `setup.py`
   - `PKGBUILD`

2. Create a new source tarball with the updated version

3. Update the checksum in PKGBUILD

4. Build and test the package locally

5. Update the AUR:
   ```bash
   # In your AUR repo
   cp /path/to/your/updated-PKGBUILD PKGBUILD
   makepkg --printsrcinfo > .SRCINFO
   cp /path/to/your/aldo-x.y.z.tar.gz .
   git add PKGBUILD .SRCINFO aldo-x.y.z.tar.gz
   git commit -m "Update to version x.y.z"
   git push
   ```

## 7. Troubleshooting

### Missing Dependencies
If users report missing dependencies, check and update the `depends` array in the PKGBUILD.

### Installation Fails
Check the package build logs for errors. Common issues include:
- Missing dependencies
- Incorrect file paths
- Permission problems

### Command Not Found
If the `aldo` command is not found after installation, verify:
- The package was correctly installed
- The entry point in pyproject.toml is correct
- The installation directory is in PATH

## 8. Best Practices

1. Always test locally before submitting to AUR
2. Keep the AUR package updated with the latest version
3. Respond to user comments on the AUR page
4. Follow [Arch packaging guidelines](https://wiki.archlinux.org/title/Arch_package_guidelines)
5. Use semantic versioning for your releases

## 9. Resources

- [Arch User Repository](https://aur.archlinux.org/)
- [Python Packaging Guide](https://packaging.python.org/guides/distributing-packages-using-setuptools/)
- [Arch Packaging Guidelines](https://wiki.archlinux.org/title/Arch_package_guidelines)
- [PKGBUILD Reference](https://wiki.archlinux.org/title/PKGBUILD)
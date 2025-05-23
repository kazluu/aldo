#!/usr/bin/env python3
"""
Version Update Utility for Aldo

This script updates the version number in all relevant files:
- aldo/__init__.py
- pyproject.toml
- PKGBUILD
"""

import sys
import re
from pathlib import Path

def update_init_py(new_version):
    """Update version in aldo/__init__.py"""
    init_file = Path("aldo/__init__.py")
    if not init_file.exists():
        print(f"Error: {init_file} not found")
        return False
    
    content = init_file.read_text()
    new_content = re.sub(
        r'__version__ = "[^"]*"',
        f'__version__ = "{new_version}"',
        content
    )
    
    if content != new_content:
        init_file.write_text(new_content)
        print(f"Updated {init_file}")
        return True
    else:
        print(f"No changes needed in {init_file}")
        return False

def update_pyproject_toml(new_version):
    """Update version in pyproject.toml"""
    toml_file = Path("pyproject.toml")
    if not toml_file.exists():
        print(f"Error: {toml_file} not found")
        return False
    
    content = toml_file.read_text()
    new_content = re.sub(
        r'version = "[^"]*"',
        f'version = "{new_version}"',
        content
    )
    
    if content != new_content:
        toml_file.write_text(new_content)
        print(f"Updated {toml_file}")
        return True
    else:
        print(f"No changes needed in {toml_file}")
        return False

def update_pkgbuild(new_version):
    """Update version in PKGBUILD"""
    pkgbuild_file = Path("PKGBUILD")
    if not pkgbuild_file.exists():
        print(f"Error: {pkgbuild_file} not found")
        return False
    
    content = pkgbuild_file.read_text()
    new_content = re.sub(
        r'pkgver=[^\n]*',
        f'pkgver={new_version}',
        content
    )
    
    if content != new_content:
        pkgbuild_file.write_text(new_content)
        print(f"Updated {pkgbuild_file}")
        return True
    else:
        print(f"No changes needed in {pkgbuild_file}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python update_version.py <new_version>")
        print("Example: python update_version.py 1.0.4")
        sys.exit(1)
    
    new_version = sys.argv[1]
    
    # Validate version format (basic check)
    if not re.match(r'^\d+\.\d+\.\d+$', new_version):
        print("Error: Version must be in format X.Y.Z (e.g., 1.0.4)")
        sys.exit(1)
    
    print(f"Updating version to {new_version}...")
    
    changes_made = False
    changes_made |= update_init_py(new_version)
    changes_made |= update_pyproject_toml(new_version)
    changes_made |= update_pkgbuild(new_version)
    
    if changes_made:
        print(f"\nVersion successfully updated to {new_version}")
        print("The following files now use imported versions:")
        print("- aldo/core.py (imports from __init__.py)")
        print("- setup.py (imports from __init__.py)")
        print("Files directly updated:")
        print("- aldo/__init__.py")
        print("- pyproject.toml") 
        print("- PKGBUILD")
    else:
        print("No changes were needed.")

if __name__ == "__main__":
    main() 
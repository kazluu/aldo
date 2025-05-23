#!/bin/bash
# Simplified script to build and test the Aldo package for Arch Linux

set -e  # Exit on any error

echo "=== Building Aldo package for Arch Linux ==="
echo

# Ensure we're in the right directory
if [ ! -f "setup.py" ] || [ ! -f "pyproject.toml" ] || [ ! -f "PKGBUILD" ]; then
    echo "Error: Must be run from the root of the aldo package directory"
    echo "Missing files: setup.py, pyproject.toml, or PKGBUILD"
    exit 1
fi

# Get version from __init__.py
VERSION=$(python -c "from aldo import __version__; print(__version__)")
echo "Current version: $VERSION"

# Create source tarball
echo "Creating source tarball..."
TEMP_SRC_DIR=$(mktemp -d)
mkdir -p "$TEMP_SRC_DIR/aldo-$VERSION"

# Copy necessary files
cp -r aldo setup.py pyproject.toml LICENSE README.md "$TEMP_SRC_DIR/aldo-$VERSION/"

# Create the tarball
tar -czf "aldo-$VERSION.tar.gz" -C "$TEMP_SRC_DIR" "aldo-$VERSION"
echo "Created: aldo-$VERSION.tar.gz"

# Clean up temp directory
rm -rf "$TEMP_SRC_DIR"

# Update PKGBUILD version if needed
PKGBUILD_VERSION=$(grep "pkgver=" PKGBUILD | cut -d'=' -f2)
if [ "$PKGBUILD_VERSION" != "$VERSION" ]; then
    echo "Updating PKGBUILD version from $PKGBUILD_VERSION to $VERSION"
    sed -i "s/pkgver=.*/pkgver=$VERSION/" PKGBUILD
fi

# Build the package
echo "Building Arch package..."
makepkg -f --clean --syncdeps

echo "=== Build completed successfully ==="
echo "Package files:"
ls -la *.pkg.tar.zst

echo "Installing the package..."
sudo pacman -U aldo-$VERSION-*.pkg.tar.zst
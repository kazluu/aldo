#!/bin/bash
# Script to build and test the Aldo package locally

echo "=== Building Aldo package locally ==="
echo

# Ensure we're in the right directory
if [ ! -f "setup.py" ] || [ ! -f "pyproject.toml" ]; then
    echo "Error: Must be run from the root of the aldo package directory"
    exit 1
fi

# Create a Python package
echo "Installing build dependencies..."
pip install build wheel setuptools --quiet

# Creating necessary setup.cfg to explicitly specify packages
echo "Creating build configuration..."
cat > setup.cfg << EOF
[options]
packages = find:
package_dir =
    = .
include_package_data = True

[options.packages.find]
include = aldo*
exclude = 
    tests
    static
    templates
    attached_assets
EOF

# Create a source distribution
echo "Creating source distribution..."
python -m build --sdist
if [ $? -ne 0 ]; then
    echo "Error: Failed to build source distribution"
    exit 1
fi

# Create a custom source tarball with just the necessary files
echo "Creating source tarball for Arch package..."
TEMP_SRC_DIR=$(mktemp -d)
mkdir -p "$TEMP_SRC_DIR/aldo-1.0.0"
cp -r aldo setup.py setup.cfg pyproject.toml LICENSE README.md "$TEMP_SRC_DIR/aldo-1.0.0/"
tar -czf "aldo-1.0.0.tar.gz" -C "$TEMP_SRC_DIR" "aldo-1.0.0"

# Copy files to a temporary build directory
echo "Setting up temporary build directory..."
BUILD_DIR=$(mktemp -d)
mv "aldo-1.0.0.tar.gz" "$BUILD_DIR/"
cp PKGBUILD "$BUILD_DIR/"

# Build the Arch package
echo "Building Arch package (this may take a while)..."
cd "$BUILD_DIR"
makepkg -f
if [ $? -ne 0 ]; then
    echo "Error: Failed to build package"
    exit 1
fi

echo
echo "=== Testing package installation ==="
echo "Do you want to install the package locally for testing? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    # Install the package
    echo "Installing the package..."
    sudo pacman -U aldo-*.pkg.tar.zst
    
    # Check if installation was successful
    if command -v aldo &> /dev/null; then
        echo "Installation successful! Testing commands..."
        
        echo "Testing version command:"
        aldo --version
        
        echo "Testing help command:"
        aldo --help
        
        echo "You can now log work hours:"
        echo "  aldo log today 4"
        echo "  aldo summary day"
        echo "  aldo generate-invoice <start-date> <end-date>"
    else
        echo "Error: The 'aldo' command was not found after installation."
        exit 1
    fi
else
    echo "Skipping installation. Package file is available at: $BUILD_DIR/aldo-*.pkg.tar.zst"
fi

echo
echo "=== Package build directory ==="
echo "The build files are located at: $BUILD_DIR"
echo "You can manually inspect or install the package from there."
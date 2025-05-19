#!/bin/bash
# Setup script for Aldo CLI

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Aldo CLI Setup ===${NC}"
echo "This script will clean up the project and prepare it for development/packaging"

# Remove web application files
echo -e "\n${YELLOW}Removing web application components...${NC}"
rm -f main.py aldo.py
rm -rf static templates

# Clean up duplicate files
echo -e "\n${YELLOW}Cleaning up duplicate files...${NC}"
rm -f config.py storage.py invoice.py

# Create CLI entry point
echo -e "\n${YELLOW}Creating CLI entry point...${NC}"
cat > aldo_cli.py << 'EOF'
#!/usr/bin/env python3
"""
Aldo CLI - Entry point for the Aldo application
"""

from aldo.core import cli

if __name__ == '__main__':
    cli()
EOF
chmod +x aldo_cli.py

# Create virtual environment
echo -e "\n${YELLOW}Creating virtual environment...${NC}"
python -m venv .venv

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate

# Install package in development mode
echo -e "\n${YELLOW}Installing Aldo in development mode...${NC}"
pip install -e .

# Test the installation
echo -e "\n${YELLOW}Testing the installation...${NC}"
aldo --help

echo -e "\n${GREEN}Setup complete!${NC}"
echo "To use Aldo, activate the virtual environment with:"
echo -e "${YELLOW}source .venv/bin/activate${NC}"
echo -e "Then run ${YELLOW}aldo --help${NC} to see available commands"
echo -e "\nTo deactivate the virtual environment when done, run: ${YELLOW}deactivate${NC}"
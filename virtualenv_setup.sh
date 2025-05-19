#!/bin/bash
# Setup script for creating a virtual environment and installing Aldo CLI

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Aldo CLI Setup${NC}"
echo "This script will set up a virtual environment for Aldo CLI"

# Create a virtual environment
echo -e "\n${YELLOW}Creating virtual environment...${NC}"
python -m venv .venv

# Activate the virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate

# Upgrade pip
echo -e "\n${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install Aldo in development mode
echo -e "\n${YELLOW}Installing Aldo...${NC}"
pip install -e .

# Test the installation
echo -e "\n${YELLOW}Testing the installation...${NC}"
echo "Running: aldo --help"
aldo --help

echo -e "\n${GREEN}Setup complete!${NC}"
echo "To use Aldo, activate the virtual environment with:"
echo -e "${YELLOW}source .venv/bin/activate${NC}"
echo -e "Then run ${YELLOW}aldo --help${NC} to see available commands"
echo -e "\nTo deactivate the virtual environment when done, run: ${YELLOW}deactivate${NC}"
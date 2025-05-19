#!/bin/bash
# Setup script for Aldo CLI development environment

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Aldo CLI Development Environment Setup ===${NC}"

# Create virtual environment
echo -e "\n${YELLOW}Creating virtual environment...${NC}"
python -m venv .venv

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate

# Install development dependencies
echo -e "\n${YELLOW}Installing development dependencies...${NC}"
pip install --upgrade pip
pip install -e .

# Show success message
echo -e "\n${GREEN}Setup complete!${NC}"
echo "To activate the environment, run:"
echo -e "${YELLOW}source .venv/bin/activate${NC}"
echo -e "To test the CLI, run: ${YELLOW}aldo --help${NC}"
echo -e "To deactivate when finished, run: ${YELLOW}deactivate${NC}"
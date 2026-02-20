#!/bin/bash
# Install all requirements.txt files found in subdirectories
# Simple shell script version

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Searching for requirements.txt files..."

# Find all requirements.txt files (excluding common directories)
REQUIREMENTS_FILES=$(find . -name "requirements.txt" -type f \
    | grep -v node_modules \
    | grep -v __pycache__ \
    | grep -v ".git" \
    | grep -v ".venv" \
    | grep -v "venv" \
    | sort)

if [ -z "$REQUIREMENTS_FILES" ]; then
    echo "No requirements.txt files found."
    exit 1
fi

echo -e "${GREEN}Found requirements.txt files:${NC}"
echo "$REQUIREMENTS_FILES" | while read -r file; do
    echo "  - $file"
done

echo ""
read -p "Install all requirements? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Install each requirements.txt file
FAILED=0
echo "$REQUIREMENTS_FILES" | while read -r file; do
    echo -e "\n${GREEN}Installing requirements from: $file${NC}"
    if pip install -r "$file"; then
        echo -e "${GREEN}✓ Successfully installed from $file${NC}"
    else
        echo -e "${YELLOW}⚠ Failed to install from $file${NC}"
        FAILED=1
    fi
done

if [ $FAILED -eq 1 ]; then
    echo -e "\n${YELLOW}Some requirements failed to install.${NC}"
    exit 1
else
    echo -e "\n${GREEN}All requirements installed successfully!${NC}"
    exit 0
fi

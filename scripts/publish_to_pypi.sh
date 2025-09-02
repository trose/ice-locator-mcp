#!/bin/bash
# Script to publish the ice-locator-mcp package to PyPI
# Usage: ./scripts/publish_to_pypi.sh

echo "Publishing ice-locator-mcp to PyPI..."

# Check if twine is installed
if ! command -v twine &> /dev/null
then
    echo "twine could not be found, installing..."
    pip install twine
fi

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: pyproject.toml not found. Please run this script from the project root directory."
    exit 1
fi

# Check if distribution files exist
if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
    echo "Distribution files not found. Building package..."
    python -m build
fi

# Publish to PyPI
echo "Publishing to PyPI..."
twine upload dist/*

echo "Package published to PyPI successfully!"
echo "You can install it using: pip install ice-locator-mcp"
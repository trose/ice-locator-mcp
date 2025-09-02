#!/bin/bash
# Script to set up GitHub Pages for documentation
# Usage: ./scripts/setup_github_pages.sh

echo "Setting up GitHub Pages for documentation..."

# Check if we're in the right directory
if [ ! -f "mkdocs.yml" ]; then
    echo "Error: mkdocs.yml not found. Please run this script from the project root directory."
    exit 1
fi

# Check if mkdocs is installed
if ! command -v mkdocs &> /dev/null
then
    echo "mkdocs could not be found, installing..."
    pip install mkdocs
fi

# Build the documentation
echo "Building documentation..."
mkdocs build

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null
then
    echo "GitHub CLI (gh) could not be found."
    echo "Please install it from https://cli.github.com/ or set up GitHub Pages manually:"
    echo "1. Go to your repository settings on GitHub"
    echo "2. Navigate to Pages section"
    echo "3. Select 'gh-pages' branch as source"
    echo "4. Save changes"
    exit 1
fi

# Create and push gh-pages branch if it doesn't exist
if ! git show-ref --quiet refs/heads/gh-pages; then
    echo "Creating gh-pages branch..."
    git checkout -b gh-pages
    git checkout main
fi

# Deploy documentation to GitHub Pages
echo "Deploying documentation to GitHub Pages..."
mkdocs gh-deploy

echo "GitHub Pages has been set up successfully!"
echo "Your documentation should be available at: https://trose.github.io/ice-locator-mcp/"
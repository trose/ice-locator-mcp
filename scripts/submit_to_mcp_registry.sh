#!/bin/bash
# Script to submit the ICE Locator MCP server to the MCP registry
# Usage: ./scripts/submit_to_mcp_registry.sh

echo "Preparing submission to MCP registry..."

# Check if we're in the right directory
if [ ! -f "mcp-manifest.json" ]; then
    echo "Error: mcp-manifest.json not found. Please run this script from the project root directory."
    exit 1
fi

echo "MCP manifest found. Please ensure it contains the correct information:"
echo "- Name: ICE Locator MCP Server"
echo "- Description: Model Context Protocol server for locating ICE detainees"
echo "- Version: 1.0.0"
echo "- Keywords: ice, detainee, locator, mcp, search"
echo "- Repository: https://github.com/trose/ice-locator-mcp"
echo "- License: MIT"
echo "- Author: TRose"
echo ""

echo "To submit to the MCP registry:"
echo "1. Visit https://registry.mcp.dev/"
echo "2. Sign in or create an account"
echo "3. Click 'Submit a New Package'"
echo "4. Fill in the form with the information from mcp-manifest.json"
echo "5. Submit the package for review"
echo ""
echo "Alternatively, you can submit via GitHub:"
echo "1. Fork the MCP registry repository"
echo "2. Add your package to the registry"
echo "3. Create a pull request"
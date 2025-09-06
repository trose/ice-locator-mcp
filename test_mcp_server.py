#!/usr/bin/env python3
"""
Test script to verify MCP server is working correctly
"""

import asyncio
import subprocess
import time
import os

def test_mcp_server():
    """Test the MCP server startup with our configuration"""
    print("Testing ICE Locator MCP Server startup...")
    
    # Set the environment variable for the config file
    env = os.environ.copy()
    env['ICE_LOCATOR_CONFIG'] = '/Users/trose/src/locator-mcp/config/production.json'
    
    # Start the server process
    process = subprocess.Popen([
        '/Users/trose/src/locator-mcp/.venv/bin/python', 
        '-m', 'ice_locator_mcp'
    ], 
    env=env,
    cwd='/Users/trose/src/locator-mcp',
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
    )
    
    # Give it a moment to start
    time.sleep(3)
    
    # Check if the process is still running
    if process.poll() is None:
        print("✅ Server started successfully and is running")
        # Terminate the process
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("✅ Server terminated cleanly")
        return True
    else:
        stdout, stderr = process.communicate()
        print(f"❌ Server failed to start")
        print(f"Return code: {process.returncode}")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}")
        return False

if __name__ == "__main__":
    test_mcp_server()
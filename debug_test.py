"""
debug_test.py - Step by step debugging
Save this entire code as debug_test.py
"""

import sys
import os

def test_step_by_step():
    """Test each component step by step."""
    
    print("🔍 D&D MCP Debug Test")
    print("=" * 25)
    
    # Test 1: Check file exists
    print("1. Checking if dnd_server.py exists...")
    if os.path.exists("dnd_server.py"):
        print("   ✅ dnd_server.py found")
    else:
        print("   ❌ dnd_server.py not found")
        print("   You need to create this file with the D&D server code")
        return
    
    # Test 2: Check imports
    print("\n2. Testing imports...")
    try:
        import mcp
        print("   ✅ mcp imported")
    except ImportError as e:
        print(f"   ❌ mcp import failed: {e}")
        print("   Run: pip install 'mcp[cli]'")
        return
    
    try:
        from mcp.server.fastmcp import FastMCP
        print("   ✅ FastMCP imported")
    except ImportError as e:
        print(f"   ❌ FastMCP import failed: {e}")
        return
    
    try:
        import pydantic
        print("   ✅ pydantic imported")
    except ImportError as e:
        print(f"   ❌ pydantic import failed: {e}")
        print("   Run: pip install pydantic")
        return
    
    # Test 3: Try to load server code
    print("\n3. Testing server code...")
    try:
        import dnd_server
        print("   ✅ dnd_server code loads successfully")
    except Exception as e:
        print(f"   ❌ dnd_server code has errors: {e}")
        print("   Check your dnd_server.py file for syntax errors")
        return
    
    # Test 4: Check if server object exists
    print("\n4. Checking server object...")
    try:
        if hasattr(dnd_server, 'mcp'):
            print("   ✅ MCP server object found")
        else:
            print("   ❌ No 'mcp' object found in dnd_server.py")
            return
    except Exception as e:
        print(f"   ❌ Error checking server object: {e}")
        return
    
    print("\n✅ All basic checks passed!")
    print("Your MCP server code appears to be working.")
    print("\nNext step: Try running the server directly:")
    print("   python dnd_server.py")

if __name__ == "__main__":
    test_step_by_step()

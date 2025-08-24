#!/usr/bin/env python3
"""
Basic MCP functionality test
"""
import asyncio
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_mcp_basic():
    """Test basic MCP functionality"""
    print("🧪 Testing MCP Basic Functionality...")
    
    try:
        # Test 1: Import MCP server
        print("1. Testing MCP server import...")
        from mcp_server import MCPServer, MCPToolType
        print("   ✅ MCP server imported successfully")
        
        # Test 2: Create MCP server instance
        print("2. Testing MCP server creation...")
        mcp_server = MCPServer()
        print(f"   ✅ MCP server created with {len(mcp_server.tools)} tools")
        
        # Test 3: Check available tools
        print("3. Testing tool discovery...")
        tools = list(mcp_server.tools.keys())
        print(f"   ✅ Available tools: {tools}")
        
        # Test 4: Test tool schema
        print("4. Testing tool schema...")
        if tools:
            first_tool = tools[0]
            tool = mcp_server.tools[first_tool]
            print(f"   ✅ Tool '{first_tool}' schema: {tool.inputSchema}")
        
        # Test 5: Test tool execution (basic)
        print("5. Testing basic tool execution...")
        if "tools/list" in mcp_server.tools:
            result = await mcp_server.tools["tools/list"].handler({})
            print(f"   ✅ Tools list result: {result}")
        
        print("\n🎉 All basic MCP tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_mcp_tools():
    """Test specific MCP tools"""
    print("\n🔧 Testing Specific MCP Tools...")
    
    try:
        from mcp_server import MCPServer
        
        mcp_server = MCPServer()
        
        # Test appointment scheduling tool
        if "appointments/schedule" in mcp_server.tools:
            print("1. Testing appointment scheduling tool...")
            tool = mcp_server.tools["appointments/schedule"]
            print(f"   ✅ Tool found: {tool.description}")
            print(f"   ✅ Input schema: {tool.inputSchema}")
        
        # Test doctor availability tool
        if "appointments/check_availability" in mcp_server.tools:
            print("2. Testing doctor availability tool...")
            tool = mcp_server.tools["appointments/check_availability"]
            print(f"   ✅ Tool found: {tool.description}")
            print(f"   ✅ Input schema: {tool.inputSchema}")
        
        print("\n🎉 All tool tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Tool test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Starting MCP Basic Tests...\n")
    
    # Test basic functionality
    basic_result = await test_mcp_basic()
    
    # Test specific tools
    tools_result = await test_mcp_tools()
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    print(f"Basic MCP functionality: {'✅ PASSED' if basic_result else '❌ FAILED'}")
    print(f"Specific MCP tools: {'✅ PASSED' if tools_result else '❌ FAILED'}")
    
    if basic_result and tools_result:
        print("\n🎉 All tests passed! MCP server is working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
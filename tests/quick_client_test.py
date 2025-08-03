"""
Quick test to connect to your running MCP server
Save as: quick_client_test.py
Run in a NEW terminal while dnd_server.py is running
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_running_server():
    """Test the running D&D MCP server."""
    
    print("🔌 Connecting to D&D MCP Server...")
    
    # Connect to the running server
    server_params = StdioServerParameters(
        command="python",
        args=["dnd_server.py"]
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                print("✅ Connected to MCP Server!")
                
                # Test available tools
                tools = await session.list_tools()
                print(f"\n🛠️  Available tools: {[t.name for t in tools.tools]}")
                
                # Test dice rolling
                print("\n🎲 Testing dice roll...")
                result = await session.call_tool("roll_dice", {
                    "dice_notation": "2d6",
                    "modifier": 3
                })
                
                dice_data = result.structuredContent
                print(f"   2d6+3: {dice_data['individual_rolls']} + 3 = {dice_data['total']}")
                
                # Test attack roll
                print("\n⚔️  Testing attack roll...")
                attack = await session.call_tool("attack_roll", {
                    "attacker_bonus": 5,
                    "target_ac": 15,
                    "damage_dice": "1d8",
                    "damage_bonus": 2
                })
                
                attack_data = attack.structuredContent
                print(f"   {attack_data['description']}")
                
                print("\n✅ All tests passed! Your D&D server is working perfectly!")
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("Make sure your dnd_server.py is running in another terminal")

if __name__ == "__main__":
    asyncio.run(test_running_server())

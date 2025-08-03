"""
test_server.py - Test your D&D MCP server
This is the code for the test_server.py file you asked about
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_dnd_server():
    """Test the D&D MCP server."""
    
    print("🎲 Testing D&D MCP Server")
    print("=" * 25)
    
    server_params = StdioServerParameters(
        command="python",
        args=["dnd_server.py"]
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                print("✅ Server connected!")
                
                # Test dice roll
                print("\n🎲 Testing dice roll...")
                result = await session.call_tool("roll_dice", {
                    "dice_notation": "1d20",
                    "modifier": 5
                })
                
                data = result.structuredContent
                print(f"   1d20+5: rolled {data['individual_rolls'][0]} + 5 = {data['total']}")
                
                # Test combat
                print("\n⚔️ Testing combat...")
                combat = await session.call_tool("attack_roll", {
                    "attacker_bonus": 4,
                    "target_ac": 15,
                    "damage_dice": "1d8", 
                    "damage_bonus": 2
                })
                
                combat_data = combat.structuredContent
                print(f"   {combat_data['description']}")
                
                # Test character creation
                print("\n🧙‍♂️ Testing character creation...")
                character = await session.call_tool("create_character", {
                    "name": "Test Hero",
                    "character_class": "Fighter",
                    "level": 1,
                    "strength": 16,
                    "dexterity": 14,
                    "constitution": 15,
                    "intelligence": 12,
                    "wisdom": 13,
                    "charisma": 10
                })
                
                char_data = character.structuredContent
                print(f"   Created: {char_data['name']} (AC: {char_data['armor_class']}, HP: {char_data['hit_points']})")
                
                print("\n🎉 Your D&D server is working perfectly!")
                print("   ✓ Dice rolling")
                print("   ✓ Combat mechanics") 
                print("   ✓ Character creation")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you have: pip install 'mcp[cli]' pydantic")
        print("2. Make sure dnd_server.py exists")
        print("3. Check that the server code is correct")

if __name__ == "__main__":
    asyncio.run(test_dnd_server())

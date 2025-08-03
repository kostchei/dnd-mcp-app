"""
working_integration_test.py - Test MCP + LM Studio together
This bypasses the CLI tools and tests everything directly
Save this entire code as working_integration_test.py
"""

import asyncio
import openai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_dnd_integration():
    """Test the full D&D experience with MCP + LM Studio."""
    
    print("🎮 D&D Integration Test")
    print("=" * 25)
    
    # Test 1: LM Studio
    print("1. Testing LM Studio...")
    try:
        ai_client = openai.OpenAI(
            base_url="http://127.0.0.1:1234/v1",
            api_key="lm-studio"
        )
        
        response = ai_client.chat.completions.create(
            model="local-model",
            messages=[{"role": "user", "content": "Say 'Ready for D&D!'"}],
            max_tokens=10
        )
        
        print(f"   ✅ LM Studio: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"   ❌ LM Studio failed: {e}")
        print("   Make sure LM Studio is running!")
        return False
    
    # Test 2: MCP Server with tools
    print("\n2. Testing MCP Server...")
    
    server_params = StdioServerParameters(
        command="python",
        args=["dnd_server.py"]
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                print("   ✅ MCP Server connected")
                
                # Test dice rolling
                print("\n3. Testing dice mechanics...")
                dice_result = await session.call_tool("roll_dice", {
                    "dice_notation": "1d20",
                    "modifier": 5
                })
                
                dice_data = dice_result.structuredContent
                roll_value = dice_data['individual_rolls'][0]
                total = dice_data['total']
                print(f"   🎲 Rolled d20: {roll_value} + 5 = {total}")
                
                # Test combat
                print("\n4. Testing combat mechanics...")
                attack_result = await session.call_tool("attack_roll", {
                    "attacker_bonus": 4,
                    "target_ac": 15,
                    "damage_dice": "1d8",
                    "damage_bonus": 2
                })
                
                attack_data = attack_result.structuredContent
                print(f"   ⚔️  {attack_data['description']}")
                
                # Test AI description of combat
                print("\n5. Testing AI + MCP integration...")
                if attack_data['hit']:
                    prompt = f"Dramatically describe a successful sword attack that deals {attack_data['damage']} damage to a goblin."
                else:
                    prompt = "Dramatically describe a sword attack that narrowly misses a goblin."
                
                ai_response = ai_client.chat.completions.create(
                    model="local-model",
                    messages=[
                        {"role": "system", "content": "You are a D&D narrator. Write 1-2 vivid sentences."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=60
                )
                
                print(f"   🎭 AI Narration: {ai_response.choices[0].message.content}")
                
                # Test character creation
                print("\n6. Testing character creation...")
                character_result = await session.call_tool("create_character", {
                    "name": "Thorin Ironbeard",
                    "character_class": "Fighter", 
                    "level": 2,
                    "strength": 16,
                    "dexterity": 12,
                    "constitution": 15,
                    "intelligence": 10,
                    "wisdom": 13,
                    "charisma": 8
                })
                
                char_data = character_result.structuredContent
                print(f"   🧙‍♂️ Created: {char_data['name']} (AC: {char_data['armor_class']}, HP: {char_data['hit_points']})")
                
                print("\n🎉 FULL INTEGRATION SUCCESS!")
                print("   ✓ LM Studio provides creative AI")
                print("   ✓ MCP provides reliable game mechanics")
                print("   ✓ Dice rolling, combat, and character creation work")
                print("   ✓ AI narration enhances the experience")
                
                return True
                
    except Exception as e:
        print(f"   ❌ MCP integration failed: {e}")
        print("   Your server components work, but there might be a connection issue")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_dnd_integration())
    
    if success:
        print("\n🚀 Your D&D system is ready!")
        print("Next: Try the full CLI interface")
    else:
        print("\n🔧 Some components need fixing")

"""
Command-line D&D interface using MCP + LM Studio
Run with: uv run python cli_dnd.py
"""

import asyncio
import openai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class DnDCLI:
    def __init__(self):
        self.ai_client = openai.OpenAI(
            base_url="http://127.0.0.1:1234/v1",
            api_key="lm-studio"
        )
        
        self.server_params = StdioServerParameters(
            command="uv",
            args=["run", "python", "dnd_server.py"]
        )
    
    async def start(self):
        """Start the CLI session."""
        print("🐉 D&D Command Line Interface")
        print("=" * 30)
        print("Commands:")
        print("  roll <dice>     - Roll dice (e.g., 'roll 2d6+3')")
        print("  attack <bonus> <ac> - Attack roll")
        print("  describe <scene> - AI describes a scene")
        print("  combat <enemy> - Quick combat")
        print("  quit - Exit")
        print()
        
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                while True:
                    try:
                        command = input("🎲 > ").strip()
                        
                        if command == "quit":
                            break
                        elif command.startswith("roll "):
                            await self.handle_roll(session, command[5:])
                        elif command.startswith("attack "):
                            await self.handle_attack(session, command[7:])
                        elif command.startswith("describe "):
                            await self.handle_describe(command[9:])
                        elif command.startswith("combat "):
                            await self.handle_combat(session, command[7:])
                        else:
                            print("❓ Unknown command")
                    
                    except KeyboardInterrupt:
                        break
                    except Exception as e:
                        print(f"❌ Error: {e}")
        
        print("\n👋 Goodbye, adventurer!")
    
    async def handle_roll(self, session, dice_str):
        """Handle dice rolling command."""
        try:
            # Parse dice notation (simple)
            if '+' in dice_str:
                dice, modifier = dice_str.split('+')
                modifier = int(modifier)
            elif '-' in dice_str:
                dice, modifier = dice_str.split('-')
                modifier = -int(modifier)
            else:
                dice = dice_str
                modifier = 0
            
            result = await session.call_tool("roll_dice", {
                "dice_notation": dice.strip(),
                "modifier": modifier
            })
            
            data = result.structuredContent
            print(f"🎲 {data['dice_notation']} + {data['modifier']}: {data['individual_rolls']} = {data['total']}")
            
        except Exception as e:
            print(f"❌ Invalid dice format: {e}")
    
    async def handle_attack(self, session, attack_str):
        """Handle attack command."""
        try:
            parts = attack_str.split()
            bonus = int(parts[0])
            ac = int(parts[1])
            
            result = await session.call_tool("attack_roll", {
                "attacker_bonus": bonus,
                "target_ac": ac,
                "damage_dice": "1d8",
                "damage_bonus": 2
            })
            
            data = result.structuredContent
            print(f"⚔️  {data['description']}")
            
        except:
            print("❌ Usage: attack <bonus> <target_ac>")
    
    async def handle_describe(self, scene):
        """Handle description command using AI."""
        try:
            response = self.ai_client.chat.completions.create(
                model="local-model",
                messages=[
                    {"role": "system", "content": "You are a D&D Dungeon Master. Describe scenes vividly in 2-3 sentences."},
                    {"role": "user", "content": f"Describe this D&D scene: {scene}"}
                ],
                max_tokens=120
            )
            
            print(f"🏰 {response.choices[0].message.content}")
            
        except Exception as e:
            print(f"❌ AI error: {e}")
    
    async def handle_combat(self, session, enemy):
        """Handle quick combat encounter."""
        print(f"\n⚔️  Combat vs {enemy}")
        
        # Roll initiative
        init_result = await session.call_tool("roll_dice", {"dice_notation": "1d20", "modifier": 2})
        init_data = init_result.structuredContent
        print(f"Initiative: {init_data['total']}")
        
        # Attack
        attack_result = await session.call_tool("attack_roll", {
            "attacker_bonus": 4,
            "target_ac": 13,
            "damage_dice": "1d8",
            "damage_bonus": 2
        })
        
        attack_data = attack_result.structuredContent
        print(f"Attack: {attack_data['description']}")
        
        # AI narration
        try:
            if attack_data['hit']:
                prompt = f"Narrate a successful attack against a {enemy} dealing {attack_data['damage']} damage"
            else:
                prompt = f"Narrate a missed attack against a {enemy}"
            
            response = self.ai_client.chat.completions.create(
                model="local-model",
                messages=[
                    {"role": "system", "content": "You are a D&D narrator. Be dramatic but brief."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=80
            )
            
            print(f"📖 {response.choices[0].message.content}")
            
        except Exception as e:
            print(f"❌ Narration failed: {e}")


async def main():
    cli = DnDCLI()
    await cli.start()

if __name__ == "__main__":
    asyncio.run(main())
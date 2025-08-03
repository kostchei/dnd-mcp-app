"""
dnd_cli.py - Interactive D&D Command Line Interface
Your complete D&D game system with AI narration and MCP mechanics
"""

import asyncio
import openai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class DnDGame:
    def __init__(self):
        # LM Studio client
        self.ai_client = openai.OpenAI(
            base_url="http://127.0.0.1:1234/v1",
            api_key="lm-studio"
        )
        
        # MCP server parameters
        self.server_params = StdioServerParameters(
            command="python",
            args=["dnd_server.py"]
        )
        
        self.character_id = None
        self.session = None
    
    async def start(self):
        """Start the D&D game session."""
        print("🐉 Welcome to D&D with AI + MCP!")
        print("=" * 40)
        print("🎲 MCP provides reliable game mechanics")
        print("🎭 LM Studio provides creative storytelling")
        print("🏰 You get the best of both worlds!")
        print()
        
        # Connect to MCP server
        print("🔌 Connecting to D&D server...")
        self.read, self.write = await stdio_client(self.server_params).__aenter__()
        self.session = await ClientSession(self.read, self.write).__aenter__()
        await self.session.initialize()
        print("✅ Connected!")
        
    async def show_commands(self):
        """Show available commands."""
        print("\n🎮 Available Commands:")
        print("  create - Create a new character")
        print("  roll <dice> - Roll dice (e.g., 'roll 2d6+3')")
        print("  attack <bonus> <target_ac> - Attack roll")
        print("  check <skill> - Skill check (perception, stealth, etc.)")
        print("  describe <scene> - Get AI description")
        print("  combat <enemy> - Quick combat encounter")
        print("  character - Show character info")
        print("  help - Show commands")
        print("  quit - Exit game")
    
    async def create_character(self):
        """Interactive character creation."""
        print("\n🧙‍♂️ Character Creation")
        print("=" * 20)
        
        name = input("Character name: ").strip()
        if not name:
            name = "Hero"
        
        print("\nChoose class:")
        print("1. Fighter (Strong melee combat)")
        print("2. Wizard (Magical spells)")
        print("3. Rogue (Stealth and skills)")
        print("4. Cleric (Healing and support)")
        
        class_choice = input("Choose (1-4): ").strip()
        classes = {"1": "Fighter", "2": "Wizard", "3": "Rogue", "4": "Cleric"}
        char_class = classes.get(class_choice, "Fighter")
        
        level = int(input("Level (1-10): ") or "1")
        
        print(f"\n🎲 Rolling ability scores for {name} the {char_class}...")
        
        # Roll ability scores using MCP
        abilities = {}
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            # Roll 4d6, drop lowest (simulate this with multiple 1d6 rolls)
            rolls = []
            for _ in range(4):
                result = await self.session.call_tool("roll_dice", {"dice_notation": "1d6"})
                rolls.append(result.structuredContent["individual_rolls"][0])
            rolls.sort(reverse=True)
            score = sum(rolls[:3])
            abilities[ability] = score
            print(f"  {ability.capitalize()}: {score}")
        
        # Create character
        result = await self.session.call_tool("create_character", {
            "name": name,
            "character_class": char_class,
            "level": level,
            **abilities
        })
        
        char_data = result.structuredContent
        self.character_id = char_data["id"]
        
        print(f"\n✅ Created {char_data['name']} the {char_class}!")
        print(f"   AC: {char_data['armor_class']}, HP: {char_data['hit_points']}")
        
        # Get AI description of character
        await self.ai_describe(f"a {char_class} named {name}", "character description")
    
    async def roll_dice(self, dice_str):
        """Roll dice with modifiers."""
        try:
            # Parse dice notation
            if '+' in dice_str:
                dice, modifier = dice_str.split('+')
                modifier = int(modifier)
            elif '-' in dice_str:
                dice, modifier = dice_str.split('-')
                modifier = -int(modifier)
            else:
                dice = dice_str
                modifier = 0
            
            result = await self.session.call_tool("roll_dice", {
                "dice_notation": dice.strip(),
                "modifier": modifier
            })
            
            data = result.structuredContent
            rolls = data['individual_rolls']
            total = data['total']
            
            print(f"🎲 {dice_str}: {rolls} = {total}")
            
            # AI comment on the roll
            if total >= 18:
                await self.ai_describe(f"rolling an amazing {total}", "excited reaction")
            elif total <= 5:
                await self.ai_describe(f"rolling a terrible {total}", "disappointed reaction")
            
        except Exception as e:
            print(f"❌ Invalid dice format: {e}")
            print("Example: roll 2d6+3")
    
    async def attack_roll(self, bonus_str, ac_str):
        """Perform an attack roll."""
        try:
            bonus = int(bonus_str)
            ac = int(ac_str)
            
            result = await self.session.call_tool("attack_roll", {
                "attacker_bonus": bonus,
                "target_ac": ac,
                "damage_dice": "1d8",
                "damage_bonus": 2
            })
            
            data = result.structuredContent
            print(f"⚔️  {data['description']}")
            
            # AI narration
            if data['hit']:
                await self.ai_describe(f"a successful attack dealing {data['damage']} damage", "combat narration")
            else:
                await self.ai_describe("a missed attack", "combat narration")
            
        except ValueError:
            print("❌ Usage: attack <bonus> <target_ac>")
            print("Example: attack 5 15")
    
    async def skill_check(self, skill):
        """Perform a skill check."""
        difficulty = 15  # Standard DC
        
        # Get character modifier if we have a character
        modifier = 0
        if self.character_id:
            char_result = await self.session.call_tool("get_character_info", {"character_id": self.character_id})
            char_data = char_result.structuredContent
            
            # Simplified modifier based on skill
            skill_abilities = {
                "perception": char_data["wisdom"],
                "stealth": char_data["dexterity"], 
                "intimidation": char_data["charisma"],
                "athletics": char_data["strength"],
                "investigation": char_data["intelligence"]
            }
            
            if skill.lower() in skill_abilities:
                ability_score = skill_abilities[skill.lower()]
                modifier = (ability_score - 10) // 2
        
        # Roll the dice
        result = await self.session.call_tool("roll_dice", {
            "dice_notation": "1d20",
            "modifier": modifier
        })
        
        data = result.structuredContent
        total = data['total']
        success = total >= difficulty
        
        print(f"🎯 {skill.capitalize()} check: {data['individual_rolls'][0]} + {modifier} = {total}")
        print(f"{'✅ SUCCESS' if success else '❌ FAILURE'} (DC {difficulty})")
        
        # AI describes the outcome
        outcome = "successful" if success else "failed"
        await self.ai_describe(f"a {outcome} {skill} check", "skill check result")
    
    async def combat_encounter(self, enemy):
        """Run a quick combat encounter."""
        print(f"\n⚔️  Combat Encounter: You vs {enemy}")
        print("=" * 30)
        
        # Initiative
        init_result = await self.session.call_tool("roll_dice", {"dice_notation": "1d20", "modifier": 2})
        init_data = init_result.structuredContent
        print(f"🎲 Initiative: {init_data['total']}")
        
        # Your attack
        attack_result = await self.session.call_tool("attack_roll", {
            "attacker_bonus": 5,
            "target_ac": 13,
            "damage_dice": "1d8",
            "damage_bonus": 3
        })
        
        attack_data = attack_result.structuredContent
        print(f"⚔️  Your attack: {attack_data['description']}")
        
        # AI narrates the entire combat
        if attack_data['hit']:
            prompt = f"Narrate a D&D combat where the player successfully attacks a {enemy} dealing {attack_data['damage']} damage. Be dramatic and exciting!"
        else:
            prompt = f"Narrate a D&D combat where the player's attack misses a {enemy}. Describe the near miss dramatically!"
        
        response = self.ai_client.chat.completions.create(
            model="local-model",
            messages=[
                {"role": "system", "content": "You are an expert D&D Dungeon Master. Create vivid, exciting combat descriptions in 2-3 sentences."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        
        print(f"🎭 {response.choices[0].message.content}")
    
    async def ai_describe(self, scene, context="scene"):
        """Get AI description of a scene."""
        prompts = {
            "scene": f"Describe this D&D scene: {scene}",
            "character description": f"Describe the appearance and personality of {scene} in 2-3 sentences",
            "combat narration": f"Dramatically narrate {scene} in D&D combat",
            "skill check result": f"Describe what happens with {scene} in a D&D game",
            "excited reaction": f"Describe a character's excited reaction to {scene}",
            "disappointed reaction": f"Describe a character's disappointed reaction to {scene}"
        }
        
        prompt = prompts.get(context, f"Describe: {scene}")
        
        try:
            response = self.ai_client.chat.completions.create(
                model="local-model",
                messages=[
                    {"role": "system", "content": "You are a creative D&D Dungeon Master. Be vivid but concise (2-3 sentences)."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=80
            )
            
            print(f"🎭 {response.choices[0].message.content}")
            
        except Exception as e:
            print(f"❌ AI description failed: {e}")
    
    async def show_character(self):
        """Show character information."""
        if not self.character_id:
            print("❌ No character created yet. Use 'create' command.")
            return
        
        result = await self.session.call_tool("get_character_info", {"character_id": self.character_id})
        char_data = result.structuredContent
        
        print(f"\n🧙‍♂️ {char_data['name']} - Level {char_data['level']} {char_data['character_class']}")
        print(f"AC: {char_data['armor_class']}, HP: {char_data['current_hp']}/{char_data['hit_points']}")
        print(f"STR: {char_data['strength']}, DEX: {char_data['dexterity']}, CON: {char_data['constitution']}")
        print(f"INT: {char_data['intelligence']}, WIS: {char_data['wisdom']}, CHA: {char_data['charisma']}")
    
    async def game_loop(self):
        """Main game loop."""
        await self.show_commands()
        
        while True:
            try:
                command = input("\n🎲 > ").strip().lower()
                
                if command == "quit":
                    print("\n👋 Thanks for playing D&D!")
                    break
                elif command == "help":
                    await self.show_commands()
                elif command == "create":
                    await self.create_character()
                elif command == "character":
                    await self.show_character()
                elif command.startswith("roll "):
                    dice = command[5:]
                    await self.roll_dice(dice)
                elif command.startswith("attack "):
                    parts = command[7:].split()
                    if len(parts) >= 2:
                        await self.attack_roll(parts[0], parts[1])
                    else:
                        print("❌ Usage: attack <bonus> <target_ac>")
                elif command.startswith("check "):
                    skill = command[6:]
                    await self.skill_check(skill)
                elif command.startswith("describe "):
                    scene = command[9:]
                    await self.ai_describe(scene)
                elif command.startswith("combat "):
                    enemy = command[7:]
                    await self.combat_encounter(enemy)
                else:
                    print("❓ Unknown command. Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                print("\n\n👋 Thanks for playing!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def cleanup(self):
        """Clean up connections."""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if hasattr(self, 'read'):
            await self.read.__aexit__(None, None, None)

async def main():
    """Main game function."""
    game = DnDGame()
    
    try:
        await game.start()
        await game.game_loop()
    except Exception as e:
        print(f"❌ Game error: {e}")
    finally:
        await game.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

"""
D&D Character Management MCP Server
This server provides tools for D&D game mechanics and character management.
"""

import random
import sqlite3
from dataclasses import dataclass
from typing import Dict, List, Optional
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from mcp.server.fastmcp import FastMCP, Context
from pydantic import BaseModel, Field


# Data Models
class Character(BaseModel):
    """D&D Character data model."""
    id: Optional[int] = None
    name: str
    character_class: str
    level: int
    armor_class: int
    hit_points: int
    current_hp: int
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int


class AttackResult(BaseModel):
    """Combat attack result."""
    hit: bool
    attack_roll: int
    damage: Optional[int] = None
    critical: bool = False
    description: str


class DiceRoll(BaseModel):
    """Dice roll result."""
    dice_notation: str
    individual_rolls: List[int]
    total: int
    modifier: int


# Database setup
class Database:
    def __init__(self, db_path: str = "dnd_characters.db"):
        self.db_path = db_path
        self.conn = None
    
    async def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        await self.create_tables()
        return self
    
    async def disconnect(self):
        if self.conn:
            self.conn.close()
    
    async def create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                character_class TEXT NOT NULL,
                level INTEGER NOT NULL,
                armor_class INTEGER NOT NULL,
                hit_points INTEGER NOT NULL,
                current_hp INTEGER NOT NULL,
                strength INTEGER NOT NULL,
                dexterity INTEGER NOT NULL,
                constitution INTEGER NOT NULL,
                intelligence INTEGER NOT NULL,
                wisdom INTEGER NOT NULL,
                charisma INTEGER NOT NULL
            )
        """)
        self.conn.commit()
    
    async def save_character(self, character: Character) -> int:
        cursor = self.conn.execute("""
            INSERT INTO characters 
            (name, character_class, level, armor_class, hit_points, current_hp,
             strength, dexterity, constitution, intelligence, wisdom, charisma)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            character.name, character.character_class, character.level,
            character.armor_class, character.hit_points, character.current_hp,
            character.strength, character.dexterity, character.constitution,
            character.intelligence, character.wisdom, character.charisma
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    async def get_character(self, character_id: int) -> Optional[Character]:
        cursor = self.conn.execute(
            "SELECT * FROM characters WHERE id = ?", (character_id,)
        )
        row = cursor.fetchone()
        if row:
            return Character(
                id=row[0], name=row[1], character_class=row[2], level=row[3],
                armor_class=row[4], hit_points=row[5], current_hp=row[6],
                strength=row[7], dexterity=row[8], constitution=row[9],
                intelligence=row[10], wisdom=row[11], charisma=row[12]
            )
        return None
    
    async def list_characters(self) -> List[Character]:
        cursor = self.conn.execute("SELECT * FROM characters")
        return [
            Character(
                id=row[0], name=row[1], character_class=row[2], level=row[3],
                armor_class=row[4], hit_points=row[5], current_hp=row[6],
                strength=row[7], dexterity=row[8], constitution=row[9],
                intelligence=row[10], wisdom=row[11], charisma=row[12]
            )
            for row in cursor.fetchall()
        ]


@dataclass
class AppContext:
    """Application context with database connection."""
    db: Database


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle."""
    db = await Database().connect()
    try:
        yield AppContext(db=db)
    finally:
        await db.disconnect()


# Create MCP server
mcp = FastMCP("D&D Character Manager", lifespan=app_lifespan)


# TOOLS - Deterministic game mechanics
@mcp.tool()
def roll_dice(dice_notation: str, modifier: int = 0) -> DiceRoll:
    """
    Roll dice using standard D&D notation (e.g., '1d20', '2d6', '4d8').
    
    Args:
        dice_notation: Dice to roll in format 'XdY' (e.g., '1d20' for 1 twenty-sided die)
        modifier: Numeric modifier to add to the total
    
    Returns:
        Detailed dice roll result with individual rolls and total
    """
    try:
        # Parse dice notation (e.g., "2d6" -> 2 dice, 6 sides each)
        parts = dice_notation.lower().split('d')
        if len(parts) != 2:
            raise ValueError("Invalid dice notation. Use format like '1d20' or '2d6'")
        
        num_dice = int(parts[0])
        num_sides = int(parts[1])
        
        if num_dice <= 0 or num_sides <= 0:
            raise ValueError("Number of dice and sides must be positive")
        
        if num_dice > 20:  # Reasonable limit
            raise ValueError("Maximum 20 dice per roll")
        
        # Roll the dice
        rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
        total = sum(rolls) + modifier
        
        return DiceRoll(
            dice_notation=dice_notation,
            individual_rolls=rolls,
            total=total,
            modifier=modifier
        )
    
    except ValueError as e:
        raise ValueError(f"Dice rolling error: {str(e)}")


@mcp.tool()
def attack_roll(
    attacker_bonus: int,
    target_ac: int,
    damage_dice: str = "1d8",
    damage_bonus: int = 0
) -> AttackResult:
    """
    Perform a D&D attack roll against a target.
    
    Args:
        attacker_bonus: Attack bonus of the attacker
        target_ac: Armor Class of the target
        damage_dice: Damage dice notation (e.g., '1d8', '2d6')
        damage_bonus: Damage bonus to add
    
    Returns:
        Complete attack result with hit/miss and damage
    """
    # Roll d20 for attack
    attack_d20 = random.randint(1, 20)
    attack_total = attack_d20 + attacker_bonus
    
    # Check for critical hit/miss
    critical = attack_d20 == 20
    critical_miss = attack_d20 == 1
    
    # Determine if attack hits
    hit = attack_total >= target_ac or critical
    
    damage = None
    description = ""
    
    if hit and not critical_miss:
        # Roll damage
        damage_roll = roll_dice(damage_dice, damage_bonus)
        damage = damage_roll.total
        
        if critical:
            # Critical hit - double damage dice (not modifiers)
            crit_damage_roll = roll_dice(damage_dice, 0)
            damage += crit_damage_roll.total
            description = f"CRITICAL HIT! Attack roll: {attack_d20} + {attacker_bonus} = {attack_total} vs AC {target_ac}. Damage: {damage}"
        else:
            description = f"Hit! Attack roll: {attack_d20} + {attacker_bonus} = {attack_total} vs AC {target_ac}. Damage: {damage}"
    else:
        if critical_miss:
            description = f"Critical Miss! Rolled natural 1."
        else:
            description = f"Miss! Attack roll: {attack_d20} + {attacker_bonus} = {attack_total} vs AC {target_ac}."
    
    return AttackResult(
        hit=hit,
        attack_roll=attack_total,
        damage=damage,
        critical=critical,
        description=description
    )


@mcp.tool()
def calculate_modifier(ability_score: int) -> int:
    """
    Calculate D&D ability modifier from ability score.
    
    Args:
        ability_score: Ability score (typically 3-20)
    
    Returns:
        Ability modifier (-5 to +5 typically)
    """
    return (ability_score - 10) // 2


@mcp.tool()
async def create_character(
    name: str,
    character_class: str,
    level: int,
    strength: int,
    dexterity: int,
    constitution: int,
    intelligence: int,
    wisdom: int,
    charisma: int,
    ctx: Context
) -> Character:
    """
    Create a new D&D character and save to database.
    
    Args:
        name: Character name
        character_class: Character class (Fighter, Wizard, etc.)
        level: Character level
        strength: Strength ability score
        dexterity: Dexterity ability score
        constitution: Constitution ability score
        intelligence: Intelligence ability score
        wisdom: Wisdom ability score
        charisma: Charisma ability score
    
    Returns:
        Created character with calculated stats
    """
    # Calculate derived stats
    con_modifier = calculate_modifier(constitution)
    hit_points = 10 + con_modifier + ((level - 1) * (6 + con_modifier))  # Simplified HP calculation
    
    # Base AC (10 + Dex modifier, would need armor system for full implementation)
    dex_modifier = calculate_modifier(dexterity)
    armor_class = 10 + dex_modifier
    
    character = Character(
        name=name,
        character_class=character_class,
        level=level,
        armor_class=armor_class,
        hit_points=hit_points,
        current_hp=hit_points,
        strength=strength,
        dexterity=dexterity,
        constitution=constitution,
        intelligence=intelligence,
        wisdom=wisdom,
        charisma=charisma
    )
    
    # Save to database
    db = ctx.request_context.lifespan_context.db
    character_id = await db.save_character(character)
    character.id = character_id
    
    await ctx.info(f"Created character: {character.name} (ID: {character_id})")
    
    return character


@mcp.tool()
async def get_character_info(character_id: int, ctx: Context) -> Character:
    """
    Retrieve character information from database.
    
    Args:
        character_id: ID of the character to retrieve
    
    Returns:
        Character information
    """
    db = ctx.request_context.lifespan_context.db
    character = await db.get_character(character_id)
    
    if not character:
        raise ValueError(f"Character with ID {character_id} not found")
    
    return character


# Global database reference for resources (since they can't access context)
_global_db = None

async def get_db():
    """Get database instance for resources."""
    global _global_db
    if _global_db is None:
        _global_db = await Database().connect()
    return _global_db

# RESOURCES - Character and campaign data
@mcp.resource("character://{character_id}")
async def get_character_sheet(character_id: str) -> str:
    """Get a character sheet as formatted text."""
    try:
        char_id = int(character_id)
        db = await get_db()
        character = await db.get_character(char_id)
        
        if not character:
            return f"Character {character_id} not found"
        
        return f"""
# {character.name} - Level {character.level} {character.character_class}

## Ability Scores
- Strength: {character.strength} ({calculate_modifier(character.strength):+d})
- Dexterity: {character.dexterity} ({calculate_modifier(character.dexterity):+d})
- Constitution: {character.constitution} ({calculate_modifier(character.constitution):+d})
- Intelligence: {character.intelligence} ({calculate_modifier(character.intelligence):+d})
- Wisdom: {character.wisdom} ({calculate_modifier(character.wisdom):+d})
- Charisma: {character.charisma} ({calculate_modifier(character.charisma):+d})

## Combat Stats
- Armor Class: {character.armor_class}
- Hit Points: {character.current_hp}/{character.hit_points}
"""
    except ValueError:
        return f"Invalid character ID: {character_id}"


@mcp.resource("characters://list")
async def list_all_characters() -> str:
    """Get a list of all characters."""
    db = await get_db()
    characters = await db.list_characters()
    
    if not characters:
        return "No characters found."
    
    result = "# All Characters\n\n"
    for char in characters:
        result += f"- {char.name} (ID: {char.id}) - Level {char.level} {char.character_class}\n"
    
    return result


# PROMPTS - Templates for AI generation
@mcp.prompt()
def generate_character_name(race: str = "Human", gender: str = "any", style: str = "fantasy") -> str:
    """Generate a character name prompt for the AI."""
    return f"""Generate a {style} name for a {race} character. 
Gender preference: {gender}. 
Provide just the name, no explanation needed."""


@mcp.prompt()
def describe_combat_action(
    attacker_name: str,
    target_name: str,
    weapon: str,
    result: str
) -> str:
    """Generate a dramatic description of a combat action."""
    return f"""Describe in vivid detail how {attacker_name} attacks {target_name} with a {weapon}. 
The result was: {result}
Write 2-3 sentences in an engaging, dramatic style suitable for a D&D session."""


@mcp.prompt()
def describe_location(
    location_type: str = "dungeon room",
    mood: str = "mysterious",
    details: str = ""
) -> str:
    """Generate a location description prompt."""
    prompt = f"""Describe a {location_type} with a {mood} atmosphere for a D&D adventure."""
    
    if details:
        prompt += f" Include these elements: {details}"
    
    prompt += " Write 3-4 sentences that bring the location to life for players."
    
    return prompt


if __name__ == "__main__":
    # Run the server
     mcp.run()
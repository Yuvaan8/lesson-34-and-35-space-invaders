import math
import random
import sys

import pygame


pygame.init()

WIDTH, HEIGHT = 960, 680
TILE = 40
ROWS, COLS = 15, 24
MAP_TOP = 72
FPS = 60

DISPLAY = pygame.display.set_mode((WIDTH, HEIGHT))
SCREEN = pygame.Surface((WIDTH, HEIGHT))
pygame.display.set_caption("Solid Coward")
CLOCK = pygame.time.Clock()
FULLSCREEN = False
FONT = pygame.font.Font(None, 28)
SMALL_FONT = pygame.font.Font(None, 22)
TINY_FONT = pygame.font.Font(None, 18)
TITLE_FONT = pygame.font.Font(None, 72)


def set_fullscreen(enabled):
    global DISPLAY, FULLSCREEN
    if enabled == FULLSCREEN:
        return
    if enabled:
        DISPLAY = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        DISPLAY = pygame.display.set_mode((WIDTH, HEIGHT))
    FULLSCREEN = enabled


def display_viewport():
    display_width, display_height = DISPLAY.get_size()
    scale = min(display_width / WIDTH, display_height / HEIGHT)
    viewport_width = round(WIDTH * scale)
    viewport_height = round(HEIGHT * scale)
    left = (display_width - viewport_width) // 2
    top = (display_height - viewport_height) // 2
    return pygame.Rect(left, top, viewport_width, viewport_height)


def logical_mouse_position(position=None):
    position = pygame.mouse.get_pos() if position is None else position
    viewport = display_viewport()
    scale_x = WIDTH / viewport.width
    scale_y = HEIGHT / viewport.height
    return (round((position[0] - viewport.left) * scale_x),
            round((position[1] - viewport.top) * scale_y))


def present_screen():
    viewport = display_viewport()
    DISPLAY.fill(DARK)
    scaled_screen = pygame.transform.scale(SCREEN, viewport.size)
    DISPLAY.blit(scaled_screen, viewport.topleft)
    pygame.display.flip()


WHITE = (245, 240, 220)
DARK = (22, 24, 34)
GOLD = (244, 194, 66)
GREEN = (83, 190, 105)
RED = (214, 75, 74)

WEAPONS = {
    "sword": {"damage": 24, "range": 64, "color": (235, 230, 215), "style": "sword"},
    "bow": {"damage": 18, "range": 360, "color": (142, 205, 255), "style": "bow"},
    "dagger": {"damage": 17, "range": 48, "color": (190, 235, 190), "style": "dagger"},
    "axe": {"damage": 34, "range": 58, "color": (255, 170, 90), "style": "axe"},
    "crowbar": {"damage": 27, "range": 62, "color": (220, 150, 255), "style": "crowbar"},
    "spear": {"damage": 25, "range": 105, "color": (145, 215, 180), "style": "spear"},
    "mace": {"damage": 32, "range": 58, "color": (185, 190, 205), "style": "mace"},
}
WEAPON_ORDER = ("sword", "bow", "dagger", "axe", "crowbar", "spear", "mace")
WEAPON_MAX_LEVEL = 5
CONTROL_DEFAULTS = {
    "move_up": pygame.K_w,
    "move_down": pygame.K_s,
    "move_left": pygame.K_a,
    "move_right": pygame.K_d,
    "attack": pygame.K_SPACE,
    "special": pygame.K_q,
    "armor": pygame.K_v,
    "interact": pygame.K_f,
    "potion": pygame.K_e,
    "rune": pygame.K_r,
    "bomb": pygame.K_b,
    "inventory": pygame.K_i,
    "crafting": pygame.K_c,
    "field_guide": pygame.K_l,
    "skip_room": pygame.K_k,
    "dialogue": pygame.K_o,
    "fullscreen": pygame.K_x,
    "upgrade": pygame.K_u,
    **{f"weapon_{index}": pygame.K_1 + index - 1 for index in range(1, 8)},
}
CONTROL_LABELS = {
    "move_up": "Move up",
    "move_down": "Move down",
    "move_left": "Move left",
    "move_right": "Move right",
    "attack": "Attack",
    "special": "Weapon special",
    "armor": "Armor ability",
    "interact": "Interact",
    "potion": "Use selected potion",
    "rune": "Place selected rune",
    "bomb": "Use bomb",
    "inventory": "Open inventory",
    "crafting": "Open crafting",
    "field_guide": "Open field guide",
    "skip_room": "Skip room",
    "dialogue": "Toggle dialogue",
    "fullscreen": "Toggle fullscreen",
    "upgrade": "Upgrade weapon",
    **{f"weapon_{index}": f"Equip weapon slot {index}" for index in range(1, 8)},
}
WEAPON_BASE_COSTS = {
    "sword": {"scrap": 4, "crystals": 2},
    "bow": {"scrap": 3, "crystals": 3},
    "dagger": {"scrap": 3, "herbs": 2},
    "axe": {"scrap": 5, "cores": 1},
    "crowbar": {"scrap": 4, "cores": 1},
    "spear": {"scrap": 4, "crystals": 2},
    "mace": {"scrap": 5, "crystals": 1},
}
WEAPON_VARIANTS = {
    "sword": [
        {"name": "Iron Shortsword", "trait": "Balanced edge", "damage": 1.0, "range": 1.0,
         "special": "Crescent Cut", "ability": "crescent_cut"},
        {"name": "Sunsteel Saber", "trait": "+10% damage", "damage": 1.1, "range": 1.0,
         "special": "Solar Flare", "ability": "solar_flare"},
        {"name": "Frostbrand", "trait": "Heavy hits briefly stun", "damage": 1.18, "range": 1.0,
         "special": "Frost Nova", "ability": "frost_nova"},
        {"name": "Twin-Star Blade", "trait": "Fast recovery", "damage": 1.25, "range": 1.0,
         "special": "Twin Echo", "ability": "twin_echo"},
        {"name": "Dawncleaver", "trait": "Wide, powerful Whirlwind", "damage": 1.35, "range": 1.0,
         "special": "Dawnburst", "ability": "dawnburst"},
    ],
    "dagger": [
        {"name": "Quickfang", "trait": "Fast strikes", "damage": 1.0, "range": 1.0,
         "special": "Rapid Flurry", "ability": "rapid_flurry"},
        {"name": "Nightbite", "trait": "Longer Shadow Dash", "damage": 1.1, "range": 1.0,
         "special": "Nightfall Lunge", "ability": "nightfall_lunge"},
        {"name": "Venomglass", "trait": "Poisoned hits", "damage": 1.18, "range": 1.0,
         "special": "Venom Bloom", "ability": "venom_bloom"},
        {"name": "Ghostpoint", "trait": "Extra dash reach", "damage": 1.25, "range": 1.0,
         "special": "Phase Step", "ability": "phase_step"},
        {"name": "Eclipse Fang", "trait": "Dash strikes through nearby foes", "damage": 1.35, "range": 1.0,
         "special": "Eclipse Rend", "ability": "eclipse_rend"},
    ],
    "bow": [
        {"name": "Ashwood Bow", "trait": "Steady shot", "damage": 1.0, "range": 1.0,
         "special": "Pinning Volley", "ability": "pinning_volley"},
        {"name": "Windstring", "trait": "Longer shot range", "damage": 1.08, "range": 1.15,
         "special": "Gale Shot", "ability": "gale_shot"},
        {"name": "Moonpiercer", "trait": "Piercing arrows", "damage": 1.18, "range": 1.2,
         "special": "Lunar Lance", "ability": "lunar_lance"},
        {"name": "Stormcaller", "trait": "Wider Arrow Storm", "damage": 1.27, "range": 1.25,
         "special": "Chain Lightning", "ability": "chain_lightning"},
        {"name": "Starfall Longbow", "trait": "Five-shot piercing storm", "damage": 1.4, "range": 1.35,
         "special": "Starfall", "ability": "starfall"},
    ],
    "axe": [
        {"name": "Woodcutter Axe", "trait": "Heavy swing", "damage": 1.0, "range": 1.0,
         "special": "Timberfall", "ability": "timberfall"},
        {"name": "Stonecleaver", "trait": "Strong stagger", "damage": 1.1, "range": 1.0,
         "special": "Stone Quake", "ability": "stone_quake"},
        {"name": "Ember Axe", "trait": "Burning edge", "damage": 1.2, "range": 1.0,
         "special": "Inferno Cleave", "ability": "inferno_cleave"},
        {"name": "Mountain Splitter", "trait": "Wider Earthshaker", "damage": 1.3, "range": 1.0,
         "special": "Faultline", "ability": "faultline"},
        {"name": "Worldbreaker", "trait": "Long-range heavy stun", "damage": 1.45, "range": 1.0,
         "special": "Cataclysm", "ability": "cataclysm"},
    ],
    "crowbar": [
        {"name": "Iron Crowbar", "trait": "Reliable hook", "damage": 1.0, "range": 1.0,
         "special": "Hook and Haul", "ability": "hook_and_haul"},
        {"name": "Vaultbreaker", "trait": "Longer reach", "damage": 1.1, "range": 1.1,
         "special": "Breach Slam", "ability": "breach_slam"},
        {"name": "Rivet Ripper", "trait": "Longer stun", "damage": 1.18, "range": 1.0,
         "special": "Rivet Storm", "ability": "rivet_storm"},
        {"name": "Foundry Bar", "trait": "Heavy knockback", "damage": 1.28, "range": 1.05,
         "special": "Foundry Blast", "ability": "foundry_blast"},
        {"name": "King's Wedge", "trait": "Crushing Hook and Stun", "damage": 1.4, "range": 1.15,
         "special": "Royal Decree", "ability": "royal_decree"},
    ],
    "spear": [
        {"name": "Reed Spear", "trait": "Long-reaching thrusts", "damage": 1.0, "range": 1.0,
         "special": "Lancing Thrust", "ability": "lancing_thrust"},
        {"name": "Pike of the Gale", "trait": "Knocks foes backward", "damage": 1.1, "range": 1.05,
         "special": "Gale Repulse", "ability": "gale_repulse"},
        {"name": "Viper Pike", "trait": "Venomous strikes", "damage": 1.18, "range": 1.1,
         "special": "Viper Impale", "ability": "viper_impale"},
        {"name": "Sunlance", "trait": "Piercing line attack", "damage": 1.28, "range": 1.15,
         "special": "Sunpiercer", "ability": "sunpiercer"},
        {"name": "Worldspike", "trait": "Rallying shockwave", "damage": 1.4, "range": 1.2,
         "special": "Worldroot", "ability": "worldroot"},
    ],
    "mace": [
        {"name": "Stone Maul", "trait": "Crushing impact", "damage": 1.0, "range": 1.0,
         "special": "Quarry Slam", "ability": "quarry_slam"},
        {"name": "Iron Morningstar", "trait": "Armor-crushing blows", "damage": 1.12, "range": 1.0,
         "special": "Armor Breaker", "ability": "armor_breaker"},
        {"name": "Thunderhead", "trait": "Stunning shockwaves", "damage": 1.2, "range": 1.05,
         "special": "Thunderclap", "ability": "thunderclap"},
        {"name": "Meteor Maul", "trait": "Heavy targeted smash", "damage": 1.32, "range": 1.0,
         "special": "Meteor Drop", "ability": "meteor_drop"},
        {"name": "World Anvil", "trait": "Pulls foes into a crushing core", "damage": 1.45, "range": 1.1,
         "special": "Gravity Well", "ability": "gravity_well"},
    ],
}

WEAPON_VFX = {
    "Iron Shortsword": ("crescent", (220, 230, 245), (255, 255, 255), 1.0, 3),
    "Sunsteel Saber": ("rays", (255, 190, 65), (255, 245, 180), 1.2, 8),
    "Frostbrand": ("snowflake", (130, 220, 255), (235, 250, 255), 1.1, 6),
    "Twin-Star Blade": ("twin_stars", (125, 185, 255), (255, 235, 145), 1.0, 2),
    "Dawncleaver": ("dawn_arc", (255, 145, 75), (255, 235, 150), 1.4, 7),
    "Quickfang": ("fangs", (170, 255, 155), (245, 255, 220), 0.8, 4),
    "Nightbite": ("shadow_crescent", (105, 75, 170), (210, 170, 255), 1.2, 3),
    "Venomglass": ("venom", (110, 230, 95), (220, 255, 140), 1.0, 5),
    "Ghostpoint": ("afterimage", (180, 160, 255), (235, 225, 255), 1.1, 4),
    "Eclipse Fang": ("eclipse", (90, 75, 145), (245, 205, 95), 1.3, 5),
    "Ashwood Bow": ("leaves", (125, 205, 125), (220, 240, 150), 0.9, 4),
    "Windstring": ("wind", (135, 220, 255), (230, 250, 255), 1.1, 3),
    "Moonpiercer": ("moon_shards", (160, 185, 255), (245, 245, 255), 1.1, 4),
    "Stormcaller": ("lightning", (100, 175, 255), (245, 250, 255), 1.3, 5),
    "Starfall Longbow": ("starfall", (255, 205, 95), (255, 250, 205), 1.4, 7),
    "Woodcutter Axe": ("woodchips", (170, 125, 75), (235, 195, 115), 1.0, 5),
    "Stonecleaver": ("stone_shards", (155, 170, 190), (225, 230, 235), 1.0, 6),
    "Ember Axe": ("flames", (255, 95, 45), (255, 215, 90), 1.2, 5),
    "Mountain Splitter": ("faultline", (220, 145, 80), (255, 220, 140), 1.4, 5),
    "Worldbreaker": ("meteor", (255, 115, 65), (255, 235, 150), 1.5, 8),
    "Iron Crowbar": ("rivets", (210, 175, 245), (255, 235, 185), 1.0, 6),
    "Vaultbreaker": ("breach", (255, 175, 95), (255, 240, 190), 1.2, 4),
    "Rivet Ripper": ("rivet_storm", (200, 125, 255), (255, 225, 255), 1.2, 8),
    "Foundry Bar": ("sparks", (255, 125, 65), (255, 235, 135), 1.1, 9),
    "King's Wedge": ("royal_hook", (245, 195, 85), (255, 245, 190), 1.3, 5),
    "Reed Spear": ("reed_thrust", (115, 220, 155), (220, 255, 200), 0.9, 4),
    "Pike of the Gale": ("gale", (125, 220, 235), (225, 255, 255), 1.2, 6),
    "Viper Pike": ("viper", (150, 220, 80), (230, 255, 145), 1.0, 5),
    "Sunlance": ("sun_lance", (255, 200, 70), (255, 250, 190), 1.3, 6),
    "Worldspike": ("roots", (135, 185, 100), (220, 245, 165), 1.4, 5),
    "Stone Maul": ("boulder", (155, 165, 185), (235, 235, 245), 1.1, 5),
    "Iron Morningstar": ("spikes", (200, 210, 225), (255, 220, 145), 1.1, 8),
    "Thunderhead": ("thunderclap", (115, 175, 255), (250, 250, 255), 1.3, 7),
    "Meteor Maul": ("meteor_drop", (255, 125, 70), (255, 235, 145), 1.4, 6),
    "World Anvil": ("gravity", (185, 130, 255), (245, 220, 255), 1.5, 7),
}
for weapon_variants in WEAPON_VARIANTS.values():
    for weapon_variant in weapon_variants:
        (weapon_variant["vfx"], weapon_variant["vfx_color"],
         weapon_variant["vfx_accent"], weapon_variant["vfx_scale"],
         weapon_variant["vfx_count"]) = WEAPON_VFX[weapon_variant["name"]]

BOSS_GIMMICKS = {
    20: {"kind": "shifting_ward", "name": "The Veiled Regent",
         "hint": "Its ward cycles: strike during the brief opening."},
    25: {"kind": "blink_hunter", "name": "The Rift Stalker",
         "hint": "It blinks across the arena; keep tracking its new position."},
    30: {"kind": "soul_summoner", "name": "The Bone Conductor",
         "hint": "It summons minions and heals while they remain alive."},
    35: {"kind": "charging_boss", "name": "The Iron Juggernaut",
         "hint": "It telegraphs a charge. Dodge its straight-line rush."},
    40: {"kind": "rune_ward", "name": "The Runebound Oracle",
         "hint": "Place a rune near it to break its ward for a short time."},
    45: {"kind": "soul_leech", "name": "The Hollow Duke",
         "hint": "Contact lets it steal health; keep your distance."},
    50: {"kind": "final_form", "name": "The Sunstone Devourer",
         "hint": "At half health it enters a faster, stronger final form."},
}
RUNE_TYPES = {
    "slow": {"name": "Frost Rune", "color": (105, 190, 255), "cost": {"herbs": 2, "scrap": 2}},
    "fire": {"name": "Ember Rune", "color": (255, 115, 55), "cost": {"herbs": 2, "crystals": 1}},
    "thunder": {"name": "Thunder Rune", "color": (255, 225, 85), "cost": {"crystals": 3, "cores": 1}},
    "lure": {"name": "Lure Rune", "color": (190, 115, 255), "cost": {"herbs": 3, "crystals": 2}},
    "teleport": {"name": "Wayfinder Rune", "color": (100, 245, 220),
                 "cost": {"herbs": 2, "crystals": 3, "cores": 1}},
}
POTION_TYPES = ("health", "strength", "speed")
CRAFT_TABS = ("Supplies", "Weapons", "Armor", "Runes")
CRAFT_RECIPES = {
    "Supplies": (1, 2, 3, 4),
    "Weapons": WEAPON_ORDER,
    "Armor": (10, 11, 12, 13, 21, 22, 23),
    "Runes": (14, 15, 16, 17, 20),
}
SPECIAL_ARMOR = {
    "knight": {
        "name": "Knight Armor",
        "description": "+25% damage | V parries next hit",
        "cost": {"scrap": 5, "herbs": 10, "cores": 10},
    },
    "samurai": {
        "name": "Samurai Armor",
        "description": "+20% speed | V dashes",
        "cost": {"scrap": 15, "herbs": 15, "crystals": 5, "cores": 15},
    },
    "phantom": {
        "name": "Phantom Armor",
        "description": "V cloaks 5s | costs 40% max HP",
        "cost": {"scrap": 15, "herbs": 15, "crystals": 8, "cores": 20},
    },
}
ARMOR_WEIGHT = {"helmet": 1, "chestplate": 3, "leggings": 2, "boots": 1}
ARMOR_PROTECTION = {"helmet": 0.15, "chestplate": 0.35, "leggings": 0.20, "boots": 0.15}

# Each wall is a rectangle in map tiles: (left, top, width, height).
LEVEL_TEMPLATES = [
    {
        "name": "Mossy Entrance", "floor": (50, 76, 62), "wall": (91, 111, 77),
        "walls": [(6, 2, 1, 5), (6, 9, 1, 4), (12, 1, 1, 4), (12, 7, 1, 6),
                  (18, 2, 1, 5), (18, 9, 1, 4)],
        "enemies": [(7, 3, 35, 7), (10, 11, 40, 8), (16, 5, 40, 8), (20, 11, 45, 9)],
        "chest": (3, 12),
    },
    {
        "name": "Crystal Caverns", "floor": (46, 65, 87), "wall": (76, 112, 145),
        "walls": [(4, 3, 5, 1), (4, 4, 1, 3), (10, 1, 1, 5), (10, 8, 1, 5),
                  (14, 3, 1, 4), (14, 9, 1, 5), (18, 2, 4, 1), (20, 3, 1, 4)],
        "enemies": [(8, 10, 45, 9), (12, 6, 50, 9), (17, 11, 50, 10), (21, 7, 55, 10)],
        "chest": (6, 13),
    },
    {
        "name": "Ashen Halls", "floor": (82, 57, 48), "wall": (130, 77, 54),
        "walls": [(3, 2, 1, 5), (3, 9, 1, 4), (7, 5, 5, 1), (7, 10, 5, 1),
                  (15, 2, 1, 4), (15, 8, 1, 5), (19, 4, 1, 5), (19, 11, 3, 1)],
        "enemies": [(6, 3, 55, 10), (12, 7, 60, 11), (17, 11, 60, 11), (21, 3, 65, 12)],
        "chest": (11, 2),
    },
    {
        "name": "Tomato King's Keep", "floor": (66, 48, 69), "wall": (115, 77, 112),
        "walls": [(5, 2, 1, 4), (5, 8, 1, 5), (9, 4, 1, 7), (14, 1, 1, 5),
                  (14, 8, 1, 6), (19, 2, 1, 4), (19, 8, 1, 5)],
        "enemies": [(8, 2, 65, 11), (12, 11, 70, 12), (17, 5, 70, 12), (21, 11, 115, 15)],
        "chest": (3, 8),
    },
    {
        "name": "The Shattered Throne", "floor": (77, 43, 48), "wall": (139, 66, 61),
        "walls": [(4, 2, 1, 4), (4, 8, 1, 5), (8, 3, 1, 8), (12, 1, 1, 4),
                  (12, 7, 1, 7), (16, 3, 1, 4), (16, 9, 1, 4), (20, 2, 1, 4)],
        "enemies": [(6, 11, 75, 12), (11, 5, 80, 13), (18, 11, 90, 14), (21, 7, 230, 18)],
        "chest": (3, 12),
    },
]

LEVELS = []
for level_number in range(1, 51):
    template = LEVEL_TEMPLATES[(level_number - 1) % len(LEVEL_TEMPLATES)]
    scale = 1 + 0.12 * (level_number - 1)
    scaled_enemies = []
    boss_level = level_number % 5 == 0
    for enemy_index, (x, y, base_hp, base_damage) in enumerate(template["enemies"]):
        if boss_level and enemy_index == len(template["enemies"]) - 1:
            boss_rank = level_number // 5 - 1
            hp, damage = 230 + boss_rank * 180, 18 + boss_rank * 8
        else:
            hp = round(base_hp * scale)
            damage = base_damage + (level_number - 1) // 3
        scaled_enemies.append((x, y, hp, damage))
    level = dict(template)
    level["enemies"] = scaled_enemies
    level["name"] = template["name"] if level_number <= 5 else f"{template['name']} — Depth {level_number}"
    if level_number in BOSS_GIMMICKS:
        level["name"] = BOSS_GIMMICKS[level_number]["name"]
        level["boss_gimmick"] = BOSS_GIMMICKS[level_number]
    LEVELS.append(level)

LEVEL_STORIES = [
    "The Tomato Kingdom's patrols have overrun the forest road. Mira's trail leads below.",
    "The crystals remember the valley before the Tomato King covered it in darkness.",
    "The ash marks the Tomato Kingdom's failed attempts to control the Sunstone.",
    "Beyond this keep, the Tomato King's forces guard the path to Mira.",
    "The Tomato Kingdom's strongest guardian blocks the way. Mira is still waiting.",
]

OPENING_STORY = [
    {"speaker": "NARRATOR", "text": "The Tomato Kingdom invaded the valley and stole your sister, Mira."},
    {"speaker": "YOU", "text": "I will bring her home. No kingdom, king, or dungeon will stop me."},
    {"speaker": "NARRATOR", "text": "The Tomato King hides behind ten bosses across fifty dangerous levels."},
    {"speaker": "NARRATOR", "text": "This is only the first chapter of a longer journey toward level 100. Press ENTER."},
]

TEN_LEVEL_COURAGE_STORIES = {
    10: [
        {"speaker": "YOU", "text": "Ten floors down. My hands are shaking. Nah, ID WIN"},
        {"speaker": "MIRA", "text": "You are lowk stupid but no fear please."},
        {"speaker": "YOU", "text": "I'm still afraid... but I can keep going. I want Mira to know I tried."},
    ],
    20: [
        {"speaker": "YOU", "text": "Another ten floors. I keep thinking I should turn back. I miss my sister."},
        {"speaker": "MIRA", "text": "Remember that storm in solid cowards: Origin? HELP ME."},
        {"speaker": "YOU", "text": "I remember. I can carry that with me."},
    ],
    30: [
        {"speaker": "YOU", "text": "The Tomato Kingdom feels endless. Maybe I can't do this."},
        {"speaker": "MIRA", "text": "You don't have to finish the whole journey today. Just make it through this room. I believe in you."},
        {"speaker": "YOU", "text": "One room at a time. I'm coming, Mira."},
    ],
    40: [
        {"speaker": "YOU", "text": "I want to give up. I'm scared, the tomato king is said to be a master of kunji."},
        {"speaker": "MIRA", "text": "You are my family, not a hero in a story. Rest when you need to, then take the next step. I love you."},
        {"speaker": "YOU", "text": "I love you too. I'll keep going, one careful step at a time."},
    ],
    50: [
        {"speaker": "YOU", "text": "Fifty floors. I'm terrified to face what's next. I don't know if I can reach the Tomato King."},
        {"speaker": "MIRA", "text": "You made it this far while afraid. That's courage. I'll be waiting, and we'll face the rest together."},
        {"speaker": "YOU", "text": "I need to train in the mystic arts of kunji."},
    ],
}

ROOM_PUZZLES = {
    6: {"kind": "arrange", "start": ["moon", "flame", "sun", "leaf"],
        "goal": ["sun", "moon", "leaf", "flame"],
        "clue": "Arrange the relics: Sun first. Moon immediately follows Sun. Leaf immediately precedes Flame."},
    7: {"kind": "sequence", "symbols": ["SUN", "LEAF", "MOON"],
        "goal": ["LEAF", "MOON", "SUN"],
        "clue": "Pull the carved levers: Leaf before Moon. Sun must be last."},
    8: {"kind": "crates", "start": ["CROWN", "ORB", "KEY", "MASK"],
        "goal": ["KEY", "MASK", "CROWN", "ORB"],
        "clue": "Slide the crates into order: Key first, Mask second. Crown is immediately before Orb."},
    9: {"kind": "path", "goal": ["UP", "RIGHT", "RIGHT", "DOWN"],
        "clue": "Trace the safe floor: step north once, east twice, then south once."},
    10: {"kind": "sequence", "symbols": ["SUN", "LEAF", "MOON"],
         "goal": ["LEAF", "MOON", "SUN"],
         "clue": "The dead king's lever order: Leaf first, Moon second, Sun last."},
    11: {"kind": "mirrors", "start": [0, 0, 0], "goal": [1, 3, 2],
         "clue": "Turn the mirrors to match the beams: left mirror right, middle mirror left, right mirror down."},
    12: {"kind": "sequence", "symbols": ["WATER", "ROOT", "STONE", "WIND"],
         "goal": ["STONE", "WATER", "WIND", "ROOT"],
         "clue": "Turn the four valves: Stone, then Water, then Wind, and Root last."},
    13: {"kind": "doors", "choices": ["IRON", "IVY", "ASH", "GLASS"], "goal": "IVY",
         "clue": "Choose the door hidden by the clue: it grows without soil, climbs without feet, and wears green."},
    14: {"kind": "sequence", "symbols": ["BELL", "BIRD", "WAVE", "FLAME"],
         "goal": ["BIRD", "BELL", "FLAME", "WAVE"],
         "clue": "Repeat the wall's silent symbols: Bird, Bell, Flame, Wave."},
    15: {"kind": "final_levers", "symbols": ["MOON", "SUN", "LEAF"],
         "goal": ["MOON", "SUN", "LEAF"],
         "clue": "The shield fades only if you pull Moon first, Sun second, Leaf last."},
}


def toggle_rune_grid(tiles, index):
    row, col = divmod(index, 3)
    for next_row, next_col in ((row, col), (row - 1, col), (row + 1, col),
                                (row, col - 1), (row, col + 1)):
         if 0 <= next_row < 3 and 0 <= next_col < 3:
             cell = next_row * 3 + next_col
             tiles[cell] = not tiles[cell]


for puzzle_level in range(16, 51):
    if puzzle_level % 5 == 0:
         continue
    if puzzle_level % 2 == 0:
         goal = [bool((cell + puzzle_level) % 3 == 0 or (cell * puzzle_level) % 7 == 0)
                 for cell in range(9)]
         start = goal[:]
         for cell in ((puzzle_level * 3) % 9, (puzzle_level + 4) % 9, (puzzle_level * 2 + 1) % 9):
             toggle_rune_grid(start, cell)
         ROOM_PUZZLES[puzzle_level] = {
             "kind": "rune_grid", "start": start, "goal": goal,
             "clue": "Restore the constellation: each rune flips itself and its orthogonal neighbors.",
         }
    else:
         cards = ["SUN", "MOON", "LEAF", "FLAME", "SUN", "MOON", "LEAF", "FLAME"]
         shift = puzzle_level % len(cards)
         ROOM_PUZZLES[puzzle_level] = {
             "kind": "pairs", "cards": cards[shift:] + cards[:shift],
             "clue": "Find all four matching pairs. Select a tablet and press SPACE to reveal it.",
         }


ARTIFACT_COLORS = {
    "sun": (245, 190, 55),
    "moon": (155, 190, 235),
    "leaf": (95, 190, 105),
    "flame": (230, 95, 55),
}

PUZZLE_COLORS = {
    "sun": (245, 190, 55), "moon": (155, 190, 235),
    "leaf": (95, 190, 105), "flame": (230, 95, 55),
    "CROWN": (235, 190, 80), "ORB": (120, 185, 245),
    "KEY": (230, 215, 155), "MASK": (190, 125, 190),
    "SUN": (245, 190, 55), "LEAF": (95, 190, 105), "MOON": (155, 190, 235),
    "WATER": (90, 165, 240), "ROOT": (115, 145, 75),
    "STONE": (150, 150, 160), "WIND": (190, 220, 220),
    "BELL": (235, 195, 85), "BIRD": (125, 200, 150),
    "WAVE": (85, 155, 230), "FLAME": (235, 100, 60),
}


def story_for_level(index):
    story = LEVEL_STORIES[index % len(LEVEL_STORIES)]
    if index >= 5:
        story = f"You descend to level {index + 1}. The monsters are stronger now. {story}"
    return {"speaker": "NARRATOR", "text": story}


def boss_dialogue_for_level(level_number):
    boss_number = level_number // 5
    boss = BOSS_GIMMICKS.get(level_number)
    boss_name = boss["name"] if boss else f"Tomato Kingdom Guardian {boss_number}"
    boss_hint = boss["hint"] if boss else "You will never pass the Tomato King's defenses."
    return [
        {"speaker": boss_name.upper(),
         "text": f"The Tomato King has your sister. He says the dungeon will break you before you reach him."},
        {"speaker": "YOU",
         "text": f"Mira is in danger, and you are standing between us. I will not turn back."},
        {"speaker": boss_name.upper(),
         "text": f"Brave words. The Tomato Kingdom reaches far beyond this floor. {boss_hint}"},
    ]


def weapon_crafting_remark(weapon_name):
    remarks = {
        "Iron Shortsword": "The balance is better than I thought, dang.",
        "Sunsteel Saber": "That edge catches the light. Maybe im a magician!.",
        "Frostbrand": "The frost pattern came out clean. I made this with my own hands.",
        "Twin-Star Blade": "Two matching edges, wonder whos older",
        "Dawncleaver": "A bright blade for a dark place, im wise.",
        "Quickfang": "Light, quick, and neat. I think i can eat this",
        "Nightbite": "A little blade small- no, no. Im changed.",
        "Venomglass": "The green glass thing does something.",
        "Ghostpoint": "It literally disappears. this is peak.",
        "Eclipse Fang": "50% bad, 50% good ahh.",
        "Ashwood Bow": "this is broken vfx lol what an idiot.",
        "Windstring": "Couldnt have yuvaan done it better lol.",
        "Moonpiercer": "bro chatgpted names and just copied it haha",
        "Stormcaller": "IM THOR!!!",
        "Starfall Longbow": "On darkest days, on brightest nights, no evil shal- whats the oath?.",
        "Woodcutter Axe": "A solid axe, i could chop a lot with this",
        "Stonecleaver": "This sucks, im bad at crafting.",
        "Ember Axe": "looks hot, get it?",
        "Mountain Splitter": "This cant split a mountain.",
        "Worldbreaker": "I DID IT, YES! cant break the world tho",
        "Iron Crowbar": "pretty mid.",
        "Vaultbreaker": "OOOOOOOOOOOOOOO.",
        "Rivet Ripper": "IT rips stuff.",
        "Foundry Bar": "uh, what even is this.",
        "King's Wedge": "BOW BEFORE ME, YE SCALLYWAGS, peak king btw.",
        "Reed Spear": "lowk this is the best.",
        "Pike of the Gale": "windpiercer ahh.",
        "Viper Pike": "thx viper!.",
        "Sunlance": "It kinda shiny.",
        "Worldspike": "Magic sucks",
        "Stone Maul": "stone sucks",
        "Iron Morningstar": "THE MORNING IS A STAR AHAHAHHAHAHA.",
        "Thunderhead": "THOR ODINSON.",
        "Meteor Maul": "METOR!!!",
        "World Anvil": "What did i just make.",
    }
    return remarks.get(weapon_name, f"I made {weapon_name} myself. I hope Mira knows I am trying to be brave.")


def dialogue_for_level(index):
    level_number = index + 1
    if level_number % 5 == 0:
        courage_pages = TEN_LEVEL_COURAGE_STORIES.get(level_number, [])
        return courage_pages + boss_dialogue_for_level(level_number)
    return [story_for_level(index)]


class Hero:
    def __init__(self):
        self.rect = pygame.Rect(TILE + 7, MAP_TOP + TILE + 7, 26, 26)
        self.hp = 100
        self.max_hp = 100
        self.potions = 3
        self.speed = 220
        self.attack_cooldown = 0
        self.special_cooldown = 0
        self.action_timer = 0
        self.invulnerable = 0
        self.parry_timer = 0
        self.armor_cooldown = 0
        self.phantom_timer = 0
        self.regen_delay = 0
        self.auto_heal_cooldown = 0
        self.strength_timer = 0
        self.speed_timer = 0
        self.facing = pygame.Vector2(1, 0)
        self.weapons = {"sword": 1}
        self.weapon_tiers = {"sword": 1}
        self.weapon = "sword"
        self.moving = False
        self.animation_time = 0
        self.special_vfx = ""
        self.special_vfx_timer = 0
        self.special_vfx_duration = 0.6
        self.special_vfx_start = self.rect.center
        self.special_vfx_end = self.rect.center
        self.special_vfx_color = WHITE
        self.special_vfx_accent = GOLD
        self.special_vfx_scale = 1.0
        self.special_vfx_count = 3
        self.special_vfx_variant = WEAPON_VARIANTS["sword"][0]
        self.bark_text = ""
        self.bark_timer = 0
        self.bark_cooldown = 0
        self.ambient_dialogue_timer = 4.0
        self.dialogue_mode = None
        self.dialogue_enabled = True
        self.room_had_enemies = False
        self.room_clear_spoken = False
        self.materials = {"scrap": 0, "herbs": 0, "crystals": 0, "cores": 0}
        self.weapon_upgrades = {name: 0 for name in WEAPON_ORDER}
        self.items = {"strength": 0, "speed": 0, "bomb": 0}
        self.equipment = {"helmet": False, "chestplate": False, "leggings": False, "boots": False}
        self.special_armors = {name: False for name in SPECIAL_ARMOR}
        self.special_armor = None
        self.runes = {kind: 0 for kind in RUNE_TYPES}
        self.selected_rune = "slow"
        self.selected_potion = "health"


class Enemy:
    def __init__(self, tile_x, tile_y, hp, damage, level_index, is_boss=False):
        size = 38 if is_boss else 26
        self.rect = pygame.Rect(tile_x * TILE + (TILE - size) // 2,
                                MAP_TOP + tile_y * TILE + (TILE - size) // 2, size, size)
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.speed = (47 if is_boss else 62) + level_index * 5
        self.attack_cooldown = 0
        self.stun_timer = 0
        self.hit_flash = 0
        self.is_boss = is_boss
        self.animation_time = random.random() * math.tau
        self.attack_flash = 0
        self.shielded = False
        self.slow_timer = 0
        self.burn_timer = 0
        self.burn_tick = 0
        self.venom_timer = 0
        self.venom_tick = 0
        self.lure_timer = 0
        self.lure_target = None
        self.boss_gimmick = None
        self.boss_name = ""
        self.gimmick_timer = 0
        self.gimmick_active = False
        self.charge_target = None
        self.is_summoned = False
        self.final_form = False


class LootChest:
    def __init__(self, tile_x, tile_y):
        self.rect = pygame.Rect(tile_x * TILE + 5, MAP_TOP + tile_y * TILE + 7, 30, 26)
        self.opened = False
        self.animation_time = random.random() * math.tau


class Lever:
    def __init__(self, x, y, symbol):
        self.rect = pygame.Rect(x * TILE + 8, MAP_TOP + y * TILE + 4, 24, 34)
        self.symbol = symbol
        self.pulled = False
        self.animation = 0


class MaterialDrop:
    COLORS = {
        "scrap": (195, 190, 170),
        "herbs": (95, 220, 115),
        "crystals": (110, 210, 255),
        "cores": (255, 95, 105),
    }

    def __init__(self, x, y, kind, amount):
        self.rect = pygame.Rect(x - 9, y - 9, 18, 18)
        self.kind = kind
        self.amount = amount
        self.animation_time = random.random() * math.tau


class Explosion:
    def __init__(self, x, y):
        self.center = (x, y)
        self.timer = 0
        self.duration = 0.55
        self.max_radius = 150


class RuneTrap:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.center = (round(x), round(y))
        self.timer = 7.0
        self.pulse_timer = 0


class Arrow:
    def __init__(self, x, y, direction, damage, color, piercing=False):
        direction = pygame.Vector2(direction)
        if direction.length_squared() == 0:
            direction = pygame.Vector2(1, 0)
        self.pos = pygame.Vector2(x, y)
        self.velocity = direction.normalize() * 430
        self.rect = pygame.Rect(round(x - 5), round(y - 3), 10, 6)
        self.damage = damage
        self.color = color
        self.piercing = piercing
        self.hit_enemies = set()
        self.alive = True


def wall_rects(level):
    walls = [pygame.Rect(x * TILE, MAP_TOP + y * TILE, w * TILE, h * TILE)
             for x, y, w, h in level["walls"]]
    # Solid outer border.
    walls.extend([
        pygame.Rect(0, MAP_TOP, WIDTH, TILE),
        pygame.Rect(0, MAP_TOP + (ROWS - 1) * TILE, WIDTH, TILE),
        pygame.Rect(0, MAP_TOP, TILE, ROWS * TILE),
        pygame.Rect((COLS - 1) * TILE, MAP_TOP, TILE, ROWS * TILE),
    ])
    return walls


def move_with_walls(rect, dx, dy, walls):
    rect.x += round(dx)
    for wall in walls:
        if rect.colliderect(wall):
            if dx > 0:
                rect.right = wall.left
            elif dx < 0:
                rect.left = wall.right
    rect.y += round(dy)
    for wall in walls:
        if rect.colliderect(wall):
            if dy > 0:
                rect.bottom = wall.top
            elif dy < 0:
                rect.top = wall.bottom


def new_level(index):
    data = LEVELS[index]
    level_number = index + 1
    boss_gimmick = data.get("boss_gimmick")
    foes = [Enemy(x, y, hp, damage, index, is_boss=(index % 5 == 4 and i == len(data["enemies"]) - 1))
            for i, (x, y, hp, damage) in enumerate(data["enemies"])]
    if boss_gimmick:
        boss = foes[-1]
        boss.boss_gimmick = boss_gimmick["kind"]
        boss.boss_name = boss_gimmick["name"]
        boss.gimmick_timer = {"shifting_ward": 2.5, "blink_hunter": 5.0,
                              "soul_summoner": 10.0, "charging_boss": 3.0,
                              "rune_ward": 0.0, "soul_leech": 0.0,
                              "final_form": 0.0}[boss.boss_gimmick]
        if boss.boss_gimmick in ("shifting_ward", "rune_ward"):
            boss.shielded = True
    if index == 14:
        foes[-1].shielded = True
    chest = LootChest(*data["chest"])
    levers = [Lever(4, 13, "SUN"), Lever(6, 13, "LEAF"), Lever(8, 13, "MOON")]
    return foes, wall_rects(data), chest, levers


def update_boss_gimmicks(enemies, hero, walls, level_index, dt):
    summoned = []
    messages = []
    for boss in (enemy for enemy in enemies if enemy.boss_gimmick):
        boss.gimmick_timer = max(0, boss.gimmick_timer - dt)
        if boss.boss_gimmick == "shifting_ward" and boss.gimmick_timer <= 0:
            boss.gimmick_active = not boss.gimmick_active
            boss.shielded = not boss.gimmick_active
            boss.gimmick_timer = 2.0 if boss.gimmick_active else 3.0
            messages.append("The Veiled Regent's ward opens!" if boss.gimmick_active
                            else "The Veiled Regent raises its ward.")
        elif boss.boss_gimmick == "blink_hunter" and boss.gimmick_timer <= 0:
            positions = []
            for tile_y in range(1, ROWS - 1):
                for tile_x in range(1, COLS - 1):
                    candidate = pygame.Rect(tile_x * TILE + 1, MAP_TOP + tile_y * TILE + 1,
                                            boss.rect.width, boss.rect.height)
                    if (pygame.Vector2(candidate.center).distance_to(hero.rect.center) >= 180
                            and not any(candidate.colliderect(wall) for wall in walls)
                            and not any(candidate.colliderect(other.rect) for other in enemies
                                        if other is not boss)):
                        positions.append(candidate.center)
            if positions:
                boss.rect.center = random.choice(positions)
                messages.append("The Rift Stalker well he teleports!")
            boss.gimmick_timer = 5.0
        elif boss.boss_gimmick == "soul_summoner":
            living_summons = [enemy for enemy in enemies
                              if enemy.is_summoned and enemy.hp > 0]
            if living_summons:
                boss.hp = min(boss.max_hp, boss.hp + 2.5 * dt * len(living_summons))
            if boss.gimmick_timer <= 0:
                if len(living_summons) < 2:
                    spawn_positions = []
                    for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
                        tile_x = max(1, min(COLS - 2, boss.rect.centerx // TILE + dx))
                        tile_y = max(1, min(ROWS - 2, (boss.rect.centery - MAP_TOP) // TILE + dy))
                        candidate = pygame.Rect(tile_x * TILE + 7, MAP_TOP + tile_y * TILE + 7, 26, 26)
                        if (not any(candidate.colliderect(wall) for wall in walls)
                                and not any(candidate.colliderect(other.rect)
                                            for other in enemies + summoned)):
                            spawn_positions.append((tile_x, tile_y))
                    if spawn_positions:
                        tile_x, tile_y = random.choice(spawn_positions)
                        minion = Enemy(tile_x, tile_y, max(35, round(boss.max_hp * 0.1)),
                                       max(5, round(boss.damage * 0.55)), level_index)
                        minion.is_summoned = True
                        summoned.append(minion)
                        messages.append("The Bone Conductor summons a soul? necromacer type crap")
                boss.gimmick_timer = 8.0
        elif boss.boss_gimmick == "charging_boss":
            if hero.phantom_timer > 0:
                boss.gimmick_active = False
                boss.charge_target = None
                boss.gimmick_timer = max(boss.gimmick_timer, 1.0)
            elif boss.gimmick_active and boss.gimmick_timer <= 0:
                boss.gimmick_active = False
                boss.charge_target = None
                boss.gimmick_timer = 3.0
            elif not boss.gimmick_active and boss.gimmick_timer <= 0:
                boss.gimmick_active = True
                boss.charge_target = hero.rect.center
                boss.gimmick_timer = 0.9
                messages.append("The Iron Juggernaut lowers its head like a bull lol")
        elif boss.boss_gimmick == "rune_ward":
            if boss.gimmick_timer <= 0:
                boss.shielded = True
            else:
                boss.shielded = False
        elif boss.boss_gimmick == "final_form" and not boss.final_form:
            if boss.hp <= boss.max_hp * 0.5:
                boss.final_form = True
                messages.append("The Sunstone Devourer? what a bum")
    enemies.extend(summoned)
    return messages


def draw_text(surface, text, font, color, center):
    image = font.render(text, True, color)
    surface.blit(image, image.get_rect(center=center))


def damage_enemy(enemy, amount):
    if enemy.shielded:
        return
    enemy.hp -= amount
    enemy.hit_flash = 0.14


def collect_defeated_enemies(enemies, drops, hero=None):
    survivors = []
    defeated = []
    for enemy in enemies:
        if enemy.hp > 0:
            survivors.append(enemy)
            continue
        defeated.append(enemy)
        x, y = enemy.rect.center
        drops.append(MaterialDrop(x, y, "scrap", random.randint(1, 3)))
        if random.random() < 0.55:
            drops.append(MaterialDrop(x + random.randint(-12, 12), y, "herbs", random.randint(1, 2)))
        if random.random() < 0.40:
            drops.append(MaterialDrop(x, y + random.randint(-12, 12), "crystals", 1))
        if enemy.is_boss:
            drops.append(MaterialDrop(x + 10, y + 10, "cores", random.randint(2, 4)))
    enemies[:] = survivors
    if hero and defeated:
        if any(enemy.is_boss for enemy in defeated):
            line = random.choice((
                "I BEAT TO A BOSS LETS GO",
                "WHAT THE GOOGOOGAGA WAS THAT.",
                "YESSSS YESSS, IM COMING!!",
            ))
        else:
            line = random.choice((
                "im sorry young one",
                "ez gg+ratio",
                "yall lowk weak",
                "YO WHAT DID I DO??",
            ))
        trigger_player_bark(hero, line, force=True)


def open_loot_chest(hero):
    hero.materials["scrap"] += random.randint(2, 4)
    roll = random.random()
    if roll < 0.10:
        hero.materials["cores"] += 1
        material_reward = "a core"
    elif roll < 0.70:
        amount = random.randint(1, 3)
        hero.materials["herbs"] += amount
        material_reward = f"{amount} herbs"
    elif roll < 0.90:
        amount = random.randint(1, 2)
        hero.materials["crystals"] += amount
        material_reward = f"{amount} crystals"
    else:
        material_reward = "no rare material"

    upgrades = [name for name in WEAPON_ORDER
                if hero.weapons.get(name, 0) < WEAPON_MAX_LEVEL]
    if upgrades:
        weapon = random.choice(upgrades)
        hero.weapons[weapon] = hero.weapons.get(weapon, 0) + 1
        hero.weapon_tiers[weapon] = hero.weapons[weapon]
        hero.weapon = weapon
        weapon_reward = f"{get_weapon_variant(hero)['name']} Lv{hero.weapon_tiers[weapon]}"
    else:
        weapon_reward = "all weapons are max level"
    return f"Chest: +scrap, {material_reward}, {weapon_reward}."


def weapon_recipe_cost(category, rank):
    cost = dict(WEAPON_BASE_COSTS[category])
    if rank > 1:
        cost["scrap"] = cost.get("scrap", 0) + (rank - 1) * 2
        cost["crystals"] = cost.get("crystals", 0) + (rank - 1)
    core_costs = {1: 1, 2: 3, 3: 5, 4: 7, 5: 10}
    if rank in core_costs:
        cost["cores"] = core_costs[rank]
    return cost


def craft_item(hero, choice):
    recipes = {
        1: ("potion", {"herbs": 3, "scrap": 2}),
        2: ("strength", {"herbs": 2, "crystals": 2}),
        3: ("speed", {"herbs": 2, "scrap": 1, "crystals": 2}),
        4: ("bomb", {"scrap": 4, "crystals": 1}),
        5: ("sword", {"scrap": 4, "crystals": 2}),
        6: ("bow", {"scrap": 3, "crystals": 3}),
        7: ("dagger", {"scrap": 3, "herbs": 2}),
        8: ("axe", {"scrap": 5, "cores": 1}),
        9: ("crowbar", {"scrap": 4, "cores": 1}),
        10: ("helmet", {"scrap": 3, "crystals": 2}),
        11: ("chestplate", {"scrap": 6, "crystals": 4, "cores": 1}),
        12: ("leggings", {"scrap": 4, "crystals": 3}),
        13: ("boots", {"scrap": 2, "herbs": 2}),
        14: ("rune_slow", RUNE_TYPES["slow"]["cost"]),
        15: ("rune_fire", RUNE_TYPES["fire"]["cost"]),
        16: ("rune_thunder", RUNE_TYPES["thunder"]["cost"]),
        17: ("rune_lure", RUNE_TYPES["lure"]["cost"]),
        18: ("spear", WEAPON_BASE_COSTS["spear"]),
        19: ("mace", WEAPON_BASE_COSTS["mace"]),
        20: ("rune_teleport", RUNE_TYPES["teleport"]["cost"]),
        21: ("knight_armor", SPECIAL_ARMOR["knight"]["cost"]),
        22: ("samurai_armor", SPECIAL_ARMOR["samurai"]["cost"]),
        23: ("phantom_armor", SPECIAL_ARMOR["phantom"]["cost"]),
    }
    if choice not in recipes:
        return "That recipe is not available."
    item, cost = recipes[choice]
    if item in WEAPONS:
        next_rank = hero.weapons.get(item, 0) + 1
        cost = weapon_recipe_cost(item, next_rank)
    if item in WEAPONS and hero.weapons.get(item, 0) >= WEAPON_MAX_LEVEL:
        return f"{item.title()} is already at maximum level {WEAPON_MAX_LEVEL}."
    if item in hero.equipment and hero.equipment[item]:
        return f"You already have {item} equipped."
    if item.endswith("_armor"):
        armor_name = item.removesuffix("_armor")
        if hero.special_armors[armor_name]:
            hero.special_armor = armor_name
            return f"Equipped {SPECIAL_ARMOR[armor_name]['name']}."
    if any(hero.materials[kind] < amount for kind, amount in cost.items()):
        return "Not enough materials for that recipe."
    for kind, amount in cost.items():
        hero.materials[kind] -= amount
    if item == "potion":
        hero.potions += 1
        return "Crafted a health potion."
    if item.startswith("rune_"):
        rune = item.removeprefix("rune_")
        hero.runes[rune] += 1
        article = "an" if rune == "fire" else "a"
        return f"Crafted {article} {RUNE_TYPES[rune]['name']}."
    if item in hero.items:
        hero.items[item] += 1
        return f"Crafted a {item} item."
    if item in hero.equipment:
        hero.equipment[item] = True
        return f"Crafted and equipped {item}. It adds armor but slows movement."
    if item.endswith("_armor"):
        armor_name = item.removesuffix("_armor")
        hero.special_armors[armor_name] = True
        hero.special_armor = armor_name
        return f"Crafted and equipped {SPECIAL_ARMOR[armor_name]['name']}!"
    hero.weapons[item] = hero.weapons.get(item, 0) + 1
    hero.weapon_tiers[item] = hero.weapons[item]
    hero.weapon = item
    weapon_name = get_weapon_variant(hero)["name"]
    remark = weapon_crafting_remark(weapon_name) if hero.dialogue_enabled else ""
    return f"Crafted and equipped {weapon_name}! {remark}".strip()


def craft_weapon_tier(hero, category, tier):
    unlocked_rank = hero.weapons.get(category, 0)
    if tier <= unlocked_rank:
        hero.weapon = category
        hero.weapon_tiers[category] = tier
        return f"Equipped {WEAPON_VARIANTS[category][tier - 1]['name']}."
    if tier != unlocked_rank + 1:
        return f"Craft weapon tier {unlocked_rank + 1} first."
    choice = {"sword": 5, "bow": 6, "dagger": 7, "axe": 8, "crowbar": 9,
              "spear": 18, "mace": 19}[category]
    return craft_item(hero, choice)


def upgrade_weapon(hero, category):
    if hero.weapons.get(category, 0) <= 0:
        return f"Craft a {category} before upgrading it."
    if hero.materials["cores"] < 3:
        return "A weapon upgrade costs 3 cores."
    hero.materials["cores"] -= 3
    hero.weapon_upgrades[category] += 1
    bonus = hero.weapon_upgrades[category] * 10
    return f"{category.title()} upgraded! Damage bonus is now +{bonus}%."


def place_rune(hero, enemies, runes, position, walls):
    kind = hero.selected_rune
    if hero.runes[kind] <= 0:
        return f"No {RUNE_TYPES[kind]['name']}s left to place."
    x, y = position
    if not (TILE <= x < (COLS - 1) * TILE
            and MAP_TOP + TILE <= y < MAP_TOP + (ROWS - 1) * TILE):
        return "Place runes inside the dungeon."
    if any(wall.collidepoint(position) for wall in walls):
        return "Runes cannot be placed inside walls."
    if kind == "teleport":
        destination = hero.rect.copy()
        destination.center = position
        if (destination.left < TILE or destination.right > (COLS - 1) * TILE
                or destination.top < MAP_TOP + TILE
                or destination.bottom > MAP_TOP + (ROWS - 1) * TILE
                or any(destination.colliderect(wall) for wall in walls)):
            return "Choose a clear, open spot to teleport to."
        hero.runes[kind] -= 1
        hero.rect = destination
        hero.invulnerable = max(hero.invulnerable, 0.5)
        hero.facing = pygame.Vector2(1, 0)
        trigger_player_bark(hero, "Whoa... the rune moved me across the room. AMAZING YOO.", 2.4, force=True)
        return "Wayfinder Rune! Teleported to the selected spot."
    hero.runes[kind] -= 1
    rune = RuneTrap(kind, x, y)
    runes.append(rune)
    ward_message = ""
    awakened_boss = next((enemy for enemy in enemies
                          if enemy.boss_gimmick == "rune_ward"
                          and pygame.Vector2(enemy.rect.center).distance_to(position) <= 150), None)
    if awakened_boss:
        awakened_boss.shielded = False
        awakened_boss.gimmick_timer = 5.0
        awakened_boss.gimmick_active = True
        ward_message = "The rune cracks the Oracle's ward! Attack before he wards himself or smth idk. "
    if kind == "thunder":
        for enemy in enemies:
            damage_enemy(enemy, 65)
            enemy.stun_timer = max(enemy.stun_timer, 0.6)
        rune.timer = 1.0
        trigger_player_bark(hero, "IM THOR AND ZEUS IF THEY HAD A BA- yeah imma shut up", 2.4, force=True)
        return ward_message + "Thunder Rune! THEY DONT CALL ME THE AVENGER FOR NUN"
    rune_lines = {
        "slow": "why it so cold ew",
        "fire": "fire is lowk fire",
        "lure": "goddamn herd mind haha losers",
    }
    trigger_player_bark(hero, rune_lines[kind], 2.4, force=True)
    return ward_message + f"{RUNE_TYPES[kind]['name']} lemme place ts wait."


def armor_weight(hero):
    return sum(weight for item, weight in ARMOR_WEIGHT.items() if hero.equipment[item])


def armor_damage_scale(hero):
    protection = sum(value for item, value in ARMOR_PROTECTION.items() if hero.equipment[item])
    return max(0.15, 1 - protection)


def get_weapon_variant(hero):
    rank = max(1, min(WEAPON_MAX_LEVEL,
                       hero.weapon_tiers.get(hero.weapon, hero.weapons.get(hero.weapon, 1))))
    return WEAPON_VARIANTS[hero.weapon][rank - 1]


def trigger_special_vfx(hero, name, start, end=None):
    hero.special_vfx = name
    hero.special_vfx_timer = 0.6
    hero.special_vfx_duration = 0.6
    hero.special_vfx_start = tuple(start)
    hero.special_vfx_end = tuple(end if end is not None else start)
    variant = get_weapon_variant(hero)
    hero.special_vfx_variant = variant
    hero.special_vfx_color = variant["vfx_color"]
    hero.special_vfx_accent = variant["vfx_accent"]
    hero.special_vfx_scale = variant["vfx_scale"]
    hero.special_vfx_count = variant["vfx_count"]


def trigger_player_bark(hero, text, duration=1.5, force=False):
    if not hero.dialogue_enabled or (hero.bark_cooldown > 0 and not force):
        return False
    hero.bark_text = text
    hero.bark_timer = duration
    hero.bark_cooldown = max(3.2, duration + 0.8)
    hero.ambient_dialogue_timer = random.uniform(7.5, 11.0)
    return True


def weapon_action_bark(hero, hit, magical=False):
    weapon_name = get_weapon_variant(hero)["name"]
    if magical:
        line = random.choice((
            f"The magic in {weapon_name} ANSWERED HOLY CRAP",
            f"OMG WHAT THE ACTUAL HELL IM DOCTOR STRANGE OR SMTH.",
            "easy im uh war.",
        ))
    elif hit:
        line = random.choice((
            f"{weapon_name} is lowk peak.",
            f"I made this weapon, im HEPESTATUS OR WHATEVER.",
            "My hands are shaking bro, ewww.",
            f"holy dr stone reference this actually works?? {weapon_name}",
        ))
    else:
        line = random.choice((
            f"IM HIM! I LOVE YOU {weapon_name}.",
            "how did i miss bro",
            "That swing was wild.",
            "I need to focus, ADHD isnt that deep",
        ))
    trigger_player_bark(hero, line, duration=2.2)


def update_ambient_dialogue(hero, dt):
    if not hero.dialogue_enabled:
        return
    mode = "walking" if hero.moving else "still"
    if mode != hero.dialogue_mode:
        hero.dialogue_mode = mode
        hero.ambient_dialogue_timer = 4.5 if mode == "still" else 3.5
        return
    hero.ambient_dialogue_timer -= dt
    if hero.ambient_dialogue_timer > 0 or hero.bark_cooldown > 0:
        return
    if mode == "walking":
        lines = (
            "One step, two step, three step. baba black sheep.",
            "I'm afraid now kinda",
            "I hope Mira lowk isnt dead.",
            "These halls are so quiet, gives me ick",
        )
    else:
        lines = (
            "I need a breath, omg pls no kill me",
            "It's quiet... too quiet aint it?",
            "Maybe I can rest for a quick sec, but eh",
            "ew, i have fear? L game design!",
        )
    trigger_player_bark(hero, random.choice(lines), duration=2.4)


def nearest_enemy(hero, enemies, max_distance):
    choices = []
    for enemy in enemies:
        distance = pygame.Vector2(enemy.rect.center).distance_to(hero.rect.center)
        if distance <= max_distance:
            choices.append((distance, enemy))
    return min(choices, key=lambda entry: entry[0])[1] if choices else None


def use_basic_attack(hero, enemies, arrows, aim_target=None):
    weapon = WEAPONS[hero.weapon]
    rank = hero.weapon_tiers.get(hero.weapon, 1)
    variant = get_weapon_variant(hero)
    damage_scale = variant["damage"] * (1 + hero.weapon_upgrades[hero.weapon] * 0.1)
    damage_scale *= 1.5 if hero.strength_timer > 0 else 1
    if hero.special_armor == "knight":
        damage_scale *= 1.25
    hero.attack_cooldown = 0.28 if hero.weapon == "dagger" else 0.42
    hero.action_timer = 0.24
    if hero.weapon == "bow":
        direction = pygame.Vector2(aim_target) - pygame.Vector2(hero.rect.center) if aim_target else hero.facing
        arrows.append(Arrow(*hero.rect.center, direction,
                            (weapon["damage"] + rank * 4) * damage_scale, weapon["color"],
                            piercing=rank >= 3))
        trigger_special_vfx(hero, "basic_bow", hero.rect.center,
                            aim_target or (pygame.Vector2(hero.rect.center) + direction * 90))
        return f"{variant['name']} fired!"
    target = nearest_enemy(hero, enemies, weapon["range"] * variant["range"])
    if target:
        damage = (weapon["damage"] + (rank - 1) * 7) * damage_scale
        damage_enemy(target, damage)
        trigger_special_vfx(hero, f"basic_{weapon['style']}", hero.rect.center, target.rect.center)
        if hero.weapon == "sword" and rank >= 3:
            target.stun_timer = max(target.stun_timer, 0.45)
        elif hero.weapon == "dagger" and rank >= 3:
            damage_enemy(target, damage * 0.18)
        return f"{hero.weapon.title()} hit for {round(damage)}!"
    trigger_special_vfx(hero, f"basic_{weapon['style']}", hero.rect.center,
                        pygame.Vector2(hero.rect.center) + hero.facing * weapon["range"])
    return "No monster in reach."


def use_special(hero, enemies, arrows, walls, aim_target=None):
    if hero.special_cooldown > 0:
        return "Special ability is recharging."
    hero.special_cooldown = 5.0
    hero.action_timer = 0.55
    rank = hero.weapon_tiers.get(hero.weapon, 1)
    variant = get_weapon_variant(hero)
    damage_scale = variant["damage"] * (1 + hero.weapon_upgrades[hero.weapon] * 0.1)
    damage_scale *= 1.5 if hero.strength_timer > 0 else 1
    if hero.special_armor == "knight":
        damage_scale *= 1.25
    ability = variant["ability"]
    damage = (38 + rank * 12) * damage_scale
    origin = pygame.Vector2(hero.rect.center)
    target = nearest_enemy(hero, enemies, 420)
    aim = pygame.Vector2(aim_target) - origin if aim_target else hero.facing
    if aim.length_squared() == 0:
        aim = pygame.Vector2(hero.facing)
    aim = aim.normalize()

    def in_front(enemy, reach, width=0.25):
        offset = pygame.Vector2(enemy.rect.center) - origin
        return (offset.length() <= reach and offset.length_squared() > 0
                and aim.dot(offset.normalize()) >= width)

    if ability == "crescent_cut":
        hit = 0
        for enemy in enemies:
            if in_front(enemy, 105, 0.15):
                damage_enemy(enemy, damage)
                hit += 1
        trigger_special_vfx(hero, ability, hero.rect.center)
        return f"Crescent Cut! {hit} foe(s) slashy slashy!."
    if ability == "solar_flare":
        for enemy in enemies:
            if pygame.Vector2(enemy.rect.center).distance_to(origin) <= 145:
                damage_enemy(enemy, damage * 0.8)
                enemy.burn_timer = max(enemy.burn_timer, 4.0)
        trigger_special_vfx(hero, ability, hero.rect.center)
        return "Solar Flare! Nearby foes are set ablaze. good thing no is a basketball!"
    if ability == "frost_nova":
        for enemy in enemies:
            if pygame.Vector2(enemy.rect.center).distance_to(origin) <= 135:
                damage_enemy(enemy, damage)
                enemy.stun_timer = max(enemy.stun_timer, 2.2)
                enemy.slow_timer = max(enemy.slow_timer, 4.0)
        trigger_special_vfx(hero, ability, hero.rect.center)
        return "Frost Nova! Nearby foes are frozen in place."
    if ability == "twin_echo":
        targets = sorted(enemies, key=lambda foe: pygame.Vector2(foe.rect.center).distance_to(origin))[:2]
        for foe in targets:
            damage_enemy(foe, damage * 1.35)
        trigger_special_vfx(hero, ability, hero.rect.center)
        return f"Twin Echo! {len(targets)} foe(s) struck by the uh... whos older?"
    if ability == "dawnburst":
        for enemy in enemies:
            if pygame.Vector2(enemy.rect.center).distance_to(origin) <= 190:
                damage_enemy(enemy, damage * 2)
        trigger_special_vfx(hero, ability, hero.rect.center)
        return "Dawnburst! I GOT FLASHBANGED!!!"
    if ability == "rapid_flurry":
        if not target:
            return "No target for Rapid Flurry."
        damage_enemy(target, damage * 2.5)
        trigger_special_vfx(hero, ability, hero.rect.center, target.rect.center)
        return "Rapid Flurry! Malevolent goddamn Kitchen."
    if ability == "nightfall_lunge":
        if not target:
            return "No target for Nightfall Lunge."
        dash_direction = pygame.Vector2(target.rect.center) - origin
        distance = dash_direction.length()
        dash_direction = dash_direction.normalize() if distance else hero.facing
        move_with_walls(hero.rect, dash_direction.x * max(0, distance - 34),
                        dash_direction.y * max(0, distance - 34), walls)
        hero.facing = dash_direction
        hero.invulnerable = max(hero.invulnerable, 0.65)
        damage_enemy(target, damage * 1.8)
        trigger_special_vfx(hero, ability, origin, hero.rect.center)
        return "Nightfall Lunge! I COME AND GO."
    if ability == "venom_bloom":
        hit = 0
        for enemy in enemies:
            if pygame.Vector2(enemy.rect.center).distance_to(origin) <= 125:
                damage_enemy(enemy, damage * 0.65)
                enemy.venom_timer = max(enemy.venom_timer, 6.0)
                hit += 1
        trigger_special_vfx(hero, ability, hero.rect.center)
        return f"Venom Bloom! {hit} foe(s) poisoned."
    if ability == "phase_step":
        if not target:
            return "No target for Phase Step."
        dash_direction = pygame.Vector2(target.rect.center) - origin
        distance = dash_direction.length()
        dash_direction = dash_direction.normalize() if distance else hero.facing
        move_with_walls(hero.rect, dash_direction.x * max(0, distance - 48),
                        dash_direction.y * max(0, distance - 48), walls)
        hero.facing = dash_direction
        hero.invulnerable = max(hero.invulnerable, 1.0)
        target.stun_timer = max(target.stun_timer, 1.5)
        trigger_special_vfx(hero, ability, origin, hero.rect.center)
        return "Phase Step! ME PHASE THRU U AND COME OUT INSIDE U."
    if ability == "eclipse_rend":
        hits = 0
        for enemy in enemies:
            if in_front(enemy, 220, 0.7):
                damage_enemy(enemy, damage * 1.8)
                hits += 1
        hero.invulnerable = max(hero.invulnerable, 0.4)
        trigger_special_vfx(hero, ability, hero.rect.center)
        return f"Eclipse Rend! {hits} foe(s) caught in the black thing."
    if ability == "pinning_volley":
        for angle in (-18, -9, 0, 9, 18):
            arrows.append(Arrow(*hero.rect.center, aim.rotate(angle), damage * 0.75,
                                WEAPONS["bow"]["color"]))
        trigger_special_vfx(hero, ability, hero.rect.center)
        return "Pinning Volley! Five arrows shoot out"
    if ability == "gale_shot":
        arrow = Arrow(*hero.rect.center, aim, damage * 2, WEAPONS["bow"]["color"], piercing=True)
        arrow.velocity *= 1.8
        arrows.append(arrow)
        trigger_special_vfx(hero, ability, hero.rect.center, aim_target or (origin + aim * 100))
        return "Gale Shot! A piercing arrow thats more precise than my math!"
    if ability == "lunar_lance":
        arrows.append(Arrow(*hero.rect.center, aim, damage * 3, (190, 205, 255), piercing=True))
        trigger_special_vfx(hero, ability, hero.rect.center, aim_target or (origin + aim * 100))
        return "Lunar Lance! A heavy moonlit arrow that pays attention more than me!"
    if ability == "chain_lightning":
        current = target
        chained = set()
        for _ in range(min(4, len(enemies))):
            if not current:
                break
            damage_enemy(current, damage * 1.15)
            current.stun_timer = max(current.stun_timer, 0.35)
            chained.add(current)
            current = min(
                (foe for foe in enemies if foe not in chained
                 and pygame.Vector2(foe.rect.center).distance_to(current.rect.center) <= 180),
                key=lambda foe: pygame.Vector2(foe.rect.center).distance_to(current.rect.center),
                default=None,
            )
        trigger_special_vfx(hero, ability, hero.rect.center,
                            target.rect.center if target else hero.rect.center)
        return f"Chain Lightning! The storm jumps across {len(chained)} foe(s)."
    if ability == "starfall":
        strike = pygame.Vector2(aim_target) if aim_target else origin + aim * 180
        strike.x = max(TILE, min(WIDTH - TILE, strike.x))
        strike.y = max(MAP_TOP + TILE, min(HEIGHT - TILE, strike.y))
        hit = 0
        for enemy in enemies:
            if pygame.Vector2(enemy.rect.center).distance_to(strike) <= 105:
                damage_enemy(enemy, damage * 2.2)
                hit += 1
        trigger_special_vfx(hero, ability, strike)
        return f"Starfall! A meteor strikes the wait what? ({hit} hit)."
    if ability == "timberfall":
        hit = 0
        for enemy in enemies:
            if in_front(enemy, 155, 0.35):
                damage_enemy(enemy, damage * 1.8)
                hit += 1
        trigger_special_vfx(hero, ability, hero.rect.center)
        return f"Timberfall! Did we just goddamn execute {hit} foe(s)."
    if ability == "stone_quake":
        hit = 0
        for enemy in enemies:
            if pygame.Vector2(enemy.rect.center).distance_to(origin) <= 105:
                damage_enemy(enemy, damage)
                enemy.stun_timer = max(enemy.stun_timer, 3.0)
                hit += 1
        trigger_special_vfx(hero, ability, hero.rect.center)
        return f"Stone Quake! {hit} foe(s) are stunny"
    if ability == "inferno_cleave":
        hit = 0
        for enemy in enemies:
            if in_front(enemy, 145, 0.25):
                damage_enemy(enemy, damage)
                enemy.burn_timer = max(enemy.burn_timer, 5.0)
                hit += 1
        trigger_special_vfx(hero, ability, hero.rect.center)
        return f"Inferno Cleave! {hit} foe(s) are HOLY WE BURNT THEM"
    if ability == "faultline":
        hit = 0
        for enemy in enemies:
            offset = pygame.Vector2(enemy.rect.center) - origin
            along = offset.dot(aim)
            across = abs(offset.cross(aim))
            if 0 < along <= 340 and across <= 42:
                damage_enemy(enemy, damage * 1.7)
                enemy.stun_timer = max(enemy.stun_timer, 0.8)
                hit += 1
        trigger_special_vfx(hero, ability, hero.rect.center, origin + aim * 340)
        return f"Faultline! A crack tears them??? {hit} foe(s)."
    if ability == "cataclysm":
        hit = 0
        for enemy in enemies:
            offset = pygame.Vector2(enemy.rect.center) - origin
            if offset.length() <= 210:
                damage_enemy(enemy, damage * 2.4)
                enemy.stun_timer = max(enemy.stun_timer, 1.2)
                if offset.length_squared():
                    knockback = offset.normalize() * 70
                    move_with_walls(enemy.rect, knockback.x, knockback.y, walls)
                hit += 1
        trigger_special_vfx(hero, ability, hero.rect.center)
        return f"Cataclysm! The ground erupts smth {hit} foe(s)."
    if ability == "hook_and_haul":
        if not target:
            return "No target for Hook and Haul."
        offset = origin - pygame.Vector2(target.rect.center)
        distance = offset.length()
        if distance:
            pull = offset.normalize() * max(0, distance - 36)
            move_with_walls(target.rect, pull.x, pull.y, walls)
        target.stun_timer = max(target.stun_timer, 0.8)
        damage_enemy(target, damage * 1.4)
        trigger_special_vfx(hero, ability, hero.rect.center, target.rect.center)
        return "Hook and Haul! The target is holy marvel reference."
    if ability == "breach_slam":
        if not target:
            return "No target for Breach Slam."
        offset = pygame.Vector2(target.rect.center) - origin
        damage_enemy(target, damage * 2)
        target.stun_timer = max(target.stun_timer, 1.0)
        if offset.length_squared():
            knockback = offset.normalize() * 110
            move_with_walls(target.rect, knockback.x, knockback.y, walls)
        trigger_special_vfx(hero, ability, hero.rect.center, target.rect.center)
        return "Breach Slam! Vaultbreaker break their ahh!."
    if ability == "rivet_storm":
        hit = 0
        for enemy in enemies:
            if pygame.Vector2(enemy.rect.center).distance_to(origin) <= 175:
                damage_enemy(enemy, damage * 1.25)
                enemy.stun_timer = max(enemy.stun_timer, 0.3)
                hit += 1
        trigger_special_vfx(hero, ability, hero.rect.center)
        return f"Rivet Storm! Metal shards. Wait did we just torture {hit} nearby foe(s)."
    if ability == "foundry_blast":
        hit = 0
        for enemy in enemies:
            if pygame.Vector2(enemy.rect.center).distance_to(origin) <= 185:
                damage_enemy(enemy, damage * 1.1)
                enemy.burn_timer = max(enemy.burn_timer, 6.0)
                hit += 1
        trigger_special_vfx(hero, ability, hero.rect.center)
        return f"Foundry Blast! {hit} foe(s) are engulfed in flames!."
    if ability == "royal_decree":
        for enemy in enemies:
            damage_enemy(enemy, damage * 0.8)
            enemy.stun_timer = max(enemy.stun_timer, 2.5)
        trigger_special_vfx(hero, ability, hero.rect.center)
        return "Royal Decree! Every foe in the room is forced to kneel dow like a good boy."
    if ability == "lancing_thrust":
        hit = 0
        for enemy in enemies:
            offset = pygame.Vector2(enemy.rect.center) - origin
            along = offset.dot(aim)
            across = abs(offset.cross(aim))
            if 0 < along <= 190 * variant["range"] and across <= 24:
                damage_enemy(enemy, damage * 1.7)
                hit += 1
        trigger_special_vfx(hero, ability, origin, origin + aim * 190)
        return f"Lancing Thrust! The spear pierces {hit} foe(s) in a line straighter than me!"
    if ability == "gale_repulse":
        hit = 0
        for enemy in enemies:
            if in_front(enemy, 150 * variant["range"], 0.3):
                damage_enemy(enemy, damage * 1.25)
                offset = pygame.Vector2(enemy.rect.center) - origin
                if offset.length_squared():
                    push = offset.normalize() * 95
                    move_with_walls(enemy.rect, push.x, push.y, walls)
                hit += 1
        trigger_special_vfx(hero, ability, origin, origin + aim * 150)
        return f"Gale Repulse! {hit} foe(s) are swept off ye feet"
    if ability == "viper_impale":
        if not target:
            return "No target for Viper Impale."
        damage_enemy(target, damage * 2)
        target.venom_timer = max(target.venom_timer, 7.0)
        target.slow_timer = max(target.slow_timer, 2.0)
        trigger_special_vfx(hero, ability, origin, target.rect.center)
        return "Viper Impale! The target is poissoned and LOCKED IN AMMONIA!"
    if ability == "sunpiercer":
        arrows.append(Arrow(*hero.rect.center, aim, damage * 2.5,
                            WEAPONS["spear"]["color"], piercing=True))
        trigger_special_vfx(hero, ability, origin, aim_target or origin + aim * 190)
        return "Sunpiercer! A radiant spear flies thru THEIR CHE- HOLY CRAP."
    if ability == "worldroot":
        hit = 0
        for enemy in enemies:
            if pygame.Vector2(enemy.rect.center).distance_to(origin) <= 165 * variant["range"]:
                damage_enemy(enemy, damage * 1.55)
                enemy.slow_timer = max(enemy.slow_timer, 5.0)
                enemy.stun_timer = max(enemy.stun_timer, 0.6)
                hit += 1
        trigger_special_vfx(hero, ability, hero.rect.center)
        return f"Worldroot! {hit} foe(s) are pinned by ew thats disgusting"
    if ability == "quarry_slam":
        hit = 0
        for enemy in enemies:
            if pygame.Vector2(enemy.rect.center).distance_to(origin) <= 100:
                damage_enemy(enemy, damage * 1.8)
                enemy.stun_timer = max(enemy.stun_timer, 1.0)
                hit += 1
        trigger_special_vfx(hero, ability, hero.rect.center)
        return f"Quarry Slam! The maul stuns {hit} nearby foe(s)."
    if ability == "armor_breaker":
        if not target:
            return "No target for Armor Breaker."
        damage_enemy(target, damage * 2.6)
        target.stun_timer = max(target.stun_timer, 0.75)
        trigger_special_vfx(hero, ability, origin, target.rect.center)
        return "Armor Breaker! A focused blow crushes the guy. Jesus christ...."
    if ability == "thunderclap":
        hit = 0
        for enemy in enemies:
            if pygame.Vector2(enemy.rect.center).distance_to(origin) <= 145:
                damage_enemy(enemy, damage * 1.4)
                enemy.stun_timer = max(enemy.stun_timer, 2.0)
                hit += 1
        trigger_special_vfx(hero, ability, hero.rect.center)
        return f"Thunderclap! {hit} foe(s) are stunned by the shockwave(W)"
    if ability == "meteor_drop":
        strike = pygame.Vector2(aim_target) if aim_target else origin + aim * 120
        strike.x = max(TILE, min(WIDTH - TILE, strike.x))
        strike.y = max(MAP_TOP + TILE, min(HEIGHT - TILE, strike.y))
        hit = 0
        for enemy in enemies:
            if pygame.Vector2(enemy.rect.center).distance_to(strike) <= 75:
                damage_enemy(enemy, damage * 2.2)
                enemy.stun_timer = max(enemy.stun_timer, 1.4)
                hit += 1
        trigger_special_vfx(hero, ability, strike)
        return f"Meteor Drop! WAIT WHAT? {hit} foe(s)."
    if ability == "gravity_well":
        hit = 0
        for enemy in enemies:
            offset = origin - pygame.Vector2(enemy.rect.center)
            if offset.length() <= 210:
                if offset.length_squared():
                    pull = offset.normalize() * max(0, offset.length() - 42)
                    move_with_walls(enemy.rect, pull.x, pull.y, walls)
                damage_enemy(enemy, damage * 1.5)
                enemy.stun_timer = max(enemy.stun_timer, 0.8)
                hit += 1
        trigger_special_vfx(hero, ability, hero.rect.center)
        return f"Gravity Well! {hit} foe(s) are dragged into the maul's HOLY JESUS U CRUSHED THEM"
    return f"{variant['special']} is not available."


def use_armor_ability(hero, walls, aim_target):
    armor = hero.special_armor
    if armor is None:
        return "No special armor equipped."
    if hero.armor_cooldown > 0:
        return "Armor ability is recharging."
    if armor == "knight":
        hero.parry_timer = 0.65
        hero.armor_cooldown = 1.0
        trigger_special_vfx(hero, "armor_knight", hero.rect.center)
        return "Parry ready! Block the next enemy hit."
    if armor == "samurai":
        direction = pygame.Vector2(aim_target) - pygame.Vector2(hero.rect.center)
        if direction.length_squared() == 0:
            direction = pygame.Vector2(hero.facing)
        direction = direction.normalize()
        start = pygame.Vector2(hero.rect.center)
        dash_distance = hero.speed * 0.2 * 1.2
        move_with_walls(hero.rect, direction.x * dash_distance, direction.y * dash_distance, walls)
        hero.facing = direction
        hero.invulnerable = max(hero.invulnerable, 0.22)
        hero.armor_cooldown = 1.0
        trigger_special_vfx(hero, "samurai_dash", start, hero.rect.center)
        return "Samurai dash! You surge forward."
    if armor == "phantom":
        health_cost = math.ceil(hero.max_hp * 0.4)
        if hero.hp <= health_cost:
            return f"Phantom cloak needs more than {health_cost} HP."
        hero.hp -= health_cost
        hero.regen_delay = 5.0
        hero.phantom_timer = 5.0
        hero.armor_cooldown = 2.0
        trigger_special_vfx(hero, "armor_phantom", hero.rect.center)
        return f"Phantom cloak! Invisible for 5 seconds; -{health_cost} HP."
    return "No special armor ability available."


def draw_dialogue(pages, page_index):
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 205))
    SCREEN.blit(shade, (0, 0))
    panel = pygame.Rect(95, 190, WIDTH - 190, 300)
    pygame.draw.rect(SCREEN, (36, 34, 49), panel, border_radius=14)
    pygame.draw.rect(SCREEN, GOLD, panel, 2, border_radius=14)
    page = pages[page_index]
    if isinstance(page, dict):
        speaker, text = page["speaker"], page["text"]
    else:
        speaker, text = "NARRATOR", page
    is_boss = speaker not in ("NARRATOR", "YOU", "MIRA")
    is_mira = speaker == "MIRA"
    speaker_color = ((255, 125, 105) if is_boss else
                     (255, 160, 195) if is_mira else
                     (140, 180, 245) if speaker == "YOU" else GOLD)
    draw_text(SCREEN, speaker, FONT, speaker_color,
              (WIDTH // 2, panel.y + 42))
    words = text.split()
    lines = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if FONT.size(candidate)[0] > panel.width - 80 and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    for i, line in enumerate(lines):
        draw_text(SCREEN, line, FONT, WHITE,
                  (WIDTH // 2, panel.centery - 10 + (i - (len(lines) - 1) / 2) * 38))
    draw_text(SCREEN, f"{page_index + 1}/{len(pages)}   ENTER: continue",
              SMALL_FONT, GOLD, (WIDTH // 2, panel.bottom - 34))


def make_puzzle_state(level_number):
    puzzle = ROOM_PUZZLES[level_number]
    if puzzle["kind"] == "rune_grid":
        return {"tiles": puzzle["start"][:], "cursor": 4}
    if puzzle["kind"] == "pairs":
        return {"matched": set(), "revealed": [], "cursor": 0}
    if puzzle["kind"] in ("arrange", "crates"):
        return {"sequence": puzzle["start"][:], "cursor": 0}
    if puzzle["kind"] in ("sequence", "final_levers", "path"):
        return {"sequence": [], "cursor": 0}
    if puzzle["kind"] == "mirrors":
        return {"orientations": puzzle["start"][:], "cursor": 0}
    return {"choice": 0}


def puzzle_solved(level_number, puzzle_state):
    puzzle = ROOM_PUZZLES[level_number]
    kind = puzzle["kind"]
    if kind in ("arrange", "crates"):
        return puzzle_state["sequence"] == puzzle["goal"]
    if kind in ("sequence", "final_levers", "path"):
        return puzzle_state["sequence"] == puzzle["goal"]
    if kind == "mirrors":
        return puzzle_state["orientations"] == puzzle["goal"]
    if kind == "rune_grid":
        return puzzle_state["tiles"] == puzzle["goal"]
    if kind == "pairs":
        return len(puzzle_state["matched"]) == len(puzzle["cards"])
    return puzzle["choices"][puzzle_state["choice"]] == puzzle["goal"]


def draw_room_puzzle(level_number, puzzle_state, feedback):
    puzzle = ROOM_PUZZLES[level_number]
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 215))
    SCREEN.blit(shade, (0, 0))
    panel = pygame.Rect(90, 150, WIDTH - 180, 380)
    pygame.draw.rect(SCREEN, (35, 37, 49), panel, border_radius=14)
    pygame.draw.rect(SCREEN, GOLD, panel, 2, border_radius=14)
    draw_text(SCREEN, f"ROOM {level_number} PUZZLE", TITLE_FONT, GOLD,
              (WIDTH // 2, panel.y + 55))
    words, lines, line = puzzle["clue"].split(), [], ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if FONT.size(candidate)[0] > panel.width - 80 and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    for i, line in enumerate(lines):
        draw_text(SCREEN, line, FONT, WHITE,
                  (WIDTH // 2, panel.y + 135 + i * 32))
    kind = puzzle["kind"]
    if kind in ("arrange", "crates"):
        sequence = puzzle_state["sequence"]
        tile_width, gap = 112, 22
        total_width = tile_width * len(sequence) + gap * (len(sequence) - 1)
        start_x = (WIDTH - total_width) // 2
        for index, label in enumerate(sequence):
            tile = pygame.Rect(start_x + index * (tile_width + gap), panel.y + 225, tile_width, 92)
            selected = index in (puzzle_state["cursor"], puzzle_state["cursor"] + 1)
            pygame.draw.rect(SCREEN, (51, 56, 70), tile, border_radius=10)
            pygame.draw.rect(SCREEN, GOLD if selected else (110, 117, 132), tile,
                             3 if selected else 1, border_radius=10)
            pygame.draw.circle(SCREEN, PUZZLE_COLORS.get(label, WHITE), (tile.centerx, tile.y + 29), 16)
            draw_text(SCREEN, label.upper(), SMALL_FONT, WHITE, (tile.centerx, tile.y + 67))
        controls = "LEFT/RIGHT select adjacent objects  |  SPACE swaps  |  ENTER checks"
    elif kind in ("sequence", "final_levers"):
        symbols = puzzle["symbols"]
        selected = puzzle_state["cursor"]
        for index, label in enumerate(symbols):
            center = (WIDTH // 2 + (index - (len(symbols) - 1) / 2) * 170, panel.y + 250)
            pygame.draw.circle(SCREEN, GOLD if index == selected else (100, 105, 120),
                               (round(center[0]), round(center[1])), 48, 4)
            pygame.draw.circle(SCREEN, PUZZLE_COLORS.get(label, WHITE),
                               (round(center[0]), round(center[1])), 28)
            draw_text(SCREEN, label, SMALL_FONT, WHITE, (round(center[0]), round(center[1]) + 68))
        entered = "  >  ".join(puzzle_state["sequence"]) or "Nothing pulled yet"
        draw_text(SCREEN, entered, FONT, GOLD, (WIDTH // 2, panel.y + 325))
        controls = "LEFT/RIGHT choose lever  |  SPACE pulls it  |  ENTER checks"
    elif kind == "path":
        symbols = ("UP", "RIGHT", "DOWN", "LEFT")
        for index, label in enumerate(symbols):
            center = (WIDTH // 2 + (index - 1.5) * 92, panel.y + 260)
            pygame.draw.circle(SCREEN, GOLD if index == puzzle_state["cursor"] else (100, 105, 120),
                               (round(center[0]), round(center[1])), 32, 3)
            draw_text(SCREEN, label, SMALL_FONT, WHITE, (round(center[0]), round(center[1])))
        entered = "  >  ".join(puzzle_state["sequence"]) or "Route not traced"
        draw_text(SCREEN, entered, FONT, GOLD, (WIDTH // 2, panel.y + 325))
        controls = "ARROWS choose direction  |  SPACE adds step  |  ENTER checks"
    elif kind == "mirrors":
        labels = ("UP", "RIGHT", "DOWN", "LEFT")
        for index, orientation in enumerate(puzzle_state["orientations"]):
            center = (WIDTH // 2 + (index - 1) * 170, panel.y + 260)
            pygame.draw.rect(SCREEN, GOLD if index == puzzle_state["cursor"] else (100, 105, 120),
                             (round(center[0] - 42), round(center[1] - 42), 84, 84), 3)
            draw_text(SCREEN, labels[orientation], FONT, WHITE,
                      (round(center[0]), round(center[1])))
        controls = "LEFT/RIGHT select mirror  |  UP rotates  |  ENTER locks mirrors"
    elif kind == "rune_grid":
        for index, active in enumerate(puzzle_state["tiles"]):
            row, col = divmod(index, 3)
            tile = pygame.Rect(WIDTH // 2 - 126 + col * 84, panel.y + 190 + row * 50, 66, 42)
            selected = index == puzzle_state["cursor"]
            fill = (220, 190, 90) if active else (48, 52, 65)
            pygame.draw.rect(SCREEN, fill, tile, border_radius=8)
            pygame.draw.rect(SCREEN, GOLD if selected else (110, 117, 132), tile,
                             3 if selected else 1, border_radius=8)
            draw_text(SCREEN, "ON" if active else "OFF", SMALL_FONT,
                      DARK if active else WHITE, tile.center)
        controls = "ARROWS move  |  SPACE flips a rune and its neighbors  |  ENTER checks"
    elif kind == "pairs":
        cards = puzzle["cards"]
        for index, label in enumerate(cards):
            row, col = divmod(index, 4)
            card = pygame.Rect(WIDTH // 2 - 280 + col * 140,
                               panel.y + 185 + row * 74, 120, 58)
            selected = index == puzzle_state["cursor"]
            shown = index in puzzle_state["matched"] or index in puzzle_state["revealed"]
            pygame.draw.rect(SCREEN, (66, 75, 91) if shown else (45, 48, 61),
                             card, border_radius=7)
            pygame.draw.rect(SCREEN, GOLD if selected else (110, 117, 132), card,
                             3 if selected else 1, border_radius=7)
            draw_text(SCREEN, label if shown else "?", FONT, GOLD if shown else WHITE, card.center)
        controls = "ARROWS select tablet  |  SPACE reveals a pair  |  ENTER checks"
    else:
        for index, label in enumerate(puzzle["choices"]):
            center = (WIDTH // 2 + (index - 1.5) * 155, panel.y + 260)
            selected = index == puzzle_state["choice"]
            pygame.draw.rect(SCREEN, (51, 56, 70), (round(center[0] - 58), round(center[1] - 42), 116, 84),
                             border_radius=8)
            pygame.draw.rect(SCREEN, GOLD if selected else (100, 105, 120),
                             (round(center[0] - 58), round(center[1] - 42), 116, 84), 3)
            draw_text(SCREEN, label, SMALL_FONT, WHITE, (round(center[0]), round(center[1])))
        controls = "LEFT/RIGHT choose door  |  ENTER opens it"
    draw_text(SCREEN, controls, SMALL_FONT, GOLD, (WIDTH // 2, panel.bottom - 35))
    if feedback:
        draw_text(SCREEN, feedback, SMALL_FONT, RED, (WIDTH // 2, panel.bottom + 27))


def draw_crafting(hero, page="main", category="sword", tab=0, selection=0, weapon_tier=1,
                  feedback=""):
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 205))
    SCREEN.blit(shade, (0, 0))
    panel = pygame.Rect(125, 25, WIDTH - 250, 630)
    pygame.draw.rect(SCREEN, (35, 37, 49), panel, border_radius=14)
    pygame.draw.rect(SCREEN, GOLD, panel, 2, border_radius=14)
    title = f"{category.title()} Crafting Table" if page == "weapon" else "CRAFTING BENCH"
    draw_text(SCREEN, title, TITLE_FONT, GOLD, (WIDTH // 2, 78))
    inventory = (f"Scrap: {hero.materials['scrap']}   Herbs: {hero.materials['herbs']}   "
                 f"Crystals: {hero.materials['crystals']}   Cores: {hero.materials['cores']}")
    draw_text(SCREEN, inventory, SMALL_FONT, WHITE, (WIDTH // 2, 126))
    if page == "weapon":
        rank = hero.weapons.get(category, 0)
        for tier, variant in enumerate(WEAPON_VARIANTS[category], 1):
            y = 185 + (tier - 1) * 82
            row = pygame.Rect(155, y - 28, 650, 66)
            owned = tier <= rank
            available = tier == rank + 1
            equipped = hero.weapon == category and hero.weapon_tiers.get(category, 1) == tier
            if available:
                pygame.draw.rect(SCREEN, (66, 72, 62), row, border_radius=7)
            elif owned:
                pygame.draw.rect(SCREEN, (53, 57, 69), row, border_radius=7)
            else:
                pygame.draw.rect(SCREEN, (42, 44, 55), row, border_radius=7)
            selected = tier - 1 == weapon_tier
            pygame.draw.rect(SCREEN, GOLD if selected or available or equipped else (100, 105, 120),
                             row, 2, border_radius=7)
            status = "EQUIPPED" if equipped else ("OWNED" if owned else ("NEXT" if available else "LOCKED"))
            draw_text(SCREEN, f"Tier {tier}: {variant['name']}  -  {status}", SMALL_FONT,
                      GOLD if selected or available else WHITE, (WIDTH // 2, y - 10))
            draw_text(SCREEN, f"Q: {variant['special']}  |  {variant['trait']}",
                      TINY_FONT, (205, 210, 220), (WIDTH // 2, y + 10))
            cost = weapon_recipe_cost(category, tier)
            cost_text = "   ".join(f"{amount} {name}" for name, amount in cost.items())
            draw_text(SCREEN, cost_text, TINY_FONT, (175, 185, 200), (WIDTH // 2, y + 28))
        upgrade_button = pygame.Rect(185, 550, 590, 40)
        can_upgrade = hero.weapons.get(category, 0) > 0 and hero.materials["cores"] >= 3
        pygame.draw.rect(SCREEN, (63, 83, 61) if can_upgrade else (48, 49, 57),
                         upgrade_button, border_radius=7)
        pygame.draw.rect(SCREEN, GREEN if can_upgrade else (105, 107, 115),
                         upgrade_button, 2, border_radius=7)
        upgrade_text = (f"UPGRADE +10% DAMAGE (x{hero.weapon_upgrades[category]})  |  3 CORES"
                        if hero.weapons.get(category, 0) else "CRAFT THIS WEAPON TO UNLOCK UPGRADES")
        draw_text(SCREEN, upgrade_text, SMALL_FONT, WHITE, upgrade_button.center)
        if feedback:
            lines = []
            line = ""
            for word in feedback.split():
                candidate = f"{line} {word}".strip()
                if TINY_FONT.size(candidate)[0] > 690 and line:
                    lines.append(line)
                    line = word
                else:
                    line = candidate
            if line:
                lines.append(line)
            for index, feedback_line in enumerate(lines[-2:]):
                draw_text(SCREEN, feedback_line, TINY_FONT, (255, 225, 160),
                          (WIDTH // 2, 598 + index * 17))
        draw_text(SCREEN, "Click upgrade or press U  |  UP/DOWN tiers  |  ENTER crafts/equips  |  C: back",
                  TINY_FONT, GOLD, (WIDTH // 2, panel.bottom - 16))
        return
    tab_width = 150
    for index, label in enumerate(CRAFT_TABS):
        tab_rect = pygame.Rect(165 + index * 157, 150, tab_width, 38)
        pygame.draw.rect(SCREEN, (78, 71, 48) if index == tab else (45, 48, 61),
                         tab_rect, border_radius=5)
        pygame.draw.rect(SCREEN, GOLD if index == tab else (100, 105, 120),
                         tab_rect, 2, border_radius=5)
        draw_text(SCREEN, label, SMALL_FONT, WHITE, tab_rect.center)

    recipes = CRAFT_RECIPES[CRAFT_TABS[tab]]
    for index, recipe in enumerate(recipes):
        y = 220 + index * 68
        row = pygame.Rect(185, y - 24, 590, 54)
        selected = index == selection
        pygame.draw.rect(SCREEN, (78, 71, 48) if selected else (45, 48, 61),
                         row, border_radius=6)
        pygame.draw.rect(SCREEN, GOLD if selected else (100, 105, 120), row, 2, border_radius=6)
        if tab == 1:
            category = recipe
            rank = hero.weapons.get(category, 0)
            equipped_name = (WEAPON_VARIANTS[category][hero.weapon_tiers.get(category, rank) - 1]["name"]
                             if rank else "Not crafted")
            description = f"{rank}/{WEAPON_MAX_LEVEL} tiers unlocked  |  Equipped: {equipped_name}"
            label = f"{category.title()} crafting table"
        else:
            item, cost = {
                1: ("Health potion", {"herbs": 3, "scrap": 2}),
                2: ("Strength potion", {"herbs": 2, "crystals": 2}),
                3: ("Speed potion", {"herbs": 2, "scrap": 1, "crystals": 2}),
                4: ("Bomb", {"scrap": 4, "crystals": 1}),
                10: ("Helmet", {"scrap": 3, "crystals": 2}),
                11: ("Chestplate", {"scrap": 6, "crystals": 4, "cores": 1}),
                12: ("Leggings", {"scrap": 4, "crystals": 3}),
                13: ("Boots", {"scrap": 2, "herbs": 2}),
                14: (RUNE_TYPES["slow"]["name"], RUNE_TYPES["slow"]["cost"]),
                15: (RUNE_TYPES["fire"]["name"], RUNE_TYPES["fire"]["cost"]),
                16: (RUNE_TYPES["thunder"]["name"], RUNE_TYPES["thunder"]["cost"]),
                17: (RUNE_TYPES["lure"]["name"], RUNE_TYPES["lure"]["cost"]),
                20: (RUNE_TYPES["teleport"]["name"], RUNE_TYPES["teleport"]["cost"]),
                21: (SPECIAL_ARMOR["knight"]["name"], SPECIAL_ARMOR["knight"]["cost"]),
                22: (SPECIAL_ARMOR["samurai"]["name"], SPECIAL_ARMOR["samurai"]["cost"]),
                23: (SPECIAL_ARMOR["phantom"]["name"], SPECIAL_ARMOR["phantom"]["cost"]),
            }[recipe]
            label = item
            description = "   ".join(f"{amount} {kind}" for kind, amount in cost.items())
            if recipe in (10, 11, 12, 13):
                description += "  |  No special ability"
            elif recipe in (21, 22, 23):
                armor_name = ("knight", "samurai", "phantom")[recipe - 21]
                status = "Equipped" if hero.special_armor == armor_name else (
                    "Owned" if hero.special_armors[armor_name] else "Not owned")
                cost_text = " ".join(f"{amount} {kind}" for kind, amount in cost.items())
                label = f"{item}  |  {status}"
                description = f"{cost_text}  |  {SPECIAL_ARMOR[armor_name]['description']}"
        draw_text(SCREEN, label, SMALL_FONT, GOLD if selected else WHITE, (WIDTH // 2, y - 8))
        draw_text(SCREEN, description, TINY_FONT, (205, 210, 220), (WIDTH // 2, y + 12))
    draw_text(SCREEN, "LEFT/RIGHT tabs  |  UP/DOWN select  |  ENTER craft/open  |  C / ESC: return",
              SMALL_FONT, GOLD, (WIDTH // 2, panel.bottom - 28))
    if feedback:
        draw_text(SCREEN, feedback, TINY_FONT, (255, 225, 160),
                  (WIDTH // 2, panel.bottom - 52))


def draw_weapon_vfx(variant, start, end, progress):
    motif = variant["vfx"]
    color = variant["vfx_color"]
    accent = variant["vfx_accent"]
    scale = variant["vfx_scale"]
    count = variant["vfx_count"]
    direction = end - start
    if direction.length_squared() == 0:
        direction = pygame.Vector2(1, 0)
    direction = direction.normalize()
    side = direction.rotate(90)
    reach = max(28, min(190, (end - start).length())) * scale
    center = end if (end - start).length_squared() else start + direction * reach

    def xy(point):
        return round(point.x), round(point.y)

    def stroke(points, shade=color, width=3):
        if len(points) > 1:
            pygame.draw.lines(SCREEN, shade, False, [xy(point) for point in points], width)

    def arc(radius, sweep, shade=color, width=3):
        points = [center + direction.rotate(-sweep / 2 + sweep * step / 12) * radius
                  for step in range(13)]
        stroke(points, shade, width)

    def shard(position, radius, shade=accent, sides=3, rotation=0):
        points = []
        for index in range(sides):
            angle = math.tau * index / sides + rotation
            points.append(position + pygame.Vector2(1, 0).rotate(math.degrees(angle)) * radius)
        pygame.draw.polygon(SCREEN, shade, [xy(point) for point in points])

    def star(position, radius, shade=accent, points=5):
        vertices = []
        for index in range(points * 2):
            point_radius = radius if index % 2 == 0 else radius * 0.42
            point = position + pygame.Vector2(1, 0).rotate(index * 180 / points) * point_radius
            vertices.append(xy(point))
        pygame.draw.polygon(SCREEN, shade, vertices)

    def ray_burst(rays, inner, outer, shade=color):
        for index in range(rays):
            angle = (index - (rays - 1) / 2) * 13
            ray = direction.rotate(angle)
            stroke([center + ray * inner, center + ray * outer], shade, 2 if index % 2 else 4)

    if motif == "crescent":
        arc(reach * (0.62 + progress * 0.2), 145, color, 5)
        arc(reach * 0.47, 105, accent, 2)
    elif motif == "rays":
        ray_burst(count, 5, reach * 0.8, color)
        star(center, 11 * scale, accent, 4)
    elif motif == "snowflake":
        for index in range(6):
            branch = direction.rotate(index * 60)
            tip = center + branch * reach * 0.48
            stroke([center - branch * 12, tip], color, 3)
            for side_sign in (-1, 1):
                fork = tip - branch * 12 + branch.rotate(side_sign * 42) * 13
                stroke([tip - branch * 12, fork], accent, 2)
        shard(center, 7 * scale, WHITE, 6, 0.2)
    elif motif == "twin_stars":
        for sign in (-1, 1):
            star(center + side * sign * reach * 0.34, 13 * scale, color, 4)
        stroke([start, end], accent, 2)
    elif motif == "dawn_arc":
        arc(reach * 0.75, 190, color, 6)
        for index in range(count):
            ray = direction.rotate(-70 + index * 140 / max(1, count - 1))
            stroke([center - ray * 7, center + ray * (20 + 8 * progress)], accent, 2)
    elif motif == "fangs":
        for sign in (-1, 1):
            tip = center + direction * reach * 0.38 + side * sign * 11
            base = center + direction * reach * 0.12 + side * sign * 25
            back = base - direction * 13
            pygame.draw.polygon(SCREEN, color, [xy(tip), xy(base), xy(back)])
            stroke([back, tip], accent, 2)
    elif motif == "shadow_crescent":
        arc(reach * 0.85, 155, color, 7)
        arc(reach * 0.68, 105, accent, 2)
        for sign in (-1, 1):
            stroke([start - direction * 20 + side * sign * 9, center + side * sign * 4],
                   color, 2)
    elif motif == "venom":
        for index in range(count):
            position = center + direction.rotate(-45 + index * 90 / max(1, count - 1)) * (10 + index * 4)
            drop = [position + direction * 9, position + side * 5, position - side * 5]
            pygame.draw.polygon(SCREEN, color if index % 2 else accent, [xy(point) for point in drop])
        arc(reach * 0.45, 70, color, 2)
    elif motif == "afterimage":
        for ghost in range(3):
            offset = side * (ghost - 1) * 11
            a, b = start - direction * (ghost * 7) + offset, end + offset
            pygame.draw.polygon(SCREEN, color if ghost == 0 else accent,
                                [xy(a + direction * 10), xy(b), xy(b - direction * 9),
                                 xy(a - side * 5)], 2)
    elif motif == "eclipse":
        outer = max(7, round(18 * scale + progress * 16))
        pygame.draw.circle(SCREEN, color, xy(center), outer, 3)
        pygame.draw.circle(SCREEN, accent, xy(center + direction * 5), max(4, outer - 6), 2)
        stroke([center - side * outer, center + side * outer], accent, 2)
    elif motif == "leaves":
        for index in range(count):
            leaf_center = center + direction * (index - (count - 1) / 2) * 11
            leaf = [leaf_center, leaf_center + direction * 8 + side * 5,
                    leaf_center + direction * 18, leaf_center + direction * 8 - side * 5]
            pygame.draw.polygon(SCREEN, color if index % 2 else accent, [xy(point) for point in leaf])
            stroke([leaf[0], leaf[2]], (55, 145, 85), 1)
    elif motif == "wind":
        for index in range(3):
            arc(reach * (0.48 + index * 0.13), 95 + index * 22,
                color if index % 2 else accent, 3)
    elif motif == "moon_shards":
        for index in range(count):
            position = center + direction.rotate(-36 + index * 72 / max(1, count - 1)) * (8 + index * 4)
            shard(position, (8 + index * 2) * scale, color if index % 2 else accent, 3,
                  index * 0.45)
    elif motif == "lightning":
        for index in range(count):
            offset = side * (index - (count - 1) / 2) * 7
            points = [start + offset, start.lerp(end, 0.35) + offset + side * 9,
                      start.lerp(end, 0.62) + offset - side * 8, end + offset]
            stroke(points, accent if index == count // 2 else color, 3)
    elif motif == "starfall":
        for index in range(count):
            position = start.lerp(end, (index + 1) / (count + 1)) + side * ((index % 2) * 24 - 12)
            star(position, (5 + index % 3 * 2) * scale, accent if index % 2 else color, 5)
            stroke([position - direction * 18, position], color, 2)
    elif motif == "woodchips":
        for index in range(count):
            position = center + direction.rotate(-55 + index * 110 / max(1, count - 1)) * (12 + index * 3)
            shard(position, (5 + index % 3) * scale, color if index % 2 else accent, 4, index * 0.8)
    elif motif == "stone_shards":
        for index in range(count):
            position = center + direction.rotate(-48 + index * 96 / max(1, count - 1)) * (10 + index * 4)
            shard(position, (8 + index % 2 * 4) * scale, color if index % 2 else accent, 5, index)
    elif motif == "flames":
        for index in range(count):
            flame_center = center + direction * (index - (count - 1) / 2) * 8
            height = (12 + (index % 3) * 5) * scale
            shape = [flame_center - side * 5, flame_center + direction * height,
                     flame_center + side * 5, flame_center + direction * height * 0.25]
            pygame.draw.polygon(SCREEN, color if index % 2 else accent, [xy(point) for point in shape])
    elif motif == "faultline":
        points = [start]
        for index in range(1, 9):
            points.append(start + direction * reach * index / 8 + side * (13 if index % 2 else -13))
        stroke(points, color, 4)
        for sign in (-1, 1):
            stroke([center, center + direction * 12 + side * sign * 23,
                    center + direction * 27 + side * sign * 31], accent, 2)
    elif motif == "meteor":
        trail = [start - direction * 23, start - direction * 11 + side * 8,
                 center + side * 5, center - side * 5]
        pygame.draw.polygon(SCREEN, color, [xy(point) for point in trail])
        star(center, 15 * scale, accent, 6)
        ray_burst(count, 14, 28 * scale, color)
    elif motif == "rivets":
        stroke([start, end], color, 4)
        for index in range(1, count + 1):
            position = start.lerp(end, index / (count + 1))
            shard(position, 4 * scale, accent, 4, math.pi / 4)
    elif motif == "breach":
        size = 14 * scale
        corners = [center + direction * size + side * size,
                   center - direction * size + side * size,
                   center - direction * size - side * size,
                   center + direction * size - side * size]
        for index in range(4):
            if index != 1:
                stroke([corners[index], corners[(index + 1) % 4]], color, 4)
        for sign in (-1, 1):
            shard(center + direction * sign * 26, 6 * scale, accent, 4, math.pi / 4)
    elif motif == "rivet_storm":
        for index in range(count):
            position = center + direction.rotate(-65 + index * 130 / max(1, count - 1)) * (10 + index * 3)
            shard(position, 4 * scale, accent if index % 2 else color, 4, math.pi / 4)
            stroke([position - direction * 9, position + direction * 9], color, 2)
    elif motif == "sparks":
        for index in range(count):
            ray = direction.rotate(-70 + index * 140 / max(1, count - 1))
            stroke([center + ray * 5, center + ray * (15 + index % 3 * 5)], accent, 3)
        star(center, 7 * scale, color, 4)
    elif motif == "royal_hook":
        arc(reach * 0.55, 230, color, 5)
        stroke([center + direction * 5, center + direction * 22,
                center + direction * 22 + side * 13], accent, 4)
        star(center + side * 18, 7 * scale, accent, 4)
    elif motif == "reed_thrust":
        stroke([start, end], color, 4)
        for index in range(count):
            position = start.lerp(end, (index + 1) / (count + 1))
            sign = -1 if index % 2 else 1
            leaf = [xy(position), xy(position + direction * 10 + side * sign * 7),
                    xy(position + direction * 18)]
            pygame.draw.polygon(SCREEN, accent if index % 2 else color, leaf)
    elif motif == "gale":
        for index in range(count):
            arc(reach * (0.35 + index * 0.09), 65 + index * 7,
                color if index % 2 else accent, 2)
    elif motif == "viper":
        points = [start]
        for index in range(1, 8):
            points.append(start + direction * reach * index / 8 + side * (11 if index % 2 else -11))
        stroke(points, color, 4)
        for sign in (-1, 1):
            shard(center + direction * 7 + side * sign * 7, 7 * scale, accent, 3, 0.1)
    elif motif == "sun_lance":
        stroke([start, end], color, 7)
        stroke([start, end], accent, 2)
        shard(center, 15 * scale, accent, 4, math.pi / 4)
        ray_burst(count, 15, 27 * scale, color)
    elif motif == "roots":
        for sign in (-1, 1):
            stroke([start, center, center + direction * 15 + side * sign * 13,
                    center + direction * 30 + side * sign * 10], color, 4)
            stroke([center + direction * 15 + side * sign * 13,
                    center + direction * 17 + side * sign * 25], accent, 2)
    elif motif == "boulder":
        rock = [center + direction * 13, center + direction * 9 + side * 12,
                center - direction * 7 + side * 13, center - direction * 15,
                center - direction * 3 - side * 12, center + direction * 10 - side * 8]
        pygame.draw.polygon(SCREEN, color, [xy(point) for point in rock], 3)
        for index in range(count):
            shard(center + direction.rotate(index * 360 / count) * 24, 4 * scale, accent, 4)
    elif motif == "spikes":
        for index in range(count):
            ray = direction.rotate((index - (count - 1) / 2) * 18)
            shard(center + ray * 19, 10 * scale, color if index % 2 else accent, 3,
                  math.atan2(ray.y, ray.x))
            stroke([center + ray * 4, center + ray * 15], accent, 2)
    elif motif == "thunderclap":
        for index in range(count):
            ray = pygame.Vector2(1, 0).rotate(index * 360 / count + progress * 10)
            stroke([center + ray * 7, center + ray * (20 + progress * 12)], color, 3)
        stroke([center + direction * 5, center - side * 5, center + direction * 12,
                center + side * 7, center + direction * 19], accent, 4)
    elif motif == "meteor_drop":
        rock = [center + direction * 15, center + direction * 4 + side * 12,
                center - direction * 12 + side * 8, center - direction * 14 - side * 9,
                center + direction * 3 - side * 12]
        pygame.draw.polygon(SCREEN, color, [xy(point) for point in rock])
        for index in range(count):
            ray = side.rotate((index - (count - 1) / 2) * 15)
            stroke([center - direction * 25 + ray * 5, center + ray * 18], accent, 2)
    elif motif == "gravity":
        for orbit in range(3):
            points = [center + direction.rotate(index * 30 + orbit * 120) *
                      (16 + orbit * 8 + progress * 7) +
                      side * math.sin(math.radians(index * 30 + orbit * 120)) * 7
                      for index in range(13)]
            stroke(points, color if orbit % 2 else accent, 2)
        star(center, 8 * scale, accent, 6)


def draw_game(hero, enemies, level_index, walls, chest, levers, lever_sequence,
              lever_solved, arrows, drops, effects, runes, message):
    level = LEVELS[level_index]
    SCREEN.fill(DARK)
    pygame.draw.rect(SCREEN, (31, 33, 44), (0, 0, WIDTH, MAP_TOP))
    title = FONT.render(f"LEVEL {level_index + 1}: {level['name']}", True, WHITE)
    SCREEN.blit(title, (18, 17))

    # Health bar and potion counter.
    pygame.draw.rect(SCREEN, (65, 67, 76), (350, 20, 190, 24), border_radius=6)
    health_width = round(186 * max(0, hero.hp) / hero.max_hp)
    pygame.draw.rect(SCREEN, GREEN if hero.hp > 30 else RED,
                     (352, 22, health_width, 20), border_radius=5)
    hp_label = SMALL_FONT.render(f"{round(hero.hp)}/{hero.max_hp} HP", True, WHITE)
    SCREEN.blit(hp_label, hp_label.get_rect(center=(445, 32)))
    rank = hero.weapon_tiers.get(hero.weapon, 1)
    variant = get_weapon_variant(hero)
    items = TINY_FONT.render(
        f"{variant['name']} Lv{rank} | E:{hero.selected_potion} R:{hero.selected_rune}", True, WHITE)
    SCREEN.blit(items, (565, 15))
    status_text = f"Enemies: {len(enemies)} | Q: {variant['special']} | R rune | E potion"
    if hero.phantom_timer > 0:
        status_text += f" | INVISIBLE {hero.phantom_timer:.1f}s"
    status = TINY_FONT.render(status_text, True, WHITE)
    SCREEN.blit(status, (565, 39))
    armor_markers = "".join(name[0].upper() for name, equipped in hero.equipment.items() if equipped) or "-"
    resources = TINY_FONT.render(
        f"Scrap {hero.materials['scrap']} Herbs {hero.materials['herbs']} "
        f"Crystals {hero.materials['crystals']} Cores {hero.materials['cores']} "
        f"Armor {armor_markers} -{round(armor_weight(hero) * 4.5)}% speed", True, WHITE)
    SCREEN.blit(resources, (565, 56))

    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * TILE, MAP_TOP + y * TILE, TILE, TILE)
            shade = 5 if (x + y) % 2 else 0
            color = tuple(min(255, c + shade) for c in level["floor"])
            pygame.draw.rect(SCREEN, color, rect)
            pygame.draw.rect(SCREEN, tuple(min(255, c + 9) for c in color), rect, 1)

    for wall in walls:
        pygame.draw.rect(SCREEN, level["wall"], wall, border_radius=5)
        pygame.draw.rect(SCREEN, tuple(min(255, c + 20) for c in level["wall"]), wall, 2, border_radius=5)

    for rune in runes:
        color = RUNE_TYPES[rune.kind]["color"]
        pulse = round(4 * math.sin(pygame.time.get_ticks() / 120))
        x, y = rune.center
        if rune.kind == "slow":
            pygame.draw.line(SCREEN, color, (x, y - 15 - pulse), (x, y + 15 + pulse), 3)
            pygame.draw.line(SCREEN, color, (x - 13, y - 8), (x + 13, y + 8), 3)
            pygame.draw.line(SCREEN, color, (x - 13, y + 8), (x + 13, y - 8), 3)
            for angle in (0, 60, 120):
                direction = pygame.Vector2(1, 0).rotate(angle)
                point = pygame.Vector2(x, y) + direction * 38
                pygame.draw.line(SCREEN, color, (x, y),
                                 (round(point.x), round(point.y)), 1)
        elif rune.kind == "fire":
            flame = [(x, y - 20 - pulse), (x + 13, y - 2), (x + 8, y + 15),
                     (x, y + 8), (x - 9, y + 16), (x - 14, y - 2)]
            pygame.draw.polygon(SCREEN, color, flame, 3)
            pygame.draw.line(SCREEN, (255, 235, 155), (x, y - 8), (x + 2, y + 8), 2)
        elif rune.kind == "thunder":
            bolt = [(x + 5, y - 20), (x - 8, y - 1), (x + 1, y - 1),
                    (x - 5, y + 20), (x + 10, y - 4), (x + 2, y - 4)]
            pygame.draw.lines(SCREEN, color, False, bolt, 4)
        elif rune.kind == "lure":
            diamond = [(x, y - 18 - pulse), (x + 18, y), (x, y + 18 + pulse), (x - 18, y)]
            pygame.draw.polygon(SCREEN, color, diamond, 3)
            pygame.draw.line(SCREEN, color, (x - 8, y), (x + 8, y), 2)
            pygame.draw.polygon(SCREEN, color, [(x + 8, y - 5), (x + 14, y), (x + 8, y + 5)])
            for angle in (0, 90, 180, 270):
                ray = pygame.Vector2(1, 0).rotate(angle) * 44
                pygame.draw.line(SCREEN, color, (x, y),
                                 (round(x + ray.x), round(y + ray.y)), 1)
        else:
            corners = [(-18, -12), (-12, -18), (12, -18), (18, -12),
                       (18, 12), (12, 18), (-12, 18), (-18, 12)]
            for index in (0, 2, 4, 6):
                a = corners[index]
                b = corners[(index + 1) % len(corners)]
                pygame.draw.line(SCREEN, color, (x + a[0], y + a[1]),
                                 (x + b[0], y + b[1]), 3)
            pygame.draw.line(SCREEN, color, (x - 8, y), (x + 8, y), 2)
            pygame.draw.line(SCREEN, color, (x, y - 8), (x, y + 8), 2)

    if level_index == 14:
        clue = ROOM_PUZZLES[15]["clue"]
        pygame.draw.rect(SCREEN, (25, 27, 38), (45, MAP_TOP + 4, WIDTH - 90, 24), border_radius=5)
        draw_text(SCREEN, clue + "  F: pull nearby lever", TINY_FONT, GOLD,
                  (WIDTH // 2, MAP_TOP + 16))
        for lever in levers:
            lever.animation += 1 / FPS
            pulse = round(2 * math.sin(lever.animation * 5))
            color = GOLD if lever.pulled else (155, 165, 185)
            pygame.draw.rect(SCREEN, (75, 78, 91), (lever.rect.x, lever.rect.bottom - 5, 24, 8), border_radius=3)
            lean = -8 if lever.pulled else 7 + pulse
            pygame.draw.line(SCREEN, color, lever.rect.midbottom,
                             (lever.rect.centerx + lean, lever.rect.y + 5), 5)
            pygame.draw.circle(SCREEN, color, (lever.rect.centerx + lean, lever.rect.y + 5), 5)
            draw_text(SCREEN, lever.symbol, TINY_FONT, WHITE,
                      (lever.rect.centerx, lever.rect.y - 8))
        if lever_solved:
            draw_text(SCREEN, "BOSS SHIELD DOWN!", SMALL_FONT, GOLD, (WIDTH // 2, MAP_TOP + 45))

    # Loot chest bobs and glows until opened.
    chest.animation_time += 1 / FPS
    chest_bob = round(math.sin(chest.animation_time * 3) * 2) if not chest.opened else 0
    chest_rect = chest.rect.move(0, chest_bob)
    if not chest.opened:
        glow = 115 + round(35 * (1 + math.sin(chest.animation_time * 4)))
        pygame.draw.circle(SCREEN, (glow, glow, 65), chest_rect.center, 21, 2)
    pygame.draw.rect(SCREEN, (93, 54, 27) if not chest.opened else (60, 51, 45), chest_rect, border_radius=4)
    lid_lift = min(10, round(chest.animation_time * 24)) if chest.opened else 0
    lid_rect = pygame.Rect(chest_rect.x, chest_rect.y - lid_lift, chest_rect.width, 10)
    pygame.draw.rect(SCREEN, (122, 74, 34) if not chest.opened else (76, 63, 47), lid_rect, border_radius=4)
    pygame.draw.rect(SCREEN, (224, 172, 65) if not chest.opened else (95, 78, 57),
                     (chest_rect.x, chest_rect.y + 8, chest_rect.width, 5), border_radius=2)
    pygame.draw.rect(SCREEN, GOLD if not chest.opened else (75, 67, 55),
                     (chest_rect.centerx - 3, chest_rect.centery - 2, 6, 8), border_radius=2)
    if not chest.opened:
        draw_text(SCREEN, "F", SMALL_FONT, WHITE, (chest_rect.centerx, chest_rect.y - 9))

    for drop in drops:
        drop.animation_time += 1 / FPS
        bob = round(math.sin(drop.animation_time * 5) * 3)
        drop_rect = drop.rect.move(0, bob)
        color = MaterialDrop.COLORS[drop.kind]
        pygame.draw.circle(SCREEN, color, drop_rect.center, 9)
        pygame.draw.circle(SCREEN, WHITE, drop_rect.center, 9, 1)
        draw_text(SCREEN, str(drop.amount), TINY_FONT, WHITE, (drop_rect.centerx + 12, drop_rect.centery - 9))

    exit_rect = pygame.Rect((COLS - 2) * TILE + 8, MAP_TOP + (ROWS - 2) * TILE + 5, 24, 30)
    exit_color = GOLD if not enemies else (90, 75, 55)
    if not enemies:
        portal_pulse = 2 + round(2 * (1 + math.sin(pygame.time.get_ticks() / 160)))
        pygame.draw.circle(SCREEN, (255, 215, 90), exit_rect.center, 19 + portal_pulse, 2)
    pygame.draw.rect(SCREEN, exit_color, exit_rect, border_radius=5)
    draw_text(SCREEN, "EXIT" if not enemies else "LOCKED", SMALL_FONT, WHITE,
              (exit_rect.centerx, exit_rect.y - 12))

    for enemy in enemies:
        enemy.animation_time += 1 / FPS
        bob = round(math.sin(enemy.animation_time * 8) * 2) if enemy.stun_timer <= 0 else 0
        enemy_rect = enemy.rect.move(0, bob)
        enemy_stride = round(math.sin(enemy.animation_time * 12) * 4) if enemy.stun_timer <= 0 else 0
        pygame.draw.line(SCREEN, (70, 35, 40), (enemy_rect.centerx - 6, enemy_rect.bottom - 3),
                         (enemy_rect.centerx - 8 + enemy_stride, enemy_rect.bottom + 5), 4)
        pygame.draw.line(SCREEN, (70, 35, 40), (enemy_rect.centerx + 6, enemy_rect.bottom - 3),
                         (enemy_rect.centerx + 8 - enemy_stride, enemy_rect.bottom + 5), 4)
        if enemy.is_boss:
            pulse = round(4 + 2 * math.sin(enemy.animation_time * 4))
            boss_ring = (120, 215, 255) if enemy.shielded else (
                (255, 125, 70) if enemy.gimmick_active or enemy.final_form else (150, 45, 50))
            pygame.draw.circle(SCREEN, boss_ring, enemy_rect.center, enemy_rect.width // 2 + pulse, 2)
            if enemy.shielded:
                pygame.draw.circle(SCREEN, (110, 205, 255), enemy_rect.center,
                                   enemy_rect.width // 2 + 11 + pulse, 3)
            gimmick_label = {
                "shifting_ward": "WARD CLOSED" if enemy.shielded else "WARD OPEN",
                "blink_hunter": "RIFT STALKER",
                "soul_summoner": "SUMMONS HEAL IT",
                "charging_boss": "CHARGING!" if enemy.gimmick_active else "CHARGE SOON",
                "rune_ward": "PLACE A RUNE" if enemy.shielded else "WARD BROKEN",
                "soul_leech": "HEALTH LEECH",
                "final_form": "FINAL FORM" if enemy.final_form else "DEVOURER",
            }.get(enemy.boss_gimmick, enemy.boss_name)
            draw_text(SCREEN, gimmick_label, TINY_FONT, GOLD,
                      (enemy_rect.centerx, enemy_rect.top - 19))
            pygame.draw.polygon(SCREEN, GOLD, [
                (enemy_rect.left + 5, enemy_rect.top + 6),
                (enemy_rect.left + 10, enemy_rect.top - 8),
                (enemy_rect.centerx, enemy_rect.top + 2),
                (enemy_rect.right - 10, enemy_rect.top - 8),
                (enemy_rect.right - 5, enemy_rect.top + 6),
            ])
        enemy_color = WHITE if enemy.hit_flash > 0 else ((125, 45, 65) if enemy.is_boss else (185, 71, 72))
        pygame.draw.ellipse(SCREEN, (40, 26, 28), enemy_rect.move(0, 5))
        pygame.draw.rect(SCREEN, enemy_color, enemy_rect, border_radius=12 if enemy.is_boss else 8)
        if enemy.burn_timer > 0:
            pygame.draw.circle(SCREEN, (255, 115, 45), enemy_rect.center, enemy_rect.width // 2 + 5, 2)
        elif enemy.slow_timer > 0:
            pygame.draw.circle(SCREEN, (105, 190, 255), enemy_rect.center, enemy_rect.width // 2 + 5, 2)
        elif enemy.venom_timer > 0:
            pygame.draw.circle(SCREEN, (145, 220, 95), enemy_rect.center, enemy_rect.width // 2 + 5, 2)
        eye_y = enemy_rect.centery - 4 if enemy.is_boss else enemy_rect.centery - 2
        pygame.draw.circle(SCREEN, (255, 220, 190), (enemy_rect.centerx - 7, eye_y), 4 if enemy.is_boss else 3)
        pygame.draw.circle(SCREEN, (255, 220, 190), (enemy_rect.centerx + 7, eye_y), 4 if enemy.is_boss else 3)
        if enemy.attack_flash > 0:
            pygame.draw.circle(SCREEN, (255, 105, 75), enemy_rect.center, enemy_rect.width // 2 + 8, 3)
        bar_width = 54 if enemy.is_boss else 30
        bar = pygame.Rect(enemy_rect.centerx - bar_width // 2, enemy_rect.y - 9, bar_width, 5)
        pygame.draw.rect(SCREEN, (55, 35, 35), bar)
        pygame.draw.rect(SCREEN, RED, (bar.x, bar.y, round(bar_width * enemy.hp / enemy.max_hp), 5))
        enemy.hit_flash = max(0, enemy.hit_flash - 1 / FPS)
        enemy.attack_flash = max(0, enemy.attack_flash - 1 / FPS)

    # Arrows have short tails so their direction is visible.
    for arrow in arrows:
        tail = pygame.Vector2(arrow.rect.center) - arrow.velocity.normalize() * 12
        pygame.draw.line(SCREEN, arrow.color, arrow.rect.center, (round(tail.x), round(tail.y)), 3)
        pygame.draw.circle(SCREEN, WHITE, arrow.rect.center, 2)

    for effect in effects:
        progress = min(1, effect.timer / effect.duration)
        radius = max(1, round(effect.max_radius * progress))
        burst = []
        for point in range(16):
            point_radius = radius if point % 2 == 0 else round(radius * 0.62)
            angle = math.tau * point / 16
            burst.append((effect.center[0] + round(math.cos(angle) * point_radius),
                          effect.center[1] + round(math.sin(angle) * point_radius)))
        pygame.draw.polygon(SCREEN, (255, 95, 55), burst, max(2, 8 - round(progress * 6)))
        for angle in range(0, 360, 45):
            direction = pygame.Vector2(1, 0).rotate(angle)
            inner = pygame.Vector2(effect.center) + direction * radius * 0.45
            outer = pygame.Vector2(effect.center) + direction * radius * 0.82
            pygame.draw.line(SCREEN, (255, 220, 125),
                             (round(inner.x), round(inner.y)),
                             (round(outer.x), round(outer.y)), 3)

    if hero.special_vfx_timer > 0:
        progress = 1 - hero.special_vfx_timer / hero.special_vfx_duration
        start = pygame.Vector2(hero.special_vfx_start)
        end = pygame.Vector2(hero.special_vfx_end)
        direction = end - start
        if direction.length_squared() == 0:
            direction = pygame.Vector2(hero.facing)
        direction = direction.normalize()
        side = direction.rotate(90)
        color = hero.special_vfx_color
        if hero.special_vfx == "armor_knight":
            shield = [start + direction * 24, start + direction * 8 + side * 19,
                      start - direction * 12 + side * 15, start - direction * 22,
                      start - direction * 12 - side * 15, start + direction * 8 - side * 19]
            pygame.draw.polygon(SCREEN, (255, 220, 120), shield, 4)
            for shard in (-1, 1):
                point = start + direction * 32 + side * shard * 22
                pygame.draw.line(SCREEN, WHITE, (round(start.x), round(start.y)),
                                 (round(point.x), round(point.y)), 3)
        elif hero.special_vfx in ("armor_phantom", "armor_impact"):
            for ghost in range(3):
                offset = side * (ghost - 1) * (8 + 14 * progress)
                a = start - direction * (ghost * 7) + offset
                b = end + offset
                points = [a + direction * 20, b + side * 7, b - direction * 10, a - side * 9]
                shade = (190, 155, 255) if hero.special_vfx == "armor_phantom" else (255, 170, 125)
                pygame.draw.polygon(SCREEN, shade, [(round(point.x), round(point.y)) for point in points], 2)
        elif hero.special_vfx == "samurai_dash" or hero.special_vfx in ("shadow_dash", "phase_step"):
            for trail in range(4):
                offset = side * (trail - 1.5) * 7
                a, b = start + offset, end + offset
                pygame.draw.line(SCREEN, color if trail != 1 else WHITE,
                                 (round(a.x), round(a.y)), (round(b.x), round(b.y)),
                                 max(1, 5 - trail))
        else:
            draw_weapon_vfx(hero.special_vfx_variant, start, end, progress)

    cloaked = hero.phantom_timer > 0
    player_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) if cloaked else SCREEN
    if cloaked or hero.invulnerable <= 0 or int(pygame.time.get_ticks() / 100) % 2 == 0:
        moving = getattr(hero, "moving", False)
        bob = round(math.sin(hero.animation_time * 14) * 2) if moving else 0
        hero_rect = hero.rect.move(0, bob)
        stride = round(math.sin(hero.animation_time * 16) * 5) if moving else 0
        if hero.strength_timer > 0:
            aura = 24 + round(3 * math.sin(hero.animation_time * 10))
            pygame.draw.circle(player_surface, (255, 190, 65), hero_rect.center, aura, 2)
        if hero.speed_timer > 0:
            trail = pygame.Vector2(hero_rect.center) - hero.facing * (12 + abs(stride))
            pygame.draw.line(player_surface, (100, 210, 255), hero_rect.center,
                             (round(trail.x), round(trail.y)), 3)
        # Animated feet, arms, and a short cape trail.
        pygame.draw.line(player_surface, (35, 55, 88), (hero_rect.centerx - 5, hero_rect.bottom - 4),
                         (hero_rect.centerx - 7 + stride, hero_rect.bottom + 5), 4)
        pygame.draw.line(player_surface, (35, 55, 88), (hero_rect.centerx + 5, hero_rect.bottom - 4),
                         (hero_rect.centerx + 7 - stride, hero_rect.bottom + 5), 4)
        pygame.draw.polygon(player_surface, (52, 104, 170), [
            (hero_rect.left + 4, hero_rect.centery),
            (hero_rect.left - 7 - abs(stride), hero_rect.bottom + 2),
            (hero_rect.centerx - 2, hero_rect.bottom - 2),
        ])
        pygame.draw.ellipse(player_surface, (30, 30, 36), hero_rect.move(0, 5))
        pygame.draw.rect(player_surface, (75, 148, 225), hero_rect, border_radius=8)
        pygame.draw.circle(player_surface, WHITE, (hero_rect.centerx + 5, hero_rect.centery - 3), 3)
        if hero.equipment["chestplate"]:
            pygame.draw.rect(player_surface, (177, 185, 198), (hero_rect.centerx - 9, hero_rect.y + 5, 18, 12), border_radius=4)
        if hero.equipment["leggings"]:
            pygame.draw.rect(player_surface, (92, 102, 125), (hero_rect.centerx - 9, hero_rect.bottom - 8, 18, 7))
        if hero.equipment["helmet"]:
            pygame.draw.arc(player_surface, (220, 225, 232),
                            (hero_rect.centerx - 9, hero_rect.y - 5, 18, 15), 0, math.pi, 4)
        if hero.equipment["boots"]:
            pygame.draw.line(player_surface, (118, 79, 53), (hero_rect.centerx - 7, hero_rect.bottom + 5),
                             (hero_rect.centerx + 7, hero_rect.bottom + 5), 5)
        if hero.special_armor == "knight":
            pygame.draw.polygon(player_surface, (205, 215, 225), [
                (hero_rect.left - 3, hero_rect.y + 7), (hero_rect.left + 4, hero_rect.y + 3),
                (hero_rect.centerx, hero_rect.y + 9), (hero_rect.left + 6, hero_rect.y + 15),
            ])
            pygame.draw.polygon(player_surface, (205, 215, 225), [
                (hero_rect.right + 3, hero_rect.y + 7), (hero_rect.right - 4, hero_rect.y + 3),
                (hero_rect.centerx, hero_rect.y + 9), (hero_rect.right - 6, hero_rect.y + 15),
            ])
            pygame.draw.polygon(player_surface, (247, 200, 80), [
                (hero_rect.centerx, hero_rect.centery - 5), (hero_rect.centerx + 5, hero_rect.centery),
                (hero_rect.centerx, hero_rect.centery + 5), (hero_rect.centerx - 5, hero_rect.centery),
            ])
            if hero.parry_timer > 0:
                pygame.draw.polygon(player_surface, (255, 230, 145), [
                    (hero_rect.centerx, hero_rect.top - 10), (hero_rect.right + 10, hero_rect.centery),
                    (hero_rect.centerx, hero_rect.bottom + 10), (hero_rect.left - 10, hero_rect.centery),
                ], 3)
        elif hero.special_armor == "samurai":
            pygame.draw.line(player_surface, (195, 65, 75),
                             (hero_rect.left - 4, hero_rect.y + 8),
                             (hero_rect.right + 4, hero_rect.y + 11), 4)
            pygame.draw.polygon(player_surface, (220, 65, 70), [
                (hero_rect.centerx - 9, hero_rect.bottom - 8),
                (hero_rect.centerx + 10, hero_rect.bottom - 8),
                (hero_rect.centerx + 7, hero_rect.bottom - 2),
                (hero_rect.centerx - 6, hero_rect.bottom - 2),
            ])
        elif hero.special_armor == "phantom":
            for shard in (-1, 1):
                pygame.draw.polygon(player_surface, (165, 120, 230), [
                    (hero_rect.centerx + shard * 10, hero_rect.y + 4),
                    (hero_rect.centerx + shard * 17, hero_rect.centery),
                    (hero_rect.centerx + shard * 10, hero_rect.bottom - 4),
                ], 2)
        arm = pygame.Vector2(hero_rect.center) + hero.facing.rotate(90) * 5
        arm_point = (round(arm.x), round(arm.y))
        pygame.draw.line(player_surface, (245, 190, 150), hero_rect.center, arm_point, 4)
        weapon_color = WEAPONS[hero.weapon]["color"]
        swing = hero.facing.rotate(35 - hero.action_timer * 100) if hero.action_timer > 0 else hero.facing
        tip = pygame.Vector2(hero_rect.center) + swing * (27 if hero.weapon == "bow" else 34)
        pygame.draw.line(player_surface, weapon_color, arm_point, (round(tip.x), round(tip.y)), 4)
        if hero.weapon == "bow":
            pygame.draw.line(player_surface, WHITE, (round(tip.x), round(tip.y)),
                             (round(tip.x - swing.x * 17), round(tip.y - swing.y * 17)), 2)
        elif hero.weapon == "spear":
            shaft = tip + swing * 11
            pygame.draw.line(player_surface, (228, 220, 190),
                             (round(tip.x), round(tip.y)), (round(shaft.x), round(shaft.y)), 3)
        elif hero.weapon == "mace":
            pygame.draw.polygon(player_surface, (205, 210, 220), [
                (round(tip.x), round(tip.y)), (round(tip.x + 5), round(tip.y - 5)),
                (round(tip.x + 10), round(tip.y)), (round(tip.x + 5), round(tip.y + 5)),
            ])
    if cloaked:
        player_surface.set_alpha(92)
        SCREEN.blit(player_surface, (0, 0))

    if hero.bark_timer > 0:
        bark_font = TINY_FONT
        bubble_width = min(320, max(165, bark_font.size(hero.bark_text)[0] + 30))
        bubble = pygame.Rect(hero.rect.centerx - bubble_width // 2,
                             max(MAP_TOP + 3, hero.rect.top - 43), bubble_width, 32)
        bubble.clamp_ip(SCREEN.get_rect())
        pygame.draw.rect(SCREEN, (250, 244, 224), bubble, border_radius=8)
        pygame.draw.rect(SCREEN, (88, 98, 125), bubble, 2, border_radius=8)
        draw_text(SCREEN, hero.bark_text, bark_font, (45, 50, 67), bubble.center)
        pygame.draw.polygon(SCREEN, (250, 244, 224), [
            (hero.rect.centerx - 5, bubble.bottom - 1),
            (hero.rect.centerx + 5, bubble.bottom - 1),
            (hero.rect.centerx, bubble.bottom + 7),
        ])

    if message:
        draw_text(SCREEN, message, SMALL_FONT, GOLD, (WIDTH // 2, HEIGHT - 18))
    if hero.weapon == "bow":
        cursor_x, cursor_y = logical_mouse_position()
        reticle = (190, 225, 255)
        pygame.draw.line(SCREEN, reticle, (cursor_x - 12, cursor_y - 12), (cursor_x - 5, cursor_y - 12), 2)
        pygame.draw.line(SCREEN, reticle, (cursor_x - 12, cursor_y - 12), (cursor_x - 12, cursor_y - 5), 2)
        pygame.draw.line(SCREEN, reticle, (cursor_x + 12, cursor_y - 12), (cursor_x + 5, cursor_y - 12), 2)
        pygame.draw.line(SCREEN, reticle, (cursor_x + 12, cursor_y - 12), (cursor_x + 12, cursor_y - 5), 2)
        pygame.draw.line(SCREEN, reticle, (cursor_x - 12, cursor_y + 12), (cursor_x - 5, cursor_y + 12), 2)
        pygame.draw.line(SCREEN, reticle, (cursor_x - 12, cursor_y + 12), (cursor_x - 12, cursor_y + 5), 2)
        pygame.draw.line(SCREEN, reticle, (cursor_x + 12, cursor_y + 12), (cursor_x + 5, cursor_y + 12), 2)
        pygame.draw.line(SCREEN, reticle, (cursor_x + 12, cursor_y + 12), (cursor_x + 12, cursor_y + 5), 2)
    elif hero.runes[hero.selected_rune] > 0:
        cursor = logical_mouse_position()
        rune_color = RUNE_TYPES[hero.selected_rune]["color"]
        if hero.selected_rune == "teleport":
            destination = hero.rect.copy()
            destination.center = cursor
            valid = (destination.left >= TILE and destination.right <= (COLS - 1) * TILE
                     and destination.top >= MAP_TOP + TILE
                     and destination.bottom <= MAP_TOP + (ROWS - 1) * TILE)
            valid = valid and not any(destination.colliderect(wall) for wall in walls)
            marker_color = rune_color if valid else RED
            pygame.draw.line(SCREEN, marker_color, destination.topleft,
                             (destination.left + 9, destination.top), 3)
            pygame.draw.line(SCREEN, marker_color, destination.topleft,
                             (destination.left, destination.top + 9), 3)
            pygame.draw.line(SCREEN, marker_color, destination.bottomright,
                             (destination.right - 9, destination.bottom), 3)
            pygame.draw.line(SCREEN, marker_color, destination.bottomright,
                             (destination.right, destination.bottom - 9), 3)
            pygame.draw.line(SCREEN, marker_color, destination.center,
                             cursor, 1)
        else:
            cx, cy = cursor
            pygame.draw.polygon(SCREEN, rune_color,
                                [(cx, cy - 10), (cx + 9, cy), (cx, cy + 10), (cx - 9, cy)], 2)
            pygame.draw.line(SCREEN, rune_color, (cx - 4, cy), (cx + 4, cy), 2)


def control_key_name(key):
    return pygame.key.name(key).upper()


def draw_controls(hero, tab, bindings, remap_mode=False, remapping_action=None):
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 215))
    SCREEN.blit(shade, (0, 0))
    panel = pygame.Rect(120, 65, WIDTH - 240, HEIGHT - 130)
    pygame.draw.rect(SCREEN, (35, 37, 49), panel, border_radius=12)
    pygame.draw.rect(SCREEN, GOLD, panel, 2, border_radius=12)
    draw_text(SCREEN, "FIELD GUIDE", TITLE_FONT, GOLD, (WIDTH // 2, 112))
    tabs = [("CONTROLS", 235), ("WEAPON GUIDE", 480), ("DIALOGUE", 725)]
    for index, (label, center_x) in enumerate(tabs):
        tab_rect = pygame.Rect(center_x - 105, 145, 210, 38)
        pygame.draw.rect(SCREEN, (78, 71, 48) if index == tab else (45, 48, 61),
                         tab_rect, border_radius=5)
        pygame.draw.rect(SCREEN, GOLD if index == tab else (100, 105, 120),
                         tab_rect, 2, border_radius=5)
        draw_text(SCREEN, label, SMALL_FONT, WHITE, tab_rect.center)

    if tab == 0:
        if remap_mode:
            draw_text(SCREEN, "CLICK AN ACTION, THEN PRESS THE KEY YOU WANT",
                      SMALL_FONT, GOLD, (WIDTH // 2, 190))
            actions = list(CONTROL_LABELS)
            for index, action in enumerate(actions):
                column, row_index = divmod(index, 9)
                row = pygame.Rect(135 + column * 230, 208 + row_index * 36, 220, 32)
                selected = action == remapping_action
                pygame.draw.rect(SCREEN, (78, 71, 48) if selected else (45, 48, 61),
                                 row, border_radius=5)
                pygame.draw.rect(SCREEN, GOLD if selected else (100, 105, 120),
                                 row, 1, border_radius=5)
                key_label = "PRESS A KEY..." if selected else control_key_name(bindings[action])
                draw_text(SCREEN, f"{CONTROL_LABELS[action]}: {key_label}",
                          TINY_FONT, GOLD if selected else WHITE, row.center)
            back_button = pygame.Rect(180, 548, 220, 34)
            reset_button = pygame.Rect(560, 548, 260, 34)
            for button in (back_button, reset_button):
                pygame.draw.rect(SCREEN, (65, 68, 80), button, border_radius=6)
                pygame.draw.rect(SCREEN, (150, 155, 170), button, 2, border_radius=6)
            draw_text(SCREEN, "BACK TO CONTROLS", SMALL_FONT, WHITE, back_button.center)
            draw_text(SCREEN, "RESTORE DEFAULT KEYS", SMALL_FONT, WHITE, reset_button.center)
        else:
            controls = [
                f"{control_key_name(bindings['move_up'])}/{control_key_name(bindings['move_left'])}/"
                f"{control_key_name(bindings['move_down'])}/{control_key_name(bindings['move_right'])}  Move",
                f"{control_key_name(bindings['attack'])}  Attack  |  Left click aims/fires bow",
                f"{control_key_name(bindings['special'])}  Weapon special ability",
                f"{control_key_name(bindings['armor'])}  Knight/Samurai/Phantom ability",
                f"{control_key_name(bindings['interact'])}  Open nearby chest or pull lever",
                f"{control_key_name(bindings['potion'])}  Use selected potion",
                f"{control_key_name(bindings['rune'])}  Place selected rune",
                f"{control_key_name(bindings['bomb'])}  Detonate a bomb",
                f"{control_key_name(bindings['inventory'])}  Open inventory",
                f"{control_key_name(bindings['crafting'])}  Open crafting",
                f"{control_key_name(bindings['field_guide'])}  Open/close Field Guide",
                f"{control_key_name(bindings['upgrade'])}  Upgrade weapon in weapon table",
                f"{control_key_name(bindings['skip_room'])}  Skip room/puzzle (not final boss)",
                f"{control_key_name(bindings['dialogue'])}  Toggle character dialogue",
                f"{control_key_name(bindings['fullscreen'])}  Toggle fullscreen",
                "Arrow keys / SPACE / ENTER  Navigate and solve puzzles",
            ]
            for index, text in enumerate(controls):
                draw_text(SCREEN, text, SMALL_FONT, WHITE, (WIDTH // 2, 195 + index * 21))
            customize_button = pygame.Rect(350, 540, 260, 34)
            pygame.draw.rect(SCREEN, (63, 83, 61), customize_button, border_radius=6)
            pygame.draw.rect(SCREEN, GREEN, customize_button, 2, border_radius=6)
            draw_text(SCREEN, "CUSTOMIZE CONTROLS", SMALL_FONT, WHITE, customize_button.center)
    elif tab == 1:
        draw_text(SCREEN, "Damage upgrades cost 3 cores each and add 10% damage.",
                  SMALL_FONT, (185, 190, 205), (WIDTH // 2, 190))
        for index, category in enumerate(WEAPON_ORDER):
            y = 210 + index * 54
            unlocked_rank = hero.weapons.get(category, 0)
            rank = hero.weapon_tiers.get(category, unlocked_rank)
            if unlocked_rank:
                variant = WEAPON_VARIANTS[category][rank - 1]
                rank_damage = rank * 4 if category == "bow" else (rank - 1) * 7
                weapon_damage = WEAPONS[category]["damage"] + rank_damage
                damage_text = (f"Unlocked {unlocked_rank}/5 | Damage "
                               f"{round(weapon_damage * variant['damage'] * (1 + hero.weapon_upgrades[category] * 0.1))} "
                               f"(+{hero.weapon_upgrades[category] * 10}%) | "
                               f"Reach {round(WEAPONS[category]['range'] * variant['range'])}")
                title = f"{index + 1}. {variant['name']}  Lv{rank}/5"
                trait = variant["trait"]
                special = variant["special"]
                color = GOLD if hero.weapon == category else WHITE
            else:
                damage_text = "Not yet found"
                title = f"{index + 1}. {category.title()}  LOCKED"
                trait = "Find or craft this weapon to unlock it."
                special = WEAPON_VARIANTS[category][0]["special"]
                color = (130, 135, 148)
            left = 165
            SCREEN.blit(FONT.render(title, True, color), (left, y))
            SCREEN.blit(TINY_FONT.render(damage_text, True, (195, 205, 220)), (left + 260, y + 3))
            SCREEN.blit(TINY_FONT.render(f"Trait: {trait}  |  Q: {special}",
                                         True, WHITE), (left + 18, y + 28))
    else:
        draw_text(SCREEN, "CHARACTER DIALOGUE", FONT, GOLD, (WIDTH // 2, 235))
        draw_text(SCREEN, "Controls the speech bubbles and story/cutscene dialogue.",
              SMALL_FONT, WHITE, (WIDTH // 2, 275))
        toggle_rect = pygame.Rect(WIDTH // 2 - 150, 320, 300, 58)
        enabled = hero.dialogue_enabled
        fill = (55, 100, 72) if enabled else (85, 55, 58)
        accent = GREEN if enabled else RED
        pygame.draw.rect(SCREEN, fill, toggle_rect, border_radius=9)
        pygame.draw.rect(SCREEN, accent, toggle_rect, 3, border_radius=9)
        draw_text(SCREEN, f"Dialogue: {'ON' if enabled else 'OFF'}",
              FONT, WHITE, toggle_rect.center)
        draw_text(SCREEN, "Click the button or press O to change this setting.",
              SMALL_FONT, (205, 210, 220), (WIDTH // 2, 415))
        draw_text(SCREEN, "When off, story scenes are skipped and character speech is hidden.",
              TINY_FONT, (175, 185, 200), (WIDTH // 2, 450))
    footer = ("Press a key to bind  |  ESC cancels binding  |  Click restore to reset"
              if tab == 0 and remap_mode else
              "TAB / LEFT / RIGHT switches tabs  |  L or ESC closes")
    draw_text(SCREEN, footer,
              SMALL_FONT, GOLD, (WIDTH // 2, panel.bottom - 28))


def draw_inventory(hero):
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 215))
    SCREEN.blit(shade, (0, 0))
    panel = pygame.Rect(90, 50, WIDTH - 180, HEIGHT - 100)
    pygame.draw.rect(SCREEN, (35, 37, 49), panel, border_radius=12)
    pygame.draw.rect(SCREEN, GOLD, panel, 2, border_radius=12)
    draw_text(SCREEN, "INVENTORY", TITLE_FONT, GOLD, (WIDTH // 2, 98))
    draw_text(SCREEN, f"Materials: scrap {hero.materials['scrap']}   herbs {hero.materials['herbs']}   "
              f"crystals {hero.materials['crystals']}   cores {hero.materials['cores']}",
              SMALL_FONT, WHITE, (WIDTH // 2, 145))

    draw_text(SCREEN, "WEAPONS  |  press 1-7 to equip", FONT, GOLD, (280, 190))
    for index, category in enumerate(WEAPON_ORDER):
        y = 220 + index * 48
        unlocked_rank = hero.weapons.get(category, 0)
        rank = hero.weapon_tiers.get(category, unlocked_rank)
        if unlocked_rank:
            variant = WEAPON_VARIANTS[category][rank - 1]
            name = f"{index + 1}. {variant['name']}  Lv{rank}"
            trait = f"{variant['trait']} | unlocked through Lv{unlocked_rank}"
            color = GOLD if hero.weapon == category else WHITE
        else:
            name, trait, color = f"{index + 1}. {category.title()}  (not found)", "", (125, 125, 135)
        draw_text(SCREEN, name, SMALL_FONT, color, (285, y))
        if trait:
            draw_text(SCREEN, trait, TINY_FONT, (185, 190, 205), (300, y + 20))

    gear_names = [name.title() for name, equipped in hero.equipment.items() if equipped]
    gear_text = ", ".join(gear_names) if gear_names else "None"
    draw_text(SCREEN, "GEAR", FONT, GOLD, (690, 190))
    draw_text(SCREEN, f"Normal: {gear_text}", TINY_FONT, WHITE, (690, 220))
    draw_text(SCREEN, f"Armor reduces damage by {round((1 - armor_damage_scale(hero)) * 100)}%",
              TINY_FONT, WHITE, (690, 241))
    special_name = (SPECIAL_ARMOR[hero.special_armor]["name"]
                    if hero.special_armor else "None")
    special_ability = (SPECIAL_ARMOR[hero.special_armor]["description"]
                       if hero.special_armor else "Normal armor has no ability.")
    draw_text(SCREEN, f"Special: {special_name}", TINY_FONT, GOLD, (690, 264))
    draw_text(SCREEN, special_ability, TINY_FONT, WHITE, (690, 283))
    draw_text(SCREEN, "ITEMS", FONT, GOLD, (690, 316))
    potion_rows = [
        ("health", f"Health potion: {hero.potions}"),
        ("strength", f"Strength potion: {hero.items['strength']}"),
        ("speed", f"Speed potion: {hero.items['speed']}"),
    ]
    for index, (kind, label) in enumerate(potion_rows):
        y = 350 + index * 25
        row = pygame.Rect(575, y - 11, 230, 23)
        pygame.draw.rect(SCREEN, (78, 71, 48) if hero.selected_potion == kind else (45, 48, 61),
                         row, border_radius=4)
        draw_text(SCREEN, label, TINY_FONT, WHITE, row.center)
    draw_text(SCREEN, "Click to select | E uses selected", TINY_FONT, GOLD, (690, 430))
    draw_text(SCREEN, f"Bombs: {hero.items['bomb']} (B)", SMALL_FONT, WHITE, (690, 455))
    draw_text(SCREEN, "RUNES  |  click to select, R places/teleports", TINY_FONT, GOLD, (690, 490))
    rune_positions = {
        "slow": (610, 520), "fire": (690, 520), "thunder": (770, 520),
        "lure": (610, 555), "teleport": (690, 555),
    }
    for kind, center in rune_positions.items():
        rune = RUNE_TYPES[kind]
        row = pygame.Rect(center[0] - 38, center[1] - 13, 76, 26)
        pygame.draw.rect(SCREEN, (78, 71, 48) if hero.selected_rune == kind else (45, 48, 61),
                         row, border_radius=4)
        pygame.draw.rect(SCREEN, rune["color"], row, 1, border_radius=4)
        draw_text(SCREEN, f"{kind.title()} {hero.runes[kind]}", TINY_FONT, WHITE, center)
    draw_text(SCREEN, f"Parry: {hero.parry_timer:.1f}s  Cloak: {hero.phantom_timer:.1f}s",
              TINY_FONT, WHITE, (690, 586))
    draw_text(SCREEN, "I or ESC to close", SMALL_FONT, GOLD, (WIDTH // 2, panel.bottom - 18))


def draw_overlay(title, subtitle):
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 185))
    SCREEN.blit(shade, (0, 0))
    draw_text(SCREEN, title, TITLE_FONT, GOLD, (WIDTH // 2, HEIGHT // 2 - 60))
    draw_text(SCREEN, subtitle, FONT, WHITE, (WIDTH // 2, HEIGHT // 2 + 5))
    draw_text(SCREEN, "WASD move | SPACE attack | Q special | F chest | 1-7 weapons | I inventory",
              SMALL_FONT, WHITE, (WIDTH // 2, HEIGHT // 2 + 50))
    draw_text(SCREEN, "C craft | L controls | E selected potion | R selected rune | B bomb | K skip room",
              SMALL_FONT, WHITE, (WIDTH // 2, HEIGHT // 2 + 78))


def main():
    hero = Hero()
    level_index = 0
    enemies, walls, chest, levers = new_level(level_index)
    hero.moving = False
    hero.room_had_enemies = bool(enemies)
    arrows = []
    drops = []
    effects = []
    runes = []
    runes = []
    state = "title"
    message = "Defeat every monster, open the chest, and reach the exit!"
    message_timer = 4.0
    dialogue_pages = []
    dialogue_index = 0
    after_dialogue = "playing"
    puzzle_state = {}
    puzzle_feedback = ""
    lever_sequence = []
    lever_solved = False
    controls_tab = 0
    controls_remap_mode = False
    remapping_action = None
    control_bindings = dict(CONTROL_DEFAULTS)
    craft_category = "sword"
    craft_tab = 0
    craft_selection = 0
    craft_tier_selection = 0
    running = True

    def load_next_level():
        nonlocal level_index, enemies, walls, chest, levers, arrows, drops, effects, runes
        nonlocal dialogue_pages, dialogue_index, after_dialogue, state, message
        nonlocal lever_sequence, lever_solved
        if level_index >= len(LEVELS) - 1:
            state = "won"
            return
        level_index += 1
        enemies, walls, chest, levers = new_level(level_index)
        arrows, drops, effects, runes = [], [], [], []
        lever_sequence = []
        lever_solved = False
        hero.rect.topleft = (TILE + 7, MAP_TOP + TILE + 7)
        hero.room_had_enemies = bool(enemies)
        hero.room_clear_spoken = False
        hero.hp = min(hero.max_hp, hero.hp + 20)
        hero.potions += 1
        dialogue_pages = dialogue_for_level(level_index)
        dialogue_index = 0
        after_dialogue = "playing"
        state = "dialogue" if hero.dialogue_enabled else "playing"
        hero.bark_text = ""
        hero.bark_timer = 0
        message = f"Level {level_index + 1}: {LEVELS[level_index]['name']}"

    while running:
        dt = min(CLOCK.tick(FPS) / 1000, 0.04)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if state == "controls" and remapping_action is not None:
                    if event.key == pygame.K_ESCAPE:
                        remapping_action = None
                    else:
                        previous_action = next(
                            (action for action, key in control_bindings.items()
                             if key == event.key and action != remapping_action),
                            None,
                        )
                        previous_key = control_bindings[remapping_action]
                        control_bindings[remapping_action] = event.key
                        if previous_action is not None:
                            control_bindings[previous_action] = previous_key
                        message = f"{CONTROL_LABELS[remapping_action]} bound to {control_key_name(event.key)}."
                        message_timer = 2.0
                        remapping_action = None
                elif event.key == control_bindings["dialogue"]:
                    hero.dialogue_enabled = not hero.dialogue_enabled
                    if not hero.dialogue_enabled:
                        hero.bark_text = ""
                        hero.bark_timer = 0
                        if state == "dialogue":
                            state = after_dialogue
                    message = f"Character dialogue {'enabled' if hero.dialogue_enabled else 'disabled'}."
                    message_timer = 2.0
                elif event.key == control_bindings["fullscreen"]:
                    set_fullscreen(not FULLSCREEN)
                elif event.key == pygame.K_ESCAPE:
                    if state == "weapon_craft":
                        state = "craft"
                    elif state in ("craft", "controls", "inventory"):
                        state = "playing"
                        controls_remap_mode = False
                    else:
                        running = False
                elif state == "craft":
                    if event.key == control_bindings["crafting"]:
                        state = "playing"
                    elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        change = -1 if event.key == pygame.K_LEFT else 1
                        craft_tab = (craft_tab + change) % len(CRAFT_TABS)
                        craft_selection = 0
                    elif event.key == pygame.K_UP:
                        craft_selection = (craft_selection - 1) % len(CRAFT_RECIPES[CRAFT_TABS[craft_tab]])
                    elif event.key == pygame.K_DOWN:
                        craft_selection = (craft_selection + 1) % len(CRAFT_RECIPES[CRAFT_TABS[craft_tab]])
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        recipe = CRAFT_RECIPES[CRAFT_TABS[craft_tab]][craft_selection]
                        if craft_tab == 1:
                            craft_category = recipe
                            rank = hero.weapons.get(craft_category, 0)
                            craft_tier_selection = min(rank + 1, WEAPON_MAX_LEVEL) - 1
                            state = "weapon_craft"
                        else:
                            message = craft_item(hero, recipe)
                            message_timer = 2.0
                elif state == "weapon_craft":
                    if event.key == control_bindings["crafting"]:
                        state = "craft"
                    elif event.key == pygame.K_UP:
                        craft_tier_selection = (craft_tier_selection - 1) % WEAPON_MAX_LEVEL
                    elif event.key == pygame.K_DOWN:
                        craft_tier_selection = (craft_tier_selection + 1) % WEAPON_MAX_LEVEL
                    elif event.key == control_bindings["upgrade"]:
                        message = upgrade_weapon(hero, craft_category)
                        message_timer = 2.0
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        message = craft_weapon_tier(hero, craft_category, craft_tier_selection + 1)
                        message_timer = 4.5
                elif state == "controls":
                    if event.key in (pygame.K_TAB, pygame.K_LEFT, pygame.K_RIGHT):
                        controls_tab = (controls_tab + 1) % 3
                    elif event.key in (control_bindings["field_guide"], pygame.K_RETURN, pygame.K_SPACE):
                        state = "playing"
                        controls_remap_mode = False
                elif state == "inventory":
                    if event.key == control_bindings["inventory"]:
                        state = "playing"
                    elif (weapon_slot := next(
                            (index for index in range(1, len(WEAPON_ORDER) + 1)
                             if event.key == control_bindings[f"weapon_{index}"]),
                            None,
                    )) is not None:
                        selected = WEAPON_ORDER[weapon_slot - 1]
                        if hero.weapons.get(selected, 0):
                            hero.weapon = selected
                            message = f"Equipped {get_weapon_variant(hero)['name']}"
                        else:
                            message = f"{selected.title()} is not in your inventory."
                        message_timer = 1.6
                elif state == "puzzle":
                    if (event.key == control_bindings["skip_room"]
                            and level_index < len(LEVELS) - 1):
                        load_next_level()
                        message = f"Puzzle skipped. Level {level_index + 1} begins."
                        message_timer = 2.0
                    else:
                        puzzle = ROOM_PUZZLES[level_index + 1]
                        kind = puzzle["kind"]
                        sequence = puzzle_state.get("sequence", [])
                        if kind in ("arrange", "crates"):
                            if event.key == pygame.K_LEFT:
                                puzzle_state["cursor"] = max(0, puzzle_state["cursor"] - 1)
                            elif event.key == pygame.K_RIGHT:
                                puzzle_state["cursor"] = min(len(sequence) - 2, puzzle_state["cursor"] + 1)
                            elif event.key == pygame.K_SPACE:
                                cursor = puzzle_state["cursor"]
                                sequence[cursor], sequence[cursor + 1] = sequence[cursor + 1], sequence[cursor]
                            elif event.key == pygame.K_RETURN:
                                if puzzle_solved(level_index + 1, puzzle_state):
                                    puzzle_feedback = "this guy dumb lol"
                                    load_next_level()
                                else:
                                    puzzle_feedback = "It opens. No it doesnt idiot"
                        elif kind == "sequence":
                            if event.key == pygame.K_LEFT:
                                puzzle_state["cursor"] = (puzzle_state["cursor"] - 1) % len(puzzle["symbols"])
                            elif event.key == pygame.K_RIGHT:
                                puzzle_state["cursor"] = (puzzle_state["cursor"] + 1) % len(puzzle["symbols"])
                            elif event.key == pygame.K_SPACE and len(sequence) < len(puzzle["goal"]):
                                sequence.append(puzzle["symbols"][puzzle_state["cursor"]])
                            elif event.key == pygame.K_BACKSPACE and sequence:
                                sequence.pop()
                            elif event.key == pygame.K_RETURN:
                                if puzzle_solved(level_index + 1, puzzle_state):
                                    puzzle_feedback = "The mechanism unlocks. finally dude"
                                    load_next_level()
                                else:
                                    puzzle_state["sequence"] = []
                                    puzzle_feedback = "Wrong order. The sequence resets; IDIOT"
                        elif kind == "path":
                            directions = ("UP", "RIGHT", "DOWN", "LEFT")
                            key_directions = {
                                pygame.K_UP: 0, pygame.K_RIGHT: 1,
                                pygame.K_DOWN: 2, pygame.K_LEFT: 3,
                            }
                            if event.key in key_directions:
                                puzzle_state["cursor"] = key_directions[event.key]
                            elif event.key == pygame.K_SPACE and len(sequence) < len(puzzle["goal"]):
                                sequence.append(directions[puzzle_state["cursor"]])
                            elif event.key == pygame.K_BACKSPACE and sequence:
                                sequence.pop()
                            elif event.key == pygame.K_RETURN:
                                if puzzle_solved(level_index + 1, puzzle_state):
                                    puzzle_feedback = "The safe path lights up. HOLY FINALLY"
                                    load_next_level()
                                else:
                                    puzzle_state["sequence"] = []
                                    puzzle_feedback = "A tile clicks shut. ARE U DUMB DUDE."
                        elif kind == "mirrors":
                            if event.key == pygame.K_LEFT:
                                puzzle_state["cursor"] = (puzzle_state["cursor"] - 1) % 3
                            elif event.key == pygame.K_RIGHT:
                                puzzle_state["cursor"] = (puzzle_state["cursor"] + 1) % 3
                            elif event.key in (pygame.K_UP, pygame.K_DOWN):
                                change = 1 if event.key == pygame.K_UP else -1
                                cursor = puzzle_state["cursor"]
                                puzzle_state["orientations"][cursor] = (puzzle_state["orientations"][cursor] + change) % 4
                            elif event.key == pygame.K_RETURN:
                                if puzzle_solved(level_index + 1, puzzle_state):
                                    puzzle_feedback = "This guy is genly dumb."
                                    load_next_level()
                                else:
                                    puzzle_feedback = "The beam misses. stupid try again"
                        elif kind == "rune_grid":
                            if event.key in (pygame.K_UP, pygame.K_DOWN,
                                             pygame.K_LEFT, pygame.K_RIGHT):
                                row, col = divmod(puzzle_state["cursor"], 3)
                                if event.key == pygame.K_UP:
                                    row = (row - 1) % 3
                                elif event.key == pygame.K_DOWN:
                                    row = (row + 1) % 3
                                elif event.key == pygame.K_LEFT:
                                    col = (col - 1) % 3
                                else:
                                    col = (col + 1) % 3
                                puzzle_state["cursor"] = row * 3 + col
                            elif event.key == pygame.K_SPACE:
                                toggle_rune_grid(puzzle_state["tiles"], puzzle_state["cursor"])
                            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                                if puzzle_solved(level_index + 1, puzzle_state):
                                    load_next_level()
                                else:
                                    puzzle_feedback = "The constellation is still scrambled are u stuipid."
                        elif kind == "pairs":
                            if event.key in (pygame.K_UP, pygame.K_DOWN,
                                             pygame.K_LEFT, pygame.K_RIGHT):
                                row, col = divmod(puzzle_state["cursor"], 4)
                                if event.key == pygame.K_UP:
                                    row = (row - 1) % 2
                                elif event.key == pygame.K_DOWN:
                                    row = (row + 1) % 2
                                elif event.key == pygame.K_LEFT:
                                    col = (col - 1) % 4
                                else:
                                    col = (col + 1) % 4
                                puzzle_state["cursor"] = row * 4 + col
                            elif event.key == pygame.K_SPACE:
                                cursor = puzzle_state["cursor"]
                                revealed = puzzle_state["revealed"]
                                if len(revealed) == 2:
                                    revealed.clear()
                                if cursor not in puzzle_state["matched"] and cursor not in revealed:
                                    revealed.append(cursor)
                                    if len(revealed) == 2:
                                        first, second = revealed
                                        if puzzle["cards"][first] == puzzle["cards"][second]:
                                            puzzle_state["matched"].update(revealed)
                                            revealed.clear()
                            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                                if puzzle_solved(level_index + 1, puzzle_state):
                                    load_next_level()
                                else:
                                    puzzle_feedback = "There are still unmatched tablets."
                        elif kind == "doors":
                            if event.key == pygame.K_LEFT:
                                puzzle_state["choice"] = (puzzle_state["choice"] - 1) % len(puzzle["choices"])
                            elif event.key == pygame.K_RIGHT:
                                puzzle_state["choice"] = (puzzle_state["choice"] + 1) % len(puzzle["choices"])
                            elif event.key == pygame.K_RETURN:
                                if puzzle_solved(level_index + 1, puzzle_state):
                                    puzzle_feedback = "The ivy door swings open."
                                    load_next_level()
                                else:
                                    puzzle_feedback = "That door is sealed. Reconsider the clue."
                elif state == "title" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if hero.dialogue_enabled:
                        dialogue_pages = OPENING_STORY + [story_for_level(0)]
                        dialogue_index = 0
                        after_dialogue = "playing"
                        state = "dialogue"
                    else:
                        state = "playing"
                elif state == "dialogue" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    dialogue_index += 1
                    if dialogue_index >= len(dialogue_pages):
                        state = after_dialogue
                        message = "Defeat every monster, open the chest, and reach the exit!"
                        message_timer = 3.0
                elif state in ("gameover", "won") and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    dialogue_enabled = hero.dialogue_enabled
                    hero = Hero()
                    hero.dialogue_enabled = dialogue_enabled
                    level_index = 0
                    enemies, walls, chest, levers = new_level(level_index)
                    hero.moving = False
                    hero.room_had_enemies = bool(enemies)
                    arrows = []
                    drops = []
                    effects = []
                    runes = []
                    lever_sequence = []
                    lever_solved = False
                    dialogue_pages = OPENING_STORY + [story_for_level(0)]
                    dialogue_index = 0
                    after_dialogue = "playing"
                    message = "Defeat every monster, open the chest, and reach the exit!"
                    message_timer = 3.0
                    state = "dialogue" if hero.dialogue_enabled else "playing"
                elif state == "playing":
                    if event.key == control_bindings["inventory"]:
                        state = "inventory"
                    elif event.key == control_bindings["field_guide"]:
                        state = "controls"
                    elif event.key == control_bindings["skip_room"]:
                        if level_index < len(LEVELS) - 1:
                            load_next_level()
                            message = f"Skipped to level {level_index + 1}."
                            message_timer = 2.0
                        else:
                            message = "The final boss cannot be skipped."
                            message_timer = 1.5
                    elif event.key == control_bindings["crafting"]:
                        state = "craft"
                    elif event.key == control_bindings["attack"] and hero.attack_cooldown <= 0:
                        aim_target = logical_mouse_position() if hero.weapon == "bow" else None
                        enemy_count = len(enemies)
                        message = use_basic_attack(hero, enemies, arrows, aim_target)
                        collect_defeated_enemies(enemies, drops, hero)
                        if len(enemies) == enemy_count:
                            weapon_action_bark(hero, message != "No monster in reach.")
                        if not enemies:
                            message = "All clear! Find the golden exit."
                        message_timer = 1.0
                    elif event.key == control_bindings["special"]:
                        aim_target = logical_mouse_position() if hero.weapon == "bow" else None
                        enemy_count = len(enemies)
                        message = use_special(hero, enemies, arrows, walls, aim_target)
                        collect_defeated_enemies(enemies, drops, hero)
                        if (len(enemies) == enemy_count
                                and message != "Special ability is recharging."
                                and not message.startswith("No target")):
                            weapon_action_bark(hero, True, magical=True)
                        message_timer = 1.5
                    elif event.key == control_bindings["armor"]:
                        message = use_armor_ability(hero, walls, logical_mouse_position())
                        message_timer = 1.5
                    elif event.key == control_bindings["interact"]:
                        nearby_lever = None
                        if level_index == 14 and not lever_solved:
                            nearby_lever = next((lever for lever in levers
                                if pygame.Vector2(lever.rect.center).distance_to(hero.rect.center) <= 58), None)
                        if nearby_lever:
                            goal = ROOM_PUZZLES[15]["goal"]
                            expected = goal[len(lever_sequence)]
                            if nearby_lever.symbol == expected:
                                nearby_lever.pulled = True
                                lever_sequence.append(nearby_lever.symbol)
                                message = f"{nearby_lever.symbol} lever pulled. {len(lever_sequence)}/3"
                                if len(lever_sequence) == len(goal):
                                    lever_solved = True
                                    enemies[-1].shielded = False
                                    message = "Shield broken! Defeat the Tomato King's guardian!"
                            else:
                                lever_sequence.clear()
                                for lever in levers:
                                    lever.pulled = False
                                message = "Wrong lever order. The levers reset. Read the clue again."
                            message_timer = 2.0
                        elif not chest.opened:
                            distance = pygame.Vector2(chest.rect.center).distance_to(hero.rect.center)
                            if distance <= 58:
                                chest.opened = True
                                message = open_loot_chest(hero)
                                message_timer = 3.0
                            else:
                                message, message_timer = "Move close to the chest or a lever and press F.", 1.2
                    elif event.key == control_bindings["potion"]:
                        selected_potion = hero.selected_potion
                        potion_used = False
                        if selected_potion == "health":
                            if hero.potions > 0 and hero.hp < hero.max_hp:
                                hero.hp = min(hero.max_hp, hero.hp + 35)
                                hero.potions -= 1
                                message = "Health potion used: +35 HP."
                                potion_used = True
                            elif hero.potions <= 0:
                                message = "No health potions left."
                            else:
                                message = "Your health is already full."
                        elif hero.items[selected_potion] > 0:
                            hero.items[selected_potion] -= 1
                            potion_used = True
                            if selected_potion == "strength":
                                hero.strength_timer = 8.0
                                message = "Strength potion: damage boosted for 8 seconds!"
                            else:
                                hero.speed_timer = 8.0
                                message = "Speed potion: move faster for 8 seconds!"
                        else:
                            message = f"No {selected_potion} potions left."
                        if potion_used:
                            potion_lines = {
                                "health": "EWW! THIS TASTES LIKE GRASS AND POOP",
                                "strength": "im muscle now!",
                                "speed": "Whoa, my feet, I LIKE FEET",
                            }
                            trigger_player_bark(hero, potion_lines[selected_potion], 2.4, force=True)
                        message_timer = 1.5
                    elif event.key == control_bindings["rune"]:
                        message = place_rune(hero, enemies, runes, logical_mouse_position(), walls)
                        collect_defeated_enemies(enemies, drops, hero)
                        message_timer = 1.8
                    elif event.key == control_bindings["bomb"] and hero.items["bomb"] > 0:
                        hero.items["bomb"] -= 1
                        effects.append(Explosion(*hero.rect.center))
                        for enemy in enemies:
                            if pygame.Vector2(enemy.rect.center).distance_to(hero.rect.center) <= 150:
                                damage_enemy(enemy, 90)
                                enemy.stun_timer = max(enemy.stun_timer, 0.8)
                        collect_defeated_enemies(enemies, drops, hero)
                        message, message_timer = "Bomb blast! Nearby enemies take 90 damage.", 1.5
                    elif (weapon_slot := next(
                            (index for index in range(1, len(WEAPON_ORDER) + 1)
                             if event.key == control_bindings[f"weapon_{index}"]),
                            None,
                    )) is not None:
                        selected = WEAPON_ORDER[weapon_slot - 1]
                        if selected in hero.weapons:
                            hero.weapon = selected
                            message = f"Equipped {get_weapon_variant(hero)['name']} — Q: {get_weapon_variant(hero)['special']}"
                        else:
                            message = f"{selected.title()} is still locked. Find a loot chest!"
                        message_timer = 1.4
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_position = logical_mouse_position(event.pos)
                if state == "controls":
                    tab_centers = (235, 480, 725)
                    selected_tab = next(
                        (index for index, center_x in enumerate(tab_centers)
                         if pygame.Rect(center_x - 105, 145, 210, 38).collidepoint(mouse_position)),
                        None,
                    )
                    if selected_tab is not None:
                        controls_tab = selected_tab
                        if controls_tab != 0:
                            controls_remap_mode = False
                            remapping_action = None
                    elif controls_tab == 2 and pygame.Rect(
                            WIDTH // 2 - 150, 320, 300, 58).collidepoint(mouse_position):
                        hero.dialogue_enabled = not hero.dialogue_enabled
                        if not hero.dialogue_enabled:
                            hero.bark_text = ""
                            hero.bark_timer = 0
                        message = f"Character dialogue {'enabled' if hero.dialogue_enabled else 'disabled'}."
                        message_timer = 2.0
                    elif controls_tab == 0:
                        if controls_remap_mode:
                            if pygame.Rect(180, 548, 220, 34).collidepoint(mouse_position):
                                controls_remap_mode = False
                                remapping_action = None
                            elif pygame.Rect(560, 548, 260, 34).collidepoint(mouse_position):
                                control_bindings = dict(CONTROL_DEFAULTS)
                                remapping_action = None
                                message = "Default controls restored."
                                message_timer = 2.0
                            else:
                                actions = list(CONTROL_LABELS)
                                selected_action = next(
                                    (action for index, action in enumerate(actions)
                                     if pygame.Rect(
                                         135 + (index // 9) * 230,
                                         208 + (index % 9) * 36,
                                         220, 32,
                                     ).collidepoint(mouse_position)),
                                    None,
                                )
                                if selected_action is not None:
                                    remapping_action = selected_action
                        elif pygame.Rect(350, 540, 260, 34).collidepoint(mouse_position):
                            controls_remap_mode = True
                elif state == "craft":
                    selected_tab = next(
                        (index for index in range(len(CRAFT_TABS))
                         if pygame.Rect(165 + index * 157, 150, 150, 38).collidepoint(mouse_position)),
                        None,
                    )
                    if selected_tab is not None:
                        craft_tab = selected_tab
                        craft_selection = 0
                    else:
                        selected_row = next(
                            (index for index in range(len(CRAFT_RECIPES[CRAFT_TABS[craft_tab]]))
                             if pygame.Rect(185, 220 + index * 68 - 24, 590, 54).collidepoint(mouse_position)),
                            None,
                        )
                        if selected_row is not None:
                            craft_selection = selected_row
                            recipe = CRAFT_RECIPES[CRAFT_TABS[craft_tab]][selected_row]
                            if craft_tab == 1:
                                craft_category = recipe
                                rank = hero.weapons.get(craft_category, 0)
                                craft_tier_selection = min(rank + 1, WEAPON_MAX_LEVEL) - 1
                                state = "weapon_craft"
                            else:
                                message = craft_item(hero, recipe)
                                message_timer = 2.0
                elif state == "weapon_craft":
                    if pygame.Rect(185, 550, 590, 40).collidepoint(mouse_position):
                        message = upgrade_weapon(hero, craft_category)
                        message_timer = 2.0
                    else:
                        for tier in range(1, WEAPON_MAX_LEVEL + 1):
                            row = pygame.Rect(155, 185 + (tier - 1) * 82 - 28, 650, 66)
                            if row.collidepoint(mouse_position):
                                craft_tier_selection = tier - 1
                                message = craft_weapon_tier(hero, craft_category, tier)
                                message_timer = 4.5
                                break
                elif state == "inventory":
                    for index, kind in enumerate(POTION_TYPES):
                        if pygame.Rect(575, 350 + index * 25 - 11, 230, 23).collidepoint(mouse_position):
                            hero.selected_potion = kind
                            break
                    rune_positions = {
                        "slow": (610, 520), "fire": (690, 520), "thunder": (770, 520),
                        "lure": (610, 555), "teleport": (690, 555),
                    }
                    for kind, center in rune_positions.items():
                        if pygame.Rect(center[0] - 38, center[1] - 13, 76, 26).collidepoint(mouse_position):
                            hero.selected_rune = kind
                            break
                elif (state == "playing" and hero.weapon == "bow"
                      and hero.attack_cooldown <= 0):
                    enemy_count = len(enemies)
                    message = use_basic_attack(hero, enemies, arrows, mouse_position)
                    collect_defeated_enemies(enemies, drops, hero)
                    if len(enemies) == enemy_count:
                        weapon_action_bark(hero, True)
                    message_timer = 0.8

        if state == "playing":
            keys = pygame.key.get_pressed()
            direction = pygame.Vector2(
                int(keys[control_bindings["move_right"]]) - int(keys[control_bindings["move_left"]]),
                int(keys[control_bindings["move_down"]]) - int(keys[control_bindings["move_up"]]),
            )
            if direction.length_squared() > 0:
                direction = direction.normalize()
                hero.facing = direction
                hero.moving = True
                move_speed = hero.speed * (1.55 if hero.speed_timer > 0 else 1)
                if hero.special_armor == "samurai":
                    move_speed *= 1.2
                else:
                    move_speed *= max(0.55, 1 - armor_weight(hero) * 0.045)
                move_with_walls(hero.rect, direction.x * move_speed * dt, direction.y * move_speed * dt, walls)
            else:
                hero.moving = False
            if hero.weapon == "bow":
                aim_direction = pygame.Vector2(logical_mouse_position()) - pygame.Vector2(hero.rect.center)
                if aim_direction.length_squared() > 0:
                    hero.facing = aim_direction.normalize()
            hero.animation_time += dt

            hero.attack_cooldown = max(0, hero.attack_cooldown - dt)
            hero.special_cooldown = max(0, hero.special_cooldown - dt)
            hero.armor_cooldown = max(0, hero.armor_cooldown - dt)
            hero.parry_timer = max(0, hero.parry_timer - dt)
            hero.phantom_timer = max(0, hero.phantom_timer - dt)
            hero.action_timer = max(0, hero.action_timer - dt)
            hero.invulnerable = max(0, hero.invulnerable - dt)
            hero.regen_delay = max(0, hero.regen_delay - dt)
            hero.auto_heal_cooldown = max(0, hero.auto_heal_cooldown - dt)
            hero.strength_timer = max(0, hero.strength_timer - dt)
            hero.speed_timer = max(0, hero.speed_timer - dt)
            hero.special_vfx_timer = max(0, hero.special_vfx_timer - dt)
            if hero.special_vfx_timer == 0:
                hero.special_vfx = ""
            hero.bark_timer = max(0, hero.bark_timer - dt)
            hero.bark_cooldown = max(0, hero.bark_cooldown - dt)
            update_ambient_dialogue(hero, dt)
            message_timer = max(0, message_timer - dt)
            if message_timer == 0:
                message = ""

            boss_messages = update_boss_gimmicks(enemies, hero, walls, level_index, dt)
            if boss_messages:
                message = boss_messages[0]
                message_timer = 2.0

            for rune in runes[:]:
                rune.timer -= dt
                rune.pulse_timer -= dt
                if rune.kind == "lure":
                    rune_position = pygame.Vector2(rune.center)
                    for enemy in enemies:
                        if pygame.Vector2(enemy.rect.center).distance_to(rune_position) <= 360:
                            enemy.lure_timer = max(enemy.lure_timer, 1.0)
                            enemy.lure_target = rune.center
                elif rune.pulse_timer <= 0:
                    for enemy in enemies:
                        if pygame.Vector2(enemy.rect.center).distance_to(rune.center) > 120:
                            continue
                        if rune.kind == "slow":
                            enemy.slow_timer = max(enemy.slow_timer, 3.0)
                        elif rune.kind == "fire":
                            enemy.burn_timer = max(enemy.burn_timer, 4.0)
                            enemy.burn_tick = max(enemy.burn_tick, 0.5)
                    rune.pulse_timer = 0.85
                if rune.timer <= 0:
                    runes.remove(rune)

            for enemy in enemies:
                enemy.stun_timer = max(0, enemy.stun_timer - dt)
                enemy.slow_timer = max(0, enemy.slow_timer - dt)
                enemy.burn_timer = max(0, enemy.burn_timer - dt)
                enemy.venom_timer = max(0, enemy.venom_timer - dt)
                enemy.lure_timer = max(0, enemy.lure_timer - dt)
                enemy.burn_tick = max(0, enemy.burn_tick - dt)
                enemy.venom_tick = max(0, enemy.venom_tick - dt)
                if enemy.burn_timer > 0 and enemy.burn_tick <= 0:
                    damage_enemy(enemy, 7)
                    enemy.burn_tick = 0.8
                if enemy.venom_timer > 0 and enemy.venom_tick <= 0:
                    damage_enemy(enemy, 9)
                    enemy.venom_tick = 0.8
                if enemy.lure_timer <= 0:
                    enemy.lure_target = None
                if enemy.stun_timer <= 0:
                    if enemy.lure_target:
                        destination = enemy.lure_target
                    elif hero.phantom_timer > 0:
                        destination = enemy.rect.center
                    elif (enemy.boss_gimmick == "charging_boss"
                            and enemy.gimmick_active and enemy.charge_target):
                        destination = enemy.charge_target
                    else:
                        destination = hero.rect.center
                    offset = pygame.Vector2(destination) - pygame.Vector2(enemy.rect.center)
                    if offset.length() > 1:
                        direction = offset.normalize()
                        slow_scale = 0.42 if enemy.slow_timer > 0 else 1.0
                        boss_speed = 2.7 if enemy.boss_gimmick == "charging_boss" and enemy.gimmick_active else (
                            1.55 if enemy.final_form else 1.0)
                        move_with_walls(enemy.rect, direction.x * enemy.speed * slow_scale * boss_speed * dt,
                                        direction.y * enemy.speed * slow_scale * boss_speed * dt, walls)
                enemy.attack_cooldown = max(0, enemy.attack_cooldown - dt)
                if (hero.phantom_timer <= 0 and enemy.stun_timer <= 0
                        and enemy.rect.inflate(6, 6).colliderect(hero.rect)
                        and enemy.attack_cooldown <= 0):
                    if hero.parry_timer > 0:
                        enemy.attack_cooldown = 0.9
                        enemy.attack_flash = 0.24
                        hero.parry_timer = 0
                        enemy.stun_timer = max(enemy.stun_timer, 1.0)
                        message, message_timer = "Parried! The attacker is stunned.", 1.2
                    elif hero.invulnerable <= 0:
                        enemy.attack_cooldown = 0.9
                        enemy.attack_flash = 0.24
                        damage_scale = 1.5 if enemy.final_form else (
                            2.0 if enemy.boss_gimmick == "charging_boss" and enemy.gimmick_active else 1.0)
                        incoming_damage = math.ceil(enemy.damage * damage_scale * armor_damage_scale(hero))
                        hero.hp -= incoming_damage
                        hero.invulnerable = 0.8
                        hero.regen_delay = 5.0
                        trigger_player_bark(hero, random.choice(
                            ("Ghh...!", "Agh! That hurt!", "HEY!!")))
                        trigger_special_vfx(hero, "armor_impact", hero.rect.center, enemy.rect.center)
                        if enemy.boss_gimmick == "soul_leech":
                            enemy.hp = min(enemy.max_hp, enemy.hp + incoming_damage * 1.5)
                        message, message_timer = f"Hit! -{incoming_damage} HP", 1.0

            for arrow in arrows:
                arrow.pos += arrow.velocity * dt
                arrow.rect.center = (round(arrow.pos.x), round(arrow.pos.y))
                if not SCREEN.get_rect().colliderect(arrow.rect) or any(arrow.rect.colliderect(wall) for wall in walls):
                    arrow.alive = False
                    continue
                for enemy in enemies:
                    if enemy not in arrow.hit_enemies and arrow.rect.colliderect(enemy.rect):
                        damage_enemy(enemy, arrow.damage)
                        arrow.hit_enemies.add(enemy)
                        if not arrow.piercing:
                            arrow.alive = False
                            break
            collect_defeated_enemies(enemies, drops, hero)
            arrows[:] = [arrow for arrow in arrows if arrow.alive]
            if hero.room_had_enemies and not enemies and not hero.room_clear_spoken:
                hero.room_clear_spoken = True
                trigger_player_bark(hero, random.choice((
                    "The room is clear. I can brea-ew, magic smells weird",
                    "I made it through, Mira, werent u a hero back then??.",
                    "I was scared, emphasis on was.",
                )), 2.6, force=True)
            for effect in effects:
                effect.timer += dt
            effects[:] = [effect for effect in effects if effect.timer < effect.duration]

            for drop in drops[:]:
                if hero.rect.colliderect(drop.rect.inflate(14, 14)):
                    hero.materials[drop.kind] += drop.amount
                    message = f"Collected {drop.amount} {drop.kind}!"
                    message_timer = 1.0
                    drops.remove(drop)

            if hero.regen_delay <= 0 and hero.hp < hero.max_hp:
                hero.hp = min(hero.max_hp, hero.hp + 1.5 * dt)
            if (hero.hp <= hero.max_hp * 0.35 and hero.moving
                    and hero.bark_timer <= 0 and hero.bark_cooldown <= 0):
                trigger_player_bark(hero, random.choice(
                    ("Hah... hah... Im mental.", "HELP HELP, TS HURTS",
                     "Can't stop now...")), 1.8)
            if hero.hp > 0 and hero.hp <= hero.max_hp * 0.30 and hero.potions > 0 and hero.auto_heal_cooldown <= 0:
                hero.hp = min(hero.max_hp, hero.hp + 40)
                hero.potions -= 1
                hero.auto_heal_cooldown = 1.5
                message, message_timer = "Auto-heal used a potion! +40 HP", 1.6

            if hero.hp <= 0:
                state = "gameover"
            exit_rect = pygame.Rect((COLS - 2) * TILE + 8, MAP_TOP + (ROWS - 2) * TILE + 5, 24, 30)
            if state == "playing" and not enemies and hero.rect.colliderect(exit_rect):
                if level_index == 14:
                    if lever_solved:
                        load_next_level()
                    else:
                        message = "The boss's shield remains. Pull the three levers in order."
                        message_timer = 2.0
                elif level_index + 1 in ROOM_PUZZLES:
                    puzzle_state = make_puzzle_state(level_index + 1)
                    puzzle_feedback = ""
                    state = "puzzle"
                else:
                    load_next_level()

        draw_game(hero, enemies, level_index, walls, chest, levers, lever_sequence,
                  lever_solved, arrows, drops, effects, runes, message)
        if state == "title":
            draw_overlay("SOLID COWARD", "A scared idiot, a stolen sister, and the braindeadness to keep going.")
            title_prompt = ("Press ENTER to hear the story" if hero.dialogue_enabled
                            else "Dialogue disabled - press ENTER to begin")
            draw_text(SCREEN, title_prompt, FONT, GOLD, (WIDTH // 2, HEIGHT // 2 + 100))
        elif state == "dialogue":
            draw_dialogue(dialogue_pages, dialogue_index)
        elif state == "craft":
            draw_crafting(hero, tab=craft_tab, selection=craft_selection, feedback=message)
        elif state == "weapon_craft":
            draw_crafting(hero, "weapon", craft_category, weapon_tier=craft_tier_selection,
                          feedback=message)
        elif state == "inventory":
            draw_inventory(hero)
        elif state == "controls":
            draw_controls(hero, controls_tab, control_bindings,
                          controls_remap_mode, remapping_action)
        elif state == "puzzle":
            draw_room_puzzle(level_index + 1, puzzle_state, puzzle_feedback)
        elif state == "gameover":
            draw_overlay("GAME OVER", "Your adventure ends here.")
            draw_text(SCREEN, "Press ENTER to try again", FONT, GOLD, (WIDTH // 2, HEIGHT // 2 + 100))
        elif state == "won":
            draw_overlay("CHAPTER ONE COMPLETE",
                         "The Tomato King's trail points toward the old forest, go in ur winter arc now.")
            draw_text(SCREEN, "Press ENTER to play again", FONT, GOLD, (WIDTH // 2, HEIGHT // 2 + 100))
        present_screen()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

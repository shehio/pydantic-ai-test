"""Static game data for Shaken but Not Stirred, extracted from the 1982 ZX Spectrum original."""

GADGETS = {
    "pocket_bomb": {"name": "Pocket bomb", "description": "Use once only", "max_uses": 1, "damage": 25},
    "walther_ppk": {"name": "Walther PPK pistol", "description": "Has 8 bullets", "max_uses": 8, "damage": 12},
    "cyanide_gun": {"name": "Secret cyanide gun", "description": "Can be used twice", "max_uses": 2, "damage": 30},
    "knife": {"name": "Concealed knife", "description": "Can be used twice", "max_uses": 2, "damage": 20},
    "watch": {"name": "Digital watch", "description": "Concealed wire for strangling", "max_uses": 1, "damage": 35},
}

CITIES = [
    "Vienna", "Cairo", "Paris", "Rome", "Munich",
    "New York", "Los Angeles", "Amsterdam", "Moscow",
]

ISLAND_DESTINATIONS = [
    "Bahamas", "Hong Kong", "Seychelles", "Bermuda", "Malta",
    "Singapore", "Bangkok", "Honolulu", "Jamaica", "Japan",
]

TRAPS = [
    {
        "description": "You receive a dish of fruit from the hotel manager.",
        "prompt": "What do you do, 007?",
        "dangerous_words": ["test", "pick", "eat", "examine", "look", "taste", "try"],
        "death_message": "The fruit was poisoned! You collapse...",
        "safe_message": "Good instincts, 007. You leave the fruit untouched.",
    },
    {
        "description": 'You receive a note which tells you to meet "X" at midnight.',
        "prompt": "What do you do now, 007?",
        "dangerous_words": ["accept", "appointment", "go", "meet", "see", "attend", "yes"],
        "death_message": 'This was a trap. You are attacked by "X" and killed.',
        "safe_message": "Wise decision, 007. You ignore the suspicious invitation.",
    },
    {
        "description": "A mysterious taxi offers you a ride.",
        "prompt": "What are you going to do, 007?",
        "dangerous_words": ["ride", "enter", "take", "accept", "in", "board", "get", "yes"],
        "death_message": "The taxi takes you to a warehouse where you are shot.",
        "safe_message": "Good thinking, 007. Never trust unmarked vehicles.",
    },
    {
        "description": (
            "You find that a vase of flowers has been placed in your hotel room. "
            "You suspect it may be a bomb."
        ),
        "prompt": "What are you going to do, 007?",
        "dangerous_words": ["lift", "pick", "check", "examine", "look", "touch", "inspect", "move"],
        "death_message": "It was a bomb and it has just blown up!",
        "safe_message": "Smart move, 007. You call the bomb squad from a safe distance.",
    },
    {
        "description": "A mysterious package is delivered to you.",
        "prompt": "What are you going to do, 007?",
        "dangerous_words": ["pick", "check", "open", "examine", "drop", "unwrap", "touch"],
        "death_message": "The package has blown up!",
        "safe_message": "Excellent instincts, 007. The package was indeed booby-trapped.",
    },
]

CLUE_EVENTS = [
    "A beautiful girl gives you a sheet of paper with a single letter on it.",
    "You find a message pushed under your bedroom door.",
    "You are given a message by the head waiter in your hotel.",
    "You find a message pushed into your cigarette packet.",
    "A mysterious oriental hands you a folded note.",
]

ENCOUNTER_INTROS = [
    "You are approached by a gang of thugs.",
    "A mysterious oriental blocks your path.",
    "A travelling priest eyes you suspiciously... then attacks!",
    "A mugger leaps from the shadows.",
    "Tic Tac, Dr. Death's midget henchman, appears!",
]

TAUNTS = [
    "Not a very good show, 007.",
    '"M" will not be pleased.',
    "Try harder, 007.",
    "Any more bright ideas, 007?",
    'Use one of "Q"\'s gadgets, 007.',
    "Please hurry up, 007.",
    "Not a very good start, 007.",
    "You should have stayed at home.",
    'Good job "M" isn\'t here.',
    "I should give up now, 007.",
]

ISLAND_GRID = [
    ["Beach",  "Sand Dunes",        "Olive Grove",  "Mountains"],
    ["Swamp",  "Dark Forest",       "Large Field",  "Large Wood"],
    ["Marsh",  "Banana Plantation", "Swamp",        "Sea"],
]

ISLAND_ENEMIES = {
    "Beach": [
        {"name": "a Scorpion", "strength": 10},
        {"name": "a Rattlesnake", "strength": 10},
        {"name": "a Giant Crab", "strength": 20},
    ],
    "Swamp": [
        {"name": "the Crocodiles", "strength": 12},
        {"name": "the Alligators", "strength": 15},
        {"name": "a Boa Constrictor", "strength": 13},
    ],
    "Dark Forest": [
        {"name": "a Wild Boar", "strength": 20},
        {"name": "a Puff Adder", "strength": 15},
        {"name": "the Tarantula Spiders", "strength": 14},
    ],
    "Sand Dunes": [
        {"name": "a Scorpion", "strength": 10},
        {"name": "a Rattlesnake", "strength": 12},
        {"name": "a Sand Viper", "strength": 15},
    ],
    "Large Field": [
        {"name": "a Charging Bull", "strength": 10},
        {"name": "a Wild Boar", "strength": 20},
        {"name": "a Stampede of Cattle", "strength": 13},
    ],
    "Mountains": [
        {"name": "a Mountain Goat", "strength": 10},
        {"name": "a Mountain Lion", "strength": 15},
        {"name": "an Abominable Snowman", "strength": 20},
    ],
    "Large Wood": [
        {"name": "a Timber Wolf", "strength": 12},
        {"name": "a Pack of Wild Dogs", "strength": 20},
        {"name": "the Angry Natives", "strength": 12},
    ],
    "Olive Grove": [
        {"name": "a Tarantula Spider", "strength": 13},
        {"name": "a Rattlesnake", "strength": 16},
        {"name": "a Dragon Lizard", "strength": 20},
    ],
    "Banana Plantation": [
        {"name": "the Tarantula Spiders", "strength": 17},
        {"name": "the Natives", "strength": 10},
        {"name": "an Anaconda", "strength": 13},
    ],
    "Marsh": [
        {"name": "a Boa Constrictor", "strength": 13},
        {"name": "an Alligator", "strength": 10},
        {"name": "a Crocodile", "strength": 13},
    ],
    "Sea": [
        {"name": "the Sharks", "strength": 14},
        {"name": "an Octopus", "strength": 15},
        {"name": "a Shoal of Barracuda", "strength": 13},
    ],
}

BENZEDRINE_POSITION = (1, 2)  # Large Field
LAIR_ENTRANCE_POSITION = (2, 3)  # Sea

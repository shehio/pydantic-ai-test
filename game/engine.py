"""Game engine for Shaken but Not Stirred."""

import random

from .data import (
    BENZEDRINE_POSITION,
    CITIES,
    CLUE_EVENTS,
    ENCOUNTER_INTROS,
    GADGETS,
    ISLAND_DESTINATIONS,
    ISLAND_ENEMIES,
    ISLAND_GRID,
    LAIR_ENTRANCE_POSITION,
    TAUNTS,
    TRAPS,
)
from .models import (
    ActionOption,
    Gadget,
    GameResponse,
    GameState,
    IslandState,
    MazeState,
    MissileState,
    PendingEvent,
    Phase,
)


# ---------------------------------------------------------------------------
# Phase 0: Create game + briefing
# ---------------------------------------------------------------------------


def create_game() -> tuple[GameState, GameResponse]:
    target = random.choice(ISLAND_DESTINATIONS)
    letters = list(target.upper())
    random.shuffle(letters)

    state = GameState(
        target_island=target,
        clue_letters_needed=letters,
    )
    state.phase = Phase.GADGET_SELECTION

    briefing = (
        'You are unexpectedly summoned by "M", the head of the Secret Service.\n\n'
        "After Miss Cashcoin has shown you into the office, "
        '"M" outlines the situation.\n\n'
        "A jet fighter has mysteriously disappeared whilst on a training mission. "
        "No wreckage has been found but it is known that the plane was "
        "carrying a nuclear missile.\n\n"
        "A ransom note has been received from Dr. Death, the well known "
        "megalomaniac, demanding a large sum of money within the next 48 hours. "
        "He threatens to flatten London unless his demands are met.\n\n"
        "Your task is to locate the plane and its deadly cargo, and defuse the missile.\n\n"
        "You must travel the world collecting clues to find Dr. Death's secret island. "
        "Be careful of traps!\n\n"
        "GOOD LUCK, 007.\n\n"
        'Pay attention, 007, Q has some new gadgets to show you. '
        "Select 3 items for your mission."
    )

    return state, GameResponse(
        game_id=state.game_id,
        phase=state.phase.value,
        narrative=briefing,
        health=state.player.health,
        location=state.player.location,
        available_actions=[
            ActionOption(
                action="/games/{game_id}/select-gadgets",
                description="Select 3 gadgets from Q's lab",
                options=list(GADGETS.keys()),
            )
        ],
    )


# ---------------------------------------------------------------------------
# Phase 1: Gadget selection
# ---------------------------------------------------------------------------


def select_gadgets(state: GameState, gadget_ids: list[str]) -> GameResponse:
    if state.phase != Phase.GADGET_SELECTION:
        raise ValueError(f"Cannot select gadgets in phase {state.phase}")
    if len(gadget_ids) != 3:
        raise ValueError("Must select exactly 3 gadgets")
    if len(set(gadget_ids)) != 3:
        raise ValueError("Must select 3 different gadgets")
    for gid in gadget_ids:
        if gid not in GADGETS:
            raise ValueError(f"Unknown gadget: {gid}")

    state.player.gadgets = [
        Gadget(
            id=gid,
            name=GADGETS[gid]["name"],
            description=GADGETS[gid]["description"],
            uses_remaining=GADGETS[gid]["max_uses"],
            max_uses=GADGETS[gid]["max_uses"],
            damage=GADGETS[gid]["damage"],
        )
        for gid in gadget_ids
    ]
    state.phase = Phase.GLOBE_TROTTING

    gadget_list = "\n".join(
        f"  - {g.name} ({g.description})" for g in state.player.gadgets
    )
    return GameResponse(
        game_id=state.game_id,
        phase=state.phase.value,
        narrative=(
            f"Excellent choices, 007. Your inventory:\n{gadget_list}\n\n"
            f"You have {len(state.clue_letters_needed)} clue letters to find. "
            "Travel the world and collect them all to discover Dr. Death's island.\n\n"
            "Where will you go to, 007?"
        ),
        health=state.player.health,
        location=state.player.location,
        gadgets=state.player.gadgets,
        clue_letters=[],
        available_actions=[
            ActionOption(
                action="/games/{game_id}/travel",
                description="Travel to a city",
                options=CITIES,
            )
        ],
    )


# ---------------------------------------------------------------------------
# Phase 2: Globe-trotting
# ---------------------------------------------------------------------------


def _travel_options(state: GameState) -> list[str]:
    opts = list(CITIES)
    if len(state.clue_letters_found) >= len(state.clue_letters_needed):
        opts += ISLAND_DESTINATIONS
    return opts


def travel(state: GameState, destination: str) -> GameResponse:
    if state.phase != Phase.GLOBE_TROTTING:
        raise ValueError(f"Cannot travel in phase {state.phase}")
    if state.pending_event:
        raise ValueError("Must respond to current event before traveling")

    # --- Try an island destination ---
    if destination in ISLAND_DESTINATIONS:
        if destination.lower() == state.target_island.lower():
            if len(state.clue_letters_found) >= len(state.clue_letters_needed):
                return _arrive_at_island(state)
            return _simple_globe_response(
                state, "You don't have enough clues yet to confirm this destination, 007."
            )
        return _simple_globe_response(
            state,
            f"You search {destination} but find no sign of Dr. Death. Wrong island, 007.",
        )

    # --- Return to London ---
    if destination == "London":
        state.player.london_returns += 1
        if state.player.london_returns >= 5:
            state.phase = Phase.GAME_OVER
            state.alive = False
            return GameResponse(
                game_id=state.game_id,
                phase=state.phase.value,
                narrative=(
                    'You have returned to London too many times without producing results. '
                    '"M" has fired you for inefficiency.'
                ),
                health=state.player.health,
                location="London",
                gadgets=state.player.gadgets,
                game_over=True,
            )
        state.player.health = 100
        for g in state.player.gadgets:
            g.uses_remaining = g.max_uses
        state.player.location = "London"
        return _simple_globe_response(
            state,
            f"Welcome back to London, 007. Health and gadgets restored.\n"
            f"Warning: you have returned {state.player.london_returns}/4 times. "
            '"M" will fire you if you return too often.',
        )

    if destination not in CITIES:
        raise ValueError(f"Unknown destination: {destination}")

    state.player.location = destination
    state.cities_visited.append(destination)

    # --- Random event ---
    roll = random.random()

    if roll < 0.35 and len(state.clue_letters_found) < len(state.clue_letters_needed):
        return _give_clue_letter(state, destination)

    if roll < 0.55:
        return _give_coded_message(state, destination)

    if roll < 0.80:
        return _trigger_trap(state, destination)

    return _trigger_encounter(state, destination)


def _simple_globe_response(state: GameState, narrative: str) -> GameResponse:
    return GameResponse(
        game_id=state.game_id,
        phase=state.phase.value,
        narrative=narrative,
        health=state.player.health,
        location=state.player.location,
        gadgets=state.player.gadgets,
        clue_letters=state.clue_letters_found,
        available_actions=[
            ActionOption(
                action="/games/{game_id}/travel",
                description="Travel to a city or island",
                options=_travel_options(state),
            )
        ],
    )


def _give_clue_letter(state: GameState, city: str) -> GameResponse:
    letter = state.clue_letters_needed[len(state.clue_letters_found)]
    state.clue_letters_found.append(letter)
    intro = random.choice(CLUE_EVENTS)

    hint = ""
    if len(state.clue_letters_found) >= len(state.clue_letters_needed):
        hint = (
            "\n\nYou now have ALL the letters! They are an anagram for "
            "Dr. Death's secret island. Figure out the destination and travel there."
        )

    return GameResponse(
        game_id=state.game_id,
        phase=state.phase.value,
        narrative=(
            f"Whilst in {city}...\n\n{intro}\n"
            f'The letter is: "{letter}"{hint}'
        ),
        health=state.player.health,
        location=city,
        gadgets=state.player.gadgets,
        clue_letters=state.clue_letters_found,
        available_actions=[
            ActionOption(
                action="/games/{game_id}/travel",
                description="Travel to a city or island",
                options=_travel_options(state),
            )
        ],
    )


def _give_coded_message(state: GameState, city: str) -> GameResponse:
    remaining = state.clue_letters_needed[len(state.clue_letters_found) :]
    if remaining:
        hint_letter = random.choice(remaining)
        pos = state.target_island.upper().index(hint_letter) + 1
        msg = f"Position {pos} of the island name is important. Pay attention to your clues."
    else:
        msg = "Keep your eyes open, 007. The island is within reach."
    state.coded_messages.append(msg)

    return GameResponse(
        game_id=state.game_id,
        phase=state.phase.value,
        narrative=(
            f"Whilst in {city}...\n\n"
            f'You receive a coded message from London:\n"{msg}"'
        ),
        health=state.player.health,
        location=city,
        gadgets=state.player.gadgets,
        clue_letters=state.clue_letters_found,
        coded_messages=state.coded_messages,
        available_actions=[
            ActionOption(
                action="/games/{game_id}/travel",
                description="Travel to a city or island",
                options=_travel_options(state),
            )
        ],
    )


def _trigger_trap(state: GameState, city: str) -> GameResponse:
    trap = random.choice(TRAPS)
    state.pending_event = PendingEvent(type="trap", data=trap)
    return GameResponse(
        game_id=state.game_id,
        phase=state.phase.value,
        narrative=f"Whilst in {city}...\n\n{trap['description']}\n\n{trap['prompt']}",
        health=state.player.health,
        location=city,
        gadgets=state.player.gadgets,
        clue_letters=state.clue_letters_found,
        available_actions=[
            ActionOption(
                action="/games/{game_id}/respond",
                description="Respond with a single action word (e.g. 'ignore', 'run', 'leave')",
            )
        ],
    )


def _trigger_encounter(state: GameState, city: str) -> GameResponse:
    intro = random.choice(ENCOUNTER_INTROS)
    strength = random.randint(5, 15)
    state.pending_event = PendingEvent(
        type="combat", data={"description": intro, "enemy_strength": strength}
    )
    gadget_opts = [g.id for g in state.player.gadgets if g.uses_remaining > 0]
    return GameResponse(
        game_id=state.game_id,
        phase=state.phase.value,
        narrative=f"Whilst in {city}...\n\n{intro}\n\nWhat are you going to do, 007?",
        health=state.player.health,
        location=city,
        gadgets=state.player.gadgets,
        clue_letters=state.clue_letters_found,
        available_actions=[
            ActionOption(
                action="/games/{game_id}/respond",
                description="Use a gadget or 'run' to flee",
                options=gadget_opts + ["run"],
            )
        ],
    )


# ---------------------------------------------------------------------------
# Event responses (traps + combat)
# ---------------------------------------------------------------------------


def respond_to_event(state: GameState, action: str) -> GameResponse:
    if not state.pending_event:
        raise ValueError("No pending event to respond to")
    event_type = state.pending_event.type
    if event_type == "trap":
        return _handle_trap(state, action)
    if event_type in ("combat", "island_combat"):
        return _handle_combat(state, action)
    raise ValueError(f"Unknown event type: {event_type}")


def _handle_trap(state: GameState, action: str) -> GameResponse:
    trap = state.pending_event.data
    is_dangerous = any(w in action.lower().strip() for w in trap["dangerous_words"])
    state.pending_event = None

    if is_dangerous:
        state.player.health = max(state.player.health - 30, 10)
        narrative = (
            f"{trap['death_message']}\n\n"
            "However, I enjoyed this game so I am going to reincarnate you.\n"
            f"Your health has been reduced to {state.player.health}."
        )
    else:
        narrative = trap["safe_message"]

    return _simple_globe_response(state, narrative)


def _handle_combat(state: GameState, action: str) -> GameResponse:
    event = state.pending_event
    enemy_strength = event.data.get("enemy_strength", 10)
    enemy_name = event.data.get("name", "the enemy")
    is_island = event.type == "island_combat"
    action_lower = action.lower().strip()
    state.pending_event = None

    if action_lower == "run":
        dmg = random.randint(3, 8)
        state.player.health -= dmg
        narrative = f"You flee! You take {dmg} damage escaping."
    else:
        gadget = next(
            (g for g in state.player.gadgets if g.id == action_lower and g.uses_remaining > 0),
            None,
        )
        if gadget:
            gadget.uses_remaining -= 1
            if gadget.damage >= enemy_strength:
                narrative = f"You use your {gadget.name} and dispatch {enemy_name}! Well done, 007."
            else:
                dmg = enemy_strength - gadget.damage
                state.player.health -= dmg
                narrative = (
                    f"You use your {gadget.name}. You prevail but take {dmg} damage."
                )
        else:
            state.player.health -= enemy_strength
            narrative = f"{random.choice(TAUNTS)} You take {enemy_strength} damage!"

    if state.player.health <= 0:
        state.phase = Phase.GAME_OVER
        state.alive = False
        return GameResponse(
            game_id=state.game_id,
            phase=state.phase.value,
            narrative=narrative + "\n\nSorry 007, you are dead. Mission failed.",
            health=0,
            location=state.player.location,
            gadgets=state.player.gadgets,
            game_over=True,
        )

    if is_island:
        return _island_post_action(state, narrative)
    return _simple_globe_response(state, narrative)


# ---------------------------------------------------------------------------
# Phase 3: Island exploration
# ---------------------------------------------------------------------------


def _arrive_at_island(state: GameState) -> GameResponse:
    state.phase = Phase.ISLAND_EXPLORATION
    state.island_state = IslandState(row=0, col=0)
    state.player.health = 100

    dirs = _island_directions(0, 0)
    return GameResponse(
        game_id=state.game_id,
        phase=state.phase.value,
        narrative=(
            f"Well done, 007! You have located Dr. Death's island: {state.target_island}!\n\n"
            "After you arrive on the beach, your task is to find the entrance "
            "to the underwater lair.\n"
            "Your strength is restored to 100%. You still have your weapons, "
            "but you cannot return to London.\n"
            "There is a secret stash of benzedrine tablets hidden on the island "
            "that will restore your strength.\n\n"
            "GOOD LUCK, 007.\n\n"
            f"YOU ARE ON THE BEACH."
        ),
        health=100,
        location="Beach",
        gadgets=state.player.gadgets,
        available_actions=[
            ActionOption(
                action="/games/{game_id}/move",
                description="Move in a direction",
                options=dirs,
            )
        ],
    )


def _island_directions(row: int, col: int) -> list[str]:
    dirs = []
    if row > 0:
        dirs.append("n")
    if row < len(ISLAND_GRID) - 1:
        dirs.append("s")
    if col > 0:
        dirs.append("w")
    if col < len(ISLAND_GRID[0]) - 1:
        dirs.append("e")
    return dirs


def _island_post_action(state: GameState, narrative: str) -> GameResponse:
    istate = state.island_state
    dirs = _island_directions(istate.row, istate.col)
    return GameResponse(
        game_id=state.game_id,
        phase=state.phase.value,
        narrative=narrative + f"\n\nYou have {state.player.health} strength points.",
        health=state.player.health,
        location=ISLAND_GRID[istate.row][istate.col],
        gadgets=state.player.gadgets,
        available_actions=[
            ActionOption(
                action="/games/{game_id}/move",
                description="Move in a direction",
                options=dirs,
            )
        ],
    )


def island_move(state: GameState, direction: str) -> GameResponse:
    if state.phase != Phase.ISLAND_EXPLORATION:
        raise ValueError("Not in island exploration phase")
    if state.pending_event:
        raise ValueError("Must resolve current encounter first")

    istate = state.island_state
    dirs = _island_directions(istate.row, istate.col)
    if direction not in dirs:
        raise ValueError(f"Cannot move {direction}. Available: {dirs}")

    if direction == "n":
        istate.row -= 1
    elif direction == "s":
        istate.row += 1
    elif direction == "e":
        istate.col += 1
    elif direction == "w":
        istate.col -= 1

    loc_name = ISLAND_GRID[istate.row][istate.col]
    state.player.location = loc_name

    # Lair entrance?
    if (istate.row, istate.col) == LAIR_ENTRANCE_POSITION:
        return _enter_maze(state)

    # Benzedrine?
    benz = ""
    if (istate.row, istate.col) == BENZEDRINE_POSITION and not istate.benzedrine_found:
        istate.benzedrine_found = True
        state.player.health = 100
        benz = (
            "\n\nYou have found the secret cache of benzedrine tablets! "
            "Your strength is back to 100%."
        )

    # Enemy encounter (70%)
    if random.random() < 0.7:
        enemies = ISLAND_ENEMIES.get(loc_name, [])
        if enemies:
            enemy = random.choice(enemies)
            state.pending_event = PendingEvent(
                type="island_combat",
                data={"name": enemy["name"], "strength": enemy["strength"]},
            )
            gadget_opts = [g.id for g in state.player.gadgets if g.uses_remaining > 0]
            return GameResponse(
                game_id=state.game_id,
                phase=state.phase.value,
                narrative=(
                    f"YOU ARE IN THE {loc_name.upper()}.{benz}\n\n"
                    f"You are attacked by {enemy['name']}!\n"
                    f"You have {state.player.health} strength points.\n\n"
                    "What are you going to do, 007?"
                ),
                health=state.player.health,
                location=loc_name,
                gadgets=state.player.gadgets,
                available_actions=[
                    ActionOption(
                        action="/games/{game_id}/respond",
                        description="Use a gadget or 'run'",
                        options=gadget_opts + ["run"],
                    )
                ],
            )

    # No encounter
    dirs = _island_directions(istate.row, istate.col)
    return GameResponse(
        game_id=state.game_id,
        phase=state.phase.value,
        narrative=(
            f"YOU ARE IN THE {loc_name.upper()}.{benz}\n\n"
            f"You have {state.player.health} strength points."
        ),
        health=state.player.health,
        location=loc_name,
        gadgets=state.player.gadgets,
        available_actions=[
            ActionOption(
                action="/games/{game_id}/move",
                description="Move in a direction",
                options=dirs,
            )
        ],
    )


# ---------------------------------------------------------------------------
# Phase 4: Maze
# ---------------------------------------------------------------------------


def _generate_maze(size: int = 10) -> list[list[dict]]:
    """Recursive-backtracking maze generator."""
    cells = [
        [{"n": True, "e": True, "s": True, "w": True} for _ in range(size)]
        for _ in range(size)
    ]
    visited = [[False] * size for _ in range(size)]
    stack = [(0, 0)]
    visited[0][0] = True

    while stack:
        r, c = stack[-1]
        neighbors = []
        for dr, dc, wall, opp in [
            (-1, 0, "n", "s"),
            (1, 0, "s", "n"),
            (0, 1, "e", "w"),
            (0, -1, "w", "e"),
        ]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc < size and not visited[nr][nc]:
                neighbors.append((nr, nc, wall, opp))
        if neighbors:
            nr, nc, wall, opp = random.choice(neighbors)
            cells[r][c][wall] = False
            cells[nr][nc][opp] = False
            visited[nr][nc] = True
            stack.append((nr, nc))
        else:
            stack.pop()

    return cells


def _maze_directions(cells: list[list[dict]], row: int, col: int) -> list[str]:
    cell = cells[row][col]
    return [d for d in ("n", "e", "s", "w") if not cell[d]]


def _move_paws(ms: MazeState) -> bool:
    """Move PAWS randomly. Returns True if PAWS is on the player."""
    if random.random() < 0.3:
        dirs = _maze_directions(ms.cells, ms.paws_row, ms.paws_col)
        if dirs:
            d = random.choice(dirs)
            if d == "n":
                ms.paws_row -= 1
            elif d == "s":
                ms.paws_row += 1
            elif d == "e":
                ms.paws_col += 1
            elif d == "w":
                ms.paws_col -= 1
    return ms.paws_row == ms.player_row and ms.paws_col == ms.player_col


def _render_maze_map(ms: MazeState) -> str:
    size = 10
    lines = []
    top = "+" + "---+" * size
    lines.append(top)

    for r in range(size):
        row_str = "|"
        for c in range(size):
            if r == ms.player_row and c == ms.player_col:
                cell_str = " O "
            elif r == ms.exit_row and c == ms.exit_col:
                cell_str = " X "
            elif r == ms.paws_row and c == ms.paws_col:
                cell_str = " P "
            else:
                cell_str = "   "
            east_wall = "|" if (c == size - 1 or ms.cells[r][c]["e"]) else " "
            row_str += cell_str + east_wall
        lines.append(row_str)

        bottom = "+"
        for c in range(size):
            south_wall = "---" if (r == size - 1 or ms.cells[r][c]["s"]) else "   "
            bottom += south_wall + "+"
        lines.append(bottom)

    lines.append("O = You, X = Exit, P = PAWS")
    return "\n".join(lines)


def _enter_maze(state: GameState) -> GameResponse:
    cells = _generate_maze(10)
    state.maze_state = MazeState(
        player_row=0, player_col=0,
        paws_row=5, paws_col=5,
        cells=cells,
    )
    state.phase = Phase.MAZE
    avail = _maze_directions(cells, 0, 0)

    return GameResponse(
        game_id=state.game_id,
        phase=state.phase.value,
        narrative=(
            "Congratulations, 007! You have found the entrance to "
            "Dr. Death's underwater lair.\n\n"
            "Navigate the maze to reach the control room (bottom-right corner).\n\n"
            "Beware of PAWS -- the steel-fisted villain who lurks in the maze. "
            "He is too powerful to fight; you must flee.\n\n"
            f"You can view the maze map {state.maze_state.max_maps} times.\n\n"
            f"Available directions: {', '.join(avail)}"
        ),
        health=state.player.health,
        location="Maze [0,0]",
        gadgets=state.player.gadgets,
        available_actions=[
            ActionOption(
                action="/games/{game_id}/move",
                description="Move through the maze or use 'map' to view it",
                options=avail + (["map"] if state.maze_state.maps_used < state.maze_state.max_maps else []),
            )
        ],
    )


def maze_move(state: GameState, direction: str) -> GameResponse:
    if state.phase != Phase.MAZE:
        raise ValueError("Not in maze phase")
    ms = state.maze_state

    # Map request
    if direction == "map":
        if ms.maps_used >= ms.max_maps:
            raise ValueError("No map views remaining")
        ms.maps_used += 1
        maze_str = _render_maze_map(ms)
        avail = _maze_directions(ms.cells, ms.player_row, ms.player_col)
        return GameResponse(
            game_id=state.game_id,
            phase=state.phase.value,
            narrative=f"Map view ({ms.max_maps - ms.maps_used} remaining):\n\n{maze_str}",
            health=state.player.health,
            location=f"Maze [{ms.player_row},{ms.player_col}]",
            gadgets=state.player.gadgets,
            maze_map=maze_str,
            available_actions=[
                ActionOption(
                    action="/games/{game_id}/move",
                    description="Move through the maze",
                    options=avail + (["map"] if ms.maps_used < ms.max_maps else []),
                )
            ],
        )

    avail = _maze_directions(ms.cells, ms.player_row, ms.player_col)
    if direction not in avail:
        raise ValueError(f"Cannot move {direction}. Available: {avail}")

    if direction == "n":
        ms.player_row -= 1
    elif direction == "s":
        ms.player_row += 1
    elif direction == "e":
        ms.player_col += 1
    elif direction == "w":
        ms.player_col -= 1

    # Reached exit?
    if ms.player_row == ms.exit_row and ms.player_col == ms.exit_col:
        return _enter_missile_disarm(state)

    # PAWS
    paws_caught = _move_paws(ms)
    paws_msg = ""
    if paws_caught:
        state.player.health -= 25
        if state.player.health <= 0:
            state.phase = Phase.GAME_OVER
            return GameResponse(
                game_id=state.game_id,
                phase=state.phase.value,
                narrative="PAWS catches you! His steel fists are too much. Sorry 007, you are dead.",
                health=0,
                location=f"Maze [{ms.player_row},{ms.player_col}]",
                gadgets=state.player.gadgets,
                game_over=True,
            )
        paws_msg = "\n\nPAWS catches you! You barely escape but take 25 damage!"
    elif (abs(ms.paws_row - ms.player_row) + abs(ms.paws_col - ms.player_col)) <= 2:
        paws_msg = "\n\nWatch out -- there's a PAWS about!"

    avail = _maze_directions(ms.cells, ms.player_row, ms.player_col)
    return GameResponse(
        game_id=state.game_id,
        phase=state.phase.value,
        narrative=(
            f"You move {direction}. Position: [{ms.player_row},{ms.player_col}]. "
            f"Exit: [{ms.exit_row},{ms.exit_col}].{paws_msg}\n\n"
            f"Available directions: {', '.join(avail)}"
        ),
        health=state.player.health,
        location=f"Maze [{ms.player_row},{ms.player_col}]",
        gadgets=state.player.gadgets,
        available_actions=[
            ActionOption(
                action="/games/{game_id}/move",
                description="Move through the maze",
                options=avail + (["map"] if ms.maps_used < ms.max_maps else []),
            )
        ],
    )


# ---------------------------------------------------------------------------
# Phase 5: Missile disarm (Mastermind)
# ---------------------------------------------------------------------------


def _enter_missile_disarm(state: GameState) -> GameResponse:
    digits = random.sample(range(10), 4)
    state.missile_state = MissileState(code=digits)
    state.phase = Phase.MISSILE_DISARM

    return GameResponse(
        game_id=state.game_id,
        phase=state.phase.value,
        narrative=(
            "Well done, 007. You have reached the control room in Dr. Death's lair.\n\n"
            "All you need to do now is disarm the missile.\n\n"
            "The disarming mechanism is a combination lock of four digits (0-9), "
            "no repeated digits.\n"
            "For each guess you'll be told:\n"
            "  RED = correct digit in the correct place\n"
            "  YELLOW = correct digit in the wrong place\n\n"
            f"You have {state.missile_state.attempts_remaining} attempts. "
            f"Otherwise the missile self-destructs, taking you and "
            f"{state.target_island} with it.\n\n"
            "Enter your first guess, 007."
        ),
        health=state.player.health,
        location="Dr. Death's Control Room",
        gadgets=state.player.gadgets,
        available_actions=[
            ActionOption(
                action="/games/{game_id}/guess",
                description="Enter a 4-digit code (e.g. '1234')",
            )
        ],
    )


def guess_code(state: GameState, code_str: str) -> GameResponse:
    if state.phase != Phase.MISSILE_DISARM:
        raise ValueError("Not in missile disarm phase")

    if len(code_str) != 4 or not code_str.isdigit():
        raise ValueError("Must be exactly 4 digits")
    guess = [int(d) for d in code_str]
    if len(set(guess)) != 4:
        raise ValueError("No repeated digits allowed")

    ms = state.missile_state
    red = sum(1 for i in range(4) if guess[i] == ms.code[i])
    yellow = sum(1 for d in guess if d in ms.code) - red
    ms.attempts_remaining -= 1

    if red == 4:
        state.phase = Phase.VICTORY
        return GameResponse(
            game_id=state.game_id,
            phase=state.phase.value,
            narrative=(
                f"Code accepted: {''.join(map(str, ms.code))}\n\n"
                "Congratulations, 007! As well as completing this adventure, "
                "you have saved the WORLD yet again.\n\n"
                "Dr. Death, however, lives to fight another day.\n\n"
                "Now you can rush home for your Vodka Martini, "
                "shaken but not stirred."
            ),
            health=state.player.health,
            location="Dr. Death's Control Room",
            gadgets=state.player.gadgets,
            victory=True,
        )

    if ms.attempts_remaining <= 0:
        state.phase = Phase.GAME_OVER
        return GameResponse(
            game_id=state.game_id,
            phase=state.phase.value,
            narrative=(
                f"Guess: {code_str} -- RED: {red}, YELLOW: {yellow}\n\n"
                "Sorry, 007, you blew it. The missile self-destructs, "
                f"taking you and {state.target_island} with it."
            ),
            health=0,
            location="Dr. Death's Control Room",
            gadgets=state.player.gadgets,
            game_over=True,
        )

    return GameResponse(
        game_id=state.game_id,
        phase=state.phase.value,
        narrative=(
            f"Guess: {code_str} -- RED: {red}, YELLOW: {yellow}\n"
            f"Attempts remaining: {ms.attempts_remaining}"
        ),
        health=state.player.health,
        location="Dr. Death's Control Room",
        gadgets=state.player.gadgets,
        missile_feedback={
            "guess": code_str,
            "red": red,
            "yellow": yellow,
            "attempts_remaining": ms.attempts_remaining,
        },
        available_actions=[
            ActionOption(
                action="/games/{game_id}/guess",
                description="Enter a 4-digit code",
            )
        ],
    )

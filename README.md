# Shaken but Not Stirred: Reloaded

A 007-inspired spy game API, faithfully recreated from the [1982 ZX Spectrum classic](https://en.wikipedia.org/wiki/Shaken_but_Not_Stirred) by Richard Shepherd Software — the first James Bond video game ever made.

Built with FastAPI + Pydantic. Designed to be played by a pydantic-ai agent (coming soon).

## Quick Start

```bash
uv venv && source .venv/bin/activate
uv pip install fastapi uvicorn pydantic
uvicorn game.api:app --port 8007
```

API docs at http://localhost:8007/docs

## How to Play

The game is a REST API. You play by sending HTTP requests through `curl`, the Swagger UI, or (soon) a pydantic-ai agent.

### Phase 1: Briefing & Gadget Selection

```bash
# Start a new game
curl -s -X POST http://localhost:8007/games | python3 -m json.tool

# Pick 3 gadgets from Q's lab
curl -s -X POST http://localhost:8007/games/{game_id}/select-gadgets \
  -H "Content-Type: application/json" \
  -d '{"gadgets": ["walther_ppk", "cyanide_gun", "knife"]}'
```

Available gadgets:

| ID | Name | Uses | Damage |
|----|------|------|--------|
| `pocket_bomb` | Pocket bomb | 1 | 25 |
| `walther_ppk` | Walther PPK pistol | 8 | 12 |
| `cyanide_gun` | Secret cyanide gun | 2 | 30 |
| `knife` | Concealed knife | 2 | 20 |
| `watch` | Digital watch (strangling wire) | 1 | 35 |

### Phase 2: Globe-Trotting

Travel the world collecting clue letters that form an anagram of Dr. Death's secret island.

```bash
# Travel to a city
curl -s -X POST http://localhost:8007/games/{game_id}/travel \
  -H "Content-Type: application/json" \
  -d '{"destination": "Vienna"}'

# Respond to traps/encounters
curl -s -X POST http://localhost:8007/games/{game_id}/respond \
  -H "Content-Type: application/json" \
  -d '{"action": "ignore"}'
```

**Trap survival tip:** When something suspicious happens (mysterious packages, poisoned fruit, shady invitations), respond with words like `ignore`, `run`, `leave`, or `decline`. Words like `eat`, `open`, `examine`, `accept` will get you killed (but you get reincarnated with reduced health).

You can return to London to restore health and gadgets, but do this more than 4 times and M fires you.

Once you have all the letters, unscramble them to figure out the island and travel there.

### Phase 3: Island Exploration

Navigate a 4x3 grid of locations (Beach, Swamp, Dark Forest, etc.) fighting enemies with your gadgets. Head for the Sea (bottom-right corner) to find the lair entrance.

```bash
# Move around the island
curl -s -X POST http://localhost:8007/games/{game_id}/move \
  -H "Content-Type: application/json" \
  -d '{"direction": "s"}'
```

Look out for the hidden benzedrine tablets — they restore your strength to 100%.

### Phase 4: The Maze

Navigate a randomly generated 10x10 maze to reach the control room (bottom-right corner). Avoid PAWS, the steel-fisted villain — he's too powerful to fight.

```bash
# Move through the maze
curl -s -X POST http://localhost:8007/games/{game_id}/move \
  -H "Content-Type: application/json" \
  -d '{"direction": "e"}'

# View the maze map (3 uses only!)
curl -s -X POST http://localhost:8007/games/{game_id}/move \
  -H "Content-Type: application/json" \
  -d '{"direction": "map"}'
```

### Phase 5: Missile Disarm

Crack a 4-digit combination lock (no repeated digits) in 10 attempts. Mastermind rules:
- **RED** = correct digit in the correct position
- **YELLOW** = correct digit in the wrong position

```bash
curl -s -X POST http://localhost:8007/games/{game_id}/guess \
  -H "Content-Type: application/json" \
  -d '{"code": "1234"}'
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/games` | Start a new game |
| GET | `/games/{game_id}` | Get current game state |
| POST | `/games/{game_id}/select-gadgets` | Pick 3 gadgets |
| POST | `/games/{game_id}/travel` | Travel to a city or island |
| POST | `/games/{game_id}/respond` | Respond to traps/combat |
| POST | `/games/{game_id}/move` | Move on island or in maze |
| POST | `/games/{game_id}/guess` | Guess missile disarm code |

Every response includes `available_actions` telling you exactly what you can do next — making this API easy for both humans and AI agents to play.

## Background

The original *Shaken but Not Stirred* (1982) was a text adventure for the ZX Spectrum 48K by Richard Shepherd Software. It was the first James Bond video game, predating the Parker Brothers' *James Bond 007* by a year. The game data (locations, gadgets, traps, enemies, story) was reverse-engineered from the original TZX binary.

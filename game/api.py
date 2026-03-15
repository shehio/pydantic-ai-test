"""FastAPI application for Shaken but Not Stirred: Reloaded."""

from fastapi import FastAPI, HTTPException

from . import engine
from .models import (
    GameResponse,
    GameState,
    GuessCodeRequest,
    MoveRequest,
    Phase,
    RespondRequest,
    SelectGadgetsRequest,
    TravelRequest,
)

app = FastAPI(
    title="Shaken but Not Stirred: Reloaded",
    description=(
        "A 007-inspired spy game API, faithfully recreated from the 1982 "
        "ZX Spectrum classic by Richard Shepherd Software."
    ),
    version="0.1.0",
)

# In-memory game storage
games: dict[str, GameState] = {}


def _get_game(game_id: str) -> GameState:
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    return games[game_id]


@app.post("/games", response_model=GameResponse)
def create_game():
    """Start a new game. Returns the briefing and gadget selection prompt."""
    state, response = engine.create_game()
    games[state.game_id] = state
    return response


@app.get("/games/{game_id}", response_model=GameResponse)
def get_game(game_id: str):
    """Get current game state."""
    state = _get_game(game_id)
    return GameResponse(
        game_id=state.game_id,
        phase=state.phase.value,
        narrative="Current game state.",
        health=state.player.health,
        location=state.player.location,
        gadgets=state.player.gadgets,
        clue_letters=state.clue_letters_found or None,
        game_over=state.phase == Phase.GAME_OVER,
        victory=state.phase == Phase.VICTORY,
    )


@app.post("/games/{game_id}/select-gadgets", response_model=GameResponse)
def select_gadgets(game_id: str, req: SelectGadgetsRequest):
    """Select 3 gadgets from Q's lab."""
    state = _get_game(game_id)
    try:
        return engine.select_gadgets(state, req.gadgets)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/games/{game_id}/travel", response_model=GameResponse)
def travel(game_id: str, req: TravelRequest):
    """Travel to a city or island destination."""
    state = _get_game(game_id)
    try:
        return engine.travel(state, req.destination)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/games/{game_id}/respond", response_model=GameResponse)
def respond(game_id: str, req: RespondRequest):
    """Respond to a trap or combat encounter."""
    state = _get_game(game_id)
    try:
        return engine.respond_to_event(state, req.action)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/games/{game_id}/move", response_model=GameResponse)
def move(game_id: str, req: MoveRequest):
    """Move on the island or in the maze. Also accepts 'map' in maze phase."""
    state = _get_game(game_id)
    try:
        if state.phase == Phase.ISLAND_EXPLORATION:
            return engine.island_move(state, req.direction)
        if state.phase == Phase.MAZE:
            return engine.maze_move(state, req.direction)
        raise ValueError(f"Cannot move in phase {state.phase}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/games/{game_id}/guess", response_model=GameResponse)
def guess(game_id: str, req: GuessCodeRequest):
    """Guess the 4-digit missile disarm code."""
    state = _get_game(game_id)
    try:
        return engine.guess_code(state, req.code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

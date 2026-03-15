"""Pydantic models for Shaken but Not Stirred game state and API."""

from __future__ import annotations

import uuid
from enum import Enum

from pydantic import BaseModel, Field


class Phase(str, Enum):
    BRIEFING = "briefing"
    GADGET_SELECTION = "gadget_selection"
    GLOBE_TROTTING = "globe_trotting"
    ISLAND_EXPLORATION = "island_exploration"
    MAZE = "maze"
    MISSILE_DISARM = "missile_disarm"
    VICTORY = "victory"
    GAME_OVER = "game_over"


# --- Game state models ---


class Gadget(BaseModel):
    id: str
    name: str
    description: str
    uses_remaining: int
    max_uses: int
    damage: int


class PlayerState(BaseModel):
    health: int = 100
    gadgets: list[Gadget] = Field(default_factory=list)
    location: str = "London"
    london_returns: int = 0


class IslandState(BaseModel):
    row: int = 0
    col: int = 0
    benzedrine_found: bool = False


class MazeState(BaseModel):
    player_row: int = 0
    player_col: int = 0
    exit_row: int = 9
    exit_col: int = 9
    paws_row: int = 5
    paws_col: int = 5
    maps_used: int = 0
    max_maps: int = 3
    cells: list[list[dict]] = Field(default_factory=list)


class MissileState(BaseModel):
    code: list[int]
    attempts_remaining: int = 10


class PendingEvent(BaseModel):
    type: str  # "trap", "combat", "island_combat"
    data: dict


class GameState(BaseModel):
    game_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    phase: Phase = Phase.BRIEFING
    player: PlayerState = Field(default_factory=PlayerState)
    target_island: str = ""
    clue_letters_needed: list[str] = Field(default_factory=list)
    clue_letters_found: list[str] = Field(default_factory=list)
    coded_messages: list[str] = Field(default_factory=list)
    cities_visited: list[str] = Field(default_factory=list)
    island_state: IslandState | None = None
    maze_state: MazeState | None = None
    missile_state: MissileState | None = None
    pending_event: PendingEvent | None = None
    alive: bool = True


# --- Request models ---


class SelectGadgetsRequest(BaseModel):
    gadgets: list[str]  # gadget IDs, must be exactly 3


class TravelRequest(BaseModel):
    destination: str


class RespondRequest(BaseModel):
    action: str


class MoveRequest(BaseModel):
    direction: str  # n, e, s, w, or "map"


class GuessCodeRequest(BaseModel):
    code: str  # 4-digit string


# --- Response models ---


class ActionOption(BaseModel):
    action: str
    method: str = "POST"
    description: str
    options: list[str] | None = None


class GameResponse(BaseModel):
    game_id: str
    phase: str
    narrative: str
    health: int
    location: str
    gadgets: list[Gadget] = Field(default_factory=list)
    available_actions: list[ActionOption] = Field(default_factory=list)
    clue_letters: list[str] | None = None
    coded_messages: list[str] | None = None
    maze_map: str | None = None
    missile_feedback: dict | None = None
    game_over: bool = False
    victory: bool = False

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from dummy_agent import DummyAgent

import traceback

# Initialize FastAPI app
app = FastAPI()

# Game state model
class Ship(BaseModel):
    x: float
    y: float
    angle: float

class Wall(BaseModel):
    x: float
    y: float
    width: float
    height: float

class GameState(BaseModel):
    ships: List[Ship]
    walls: List[Wall]

# Initialize DummyAgent with ship_index 0
agent = DummyAgent(ship_index=0)

@app.post("/decide/")
async def decide(game_state: GameState):
    # Get actions from DummyAgent
    actions = agent.decide(game_state.dict(), game_state.walls)
    return actions

@app.get("/game_state")
async def get_game_state():
    # Return an example game state with ships and walls
    return {
        "ships": [{"x": 100, "y": 100, "angle": 90}, {"x": 200, "y": 200, "angle": 270}],
        "walls": [{"x": 150, "y": 150, "width": 50, "height": 10}]
    }